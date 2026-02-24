from pathlib import Path

import pytest
from hamcrest import assert_that, contains_exactly, empty
from yarl import URL

from rss_agg.services import FeedsService
from rss_agg.types import BaseUrl, FeedsFile, FeedUrl


@pytest.mark.asyncio
async def test_feeds_service_returns_urls(fs):
    # Given
    feeds_file = Path("/tmp/feeds.txt")
    fs.create_file(str(feeds_file), contents="uk\nworld\n")
    service = FeedsService(FeedsFile(feeds_file), BaseUrl(URL("https://www.theguardian.com")))

    # When
    result = await service.get_feeds()

    # Then
    assert_that(
        result,
        contains_exactly(
            FeedUrl(URL("https://www.theguardian.com/uk/rss")),
            FeedUrl(URL("https://www.theguardian.com/world/rss")),
        ),
    )


@pytest.mark.asyncio
async def test_feeds_service_handles_empty_file(fs):
    # Given
    feeds_file = Path("/tmp/empty.txt")
    fs.create_file(str(feeds_file), contents="")
    service = FeedsService(FeedsFile(feeds_file), BaseUrl(URL("https://www.theguardian.com")))

    # When
    result = await service.get_feeds()

    # Then
    assert_that(result, empty())
