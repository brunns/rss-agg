# Copyright 2024-2026 Simon Brunning
from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

import pytest
from hamcrest import assert_that, contains_inanyorder, empty, has_length, instance_of
from mockito import mock
from mockito.matchers import ANY
from yarl import URL

from rss_agg.services import Fetcher, RSSParser
from rss_agg.services.feeds_services.base_feeds_service import FeedsAndExclusions

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.asyncio
async def test_parses_rss(rss_string: str, when: Callable[..., Any]):
    # Given
    mock_fetcher = mock(Fetcher)
    when(mock_fetcher).fetch_all(ANY).thenReturn([rss_string])
    feeds_and_exclusions = FeedsAndExclusions([URL("https://example.com/")], [])

    parser = RSSParser(mock_fetcher)

    # When
    actual = await parser.read_rss_feeds(feeds_and_exclusions)

    # Then
    assert_that(actual, contains_inanyorder(instance_of(ET.Element), instance_of(ET.Element), instance_of(ET.Element)))


@pytest.mark.asyncio
async def test_deduplicates_on_guid(rss_string_with_duplicate_guids: str, when: Callable[..., Any]):
    # Given
    mock_fetcher = mock(Fetcher)
    when(mock_fetcher).fetch_all(ANY).thenReturn([rss_string_with_duplicate_guids])
    feeds_and_exclusions = FeedsAndExclusions([URL("https://example.com/")], [])

    parser = RSSParser(mock_fetcher)

    # When
    actual = await parser.read_rss_feeds(feeds_and_exclusions)

    # Then
    assert_that(actual, has_length(1))


@pytest.mark.asyncio
async def test_skips_items_without_guid(when: Callable[..., Any]):
    # Given - feed with one item that has a guid and one that doesn't
    feed_xml = (
        '<rss version="2.0"><channel>'
        "<item><title>Has GUID</title><guid>guid-1</guid></item>"
        "<item><title>No GUID</title></item>"
        "</channel></rss>"
    )
    mock_fetcher = mock(Fetcher)
    when(mock_fetcher).fetch_all(ANY).thenReturn([feed_xml])
    feeds_and_exclusions = FeedsAndExclusions([URL("https://example.com/")], [])

    parser = RSSParser(mock_fetcher)

    # When
    actual = await parser.read_rss_feeds(feeds_and_exclusions)

    # Then - only the item with a guid is returned
    assert_that(actual, has_length(1))


@pytest.mark.asyncio
async def test_handles_empty_response(when: Callable[..., Any]):
    # Given - fetcher returns an empty string (e.g. from a feed with no body)
    mock_fetcher = mock(Fetcher)
    when(mock_fetcher).fetch_all(ANY).thenReturn([""])
    feeds_and_exclusions = FeedsAndExclusions([URL("https://example.com/")], [])

    parser = RSSParser(mock_fetcher)

    # When
    actual = await parser.read_rss_feeds(feeds_and_exclusions)

    # Then
    assert_that(actual, empty())


@pytest.mark.asyncio
async def test_raises_on_invalid_xml(when: Callable[..., Any]):
    # Given - fetcher returns something that isn't XML at all
    mock_fetcher = mock(Fetcher)
    when(mock_fetcher).fetch_all(ANY).thenReturn(["not valid xml"])
    feeds_and_exclusions = FeedsAndExclusions([URL("https://example.com/")], [])

    parser = RSSParser(mock_fetcher)

    # When / Then - parse error propagates (not silently swallowed)
    with pytest.raises(ET.ParseError):
        await parser.read_rss_feeds(feeds_and_exclusions)


@pytest.mark.asyncio
async def test_ignores_items_with_category_matching_excluded(rss_string: str, when: Callable[..., Any]):
    # Given
    mock_fetcher = mock(Fetcher)
    when(mock_fetcher).fetch_all(ANY).thenReturn([rss_string])
    feeds_and_exclusions = FeedsAndExclusions([URL("https://example.com/")], [URL("https://example.com/article2")])

    parser = RSSParser(mock_fetcher)

    # When
    actual = await parser.read_rss_feeds(feeds_and_exclusions)
    links = [item.findtext("link") for item in actual]

    # Then
    assert_that(links, contains_inanyorder("https://example.com/article1", "https://example.com/article3"))
