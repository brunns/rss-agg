from http import HTTPStatus

from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from hamcrest import assert_that, equal_to
from mockito import any as mock_any
from mockito import mock

from rss_agg.services import RSSService


def test_get_data_route_logic(client, container, when):
    # Given
    mock_service = mock(RSSService)
    expected_rss = "<rss>fake feed</rss>"

    async def make_coro():
        return expected_rss

    when(mock_service).read_and_generate_rss(base_url=mock_any(), self_url=mock_any()).thenReturn(make_coro())

    # When
    with container.override.service(RSSService, new=mock_service):
        response = client.get("/")

    # Then
    assert_that(
        response,
        is_response()
        .with_status_code(HTTPStatus.OK)
        .and_text(equal_to(expected_rss))
        .and_mimetype("application/rss+xml"),
    )
