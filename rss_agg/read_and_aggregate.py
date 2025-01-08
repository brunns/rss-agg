import asyncio
import logging
from collections import OrderedDict
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from time import mktime
from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

import httpx
from defusedxml.ElementTree import fromstring
from feedparser import datetimes
from yarl import URL

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Collection

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
        else:
            logger.warning("empty response from %s", url)
            return ""


async def read_rss_feeds(feed_urls: list[URL]) -> list[ET.Element]:
    items: dict[str, ET.Element] = OrderedDict()
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, feed_url) for feed_url in feed_urls]
        responses: Collection[str] = await asyncio.gather(*tasks)
        for response in responses:
            if response:
                feed: ET.Element = fromstring(response)
                for item in feed.findall(".//item"):
                    if (guid := item.findtext("guid")) and guid not in items:
                        items[guid] = item
    return list(items.values())


def generate_new_rss_feed(items: list[ET.Element]) -> str:
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "theguardian.com"
    ET.SubElement(channel, "description").text = "@brunns's curated, de-duplicated theguardian.com feed"
    ET.SubElement(channel, "link").text = "https://brunn.ing"
    latest_published: datetime = datetime.min
    for item in items:
        channel.append(item)
        pub_date = item.find("pubDate")
        if pub_date is not None:
            item_published = datetime.fromtimestamp(mktime(datetimes._parse_date(pub_date.text)))
            latest_published = max(latest_published, item_published)
    if latest_published != datetime.min:
        ET.SubElement(channel, "pubDate").text = format_datetime(latest_published)
    return ET.tostring(root, encoding="unicode")


async def read_and_generate_rss(base_url: URL, feeds_file: Path) -> str:
    with feeds_file.open() as f:
        feed_urls = [base_url / path.strip() / "rss" for path in f]

    items = await read_rss_feeds(feed_urls)
    return generate_new_rss_feed(items)
