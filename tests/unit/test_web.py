import asyncio
from http import HTTPStatus

import pytest
from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from flask import request
from hamcrest import assert_that, equal_to
from mockito import any as mock_any
from mockito import mock
from werkzeug.test import TestResponse

from rss_agg.services import RSSService
from rss_agg.web import app, container, get_data


@pytest.mark.asyncio
async def test_get_data_route_logic(when):
    # Given
    mock_service = mock(RSSService)
    expected_rss = "<rss>fake feed</rss>"

    future = asyncio.Future()
    future.set_result(expected_rss)

    when(mock_service).read_and_generate_rss(base_url=mock_any(), self_url=mock_any()).thenReturn(future)

    with container.override.service(RSSService, new=mock_service), app.test_request_context("/"):
        # When
        response = await get_data()
        test_response = TestResponse(
            response.response,
            response.status,
            response.headers,
            request=request._get_current_object(),  # noqa: SLF001
        )

    # Then
    assert_that(
        test_response,
        is_response()
        .with_status_code(HTTPStatus.OK)
        .and_text(equal_to(expected_rss))
        .and_mimetype("application/rss+xml"),
    )
