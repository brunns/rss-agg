import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import wireup
from flask import Flask
from yarl import URL

import rss_agg.services
from rss_agg.logging_utils import init_logging
from rss_agg.routes import rss_bp

if TYPE_CHECKING:
    from collections.abc import Mapping


class WireupFlask(Flask):
    container: wireup.SyncContainer


def create_app(config_override: Mapping[str, Any] | None = None) -> tuple[Flask, wireup.SyncContainer]:
    # Initialize logging for Lambda/web mode
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level_map = {"ERROR": 0, "WARNING": 1, "INFO": 2, "DEBUG": 3}
    verbosity = log_level_map.get(log_level, 2)  # Default to INFO
    init_logging(verbosity, silence_packages=["urllib3", "httpcore"])

    app = WireupFlask(__name__)

    config = build_config()
    config_override = config_override or {}
    container = wireup.create_sync_container(injectables=[rss_agg.services], config={**config, **config_override})
    app.container = container

    app.register_blueprint(rss_bp)

    return app, container


def build_config() -> dict[str, Any]:
    return {
        "feeds_file": Path(os.environ.get("FEEDS_FILE", "feeds.txt")),
        "base_url": URL("https://www.theguardian.com"),
        "max_items": int(os.environ.get("MAX_ITEMS", "50")),
        "max_connections": int(os.environ.get("MAX_CONNECTIONS", "16")),
        "timeout": int(os.environ.get("TIMEOUT", "3")),
        "feed_title": "@brunns's theguardian.com",
        "feed_description": "@brunns's curated, de-duplicated theguardian.com RSS feed",
        "feed_link": URL("https://brunn.ing"),
    }
