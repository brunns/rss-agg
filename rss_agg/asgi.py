"""ASGI entrypoint for Flask app using uvicorn workers."""

from asgiref.wsgi import WsgiToAsgi

from rss_agg.web import app

# Wrap the WSGI Flask app to make it ASGI-compatible
asgi_app = WsgiToAsgi(app)
