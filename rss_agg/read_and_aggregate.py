import asyncio
from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING
from xml.etree import ElementTree

import aiohttp
from defusedxml.ElementTree import fromstring
from yarl import URL

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Collection


async def fetch(session: aiohttp.ClientSession, url: URL) -> str:
    async with session.get(url) as response:
        return await response.text()


async def read_rss_feeds(feed_urls: list[URL]) -> list[ElementTree.Element]:
    items: dict[str, ElementTree.Element] = OrderedDict()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, feed_url) for feed_url in feed_urls]
        responses: Collection[str] = await asyncio.gather(*tasks)
        for response in responses:
            feed: ElementTree.Element = fromstring(response)
            for item in feed.findall(".//item"):
                if (guid := item.findtext("guid")) and guid not in items:
                    items[guid] = item
    return list(items.values())


def generate_new_rss_feed(items: list[ElementTree.Element]) -> str:
    root = ElementTree.Element("rss", version="2.0")
    channel = ElementTree.SubElement(root, "channel")
    ElementTree.SubElement(channel, "title").text = "theguardian.com"
    ElementTree.SubElement(
        channel, "description"
    ).text = "@brunns's curated, de-duplicated theguardian.com feed"
    ElementTree.SubElement(channel, "link").text = "https://brunn.ing"
    for item in items:
        channel.append(item)
    return ElementTree.tostring(root, encoding="unicode")


async def read_and_generate_rss(base_url: URL, feeds_file: Path) -> str:
    with feeds_file.open() as f:
        feed_urls = [base_url / path.strip() / "rss" for path in f]

    items = await read_rss_feeds(feed_urls)
    return generate_new_rss_feed(items)
