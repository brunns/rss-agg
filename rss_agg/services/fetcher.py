import asyncio
import logging
from typing import TYPE_CHECKING, Annotated

import httpx
from wireup import Inject, injectable

if TYPE_CHECKING:
    from collections.abc import Collection

    from yarl import URL

logger = logging.getLogger(__name__)


@injectable
class Fetcher:
    def __init__(self, max_connections: Annotated[int, Inject(config="max_connections")]) -> None:
        self.max_connections = max_connections

    async def fetch_all(self, feed_urls: list[URL]) -> Collection[str]:
        async with httpx.AsyncClient(
            follow_redirects=True, limits=httpx.Limits(max_connections=self.max_connections)
        ) as client:
            tasks = [self.fetch(client, feed_url) for feed_url in feed_urls]
            responses: Collection[str] = await asyncio.gather(*tasks)
        return responses

    @staticmethod
    async def fetch(client: httpx.AsyncClient, url: URL) -> str:
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
