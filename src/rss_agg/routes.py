import logging
from http import HTTPStatus

from flask import Blueprint, Response, request
from wireup import Injected  # noqa: TC002
from yarl import URL

from rss_agg.logging_utils import log_duration
from rss_agg.services import RSSService  # noqa: TC001

logger = logging.getLogger(__name__)
rss_blueprint = Blueprint("rss", __name__)


@rss_blueprint.route("/")
async def get_rss(rss_service: Injected[RSSService]) -> Response:
    with log_duration(logger.info, "request", path=request.path):
        rss = await rss_service.read_and_generate_rss(self_url=URL(request.base_url))
    return Response(rss, mimetype="application/rss+xml", status=HTTPStatus.OK)


@rss_blueprint.route("/health")
def health() -> Response:
    return Response("OK", status=HTTPStatus.OK)
