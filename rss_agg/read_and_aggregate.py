import asyncio
import logging
from collections import OrderedDict
from datetime import UTC, datetime
from email.utils import format_datetime, parsedate_to_datetime
from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

import httpx
from defusedxml.ElementTree import fromstring

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Collection
    from pathlib import Path

    from yarl import URL

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
    async with httpx.AsyncClient(follow_redirects=True) as client:
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


def generate_new_rss_feed(items: list[ET.Element], limit: int = 50) -> str:
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "theguardian.com"
    ET.SubElement(channel, "description").text = "@brunns's curated, de-duplicated theguardian.com feed"
    ET.SubElement(channel, "link").text = "https://brunn.ing"

    newest_first = sorted(items, key=get_date, reverse=True)
    limited_items = newest_first[:limit]
    latest_published: datetime = datetime.min.replace(tzinfo=UTC)

    for item in limited_items:
        channel.append(item)
        pub_date = item.find("pubDate")
        if pub_date is not None and pub_date.text:
            item_published = get_date(item)
            latest_published = max(latest_published, item_published)

    if latest_published != datetime.min.replace(tzinfo=UTC):
        ET.SubElement(channel, "pubDate").text = format_datetime(latest_published)

    return ET.tostring(root, encoding="unicode")


async def read_and_generate_rss(base_url: URL, feeds_file: Path) -> str:
    with feeds_file.open() as f:
        feed_urls = [base_url / path.strip() / "rss" for path in f]

    items = await read_rss_feeds(feed_urls)
    return generate_new_rss_feed(items, limit=50)
