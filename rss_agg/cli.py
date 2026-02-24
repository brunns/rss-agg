#!/usr/bin/env python3
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Any

import wireup
from yarl import URL

import rss_agg.services
from rss_agg.logging_utils import init_logging
from rss_agg.types import (
    BaseUrl,
    FeedDescription,
    FeedLink,
    FeedsFile,
    FeedTitle,
    KeepaliveExpiry,
    MaxConnections,
    MaxItems,
    MaxKeepaliveConnections,
    Retries,
    Timeout,
)

VERSION = "0.1.0"

logger = logging.getLogger(__name__)


def main() -> None:
    args = parse_args()
    logger.debug("args", extra=vars(args))

    config = build_config(args)
    container = wireup.create_sync_container(injectables=[rss_agg.services], config={**config})

    rss_service = container.get(rss_agg.services.RSSService)

    rss = asyncio.run(rss_service.read_and_generate_rss(self_url=URL("https://example.com")))
    print(rss)  # noqa: T201


def build_config(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "feeds_file": FeedsFile(args.feeds_file),
        "base_url": BaseUrl(args.base_url),
        "max_items": MaxItems(args.max_items),
        "timeout": Timeout(args.timeout),
        "max_connections": MaxConnections(args.max_connections),
        "max_keepalive_connections": MaxKeepaliveConnections(args.max_keepalive_connections),
        "keepalive_expiry": KeepaliveExpiry(args.keepalive_expiry),
        "retries": Retries(args.retries),
        "feed_title": FeedTitle("@brunns's theguardian.com"),
        "feed_description": FeedDescription("@brunns's curated, de-duplicated theguardian.com RSS feed"),
        "feed_link": FeedLink(URL("https://brunn.ing")),
    }


def parse_args() -> argparse.Namespace:
    args = create_parser().parse_args()
    init_logging(args.verbosity, silence_packages=["urllib3", "httpcore", "httpx", "hpack"])

    return args


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Aggregate, de-duplicate and republish RSS feeds.")

    parser.add_argument(
        "--base-url",
        type=URL,
        default=URL("https://www.theguardian.com"),
        help="Base URL. Default: %(default)s",
    )
    parser.add_argument(
        "--feeds-file",
        type=Path,
        default=Path("feeds.txt"),
        help="Feeds file. Default: %(default)s",
    )
    parser.add_argument(
        "-m",
        "--max-items",
        type=int,
        default=50,
        help="Maximum items to return. Default: %(default)s",
    )
    parser.add_argument(
        "--max-connections",
        type=int,
        default=16,
        help="Maximum concurrent HTTP connections. Default: %(default)s",
    )
    parser.add_argument(
        "--max-keepalive-connections",
        type=int,
        default=16,
        help="Maximum keep-alive connections. Default: %(default)s",
    )
    parser.add_argument(
        "--keepalive-expiry",
        type=int,
        default=5,
        help="Keep-alive expiry. Default: %(default)s",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Maximum HTTP retries. Default: %(default)s",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=3,
        help="Timeout for feed fetching. Default: %(default)s",
    )

    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="specify up to four times to increase verbosity, "
        "i.e. -v to see warnings, -vv for information messages, "
        "-vvv for debug messages, or -vvvv for trace messages.",
    )
    parser.add_argument("-V", "--version", action="version", version=VERSION)
    return parser


if __name__ == "__main__":
    main()
