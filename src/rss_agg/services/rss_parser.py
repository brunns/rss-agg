# Copyright 2024-2026 Simon Brunning
import logging
from collections import OrderedDict
from typing import TYPE_CHECKING

from defusedxml.ElementTree import fromstring
from wireup import injectable
from yarl import URL

from rss_agg.logging_utils import log_duration

if TYPE_CHECKING:
    from collections.abc import Iterable
    from xml.etree import ElementTree as ET

    from rss_agg.domain import ExcludeTag
    from rss_agg.services.feeds_services.base_feeds_service import FeedsAndExclusions


from rss_agg.services import Fetcher  # noqa: TC001

logger = logging.getLogger(__name__)


@injectable
class RSSParser:
    def __init__(self, fetcher: Fetcher) -> None:
        self.fetcher = fetcher

    async def read_rss_feeds(self, feeds_and_exclusions: FeedsAndExclusions) -> Iterable[ET.Element]:
        exclusions = set(feeds_and_exclusions.exclusions)
        items: dict[str, ET.Element] = OrderedDict()
        responses = await self.fetcher.fetch_all(feeds_and_exclusions.feeds)
        with log_duration(logger.debug, "deduping", response_count=len(responses)):
            for response in responses:
                for guid, item in self._parse_feed_items(response, exclusions):
                    if guid not in items:
                        items[guid] = item
        logger.debug("deduped-items", extra={"count": len(items)})
        return list(items.values())

    def _parse_feed_items(self, response: str, exclusions: set[ExcludeTag]) -> Iterable[tuple[str, ET.Element]]:
        if not response:
            return

        feed: ET.Element = fromstring(response)
        for item in feed.findall(".//item"):
            guid = item.findtext("guid")
            if guid and not self._is_excluded(item, exclusions):
                yield guid, item

    @staticmethod
    def _is_excluded(item: ET.Element, exclusions: set[ExcludeTag]) -> bool:
        categories = {URL(domain) for cat in item.findall("category") if (domain := cat.get("domain"))}
        is_excluded = bool(categories & exclusions)
        if is_excluded:
            logger.debug(
                "exclusion",
                extra={"exclusions": exclusions, "categories": categories, "cause": categories & exclusions},
            )
        return is_excluded
