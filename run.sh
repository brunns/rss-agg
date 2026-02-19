#!/bin/bash
# Set gunicorn timeout to Lambda timeout minus buffer (15s - 1s = 14s)
# This prevents gunicorn from timing out workers when Lambda times out first
# Use uvicorn workers with ASGI wrapper to properly handle async Flask routes

# Use uv run if available (local dev), otherwise use python3 directly (Lambda)
if command -v uv >/dev/null 2>&1; then
  exec uv run gunicorn \
    -b 0.0.0.0:8080 \
    -k uvicorn.workers.UvicornWorker \
    --timeout 14 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --no-control-socket \
    rss_agg.asgi:asgi_app
else
  exec python3 -m gunicorn \
    -b 0.0.0.0:8080 \
    -k uvicorn.workers.UvicornWorker \
    --timeout 14 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --no-control-socket \
    rss_agg.asgi:asgi_app
fi
