from boto3 import Session
from hamcrest import assert_that, contains_exactly, instance_of, same_instance
from mockito import mock, when
from yarl import URL

from rss_agg.services.feeds_services.s3_feeds_service import S3FeedsService, boto3_session_factory, s3_client_factory
from rss_agg.types import AwsAccessKey, AwsRegion, AwsSecretAccessKey, BaseUrl, BucketName, FeedUrl, ObjectName


def test_s3_feeds_service_returns_urls():
    # Given
    body = mock()
    when(body).read().thenReturn(b"uk\nworld\n")
    s3_client = mock()
    when(s3_client).get_object(Bucket="my-bucket", Key="feeds.txt").thenReturn({"Body": body})
    service = S3FeedsService(
        s3_client,
        BucketName("my-bucket"),
        ObjectName("feeds.txt"),
        BaseUrl(URL("https://www.theguardian.com")),
    )

    # When
    result = service.get_feeds()

    # Then
    assert_that(
        result,
        contains_exactly(
            FeedUrl(URL("https://www.theguardian.com/uk/rss")),
            FeedUrl(URL("https://www.theguardian.com/world/rss")),
        ),
    )


def test_boto3_session_factory():
    # When
    result = boto3_session_factory(AwsRegion("us-east-1"), AwsAccessKey("fake-key"), AwsSecretAccessKey("fake-secret"))

    # Then
    assert_that(result, instance_of(Session))


def test_s3_client_factory_without_endpoint():
    # Given
    session = mock(Session)
    s3_client = mock()
    when(session).client("s3", endpoint_url=None).thenReturn(s3_client)

    # When
    result = s3_client_factory(session, None)

    # Then
    assert_that(result, same_instance(s3_client))


def test_s3_client_factory_with_endpoint():
    # Given
    session = mock(Session)
    s3_client = mock()
    endpoint = URL("http://localhost:9000")
    when(session).client("s3", endpoint_url="http://localhost:9000").thenReturn(s3_client)

    # When
    result = s3_client_factory(session, endpoint)

    # Then
    assert_that(result, same_instance(s3_client))
