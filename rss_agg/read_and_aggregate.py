import asyncio
from collections import OrderedDict
from pathlib import Path
from xml.etree import ElementTree as ET

import aiohttp
import yarl


async def fetch_feed(session: aiohttp.ClientSession, url: yarl.URL) -> str:
    async with session.get(url) as response:
        return await response.text()


async def read_rss_feeds(feed_urls: list[yarl.URL]) -> list[ET.Element]:
    items: dict[str, ET.Element] = OrderedDict()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, feed_url) for feed_url in feed_urls]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            feed = ET.fromstring(response)
            for item in feed.findall(".//item"):
                if guid := item.findtext("guid"):
                    if guid not in items:
                        items[guid] = item
    return list(items.values())


def generate_new_rss_feed(items: list[ET.Element]) -> str:
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "theguardian.com"
    ET.SubElement(
        channel, "description"
    ).text = "@brunns's curated, de-duplicated theguardian.com feed"
    ET.SubElement(channel, "link").text = "https://brunn.ing"
    for item in items:
        channel.append(item)
    return ET.tostring(root, encoding="unicode")


async def read_and_generate_rss(base_url: yarl.URL, feeds_file: Path) -> str:
    with feeds_file.open() as f:
        feed_urls = [base_url / path.strip() / "rss" for path in f]

    items = await read_rss_feeds(feed_urls)
    new_rss_feed = generate_new_rss_feed(items)
    return new_rss_feed
