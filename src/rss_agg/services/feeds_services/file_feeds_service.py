# Copyright 2024-2026 Simon Brunning
import logging
from typing import Annotated, override

from wireup import Inject, injectable

from rss_agg import domain
from rss_agg.services.feeds_services.base_feeds_service import FeedsAndExclusions, FeedsService

logger = logging.getLogger(__name__)


@injectable(as_type=FeedsService)
class FileFeedsService(FeedsService):
    def __init__(
        self,
        feeds_file: Annotated[domain.FeedsFile, Inject(config="feeds_file")],
        base_url: Annotated[domain.BaseUrl, Inject(config="base_url")],
    ) -> None:
        self.feeds_file = feeds_file
        self.base_url = base_url

    @override
    def get_feeds_and_exclusions(self) -> FeedsAndExclusions:
        feeds, exclusions = [], []
        with self.feeds_file.open() as f:
            for path in f:
                if path.strip():
                    match path[0]:
                        case "#":
                            continue
                        case "-":
                            exclusions.append(domain.FeedUrl(self.base_url / path[1:].strip()))
                        case _:
                            feeds.append(domain.FeedUrl(self.base_url / path.strip() / "rss"))
        feeds_and_exclusions = FeedsAndExclusions(feeds, exclusions)
        logger.debug("feeds_and_exclusions-items", extra={"feeds": feeds, "exclusions": exclusions})
        return feeds_and_exclusions


FILE_INJECTABLES = [FileFeedsService]
