import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import wireup
from flask import Flask
from yarl import URL

from rss_agg.logging_utils import init_logging
from rss_agg.routes import rss_blueprint
from rss_agg.services import BASE_INJECTABLES
from rss_agg.services.feeds_services import FILE_INJECTABLES, S3_INJECTABLES
from rss_agg.types import (
    BaseUrl,
    FeedDescription,
    FeedLink,
    FeedsFile,
    FeedsServiceName,
    FeedTitle,
    KeepaliveExpiry,
    MaxConnections,
    MaxItems,
    MaxKeepaliveConnections,
    Retries,
    Timeout,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


def create_app(config_override: Mapping[str, Any] | None = None) -> tuple[Flask, wireup.AsyncContainer]:
    config_override = config_override or {}

    # Initialize logging
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level_map = {"ERROR": 0, "WARNING": 1, "INFO": 2, "DEBUG": 3}
    verbosity = log_level_map.get(log_level, 2)  # Default to INFO
    init_logging(verbosity, silence_packages=["urllib3", "httpcore", "httpx", "hpack"])

    app = Flask(__name__)

    config = {**(build_config()), **config_override}
    injectables = build_injectables(config)
    container = wireup.create_async_container(injectables=injectables, config=config)

    app.register_blueprint(rss_blueprint)
    inject_view = wireup.inject_from_container(container)
    app.view_functions = {name: inject_view(view) for name, view in app.view_functions.items()}

    return app, container


def build_config() -> dict[str, Any]:
    return {
        "feeds_service": os.environ.get("FEEDS_SERVICE", "FileFeedsService"),
        "feeds_file": FeedsFile(Path(os.environ.get("FEEDS_FILE", "feeds.txt"))),
        "base_url": BaseUrl(URL("https://www.theguardian.com")),
        "max_items": MaxItems(int(os.environ.get("MAX_ITEMS", "50"))),
        "max_connections": MaxConnections(int(os.environ.get("MAX_CONNECTIONS", "16"))),
        "max_keepalive_connections": MaxKeepaliveConnections(int(os.environ.get("MAX_KEEPALIVE_CONNECTIONS", "16"))),
        "keepalive_expiry": KeepaliveExpiry(int(os.environ.get("KEEPALIVE_EXPIRY", "5"))),
        "retries": Retries(int(os.environ.get("RETRIES", "3"))),
        "timeout": Timeout(int(os.environ.get("TIMEOUT", "3"))),
        "feed_title": FeedTitle("@brunns's theguardian.com"),
        "feed_description": FeedDescription("@brunns's curated, de-duplicated theguardian.com RSS feed"),
        "feed_link": FeedLink(URL("https://brunn.ing")),
    }


def build_injectables(config: dict[Any, Any]) -> list[Any]:
    """We need to inject only the FileService services for the feeds_service setting."""
    injectables = list(BASE_INJECTABLES)
    feeds_service: FeedsServiceName | None = config.get("feeds_service")
    if feeds_service == "FileFeedsService":
        injectables += FILE_INJECTABLES
    elif feeds_service == "S3FeedsService":
        injectables += S3_INJECTABLES
    return injectables
