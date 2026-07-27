# Copyright 2024-2026 Simon Brunning
import logging
from collections import OrderedDict
from typing import TYPE_CHECKING

from defusedxml.ElementTree import fromstring
from wireup import injectable

from rss_agg.logging_utils import log_duration

if TYPE_CHECKING:
    from collections.abc import Iterable
    from xml.etree import ElementTree as ET

    from rss_agg.services.feeds_services.base_feeds_service import FeedsAndExclusions


from rss_agg.services import Fetcher  # noqa: TC001

logger = logging.getLogger(__name__)


@injectable
class RSSParser:
    def __init__(self, fetcher: Fetcher) -> None:
        self.fetcher = fetcher

    async def read_rss_feeds(self, feeds_and_exclusions: FeedsAndExclusions) -> Iterable[ET.Element]:
        items: dict[str, ET.Element] = OrderedDict()
        responses = await self.fetcher.fetch_all(feeds_and_exclusions.feeds)
        with log_duration(logger.debug, "deduping", response_count=len(responses)):
            for response in responses:
                if response:
                    feed: ET.Element = fromstring(response)
                    for item in feed.findall(".//item"):
                        if (guid := item.findtext("guid")) and guid not in items:
                            items[guid] = item
        logger.debug("deduped-items", extra={"count": len(items)})
        return list(items.values())
