from unittest.mock import AsyncMock, MagicMock
from xml.etree import ElementTree as ET

import pytest
from hamcrest import assert_that, contains_inanyorder, has_length, instance_of
from yarl import URL

from rss_agg.services import Fetcher, RSSParser


@pytest.mark.asyncio
async def test_parses_rss(rss_string):
    # Given
    mock_fetcher = MagicMock(spec=Fetcher)
    mock_fetcher.fetch_all = AsyncMock(return_value=[rss_string])
    parser = RSSParser(mock_fetcher)

    # When
    actual = await parser.read_rss_feeds([URL("http://example.com/")])

    # Then
    assert_that(actual, contains_inanyorder(instance_of(ET.Element), instance_of(ET.Element), instance_of(ET.Element)))


@pytest.mark.asyncio
async def test_deduplicates_on_guid(rss_string_with_duplicate_guids):
    # Given
    mock_fetcher = MagicMock(spec=Fetcher)
    mock_fetcher.fetch_all = AsyncMock(return_value=[rss_string_with_duplicate_guids])
    parser = RSSParser(mock_fetcher)

    # When
    actual = await parser.read_rss_feeds([URL("http://example.com/")])

    # Then
    assert_that(actual, has_length(1))
