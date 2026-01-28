#!/usr/bin/env python3
import argparse
import asyncio
import logging
import sys
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

from pythonjsonlogger.json import JsonFormatter
from yarl import URL

from rss_agg.read_and_aggregate import read_and_generate_rss

if TYPE_CHECKING:
    from collections.abc import Sequence

VERSION = "0.1.0"

LOG_LEVELS = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
logger = logging.getLogger(__name__)


def main() -> None:
    args = parse_args()
    logger.debug("args", extra=vars(args))

    rss = asyncio.run(
        read_and_generate_rss(base_url=args.base_url, feeds_file=args.feeds_file, self_url=URL("https://example.com"))
    )
    print(rss)  # noqa: T201


def parse_args() -> argparse.Namespace:
    args = create_parser().parse_args()
    init_logging(args.verbosity, silence_packages=["urllib3", "httpcore"])

    return args


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Display status of GitHub Actions..")

    parser.add_argument(
        "--base_url",
        type=URL,
        default=URL("https://www.theguardian.com"),
        help="Base URL. Default: %(default)s",
    )
    parser.add_argument(
        "--feeds_file",
        type=Path,
        default=Path("feeds.txt"),
        help="Feeds file. Default: %(default)s",
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
