from typing import Annotated

from wireup import Inject, injectable

from rss_agg import domain
from rss_agg.services.feeds_services.base_feeds_service import FeedsService


@injectable(as_type=FeedsService)
class FileFeedsService(FeedsService):
    def __init__(
        self,
        feeds_file: Annotated[domain.FeedsFile, Inject(config="feeds_file")],
        base_url: Annotated[domain.BaseUrl, Inject(config="base_url")],
    ) -> None:
        self.feeds_file = feeds_file
        self.base_url = base_url

    def get_feeds(self) -> list[domain.FeedUrl]:
        with self.feeds_file.open() as f:
            return [domain.FeedUrl(self.base_url / path.strip() / "rss") for path in f]


FILE_INJECTABLES = [FileFeedsService]
