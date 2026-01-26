import logging
from pathlib import Path

from flask import Flask, Response
from yarl import URL

from rss_agg.read_and_aggregate import read_and_generate_rss

logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route("/")
async def get_data() -> Response:
    base_url = URL("https://www.theguardian.com")
    feeds_file = Path("feeds.txt")
    rss = await read_and_generate_rss(base_url=base_url, feeds_file=feeds_file)
    return Response(rss, mimetype="application/rss+xml")
