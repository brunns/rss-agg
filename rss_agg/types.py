from pathlib import Path
from typing import Literal, NewType

from yarl import URL

AwsAccessKey = NewType("AwsAccessKey", str)
AwsRegion = NewType("AwsRegion", str)
AwsSecretAccessKey = NewType("AwsSecretAccessKey", str)
BaseUrl = NewType("BaseUrl", URL)
BucketName = NewType("BucketName", str)
FeedDescription = NewType("FeedDescription", str)
FeedLink = NewType("FeedLink", URL)
FeedTitle = NewType("FeedTitle", str)
FeedUrl = NewType("FeedUrl", URL)
FeedsFile = NewType("FeedsFile", Path)
FeedsServiceName = Literal["FileFeedsService", "S3FeedsService"]
KeepaliveExpiry = NewType("KeepaliveExpiry", int)
MaxConnections = NewType("MaxConnections", int)
MaxItems = NewType("MaxItems", int)
MaxKeepaliveConnections = NewType("MaxKeepaliveConnections", int)
ObjectName = NewType("ObjectName", str)
Retries = NewType("Retries", int)
RssContent = NewType("RssContent", str)
S3Endpoint = NewType("S3Endpoint", URL)
Timeout = NewType("Timeout", int)
