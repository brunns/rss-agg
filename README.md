# RSS aggregator

Aggregate, de-duplicate and republish RSS feeds

## Tasks

### run

```sh
poetry run cli
```

### web

```sh
poetry run flask --app rss_agg/web.py run
```

### test

```sh
# colima status || colima start
poetry run pytest tests/ --durations=10 --cov-report term-missing --cov-fail-under 100 --cov rss_agg
```

### format

Format code

```sh 
poetry run ruff format .
poetry run ruff check . --fix
```

### lint

Lint code

```sh 
poetry run ruff format . --check
poetry run ruff check .
poetry run pyright
```

## Setup steps

For future reference...

```sh 
poetry new rss-agg
cd rss-agg
git init
poetry install
curl https://www.toptal.com/developers/gitignore/api/python,intellij,emacs > .gitignore
poetry add flask[async] httpx yarl defusedxml
poetry add ruff pyright pytest refurb --group dev
idea .
```
