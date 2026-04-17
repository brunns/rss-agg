from pathlib import Path
from typing import TYPE_CHECKING

from brunns.matchers.url import is_url
from hamcrest import assert_that, contains_exactly, empty
from yarl import URL

from rss_agg.domain import BaseUrl, FeedsFile
from rss_agg.services.feeds_services import FileFeedsService

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


def test_feeds_service_returns_urls(fs: FakeFilesystem):
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
            is_url().with_host("www.theguardian.com").and_path("/uk/rss"),
            is_url().with_host("www.theguardian.com").and_path("/world/rss"),
        ),
    )


def test_feeds_service_handles_empty_file(fs: FakeFilesystem):
    # Given
    feeds_file = Path("/tmp/empty.txt")
    fs.create_file(str(feeds_file), contents="")
    service = FileFeedsService(FeedsFile(feeds_file), BaseUrl(URL("https://www.theguardian.com")))

    # When
    result = service.get_feeds()

    # Then
    assert_that(result, empty())


def test_feeds_service_skips_blank_lines(fs: FakeFilesystem):
    # Given
    feeds_file = Path("/tmp/empty.txt")
    fs.create_file(str(feeds_file), contents="uk\n\nworld\n\n")
    service = FileFeedsService(FeedsFile(feeds_file), BaseUrl(URL("https://www.theguardian.com")))

    # When
    result = service.get_feeds()

    # Then
    assert_that(
        result,
        contains_exactly(
            is_url().with_host("www.theguardian.com").and_path("/uk/rss"),
            is_url().with_host("www.theguardian.com").and_path("/world/rss"),
        ),
    )
