from http import HTTPStatus

from brunns.matchers.rss import is_rss_feed
from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from hamcrest import assert_that


def test_get_rss_from_guardian_integration(client):
    # When
    response = client.get("/")

    # Then
    assert_that(
        response,
        is_response().with_status_code(HTTPStatus.OK).and_text(is_rss_feed()).and_mimetype("application/rss+xml"),
    )
