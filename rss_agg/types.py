from pathlib import Path
from typing import NewType

from yarl import URL

BaseUrl = NewType("BaseUrl", URL)
FeedDescription = NewType("FeedDescription", str)
FeedLink = NewType("FeedLink", URL)
FeedTitle = NewType("FeedTitle", str)
FeedUrl = NewType("FeedUrl", URL)
FeedsFile = NewType("FeedsFile", Path)
KeepaliveExpiry = NewType("KeepaliveExpiry", int)
MaxConnections = NewType("MaxConnections", int)
MaxItems = NewType("MaxItems", int)
MaxKeepaliveConnections = NewType("MaxKeepaliveConnections", int)
Retries = NewType("Retries", int)
Timeout = NewType("Timeout", int)
