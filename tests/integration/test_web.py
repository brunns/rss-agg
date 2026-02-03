from http import HTTPStatus

import pytest
from brunns.matchers.rss import is_rss_feed
from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from hamcrest import assert_that, has_length
from mbtest.imposters import Imposter, Predicate, Response, Stub

from rss_agg.flask_app_factory import create_app


def test_get_rss_from_over_the_wire_feed(mountebank_client):
    # When
    response = mountebank_client.get("/")

    # Then
    assert_that(
        response,
        is_response()
        .with_status_code(HTTPStatus.OK)
        .and_text(is_rss_feed().with_entries(has_length(3)))
        .and_mimetype("application/rss+xml"),
    )


@pytest.fixture
def mountebank_client(mock_server, rss_string, sausages_feeds_file):
    imposter = Imposter(Stub(Predicate(path="/sausages/rss"), Response(body=rss_string)), port=4545)

    with mock_server(imposter):
        app, _container = create_app({"base_url": imposter.url, "feeds_file": sausages_feeds_file})
        yield app.test_client()
