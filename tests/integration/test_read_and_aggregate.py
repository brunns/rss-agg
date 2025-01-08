from pathlib import Path
from xml.etree.ElementTree import Element

import feedparser
import httpx
import pytest
from mbtest.imposters import Imposter, Predicate, Response, Stub
from mbtest.server import MountebankServer
from pyfakefs.fake_filesystem import FakeFilesystem
from yarl import URL

from rss_agg.read_and_aggregate import (
    fetch,
    generate_new_rss_feed,
    read_and_generate_rss,
    read_rss_feeds,
)


@pytest.mark.asyncio()
async def test_fetch_feed(mock_server: MountebankServer, rss_string: str):
    imposter = Imposter(Stub(Predicate(path="/valid"), Response(body=rss_string)), port=4545)
    with mock_server(imposter):
        imposter_url = imposter.url

        url = URL(str(imposter_url)) / "valid"
        async with httpx.AsyncClient() as client:
            feed = await fetch(client, url)
        assert feed is not None
        assert "title" in feed


@pytest.mark.asyncio()
async def test_read_rss_feeds(mock_server: MountebankServer, rss_string: str):
    imposter = Imposter(
        stubs=[
            Stub(Predicate(path="/valid1"), Response(body=rss_string)),
            Stub(Predicate(path="/valid2"), Response(body=rss_string)),
        ],
        port=4545,
    )

    with mock_server(imposter):
        # Test reading a list of feeds
        imposter_url = imposter.url

        feed_urls = [URL(str(imposter_url)) / "valid1", URL(str(imposter_url)) / "valid2"]
        feeds = await read_rss_feeds(feed_urls)
        assert feeds
        assert len(feeds) == 2

        # Test reading an empty list of feeds
        feed_urls = []
        feeds = await read_rss_feeds(feed_urls)
        assert not feeds


def test_generate_new_rss_feed_creates_correct_rss():
    items = [Element("item", {"guid": "1"}), Element("item", {"guid": "2"})]
    rss_feed = generate_new_rss_feed(items)
    assert "<rss" in rss_feed
    assert "<channel" in rss_feed
    assert "<item" in rss_feed
    assert "theguardian.com" in rss_feed


@pytest.mark.asyncio()
async def test_read_and_generate_rss_creates_aggregated_feed(
    mock_server: MountebankServer, rss_string: str, fs: FakeFilesystem
):
    imposter = Imposter(
        stubs=[
            Stub(Predicate(path="/valid1/rss"), Response(body=rss_string)),
            Stub(Predicate(path="/valid2/rss"), Response(body=rss_string)),
        ],
        port=4545,
    )

    feed_urls = ["valid1", "valid2"]
    file_path = "/foo/bar/test.txt"
    fs.create_file(file_path, contents="\n".join(feed_urls))
    feeds_file = Path(file_path)

    with mock_server(imposter):
        rss_text = await read_and_generate_rss(URL(str(imposter.url)), feeds_file=feeds_file)
        rss = feedparser.parse(rss_text)
        assert rss.feed.title == "theguardian.com"
