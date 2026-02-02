from http import HTTPStatus

import httpx
import pytest
from hamcrest import assert_that, contains_inanyorder
from yarl import URL

from rss_agg.read_and_aggregate import Fetcher


@pytest.mark.asyncio
async def test_fetch_all_data_from_urls(respx_mock):
    # Given
    fetcher = Fetcher()
    respx_mock.get("http://example.com/1").mock(return_value=httpx.Response(HTTPStatus.OK, text="1"))
    respx_mock.get("http://example.com/2").mock(return_value=httpx.Response(HTTPStatus.OK, text="2"))

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/1"), URL("http://example.com/2")])

    # Then
    assert_that(actual, contains_inanyorder("1", "2"))


@pytest.mark.asyncio
async def test_passes_exceptions_thru(respx_mock):
    # Given
    fetcher = Fetcher()
    respx_mock.get("http://example.com/").mock(return_value=httpx.Response(HTTPStatus.INTERNAL_SERVER_ERROR))

    # When
    with pytest.raises(httpx.HTTPError):
        await fetcher.fetch_all([URL("http://example.com/")])


@pytest.mark.asyncio
async def test_handles_empth_text(respx_mock):
    # Given
    fetcher = Fetcher()
    respx_mock.get("http://example.com/").mock(return_value=httpx.Response(HTTPStatus.OK, text=None))

    # When
    actual = await fetcher.fetch_all([URL("http://example.com/")])

    # Then
    assert_that(actual, contains_inanyorder(""))
