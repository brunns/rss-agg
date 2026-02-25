from http import HTTPStatus

from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from flask import Flask
from hamcrest import assert_that, equal_to, instance_of
from mockito import mock
from mockito.matchers import ANY

from rss_agg.flask_app_factory import create_app
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


def test_health_endpoint(client):
    # When
    response = client.get("/health")

    # Then
    assert_that(response, is_response().with_status_code(HTTPStatus.OK).and_text(equal_to("OK")))


def test_create_app_with_s3_feeds_service():
    # When
    app, _ = create_app(
        {
            "feeds_service": "S3FeedsService",
            "aws_default_region": "us-east-1",
            "aws_access_key_id": "fake-key",
            "aws_secret_access_key": "fake-secret",
            "s3_endpoint": None,
            "feeds_bucket_name": "my-bucket",
            "feeds_object_name": "feeds.txt",
        }
    )

    # Then
    assert_that(app, instance_of(Flask))
