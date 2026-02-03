#!/usr/bin/env python3
import argparse
import asyncio
import logging
import sys
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any

import wireup
from pythonjsonlogger.json import JsonFormatter
from yarl import URL

import rss_agg.services

if TYPE_CHECKING:
    from collections.abc import Sequence

VERSION = "0.1.0"

LOG_LEVELS = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
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
        "feeds_file": args.feeds_file,
        "base_url": args.base_url,
        "max_items": args.max_items,
        "max_connections": args.max_connections,
        "feed_title": "@brunns's theguardian.com",
        "feed_description": "@brunns's curated, de-duplicated theguardian.com RSS feed",
        "feed_link": URL("https://brunn.ing"),
    }


def parse_args() -> argparse.Namespace:
    args = create_parser().parse_args()
    init_logging(args.verbosity, silence_packages=["urllib3", "httpcore"])

    return args


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Display status of GitHub Actions.")

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


def init_logging(
    verbosity: int,
    handler: logging.Handler | None = None,
    silence_packages: Sequence[str] = (),
) -> None:
    handler = handler or logging.StreamHandler(stream=sys.stdout)
    level = LOG_LEVELS[min(verbosity, len(LOG_LEVELS) - 1)]
    msg_format = "%(message)s"
    if level <= logging.DEBUG:
        warnings.filterwarnings("ignore")
        msg_format = "%(asctime)s %(levelname)-8s %(name)s %(module)s.py:%(funcName)s():%(lineno)d %(message)s"
    handler.setFormatter(JsonFormatter(msg_format))
    logging.basicConfig(level=level, format=msg_format, handlers=[handler])

    for package in silence_packages:
        logging.getLogger(package).setLevel(max([level, logging.WARNING]))


if __name__ == "__main__":
    main()
