from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from hamcrest import assert_that, contains_inanyorder, empty
from yarl import URL

from rss_agg.services import Fetcher

if TYPE_CHECKING:
    from respx import Router


@pytest.mark.asyncio
async def test_fetch_all_data_from_urls(httpx2_mock: Router):
    # Given
    fetcher = Fetcher(3, 16, 16, 5, 3)
    httpx2_mock.get("http://example.com/1").respond(HTTPStatus.OK, text="1")
    httpx2_mock.get("http://example.com/2").respond(HTTPStatus.OK, text="2")
    # When
    actual = await fetcher.fetch_all([URL("http://example.com/1"), URL("http://example.com/2")])

    # Then
    assert_that(actual, contains_inanyorder("1", "2"))


@pytest.mark.asyncio
async def test_skips_failed_feeds(httpx2_mock: Router):
    # Given
    fetcher = Fetcher(3, 16, 16, 5, 3)
    httpx2_mock.get("http://example.com/").respond(HTTPStatus.INTERNAL_SERVER_ERROR)

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/")])

    # Then
    assert_that(actual, empty())


@pytest.mark.asyncio
async def test_partial_failure_returns_successful_feeds(httpx2_mock: Router):
    # Given
    fetcher = Fetcher(3, 16, 16, 5, 3)
    httpx2_mock.get("http://example.com/1").respond(HTTPStatus.OK, text="1")
    httpx2_mock.get("http://example.com/2").respond(HTTPStatus.INTERNAL_SERVER_ERROR)

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/1"), URL("http://example.com/2")])

    # Then
    assert_that(actual, contains_inanyorder("1"))


@pytest.mark.asyncio
async def test_handles_empty_text(httpx2_mock: Router):
    # Given
    fetcher = Fetcher(3, 16, 16, 5, 3)
    httpx2_mock.get("http://example.com/").respond(HTTPStatus.OK, text=None)

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/")])

    # Then
    assert_that(actual, contains_inanyorder(""))
