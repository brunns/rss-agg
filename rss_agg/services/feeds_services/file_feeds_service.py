from typing import Annotated

from wireup import Inject, injectable

from rss_agg.services.feeds_services.base_feeds_service import FeedsService
from rss_agg.types import BaseUrl, FeedsFile, FeedUrl


@injectable(as_type=FeedsService)
class FileFeedsService(FeedsService):
    def __init__(
        self,
        feeds_file: Annotated[FeedsFile, Inject(config="feeds_file")],
        base_url: Annotated[BaseUrl, Inject(config="base_url")],
    ) -> None:
        self.feeds_file = feeds_file
        self.base_url = base_url

    def get_feeds(self) -> list[FeedUrl]:
        with self.feeds_file.open() as f:
            return [FeedUrl(self.base_url / path.strip() / "rss") for path in f]


FILE_INJECTABLES = [FileFeedsService]
