#!/bin/bash
# Set gunicorn timeout to Lambda timeout minus buffer (15s - 1s = 14s)
# This prevents gunicorn from timing out workers when Lambda times out first
# Use sync workers: Flask handles async views via asgiref.sync.async_to_sync,
# giving each request a fresh event loop. Avoids worker timeouts caused by
# uvicorn's persistent event loop breaking on Lambda freeze/thaw cycles.

# Use uv run if available (local dev), otherwise use python3 directly (Lambda)
if command -v uv >/dev/null 2>&1; then
  GUNICORN="uv run gunicorn"
else
  GUNICORN="python3 -m gunicorn"
fi

exec $GUNICORN \
  -b 0.0.0.0:8080 \
  --timeout 14 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  --no-control-socket \
  rss_agg.web:app
