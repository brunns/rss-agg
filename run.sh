#!/bin/bash
# Use --timeout 0 to disable gunicorn's worker timeout entirely.
# Lambda's OS clock advances during freeze/thaw cycles, so any fixed timeout
# will kill workers on warm requests (they appear "silent" for the freeze duration).
# Lambda's own 15-second function timeout is the safety net.
# Use sync workers: Flask handles async views via asgiref.sync.async_to_sync,
# giving each request a fresh event loop.

# Use uv run if available (local dev), otherwise use python3 directly (Lambda)
if command -v uv >/dev/null 2>&1; then
  GUNICORN="uv run gunicorn"
else
  GUNICORN="python3 -m gunicorn"
fi

exec $GUNICORN \
  -b 0.0.0.0:8080 \
  --timeout 0 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  --no-control-socket \
  rss_agg.web:app
