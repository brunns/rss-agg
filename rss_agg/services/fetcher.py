import asyncio
import logging
from typing import TYPE_CHECKING, Annotated

from httpx import AsyncClient, AsyncHTTPTransport, Limits
from httpx import Timeout as HttpxTimeout
from wireup import Inject, injectable

from rss_agg.logging_utils import log_duration
from rss_agg.types import (
    FeedUrl,
    KeepaliveExpiry,
    MaxConnections,
    MaxKeepaliveConnections,
    Retries,
    RssContent,
    Timeout,
)

if TYPE_CHECKING:
    from collections.abc import Collection

logger = logging.getLogger(__name__)


@injectable
class Fetcher:
    def __init__(
        self,
        timeout: Annotated[Timeout, Inject(config="timeout")],
        max_connections: Annotated[MaxConnections, Inject(config="max_connections")],
        max_keepalive_connections: Annotated[MaxKeepaliveConnections, Inject(config="max_keepalive_connections")],
        keepalive_expiry: Annotated[KeepaliveExpiry, Inject(config="keepalive_expiry")],
        retries: Annotated[Retries, Inject(config="retries")],
    ) -> None:
        self.headers = {
            "User-Agent": "rss-aggregator/1.0 (+https://github.com/brunns/rss-agg)",
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9",
        }
        self.timeout = HttpxTimeout(timeout)
        self.limits = Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        )
        self.retries = retries

    async def fetch_all(self, feed_urls: list[FeedUrl]) -> Collection[RssContent]:
        transport = AsyncHTTPTransport(http2=True, retries=self.retries, limits=self.limits)
        async with AsyncClient(
            headers=self.headers, timeout=self.timeout, follow_redirects=True, transport=transport
        ) as client:
            tasks = [self.fetch(client, feed_url) for feed_url in feed_urls]
            results: list[RssContent | BaseException] = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, BaseException)]

    @staticmethod
    async def fetch(client: AsyncClient, url: FeedUrl) -> RssContent:
        try:
            with log_duration(logger.debug, "fetching feed", url=str(url)):
                response = await client.get(str(url))
                response.raise_for_status()
        except Exception as e:
            logger.exception("fetch failed", extra={"url": str(url), "error": str(e)}, exc_info=e)
            raise
        else:
            if response.text:
                return RssContent(response.text)
            logger.warning("empty response", extra={"url": str(url)})
            return RssContent("")
