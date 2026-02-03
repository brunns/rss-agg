import asyncio
import logging
from collections import OrderedDict
from datetime import UTC, datetime
from email.utils import format_datetime, parsedate_to_datetime
from pathlib import Path  # noqa: TC003
from typing import TYPE_CHECKING, Annotated
from xml.etree import ElementTree as ET

import httpx
from defusedxml.ElementTree import fromstring
from wireup import Inject, injectable
from yarl import URL

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Collection


logger = logging.getLogger(__name__)


@injectable
class RSSService:
    def __init__(
        self,
        parser: RSSParser,
        generator: RSSGenerator,
        base_url: Annotated[URL, Inject(config="base_url")],
        feeds_file: Annotated[Path, Inject(config="feeds_file")],
        max_items: Annotated[int, Inject(config="max_items")],
    ) -> None:
        self.parser = parser
        self.generator = generator
        self.base_url = base_url
        self.feeds_file = feeds_file
        self.max_items = max_items

    async def read_and_generate_rss(self, self_url: URL) -> str:
        with self.feeds_file.open() as f:
            feed_urls = [self.base_url / path.strip() / "rss" for path in f]

        items = await self.parser.read_rss_feeds(feed_urls)
        return self.generator.generate_new_rss_feed(items, self_url=self_url, limit=self.max_items)


@injectable
class RSSParser:
    def __init__(self, fetcher: Fetcher) -> None:
        self.fetcher = fetcher

    async def read_rss_feeds(self, feed_urls: list[URL]) -> list[ET.Element]:
        items: dict[str, ET.Element] = OrderedDict()
        responses = await self.fetcher.fetch_all(feed_urls)
        for response in responses:
            if response:
                feed: ET.Element = fromstring(response)
                for item in feed.findall(".//item"):
                    if (guid := item.findtext("guid")) and guid not in items:
                        items[guid] = item
        return list(items.values())


@injectable
class RSSGenerator:
    FEED_TITLE = "@brunns's theguardian.com"
    FEED_DESCRIPTION = "@brunns's curated, de-duplicated theguardian.com RSS feed"
    FEED_LINK = URL("https://brunn.ing")
    ATOM_NS = "http://www.w3.org/2005/Atom"
    DC_NS = "http://purl.org/dc/elements/1.1/"

    def generate_new_rss_feed(self, items: list[ET.Element], self_url: URL, limit: int = 50) -> str:
        ET.register_namespace("atom", RSSGenerator.ATOM_NS)

        root = ET.Element("rss", version="2.0")
        channel = ET.SubElement(root, "channel")
        ET.SubElement(channel, "title").text = RSSGenerator.FEED_TITLE
        ET.SubElement(channel, "description").text = RSSGenerator.FEED_DESCRIPTION
        ET.SubElement(channel, "link").text = str(RSSGenerator.FEED_LINK)

        atom_link = ET.SubElement(channel, f"{{{RSSGenerator.ATOM_NS}}}link")
        atom_link.set("href", str(self_url))
        atom_link.set("rel", "self")
        atom_link.set("type", "application/rss+xml")

        newest_first = sorted(items, key=self._get_date, reverse=True)
        limited_items = newest_first[:limit]

        if limited_items:
            latest_date = self._get_date(limited_items[0])
            if latest_date != datetime.min.replace(tzinfo=UTC):
                ET.SubElement(channel, "pubDate").text = format_datetime(latest_date)

        for item in limited_items:
            for dc_date in item.findall(f"{{{RSSGenerator.DC_NS}}}date"):
                item.remove(dc_date)

            channel.append(item)

        ET.indent(root, space=" ")
        return ET.tostring(root, encoding="unicode")

    @staticmethod
    def _get_date(item: ET.Element) -> datetime:
        pub_date = item.find("pubDate")
        if pub_date is not None and pub_date.text:
            try:
                return parsedate_to_datetime(pub_date.text)
            except (ValueError, TypeError):  # pragma: no cover
                pass
        return datetime.min.replace(tzinfo=UTC)


@injectable
class Fetcher:
    def __init__(self, max_connections: Annotated[int, Inject(config="max_connections")]) -> None:
        self.max_connections = max_connections

    async def fetch_all(self, feed_urls: list[URL]) -> Collection[str]:
        async with httpx.AsyncClient(
            follow_redirects=True, limits=httpx.Limits(max_connections=self.max_connections)
        ) as client:
            tasks = [self.fetch(client, feed_url) for feed_url in feed_urls]
            responses: Collection[str] = await asyncio.gather(*tasks)
        return responses

    @staticmethod
    async def fetch(client: httpx.AsyncClient, url: URL) -> str:
        try:
            logger.info("getting from %s", url)
            response = await client.get(str(url))
            response.raise_for_status()
        except Exception as e:
            logger.exception("Unexpected", exc_info=e)
            raise
        else:
            if response.text:
                return response.text
            logger.warning("empty response from %s", url)
            return ""
