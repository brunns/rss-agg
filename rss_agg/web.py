import logging
from pathlib import Path

import wireup.integration.flask
from flask import Flask, Response, request
from yarl import URL

import rss_agg.read_and_aggregate

logger = logging.getLogger(__name__)
app = Flask(__name__)

container = wireup.create_sync_container(injectables=[rss_agg.read_and_aggregate], config={**app.config})


@app.route("/")
async def get_data() -> Response:
    rss_service = container.get(rss_agg.read_and_aggregate.RSSService)
    base_url = URL("https://www.theguardian.com")
    feeds_file = Path("feeds.txt")
    rss = await rss_service.read_and_generate_rss(
        base_url=base_url, feeds_file=feeds_file, self_url=URL(request.base_url)
    )
    return Response(rss, mimetype="application/rss+xml")
