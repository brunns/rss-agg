#!/usr/bin/env python3

import asyncio
import xml.etree.ElementTree as ET
from collections import OrderedDict

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
                guid: str | None = item.findtext("guid") or item.findtext("id") or None
                if guid and guid not in items:
                    items[guid] = item
    return list(items.values())


def generate_new_rss_feed(items: list[ET.Element]):
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


async def read_and_generate_rss():
    base_url = yarl.URL("https://www.theguardian.com")
    with open("feeds.txt") as f:
        feed_urls = [base_url / path.strip() / "rss" for path in f]

    items = await read_rss_feeds(feed_urls)
    new_rss_feed = generate_new_rss_feed(items)
    print(new_rss_feed)


def main():
    asyncio.run(read_and_generate_rss())


if __name__ == "__main__":
    main()
