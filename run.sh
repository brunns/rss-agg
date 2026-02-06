#!/bin/bash
exec python3 -m gunicorn -b 0.0.0.0:8080 rss_agg.web:app
