# RSS aggregator

Aggregate, de-duplicate and republish RSS feeds.

The problem I'm solving here is this; if I subscribe to the main [Guardian](https://www.theguardian.com/) 
[RSS](https://en.wikipedia.org/wiki/RSS) feed, I see a great many articles I'm not interested in[^1]. But if instead I 
subscribe to the feeds for individual tags, while I don't see the things I'm interested in, I do see a great many 
duplicates - articles with multiple tags show up in multiple feeds. This little app allows me to have the best of both 
worlds - I can see only[^2] the articles I'm interested in my reader[^3], and only once.

[^1]: How is there so much sport in the world, and so many people writing and talking about it?
[^2]: Or mostly only - the sub-editors do seem to do some questionable tagging sometimes.
[^3]: Currently [Feedly](https://feedly.com/).

## Design

The application is a [Flask](https://flask.palletsprojects.com/) async web app deployed as an 
[AWS Lambda](https://aws.amazon.com/lambda/) function via the 
[Lambda Web Adapter](https://github.com/awslabs/aws-lambda-web-adapter). 
[web.py](rss_agg/web.py), the entry point, is a good place to start looking at the code. 

On each request, [RSSService](rss_agg/services/rss_service.py) orchestrates the full pipeline: 
[FeedsService](rss_agg/services/feeds_service.py) reads a list of feed paths from [feeds.txt](feeds.txt) and constructs full 
Guardian RSS URLs; [Fetcher](rss_agg/services/fetcher.py) retrieves all feeds concurrently using [httpx](https://www.python-httpx.org/) with
HTTP/2 and connection pooling; [RSSParser](rss_agg/services/rss_parser.py) parses the responses with 
[defusedxml](https://github.com/tiran/defusedxml) and de-duplicates items by GUID; and 
[RSSGenerator](rss_agg/services/rss_generator.py) sorts by date, applies a configurable item limit, and emits a fresh 
RSS feed. Services are wired together with [wireup](https://maldoinc.github.io/wireup/) for dependency injection, with 
configuration sourced from environment variables. [API Gateway](https://aws.amazon.com/api-gateway/) provides the 
public HTTP endpoint, backed by [Terraform](https://developer.hashicorp.com/terraform)-managed infrastructure-as-code located in [terraform](terraform/).

Some fun AI generated docs: [![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/brunns/rss-agg)

## Prerequisites 

Requires [uv](https://docs.astral.sh/uv/), [xc](https://xcfile.dev/), [colima](//github.com/abiosoft/colima/)[^4], 
[terraform](https://developer.hashicorp.com/terraform) and [libxml2](http://xmlsoft.org/):

[^4]: On a Mac - I'm not sure what you might use on other platforms.

```sh
brew install uv xc colima terraform libxml2
```

## Tasks

These tasks can be run using [xc](https://xcfile.dev/).

### pc

Precommit tasks

Requires: test, lint

```python
#!/usr/bin/env python
import this
```

### cli

Run CLI - outputs RSS to stdout

```sh
uv run cli -vv
```

### web

Run web server

```sh
./run.sh
```

### test

Run all tests

Requires: unit, integration

### unit

Unit tests

```sh
uv run pytest tests/unit/ --durations=10 --cov-report term-missing --cov-fail-under 100 --cov rss_agg
```

### integration

Integration tests

```sh
if command -v colima > /dev/null; then colima status || colima start; fi
uv run pytest tests/integration/ -s --durations=10
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

### build

Build lambda image

```sh
uv export --no-dev --python 3.14 --format requirements-txt --output-file requirements.txt
uv pip install -r requirements.txt --target build --python 3.14
cp -r rss_agg build/
cp run.sh build/
cp feeds.txt build/
chmod +x build/run.sh
cd build
zip -r ../terraform/deployment_package.zip .
cd ..
```

### plan

Plan infrastructure changes

Requires: build, terraform-init

```sh
cd terraform
terraform plan
cd ..
```

### push

Push to origin, and monitor CI run 

```sh
git push
sleep 5
RUN_ID=$(gh run list --workflow=ci.yml --limit=1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN_ID" --exit-status
```

### deploy

Run deployment workflow

```sh
gh workflow run cd.yml
sleep 5
RUN_ID=$(gh run list --workflow=cd.yml --limit=1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN_ID" --exit-status
```

### healthcheck

Check feed is running and returning XML

Inputs: API_URL

```sh
set +x
echo "Testing API at: $API_URL"

# curl will retry up to 5 times with 5 second delays, fail on non-200 status
if curl -fsSL --retry 5 --retry-delay 5 "$API_URL" | xmllint --noout - 2>/dev/null; then
    echo "✓ API returned valid XML"
else
    echo "✗ API check failed (ensure xmllint is installed: brew install libxml2)"
    exit 1
fi
```

### logs

Query CloudWatch logs for recent Lambda activity

```sh
aws logs tail /aws/lambda/rss_aggregator --since 3h --format short
```

### create-s3-bucket

One-off commands to set up the [AWS S3](https://aws.amazon.com/s3/) bucket that terraform will use to store
infrastructure state. Run `aws configure` first to authenticate if necessary.

```sh
aws s3 mb s3://brunns-rss-agg-terraform-state --region eu-west-2
aws s3api put-bucket-versioning --bucket brunns-rss-agg-terraform-state --versioning-configuration Status=Enabled
```

### terraform-init

Initialise terraform

```sh
cd terraform
terraform init
cd ..
```

## Initial setup steps

Use [brunns-python-template](https://github.com/brunns/brunns-python-template) or similar.
