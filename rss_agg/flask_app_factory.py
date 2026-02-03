import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import wireup
from flask import Flask
from yarl import URL

import rss_agg.services
from rss_agg.routes import rss_bp

if TYPE_CHECKING:
    from collections.abc import Mapping


class WireupFlask(Flask):
    container: wireup.SyncContainer


def create_app(config_override: Mapping[str, Any] | None = None) -> tuple[Flask, wireup.SyncContainer]:
    app = WireupFlask(__name__)

    # Configuration
    config = {
        "feeds_file": Path(os.environ.get("FEEDS_FILE", "feeds.txt")),
        "base_url": URL("https://www.theguardian.com"),
        "max_items": int(os.environ.get("MAX_ITEMS", "50")),
        "max_connections": int(os.environ.get("MAX_CONNECTIONS", "32")),
    }
    if config_override:
        config.update(config_override)

    container = wireup.create_sync_container(injectables=[rss_agg.services], config=config)
    app.container = container

    app.register_blueprint(rss_bp)

    return app, container
