import logging

from wireup import injectable
from yarl import URL  # noqa: TC002

from rss_agg.services.feeds_services import FeedsService  # noqa: TC001
from rss_agg.services.rss_generator import RSSGenerator  # noqa: TC001
from rss_agg.services.rss_parser import RSSParser  # noqa: TC001

logger = logging.getLogger(__name__)


@injectable
class RSSService:
    def __init__(
        self,
        feeds_service: FeedsService,
        parser: RSSParser,
        generator: RSSGenerator,
    ) -> None:
        self.feeds_service = feeds_service
        self.parser = parser
        self.generator = generator

    async def read_and_generate_rss(self, self_url: URL) -> str:
        feed_urls = self.feeds_service.get_feeds()
        items = await self.parser.read_rss_feeds(feed_urls)
        return self.generator.generate_new_rss_feed(items, self_url=self_url)
