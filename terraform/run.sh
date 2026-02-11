#!/bin/bash
# Set gunicorn timeout to Lambda timeout minus buffer (15s - 1s = 14s)
# This prevents gunicorn from timing out workers when Lambda times out first
exec python3 -m gunicorn \
  -b 0.0.0.0:8080 \
  --timeout 14 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  rss_agg.web:app
