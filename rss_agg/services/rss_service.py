import logging
from typing import Annotated

from wireup import Inject, injectable
from yarl import URL  # noqa: TC002

from rss_agg.services.rss_generator import RSSGenerator  # noqa: TC001
from rss_agg.services.rss_parser import RSSParser  # noqa: TC001
from rss_agg.types import BaseUrl, FeedsFile, FeedUrl, MaxItems

logger = logging.getLogger(__name__)


@injectable
class RSSService:
    def __init__(
        self,
        parser: RSSParser,
        generator: RSSGenerator,
        base_url: Annotated[BaseUrl, Inject(config="base_url")],
        feeds_file: Annotated[FeedsFile, Inject(config="feeds_file")],
        max_items: Annotated[MaxItems, Inject(config="max_items")],
    ) -> None:
        self.parser = parser
        self.generator = generator
        self.base_url = base_url
        self.feeds_file = feeds_file
        self.max_items = max_items

    async def read_and_generate_rss(self, self_url: URL) -> str:
        with self.feeds_file.open() as f:
            feed_urls = [FeedUrl(self.base_url / path.strip() / "rss") for path in f]

        items = await self.parser.read_rss_feeds(feed_urls)
        return self.generator.generate_new_rss_feed(items, self_url=self_url, limit=self.max_items)
