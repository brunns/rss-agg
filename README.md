# RSS aggregator

Aggregate, de-duplicate and republish RSS feeds

## Tasks

### run

```sh
poetry run cli
```

### format

Format code

```sh 
poetry run ruff check . --select I --fix
poetry run ruff format .
```

### lint

Lint code

```sh 
poetry run ruff check . --select I
poetry run ruff format . --check
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
