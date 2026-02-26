from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

import pytest
from hamcrest import assert_that, contains_inanyorder, has_length, instance_of
from mockito import mock
from mockito.matchers import ANY
from yarl import URL

from rss_agg.services import Fetcher, RSSParser
from tests.utils import async_value

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.asyncio
async def test_parses_rss(rss_string: str, when: Callable[..., Any]):
    # Given
    mock_fetcher = mock(Fetcher)
    when(mock_fetcher).fetch_all(ANY).thenReturn(async_value([rss_string]))

    parser = RSSParser(mock_fetcher)

    # When
    actual = await parser.read_rss_feeds([URL("https://example.com/")])

    # Then
    assert_that(actual, contains_inanyorder(instance_of(ET.Element), instance_of(ET.Element), instance_of(ET.Element)))


@pytest.mark.asyncio
async def test_deduplicates_on_guid(rss_string_with_duplicate_guids: str, when: Callable[..., Any]):
    # Given
    mock_fetcher = mock(Fetcher)
    when(mock_fetcher).fetch_all(ANY).thenReturn(async_value([rss_string_with_duplicate_guids]))

    parser = RSSParser(mock_fetcher)

    # When
    actual = await parser.read_rss_feeds([URL("https://example.com/")])

    # Then
    assert_that(actual, has_length(1))
