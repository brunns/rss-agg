from typing import Annotated

from boto3 import Session
from botocore.client import BaseClient  # noqa: TC002
from wireup import Inject, injectable

from rss_agg.services.feeds_services.base_feeds_service import FeedsService
from rss_agg.types import (
    AwsAccessKey,
    AwsRegion,
    AwsSecretAccessKey,
    BaseUrl,
    BucketName,
    FeedUrl,
    ObjectName,
    S3Endpoint,
)


@injectable
def boto3_session_factory(
    aws_default_region: Annotated[AwsRegion, Inject(config="aws_default_region")],
    aws_access_key_id: Annotated[AwsAccessKey, Inject(config="aws_access_key_id")],
    aws_secret_access_key: Annotated[AwsSecretAccessKey, Inject(config="aws_secret_access_key")],
) -> Session:
    return Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_default_region,
    )


@injectable(qualifier="s3")
def s3_client_factory(
    session: Session,
    s3_endpoint: Annotated[S3Endpoint, Inject(config="s3_endpoint")],
) -> BaseClient:
    endpoint_url = str(s3_endpoint) if s3_endpoint is not None else None
    return session.client("s3", endpoint_url=endpoint_url)


@injectable(as_type=FeedsService)
class S3FeedsService(FeedsService):
    def __init__(
        self,
        s3_client: Annotated[BaseClient, Inject(qualifier="s3")],
        bucket_name: Annotated[BucketName, Inject(config="feeds_bucket_name")],
        object_name: Annotated[ObjectName, Inject(config="feeds_object_name")],
        base_url: Annotated[BaseUrl, Inject(config="base_url")],
    ) -> None:
        self.s3_client = s3_client
        self.base_url = base_url
        self.bucket_name = bucket_name
        self.object_name = object_name

    def get_feeds(self) -> list[FeedUrl]:
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=self.object_name)
        content = response["Body"].read().decode()
        return [FeedUrl(self.base_url / path.strip() / "rss") for path in content.splitlines()]


S3_INJECTABLES = [boto3_session_factory, s3_client_factory, S3FeedsService]
