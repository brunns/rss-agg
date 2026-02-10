import logging
from collections import OrderedDict
from typing import TYPE_CHECKING

from defusedxml.ElementTree import fromstring
from wireup import injectable

from rss_agg.logging_utils import log_duration

if TYPE_CHECKING:
    from xml.etree import ElementTree as ET

    from yarl import URL

from rss_agg.services import Fetcher  # noqa: TC001

logger = logging.getLogger(__name__)


@injectable
class RSSParser:
    def __init__(self, fetcher: Fetcher) -> None:
        self.fetcher = fetcher

    async def read_rss_feeds(self, feed_urls: list[URL]) -> list[ET.Element]:
        items: dict[str, ET.Element] = OrderedDict()
        responses = await self.fetcher.fetch_all(feed_urls)
        with log_duration(logger.info, "deduping", response_count=len(responses)):
            for response in responses:
                if response:
                    feed: ET.Element = fromstring(response)
                    for item in feed.findall(".//item"):
                        if (guid := item.findtext("guid")) and guid not in items:
                            items[guid] = item
        logger.info("deduped-items", extra={"count": len(items)})
        return list(items.values())
