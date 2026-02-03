from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

import pytest

from rss_agg.flask_app_factory import create_app

if TYPE_CHECKING:
    from collections.abc import Callable
DC_NS = "http://purl.org/dc/elements/1.1/"


def _generate_rss_xml(
    count: int,
    time_formatter: Callable[[int], str] | None = None,
    include_dc_date: bool = False,
    guid_override: str | None = None,
) -> str:
    time_formatter = time_formatter or (lambda i: f"12:{i:02d}:00")

    rss_root = ET.Element("rss", version="2.0")
    ET.register_namespace("dc", DC_NS)
    channel = ET.SubElement(rss_root, "channel")
    ET.SubElement(channel, "title").text = "Test channel"
    ET.SubElement(channel, "description").text = "Test channel"
    ET.SubElement(channel, "link").text = "https://example.com"
    ET.SubElement(channel, "pubDate").text = "Sun, 6 Sep 2009 16:20:00 +0000"

    for i in range(1, count + 1):
        item = ET.Element("item")
        ET.SubElement(item, "title").text = f"Test article {i}"
        ET.SubElement(item, "description").text = f"Test article {i}"
        ET.SubElement(item, "link").text = f"https://example.com/article{i}"
        ET.SubElement(item, "guid").text = guid_override or f"guid-{i}"

        time_str = time_formatter(i)
        ET.SubElement(item, "pubDate").text = f"Sun, 6 Sep 2009 {time_str} +0000"

        if include_dc_date:
            dc_date = ET.SubElement(item, f"{{{DC_NS}}}date")
            dc_date.text = f"2009-09-06T{time_str}+00:00"

        channel.append(item)

    return ET.tostring(rss_root, encoding="unicode")


@pytest.fixture(scope="session")
def rss_string() -> str:
    return _generate_rss_xml(count=3, time_formatter=lambda i: f"{i + 12}:20:00", include_dc_date=True)


@pytest.fixture(scope="session")
def empty_rss_string() -> str:
    return _generate_rss_xml(count=0)


@pytest.fixture(scope="session")
def large_rss_string() -> str:
    return _generate_rss_xml(count=59, time_formatter=lambda i: f"12:{i:02d}:00")


@pytest.fixture(scope="session")
def rss_string_with_duplicate_guids() -> str:
    return _generate_rss_xml(
        count=2, time_formatter=lambda i: f"{i + 12}:20:00", include_dc_date=True, guid_override="guid"
    )


@pytest.fixture
def app_and_container():
    app, container = create_app({"TESTING": True, "max_items": 10})
    return app, container


@pytest.fixture
def client(app_and_container):
    app, _ = app_and_container
    return app.test_client()


@pytest.fixture
def container(app_and_container):
    _, container = app_and_container
    return container
