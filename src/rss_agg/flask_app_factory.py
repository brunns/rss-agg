import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import wireup
from flask import Flask
from yarl import URL

from rss_agg import domain
from rss_agg.logging_utils import init_logging
from rss_agg.routes import rss_blueprint
from rss_agg.services import BASE_INJECTABLES
from rss_agg.services.feeds_services import FILE_INJECTABLES, S3_INJECTABLES

if TYPE_CHECKING:
    from collections.abc import Mapping

logger = logging.getLogger(__name__)


def create_app(config_override: Mapping[str, Any] | None = None) -> tuple[Flask, wireup.AsyncContainer]:
    config_override = config_override or {}

    # Initialize logging
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level_map = {"ERROR": 0, "WARNING": 1, "INFO": 2, "DEBUG": 3}
    verbosity = log_level_map.get(log_level, 2)  # Default to INFO
    init_logging(verbosity, silence_packages=["urllib3", "httpcore", "httpx", "hpack"])

    app = Flask(__name__)

    config = {**build_config(), **config_override}
    injectables = build_injectables(config)
    container = wireup.create_async_container(injectables=injectables, config=config)

    app.register_blueprint(rss_blueprint)
    inject_view = wireup.inject_from_container(container)
    app.view_functions = {name: inject_view(view) for name, view in app.view_functions.items()}

    return app, container


def build_config() -> Mapping[str, Any]:
    return {
        "feeds_service": os.environ.get("FEEDS_SERVICE", "FileFeedsService"),
        "feeds_file": domain.FeedsFile(Path(os.environ.get("FEEDS_FILE", "feeds.txt"))),
        "base_url": domain.BaseUrl(URL("https://www.theguardian.com")),
        "max_items": domain.MaxItems(int(os.environ.get("MAX_ITEMS", "50"))),
        "max_connections": domain.MaxConnections(int(os.environ.get("MAX_CONNECTIONS", "16"))),
        "max_keepalive_connections": domain.MaxKeepaliveConnections(
            int(os.environ.get("MAX_KEEPALIVE_CONNECTIONS", "16"))
        ),
        "keepalive_expiry": domain.KeepaliveExpiry(int(os.environ.get("KEEPALIVE_EXPIRY", "5"))),
        "retries": domain.Retries(int(os.environ.get("RETRIES", "3"))),
        "timeout": domain.Timeout(int(os.environ.get("TIMEOUT", "3"))),
        "feed_title": domain.FeedTitle("@brunns's theguardian.com"),
        "feed_description": domain.FeedDescription("@brunns's curated, de-duplicated theguardian.com RSS feed"),
        "feed_link": domain.FeedLink(URL("https://brunn.ing")),
        "aws_default_region": domain.AwsRegion(os.environ.get("AWS_DEFAULT_REGION", "eu-test-2")),
        "aws_access_key_id": domain.AwsAccessKey(os.environ.get("AWS_ACCESS_KEY_ID", "")),
        "aws_secret_access_key": domain.AwsSecretAccessKey(os.environ.get("AWS_SECRET_ACCESS_KEY", "")),
        "s3_endpoint": domain.S3Endpoint(URL(v)) if (v := os.environ.get("S3_ENDPOINT")) else None,
        "feeds_bucket_name": domain.BucketName(os.environ.get("FEEDS_BUCKET_NAME", "brunns-rss-agg-feeds")),
        "feeds_object_name": domain.ObjectName(os.environ.get("FEEDS_OBJECT_NAME", "feeds.txt")),
    }


def build_injectables(config: Mapping[str, Any]) -> list[Any]:
    """We need to inject only the FileService services for the feeds_service setting."""
    injectables = list(BASE_INJECTABLES)
    feeds_service: domain.FeedsServiceName | None = config.get("feeds_service")
    match feeds_service:
        case "FileFeedsService":
            injectables += FILE_INJECTABLES
        case "S3FeedsService":
            injectables += S3_INJECTABLES
        case _:
            logger.critical("Unknown feeds_service", extra={"feeds_service": feeds_service})
            msg = f"Unknown feeds_service {feeds_service}"
            raise ValueError(msg)
    return injectables
