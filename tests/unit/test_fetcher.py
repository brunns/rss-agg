from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from hamcrest import assert_that, contains_inanyorder, empty
from yarl import URL

from rss_agg.services import Fetcher

if TYPE_CHECKING:
    from niquests_mock import MockRouter


@pytest.mark.asyncio
async def test_fetch_all_data_from_urls(niquests_mock: MockRouter):
    # Given
    fetcher = Fetcher(3, 16, 16, 3)
    niquests_mock.get("http://example.com/1").respond(status_code=HTTPStatus.OK, text="1")
    niquests_mock.get("http://example.com/2").respond(status_code=HTTPStatus.OK, text="2")

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/1"), URL("http://example.com/2")])

    # Then
    assert_that(actual, contains_inanyorder("1", "2"))


@pytest.mark.asyncio
async def test_skips_failed_feeds(niquests_mock: MockRouter):
    # Given
    fetcher = Fetcher(3, 16, 16, 3)
    niquests_mock.get("http://example.com/").respond(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/")])

    # Then
    assert_that(actual, empty())


@pytest.mark.asyncio
async def test_partial_failure_returns_successful_feeds(niquests_mock: MockRouter):
    # Given
    fetcher = Fetcher(3, 16, 16, 3)
    niquests_mock.get("http://example.com/1").respond(status_code=HTTPStatus.OK, text="1")
    niquests_mock.get("http://example.com/2").respond(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/1"), URL("http://example.com/2")])

    # Then
    assert_that(actual, contains_inanyorder("1"))


@pytest.mark.asyncio
async def test_handles_empty_text(niquests_mock: MockRouter):
    # Given
    fetcher = Fetcher(3, 16, 16, 3)
    niquests_mock.get("http://example.com/").respond(status_code=HTTPStatus.OK, text="")

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/")])

    # Then
    assert_that(actual, contains_inanyorder(""))
