from typing import TYPE_CHECKING, Annotated, override

from wireup import Inject, injectable

from rss_agg import domain
from rss_agg.services.feeds_services.base_feeds_service import FeedsService

if TYPE_CHECKING:
    from collections.abc import Iterable


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
    def get_feeds(self) -> Iterable[domain.FeedUrl]:
        feeds = []
        with self.feeds_file.open() as f:
            for path in f:
                if path.strip():
                    match path[0]:
                        case "#":
                            continue
                        case _:
                            feeds.append(domain.FeedUrl(self.base_url / path.strip() / "rss"))
        return feeds


FILE_INJECTABLES = [FileFeedsService]
