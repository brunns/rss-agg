from typing import TYPE_CHECKING, cast

from flask import Blueprint, Response, current_app, request
from yarl import URL

from rss_agg.services import RSSService

if TYPE_CHECKING:
    from rss_agg.flask_app_factory import WireupFlask

rss_bp = Blueprint("rss", __name__)


@rss_bp.route("/")
async def get_data() -> Response:
    container = cast("WireupFlask", current_app).container
    rss_service = container.get(RSSService)
    rss = await rss_service.read_and_generate_rss(self_url=URL(request.base_url))
    return Response(rss, mimetype="application/rss+xml")
