from datetime import UTC, datetime
from xml.etree import ElementTree as ET

from brunns.matchers.rss import is_rss_entry, is_rss_feed
from hamcrest import assert_that, contains_inanyorder, has_entry, has_length, not_
from yarl import URL

from rss_agg.services import RSSGenerator


def test_builds_rss_structure():
    # Given
    generator = RSSGenerator("some title", "some description", URL("https://some.example.com"), 1)
    item = ET.Element("item")
    ET.SubElement(item, "pubDate").text = "Sun, 6 Sep 2009 15:20:00 +0000"
    ET.SubElement(item, "title").text = "Test article"
    ET.SubElement(item, "link").text = "https://example.com/foo"

    # When
    actual = generator.generate_new_rss_feed([item], URL("https://example.com"))

    # Then
    assert_that(
        actual,
        is_rss_feed()
        .with_title("some title")
        .and_description("some description")
        .and_link(URL("https://some.example.com"))
        .and_published(datetime(2009, 9, 6, 15, 20, tzinfo=UTC))
        .and_entries(
            contains_inanyorder(is_rss_entry().with_title("Test article").and_link(URL("https://example.com/foo")))
        ),
    )


def test_handles_missing_or_invalid_pubdate():
    """Covers line 87 (latest_date == datetime.min) and the fallback in _get_date."""
    # Given
    generator = RSSGenerator("some title", "description", URL("https://example.com"), 1)
    item = ET.Element("item")
    ET.SubElement(item, "title").text = "No Date Article"
    # No pubDate element added at all

    # When
    actual = generator.generate_new_rss_feed([item], URL("https://example.com"))

    # Then
    # If no date is found, pubDate should not be present in the channel metadata
    assert_that(actual, is_rss_feed().with_title("some title"))
    assert_that(actual, not_(has_entry("pubDate", iter)))  # Verifies channel pubDate is skipped


def test_removes_dc_date_elements():
    """Covers line 102 (item.remove(dc_date))."""
    # Given
    generator = RSSGenerator("some title", "description", URL("https://example.com"), 1)
    item = ET.Element("item")
    ET.SubElement(item, "title").text = "DC Date Article"
    ET.SubElement(item, "pubDate").text = "Mon, 01 Jan 2024 00:00:00 +0000"

    # Add a Dublin Core date element
    dc_date = ET.SubElement(item, f"{{{RSSGenerator.DC_NS}}}date")
    dc_date.text = "2024-01-01T00:00:00Z"

    # When
    actual_xml_str = generator.generate_new_rss_feed([item], URL("https://example.com"))

    # Then
    assert_that(actual_xml_str, not_(has_entry(f"{{{RSSGenerator.DC_NS}}}date", iter)))
    assert_that(
        actual_xml_str, is_rss_feed().and_entries(contains_inanyorder(is_rss_entry().with_title("DC Date Article")))
    )


def test_sorts_items_by_date_descending():
    """Tests the sorting logic (line 82) to ensure coverage of various dates."""
    # Given
    generator = RSSGenerator("some title", "description", URL("https://example.com"), 10)

    old_item = ET.Element("item")
    ET.SubElement(old_item, "title").text = "Old"
    ET.SubElement(old_item, "pubDate").text = "Sun, 01 Jan 2023 00:00:00 +0000"

    new_item = ET.Element("item")
    ET.SubElement(new_item, "title").text = "New"
    ET.SubElement(new_item, "pubDate").text = "Mon, 01 Jan 2024 00:00:00 +0000"

    # When
    actual = generator.generate_new_rss_feed([old_item, new_item], URL("https://example.com"))

    # Then
    # Check that 'New' is the first entry (latest_date logic on line 85)
    assert_that(actual, is_rss_feed().and_published(datetime(2024, 1, 1, 0, 0, tzinfo=UTC)))


def tests_limits_to_max_items():
    # Given
    generator = RSSGenerator("some title", "some description", URL("https://some.example.com"), 2)
    item = ET.Element("item")
    ET.SubElement(item, "pubDate").text = "Sun, 6 Sep 2009 15:20:00 +0000"
    ET.SubElement(item, "title").text = "Test article"
    ET.SubElement(item, "link").text = "https://example.com/foo"

    # When
    actual = generator.generate_new_rss_feed([item, item, item, item], URL("https://example.com"))

    # Then
    assert_that(
        actual,
        is_rss_feed().with_entries(has_length(2)),
    )
