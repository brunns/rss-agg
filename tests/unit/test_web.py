import re
from datetime import UTC, datetime
from http import HTTPStatus
from xml.etree import ElementTree as ET

import httpx
import pytest
from brunns.matchers.rss import is_rss_entry, is_rss_feed
from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from hamcrest import assert_that, contains_inanyorder, equal_to, has_items, has_length, not_, not_none
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
        .and_mimetype("application/rss+xml")
        .and_text(
            is_rss_feed()
            .with_title("@brunns's theguardian.com")
            .and_link(URL("https://brunn.ing"))
            .and_description("@brunns's curated, de-duplicated theguardian.com RSS feed")
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
            .with_title("@brunns's theguardian.com")
            .and_link(URL("https://brunn.ing"))
            .and_description("@brunns's curated, de-duplicated theguardian.com RSS feed")
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
            .with_title("@brunns's theguardian.com")
            .and_link(URL("https://brunn.ing"))
            .and_description("@brunns's curated, de-duplicated theguardian.com RSS feed")
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


@pytest.mark.respx(base_url="https://www.theguardian.com")
def test_atom_link(respx_mock, rss_string):
    # Given
    respx_mock.get(re.compile(r".*")).mock(return_value=httpx.Response(HTTPStatus.OK, text=rss_string))

    # When
    response = app.test_client().get("/")

    # Then
    root = ET.fromstring(response.text)

    namespaces = {"atom": "http://www.w3.org/2005/Atom"}

    atom_link = root.find(".//channel/atom:link[@rel='self']", namespaces)

    assert_that(atom_link, not_none(), "Missing atom:link element")
    assert_that(atom_link.attrib["href"], equal_to("http://localhost/"))
    assert_that(atom_link.attrib["type"], equal_to("application/rss+xml"))


@pytest.mark.respx(base_url="https://www.theguardian.com")
def test_dublin_core_removal(respx_mock, rss_string):
    # Given
    respx_mock.get(re.compile(r".*")).mock(return_value=httpx.Response(HTTPStatus.OK, text=rss_string))

    # When
    response = app.test_client().get("/")

    # Then
    root = ET.fromstring(response.text)

    namespaces = {"dc": "http://purl.org/dc/elements/1.1/"}

    dc_dates = root.findall(".//dc:date", namespaces)

    assert_that(dc_dates, has_length(0), "Found forbidden dc:date elements that should have been stripped")
