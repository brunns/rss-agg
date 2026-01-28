import re
from datetime import UTC, datetime
from http import HTTPStatus

import httpx
import pytest
from brunns.matchers.rss import is_rss_entry, is_rss_feed
from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from hamcrest import assert_that, contains_inanyorder, has_items, has_length, not_
from yarl import URL

from rss_agg.web import app


@pytest.mark.respx(base_url="https://www.theguardian.com")
def test_get_data_returns_rss_response(respx_mock, rss_string):
    # Given
    respx_mock.get(re.compile(r".*")).mock(return_value=httpx.Response(HTTPStatus.OK, text=rss_string))

    # When
    response = app.test_client().get("/")

    # Then
    assert_that(
        response,
        is_response()
        .with_status_code(HTTPStatus.OK)
        .and_text(
            is_rss_feed()
            .with_title("theguardian.com")
            .and_link(URL("https://brunn.ing"))
            .and_description("@brunns's curated, de-duplicated theguardian.com feed")
            .and_published(datetime(2009, 9, 6, 15, 20, tzinfo=UTC))
            .and_entries(
                contains_inanyorder(
                    is_rss_entry().with_title("Test article 1").and_link(URL("https://example.com/article1")),
                    is_rss_entry().with_title("Test article 2").and_link(URL("https://example.com/article2")),
                    is_rss_entry().with_title("Test article 3").and_link(URL("https://example.com/article3")),
                )
            )
        )
        .and_mimetype("application/rss+xml"),
    )


@pytest.mark.respx(base_url="https://www.theguardian.com")
def test_get_data_handles_empty_rss(respx_mock, empty_rss_string):
    # Given
    respx_mock.get(re.compile(r".*")).mock(return_value=httpx.Response(HTTPStatus.OK, text=empty_rss_string))

    # When
    response = app.test_client().get("/")

    # Then
    assert_that(
        response,
        is_response()
        .with_status_code(HTTPStatus.OK)
        .and_text(
            is_rss_feed()
            .with_title("theguardian.com")
            .and_link(URL("https://brunn.ing"))
            .and_description("@brunns's curated, de-duplicated theguardian.com feed")
        )
        .and_mimetype("application/rss+xml"),
    )


def test_get_data_handles_exception(respx_mock):
    # Given
    respx_mock.get(re.compile(r".*")).mock(return_value=httpx.Response(HTTPStatus.INTERNAL_SERVER_ERROR))

    # When
    response = app.test_client().get("/")

    # Then
    assert_that(response, is_response().with_status_code(HTTPStatus.INTERNAL_SERVER_ERROR))


def test_empty_response(respx_mock):
    # Given
    respx_mock.get(re.compile(r".*")).mock(return_value=httpx.Response(HTTPStatus.OK, text=""))

    # When
    response = app.test_client().get("/")

    # Then
    assert_that(
        response,
        is_response()
        .with_status_code(HTTPStatus.OK)
        .and_text(
            is_rss_feed()
            .with_title("theguardian.com")
            .and_link(URL("https://brunn.ing"))
            .and_description("@brunns's curated, de-duplicated theguardian.com feed")
        )
        .and_mimetype("application/rss+xml"),
    )


@pytest.mark.respx(base_url="https://www.theguardian.com")
def test_get_data_limits_to_50_newest_items(respx_mock, large_rss_string):
    respx_mock.get(re.compile(r".*")).mock(return_value=httpx.Response(HTTPStatus.OK, text=large_rss_string))

    # When
    response = app.test_client().get("/")

    # Then
    assert_that(
        response,
        is_response()
        .with_status_code(HTTPStatus.OK)
        .and_text(
            is_rss_feed()
            .and_entries(has_length(50))
            .and_entries(
                has_items(
                    is_rss_entry().with_title("Test article 59"),
                    is_rss_entry().with_title("Test article 10"),
                )
            )
            .and_entries(
                not_(
                    has_items(
                        is_rss_entry().with_title("Test article 1"),
                        is_rss_entry().with_title("Test article 9"),
                    )
                )
            )
        ),
    )
