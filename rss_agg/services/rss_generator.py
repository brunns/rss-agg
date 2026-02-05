import logging
from datetime import UTC, datetime
from email.utils import format_datetime, parsedate_to_datetime
from typing import Annotated
from xml.etree import ElementTree as ET

from wireup import Inject, injectable
from yarl import URL  # noqa: TC002

logger = logging.getLogger(__name__)


@injectable
class RSSGenerator:
    ATOM_NS = "http://www.w3.org/2005/Atom"
    DC_NS = "http://purl.org/dc/elements/1.1/"

    def __init__(
        self,
        feed_title: Annotated[str, Inject(config="feed_title")],
        feed_description: Annotated[str, Inject(config="feed_description")],
        feed_link: Annotated[URL, Inject(config="feed_link")],
    ) -> None:
        self.feed_title = feed_title
        self.feed_description = feed_description
        self.feed_link = feed_link

    def generate_new_rss_feed(self, items: list[ET.Element], self_url: URL, limit: int = 50) -> str:
        ET.register_namespace("atom", RSSGenerator.ATOM_NS)

        root = ET.Element("rss", version="2.0")
        channel = ET.SubElement(root, "channel")
        ET.SubElement(channel, "title").text = self.feed_title
        ET.SubElement(channel, "description").text = self.feed_description
        ET.SubElement(channel, "link").text = str(self.feed_link)

        atom_link = ET.SubElement(channel, f"{{{RSSGenerator.ATOM_NS}}}link")
        atom_link.set("href", str(self_url))
        atom_link.set("rel", "self")
        atom_link.set("type", "application/rss+xml")

        newest_first = sorted(items, key=self._get_date, reverse=True)
        limited_items = newest_first[:limit]

        if limited_items:
            latest_date = self._get_date(limited_items[0])
            if latest_date != datetime.min.replace(tzinfo=UTC):
                ET.SubElement(channel, "pubDate").text = format_datetime(latest_date)

        for item in limited_items:
            for dc_date in item.findall(f"{{{RSSGenerator.DC_NS}}}date"):
                item.remove(dc_date)

            channel.append(item)

        ET.indent(root, space=" ")
        return ET.tostring(root, encoding="unicode")

    @staticmethod
    def _get_date(item: ET.Element) -> datetime:
        pub_date = item.find("pubDate")
        if pub_date is not None and pub_date.text:
            try:
                return parsedate_to_datetime(pub_date.text)
            except ValueError, TypeError:  # pragma: no cover
                pass
        return datetime.min.replace(tzinfo=UTC)
