from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

import pytest
from hamcrest import assert_that, equal_to
from mockito import mock
from yarl import URL

from rss_agg.services import FeedsService, RSSGenerator, RSSParser, RSSService
from tests.utils import async_value

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.asyncio
async def test_rss_service_orchestration(when: Callable[..., Any]):
    # Given
    self_url = URL("https://myfeed.com")
    expected_urls = [
        URL("https://www.theguardian.com/uk/rss"),
        URL("https://www.theguardian.com/world/rss"),
    ]

    mock_feeds_service = mock(FeedsService)
    when(mock_feeds_service).get_feeds().thenReturn(expected_urls)

    mock_items = [ET.Element("item"), ET.Element("item")]
    mock_parser = mock(RSSParser)
    when(mock_parser).read_rss_feeds(expected_urls).thenReturn(async_value(mock_items))

    expected_xml = "<rss>dummy</rss>"
    mock_generator = mock(RSSGenerator)
    when(mock_generator).generate_new_rss_feed(mock_items, self_url=self_url, limit=50).thenReturn(expected_xml)

    service = RSSService(mock_feeds_service, mock_parser, mock_generator, 50)

    # When
    actual = await service.read_and_generate_rss(self_url)

    # Then
    assert_that(actual, equal_to(expected_xml))


@pytest.mark.asyncio
async def test_rss_service_handles_empty_feeds(when: Callable[..., Any]):
    # Given
    self_url = URL("https://myfeed.com")

    mock_feeds_service = mock(FeedsService)
    when(mock_feeds_service).get_feeds().thenReturn([])

    mock_parser = mock(RSSParser)
    when(mock_parser).read_rss_feeds([]).thenReturn(async_value([]))

    expected_xml = "<rss>dummy</rss>"
    mock_generator = mock(RSSGenerator)
    when(mock_generator).generate_new_rss_feed([], self_url=self_url, limit=50).thenReturn(expected_xml)

    service = RSSService(mock_feeds_service, mock_parser, mock_generator, 50)

    # When
    actual = await service.read_and_generate_rss(self_url)

    # Then
    assert_that(actual, equal_to(expected_xml))
