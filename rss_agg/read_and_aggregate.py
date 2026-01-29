import asyncio
import logging
from collections import OrderedDict
from datetime import UTC, datetime
from email.utils import format_datetime, parsedate_to_datetime
from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

import httpx
from defusedxml.ElementTree import fromstring
from yarl import URL

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Collection
    from pathlib import Path

FEED_TITLE = "@brunns's theguardian.com"
FEED_DESCRIPTION = "@brunns's curated, de-duplicated theguardian.com RSS feed"
FEED_LINK = URL("https://brunn.ing")
MAX_ITEMS = 50
MAX_CONNECTIONS = 32
ATOM_NS = "http://www.w3.org/2005/Atom"
DC_NS = "http://purl.org/dc/elements/1.1/"

logger = logging.getLogger(__name__)


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


async def read_rss_feeds(feed_urls: list[URL]) -> list[ET.Element]:
    items: dict[str, ET.Element] = OrderedDict()
    async with httpx.AsyncClient(follow_redirects=True, limits=httpx.Limits(max_connections=MAX_CONNECTIONS)) as client:
        tasks = [fetch(client, feed_url) for feed_url in feed_urls]
        responses: Collection[str] = await asyncio.gather(*tasks)
        for response in responses:
            if response:
                feed: ET.Element = fromstring(response)
                for item in feed.findall(".//item"):
                    if (guid := item.findtext("guid")) and guid not in items:
                        items[guid] = item
    return list(items.values())


def get_date(item: ET.Element) -> datetime:
    pub_date = item.find("pubDate")
    if pub_date is not None and pub_date.text:
        try:
            return parsedate_to_datetime(pub_date.text)
        except (ValueError, TypeError):  # pragma: no cover
            pass
    return datetime.min.replace(tzinfo=UTC)


def generate_new_rss_feed(items: list[ET.Element], self_url: URL, limit: int = 50) -> str:
    ET.register_namespace("atom", ATOM_NS)

    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = FEED_TITLE
    ET.SubElement(channel, "description").text = FEED_DESCRIPTION
    ET.SubElement(channel, "link").text = str(FEED_LINK)

    atom_link = ET.SubElement(channel, f"{{{ATOM_NS}}}link")
    atom_link.set("href", str(self_url))
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    newest_first = sorted(items, key=get_date, reverse=True)
    limited_items = newest_first[:limit]

    if limited_items:
        latest_date = get_date(limited_items[0])
        if latest_date != datetime.min.replace(tzinfo=UTC):
            ET.SubElement(channel, "pubDate").text = format_datetime(latest_date)

    for item in limited_items:
        for dc_date in item.findall(f"{{{DC_NS}}}date"):
            item.remove(dc_date)

        channel.append(item)

    ET.indent(root, space=" ")
    return ET.tostring(root, encoding="unicode")


async def read_and_generate_rss(base_url: URL, feeds_file: Path, self_url: URL) -> str:
    with feeds_file.open() as f:
        feed_urls = [base_url / path.strip() / "rss" for path in f]

    items = await read_rss_feeds(feed_urls)
    return generate_new_rss_feed(items, self_url=self_url, limit=MAX_ITEMS)
