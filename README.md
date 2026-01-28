# RSS aggregator

Aggregate, de-duplicate and republish RSS feeds

## Tasks

### pc

Precommit tasks

Requires: test, lint

```python
#!/usr/bin/env python
import this
```

### run

```sh
uv run cli -vv
```

### web

```sh
uv run flask --app rss_agg/web.py run
```

### test

```sh
colima status || colima start
uv run pytest tests/ --durations=10 --cov-report term-missing --cov-fail-under 100 --cov rss_agg
```

### format

Format code

```sh 
uv run ruff format .
uv run ruff check . --fix-only
```

### lint

Lint code

```sh 
uv run ruff format . --check
uv run ruff check .
uv run pyright
```

## Setup steps

For future reference...

```sh 
uv init rss-agg
cd rss-agg
git init
curl https://www.toptal.com/developers/gitignore/api/python,intellij,emacs > .gitignore
uv sync
uv add "flask[async]" httpx yarl arrow defusedxml python-json-logger aws-wsgi
uv add ruff pyright pytest pytest-asyncio pytest-cov pytest-docker feedparser pyhamcrest mbtest respx brunns-matchers pyfakefs --dev
idea .
```
