from http import HTTPStatus

from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from hamcrest import assert_that, equal_to
from mockito import mock
from mockito.matchers import ANY

from rss_agg.services import RSSService
from tests.utils import async_value


def test_get_data_route_logic(client, container, when):
    # Given
    mock_service = mock(RSSService)
    expected_rss = "<rss>fake feed</rss>"

    when(mock_service).read_and_generate_rss(self_url=ANY).thenReturn(async_value(expected_rss))

    # When
    with container.override.injectable(RSSService, new=mock_service):
        response = client.get("/")

    # Then
    assert_that(
        response,
        is_response()
        .with_status_code(HTTPStatus.OK)
        .and_text(equal_to(expected_rss))
        .and_mimetype("application/rss+xml"),
    )
