# Copyright 2024-2026 Simon Brunning
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
    feeds_and_exclusions = service.get_feeds_and_exclusions()

    # Then
    assert_that(
        feeds_and_exclusions.feeds,
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
    feeds_and_exclusions = service.get_feeds_and_exclusions()

    # Then
    assert_that(feeds_and_exclusions.feeds, empty())


def test_feeds_service_skips_blank_lines(fs: FakeFilesystem):
    # Given
    feeds_file = Path("/tmp/empty.txt")
    fs.create_file(str(feeds_file), contents="uk\n\nworld")
    service = FileFeedsService(FeedsFile(feeds_file), BaseUrl(URL("https://www.theguardian.com")))

    # When
    feeds_and_exclusions = service.get_feeds_and_exclusions()

    # Then
    assert_that(
        feeds_and_exclusions.feeds,
        contains_exactly(
            is_url().with_host("www.theguardian.com").and_path("/uk/rss"),
            is_url().with_host("www.theguardian.com").and_path("/world/rss"),
        ),
    )


def test_feeds_service_ignores_commented_lines(fs: FakeFilesystem):
    # Given
    feeds_file = Path("/tmp/empty.txt")
    fs.create_file(str(feeds_file), contents="uk\n\nworld\n\n#sausages\n\n# chips")
    service = FileFeedsService(FeedsFile(feeds_file), BaseUrl(URL("https://www.theguardian.com")))

    # When
    feeds_and_exclusions = service.get_feeds_and_exclusions()

    # Then
    assert_that(
        feeds_and_exclusions.feeds,
        contains_exactly(
            is_url().with_host("www.theguardian.com").and_path("/uk/rss"),
            is_url().with_host("www.theguardian.com").and_path("/world/rss"),
        ),
    )


def test_file_feeds_service_returns_excluded_tags(fs: FakeFilesystem):
    # Given
    feeds_file = Path("/tmp/empty.txt")
    fs.create_file(str(feeds_file), contents="uk\n\nworld\n\n- football\n\n")
    service = FileFeedsService(FeedsFile(feeds_file), BaseUrl(URL("https://www.theguardian.com")))

    # When
    feeds_and_exclusions = service.get_feeds_and_exclusions()

    # Then
    assert_that(
        feeds_and_exclusions.exclusions,
        contains_exactly(
            is_url().with_host("www.theguardian.com").and_path("/football"),
        ),
    )
