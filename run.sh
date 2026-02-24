#!/bin/bash

# Use uv run if available, otherwise use python3 directly
if command -v uv >/dev/null 2>&1; then
  GUNICORN="uv run gunicorn"
else
  GUNICORN="python3 -m gunicorn"
fi

exec $GUNICORN \
  -b 0.0.0.0:8080 \
  --workers 1 \
  --timeout 0 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  --no-control-socket \
  rss_agg.web:app
