import asyncio
import logging
from typing import TYPE_CHECKING, Annotated

from httpx import AsyncClient, AsyncHTTPTransport, Limits, Timeout
from wireup import Inject, injectable

if TYPE_CHECKING:
    from collections.abc import Collection

    from yarl import URL

logger = logging.getLogger(__name__)


@injectable
class Fetcher:
    def __init__(
        self,
        timeout: Annotated[int, Inject(config="timeout")],
        max_connections: Annotated[int, Inject(config="max_connections")],
    ) -> None:
        self.headers = {
            "User-Agent": "rss-aggregator/1.0 (+https://github.com/brunns/rss-agg)",
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9",
        }
        self.timeout = Timeout(timeout)
        limits = Limits(max_connections=max_connections, max_keepalive_connections=max_connections, keepalive_expiry=5)
        self.transport = AsyncHTTPTransport(http2=True, retries=3, limits=limits)

    async def fetch_all(self, feed_urls: list[URL]) -> Collection[str]:
        async with AsyncClient(
            headers=self.headers, timeout=self.timeout, follow_redirects=True, transport=self.transport
        ) as client:
            tasks = [self.fetch(client, feed_url) for feed_url in feed_urls]
            responses: Collection[str] = await asyncio.gather(*tasks)
        return responses

    @staticmethod
    async def fetch(client: AsyncClient, url: URL) -> str:
        try:
            logger.info("getting from %s", url)
            response = await client.get(str(url))
            response.raise_for_status()
        except Exception as e:
            logger.exception("Unexpected", exc_info=e)
            raise
        else:
            if response.text:
                return response.text
            logger.warning("empty response from %s", url)
            return ""
