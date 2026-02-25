from http import HTTPStatus
from typing import Any

import boto3
import pytest
from brunns.matchers.rss import is_rss_feed
from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from hamcrest import assert_that, has_length
from mbtest.imposters import Imposter, Predicate, Response, Stub

from rss_agg.flask_app_factory import create_app


def test_get_rss_from_over_the_wire_feed(client_with_fake_upstream):
    # When
    response = client_with_fake_upstream.get("/")

    # Then
    assert_that(
        response,
        is_response()
        .with_status_code(HTTPStatus.OK)
        .and_text(is_rss_feed().with_entries(has_length(3)))
        .and_mimetype("application/rss+xml"),
    )


def test_get_rss_from_s3_feeds_file(client_with_fake_upstream_and_s3_feeds):
    # When
    response = client_with_fake_upstream_and_s3_feeds.get("/")

    # Then
    assert_that(
        response,
        is_response()
        .with_status_code(HTTPStatus.OK)
        .and_text(is_rss_feed().with_entries(has_length(3)))
        .and_mimetype("application/rss+xml"),
    )


@pytest.fixture
def client_with_fake_upstream(mock_server, rss_string, sausages_feeds_file):
    imposter = Imposter(Stub(Predicate(path="/sausages/rss"), Response(body=rss_string)), port=4545)

    with mock_server(imposter):
        app, _container = create_app({"base_url": imposter.url, "feeds_file": sausages_feeds_file})
        yield app.test_client()


@pytest.fixture
def client_with_fake_upstream_and_s3_feeds(mock_server, rss_string, s3_config: dict[str, Any]):
    s3 = boto3.client(
        "s3",
        endpoint_url=str(s3_config["s3_endpoint"]),
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
        region_name=s3_config["aws_default_region"],
    )
    s3.put_object(Bucket=s3_config["feeds_bucket_name"], Key="feeds.txt", Body=b"sausages")

    imposter = Imposter(Stub(Predicate(path="/sausages/rss"), Response(body=rss_string)), port=4545)
    with mock_server(imposter):
        app, _ = create_app(
            {
                **s3_config,
                "feeds_service": "S3FeedsService",
                "feeds_object_name": "feeds.txt",
                "base_url": imposter.url,
            }
        )
        yield app.test_client()
