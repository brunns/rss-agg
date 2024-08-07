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
poetry run pyright .
poetry run refurb .
```

## Setup steps

For future reference...

```sh 
poetry new rss-agg
cd rss-agg
git init
poetry install
curl https://www.toptal.com/developers/gitignore/api/python,intellij,emacs > .gitignore
poetry add aiohttp yarl
poetry add ruff pyright pytest refurb --group dev
idea .
```
