import asyncio
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from hamcrest import assert_that, equal_to
from mockito import mock, when
from yarl import URL

from rss_agg.read_and_aggregate import RSSGenerator, RSSParser, RSSService


@pytest.mark.asyncio
async def test_rss_service_orchestration_mockito(fs):
    # Given
    feeds_content = "uk\nworld\n"
    feeds_file = Path("/tmp/feeds.txt")
    fs.create_file(str(feeds_file), contents=feeds_content)

    base_url = URL("https://www.theguardian.com")
    self_url = URL("https://myfeed.com")

    expected_urls = [
        URL("https://www.theguardian.com/uk/rss"),
        URL("https://www.theguardian.com/world/rss"),
    ]

    mock_items = [ET.Element("item"), ET.Element("item")]
    mock_parser = mock(RSSParser)

    future = asyncio.Future()
    future.set_result(mock_items)

    when(mock_parser).read_rss_feeds(expected_urls).thenReturn(future)

    expected_xml = "<rss>dummy</rss>"
    mock_generator = mock(RSSGenerator)
    when(mock_generator).generate_new_rss_feed(mock_items, self_url=self_url, limit=RSSService.MAX_ITEMS).thenReturn(
        expected_xml
    )

    service = RSSService(mock_parser, mock_generator)

    # When
    actual = await service.read_and_generate_rss(base_url, feeds_file, self_url)

    # Then
    assert_that(actual, equal_to(expected_xml))


@pytest.mark.asyncio
async def test_rss_service_handles_empty_feeds_file(fs):
    # Given
    feeds_file = Path("/tmp/empty.txt")
    fs.create_file(str(feeds_file), contents="")

    base_url = URL("https://www.theguardian.com")
    self_url = URL("https://myfeed.com")

    expected_urls = []
    mock_parser = mock(RSSParser)

    future = asyncio.Future()
    future.set_result(expected_urls)

    when(mock_parser).read_rss_feeds(expected_urls).thenReturn(future)

    expected_xml = "<rss>dummy</rss>"
    mock_generator = mock(RSSGenerator)
    when(mock_generator).generate_new_rss_feed(expected_urls, self_url=self_url, limit=RSSService.MAX_ITEMS).thenReturn(
        expected_xml
    )

    service = RSSService(mock_parser, mock_generator)

    # When
    actual = await service.read_and_generate_rss(base_url, feeds_file, self_url)

    # Then
    assert_that(actual, equal_to(expected_xml))
