#!/bin/bash
exec python3 -m gunicorn \
  -b 0.0.0.0:8080 \
  --timeout 10 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  rss_agg.web:app
