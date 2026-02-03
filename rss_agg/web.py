import logging
import os
from pathlib import Path

import wireup.integration.flask
from flask import Flask, Response, request
from yarl import URL

import rss_agg.services

logger = logging.getLogger(__name__)
app = Flask(__name__)

config = {
    "feeds_file": Path(os.environ.get("FEEDS_FILE", "feeds.txt")),
    "max_items": int(os.environ.get("MAX_ITEMS", "50")),
    "max_connections": int(os.environ.get("MAX_CONNECTIONS", "32")),
}
container = wireup.create_sync_container(injectables=[rss_agg.services], config={**config, **app.config})


@app.route("/")
async def get_data() -> Response:
    rss_service = container.get(rss_agg.services.RSSService)
    base_url = URL("https://www.theguardian.com")
    rss = await rss_service.read_and_generate_rss(base_url=base_url, self_url=URL(request.base_url))
    return Response(rss, mimetype="application/rss+xml")
