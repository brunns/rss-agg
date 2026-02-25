from pathlib import Path

from hamcrest import assert_that, contains_exactly, empty
from yarl import URL

from rss_agg.services.feeds_services import FileFeedsService
from rss_agg.types import BaseUrl, FeedsFile, FeedUrl


def test_feeds_service_returns_urls(fs):
    # Given
    feeds_file = Path("/tmp/feeds.txt")
    fs.create_file(str(feeds_file), contents="uk\nworld\n")
    service = FileFeedsService(FeedsFile(feeds_file), BaseUrl(URL("https://www.theguardian.com")))

    # When
    result = service.get_feeds()

    # Then
    assert_that(
        result,
        contains_exactly(
            FeedUrl(URL("https://www.theguardian.com/uk/rss")),
            FeedUrl(URL("https://www.theguardian.com/world/rss")),
        ),
    )


def test_feeds_service_handles_empty_file(fs):
    # Given
    feeds_file = Path("/tmp/empty.txt")
    fs.create_file(str(feeds_file), contents="")
    service = FileFeedsService(FeedsFile(feeds_file), BaseUrl(URL("https://www.theguardian.com")))

    # When
    result = service.get_feeds()

    # Then
    assert_that(result, empty())
