from http import HTTPStatus

import httpx
import pytest
from hamcrest import assert_that, contains_inanyorder, empty
from yarl import URL

from rss_agg.services import Fetcher


@pytest.mark.asyncio
async def test_fetch_all_data_from_urls(respx_mock):
    # Given
    fetcher = Fetcher(3, 16, 16, 5, 3)
    respx_mock.get("http://example.com/1").mock(return_value=httpx.Response(HTTPStatus.OK, text="1"))
    respx_mock.get("http://example.com/2").mock(return_value=httpx.Response(HTTPStatus.OK, text="2"))

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/1"), URL("http://example.com/2")])

    # Then
    assert_that(actual, contains_inanyorder("1", "2"))


@pytest.mark.asyncio
async def test_skips_failed_feeds(respx_mock):
    # Given
    fetcher = Fetcher(3, 16, 16, 5, 3)
    respx_mock.get("http://example.com/").mock(return_value=httpx.Response(HTTPStatus.INTERNAL_SERVER_ERROR))

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/")])

    # Then
    assert_that(actual, empty())


@pytest.mark.asyncio
async def test_partial_failure_returns_successful_feeds(respx_mock):
    # Given
    fetcher = Fetcher(3, 16, 16, 5, 3)
    respx_mock.get("http://example.com/1").mock(return_value=httpx.Response(HTTPStatus.OK, text="1"))
    respx_mock.get("http://example.com/2").mock(return_value=httpx.Response(HTTPStatus.INTERNAL_SERVER_ERROR))

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/1"), URL("http://example.com/2")])

    # Then
    assert_that(actual, contains_inanyorder("1"))


@pytest.mark.asyncio
async def test_handles_empty_text(respx_mock):
    # Given
    fetcher = Fetcher(3, 16, 16, 5, 3)
    respx_mock.get("http://example.com/").mock(return_value=httpx.Response(HTTPStatus.OK, text=None))

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/")])

    # Then
    assert_that(actual, contains_inanyorder(""))
