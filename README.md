# RSS aggregator

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg?logo=python)](https://www.python.org/)
[![made-with-uv](https://img.shields.io/badge/Made%20with-uv-1f425f.svg?logo=uv)](https://docs.astral.sh/uv/)
[![Licence](https://img.shields.io/github/license/brunns/rss-agg.svg)](https://github.com/brunns/rss-agg/blob/master/LICENSE)
[![ci](https://github.com/brunns/rss-agg/actions/workflows/ci.yml/badge.svg)](https://github.com/brunns/rss-agg/actions/workflows/ci.yml)
[![deploy](https://github.com/brunns/rss-agg/actions/workflows/cd.yml/badge.svg)](https://github.com/brunns/rss-agg/actions/workflows/cd.yml)
[![GitHub forks](https://img.shields.io/github/forks/brunns/rss-agg.svg?label=Fork&logo=github)](https://github.com/brunns/rss-agg/network/members)
[![GitHub stars](https://img.shields.io/github/stars/brunns/rss-agg.svg?label=Star&logo=github)](https://github.com/brunns/rss-agg/stargazers/)
[![GitHub watchers](https://img.shields.io/github/watchers/brunns/rss-agg.svg?label=Watch&logo=github)](https://github.com/brunns/rss-agg/watchers/)
[![GitHub contributors](https://img.shields.io/github/contributors/brunns/rss-agg.svg?logo=github)](https://github.com/brunns/rss-agg/graphs/contributors/)
[![GitHub issues](https://img.shields.io/github/issues/brunns/rss-agg.svg?logo=github)](https://github.com/brunns/rss-agg/issues/)
[![GitHub issues-closed](https://img.shields.io/github/issues-closed/brunns/rss-agg.svg?logo=github)](https://github.com/brunns/rss-agg/issues?q=is%3Aissue+is%3Aclosed)
[![GitHub pull-requests](https://img.shields.io/github/issues-pr/brunns/rss-agg.svg?logo=github)](https://github.com/brunns/rss-agg/pulls)
[![GitHub pull-requests closed](https://img.shields.io/github/issues-pr-closed/brunns/rss-agg.svg?logo=github)](https://github.com/brunns/rss-agg/pulls?utf8=%E2%9C%93&q=is%3Apr+is%3Aclosed)
[![Lines of Code](https://img.shields.io/endpoint?url=https%3A%2F%2Ftokei.kojix2.net%2Fbadge%2Fgithub%2Fbrunns%2Frss-agg%2Flines)](https://tokei.kojix2.net/github/brunns/rss-agg)
[![Top Language](https://img.shields.io/endpoint?url=https%3A%2F%2Ftokei.kojix2.net%2Fbadge%2Fgithub%2Fbrunns%2Frss-agg%2Flanguage)](https://tokei.kojix2.net/github/brunns/rss-agg)
[![Languages](https://img.shields.io/endpoint?url=https%3A%2F%2Ftokei.kojix2.net%2Fbadge%2Fgithub%2Fbrunns%2Frss-agg%2Flanguages)](https://tokei.kojix2.net/github/brunns/rss-agg)
[![Code to Comment](https://img.shields.io/endpoint?url=https%3A%2F%2Ftokei.kojix2.net%2Fbadge%2Fgithub%2Fbrunns%2Frss-agg%2Fratio)](https://tokei.kojix2.net/github/brunns/rss-agg)
[![xc compatible](https://xcfile.dev/badge.svg)](https://xcfile.dev)
[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/brunns/rss-agg)

Aggregate, de-duplicate and republish RSS feeds.

The problem I'm solving here is this; if I subscribe to the main [Guardian](https://www.theguardian.com/) 
[RSS](https://en.wikipedia.org/wiki/RSS) feed, I see a great many articles I'm not interested in[^1]. But if instead I 
subscribe to the feeds for individual tags, while I don't see the things I'm not interested in, I do see a great many 
duplicates - articles with multiple tags show up in multiple feeds. This little app allows me to have the best of both 
worlds - I can see only[^2] the articles I'm interested in my reader[^3], and only once.

[^1]: How is there so much sport in the world, and so many people writing and talking about it?
[^2]: Or mostly only - the sub-editors do seem to do some questionable tagging sometimes.
[^3]: Currently [Feedly](https://feedly.com/).

## Prerequisites

Local development requires:

* [uv](https://docs.astral.sh/uv/) for all things Python
* [xc](https://xcfile.dev/) as a task runner
* [gh](https://cli.github.com/) for controlling GitHub actions
* [AWS CLI](https://aws.amazon.com/cli/) for controlling & querying AWS
* [colima](https://colima.run/)[^4] for running the docker images we need for our integration tests
* [terraform](https://developer.hashicorp.com/terraform) for deployment (version pinned in [`.tool-versions`](.tool-versions))
* [Node.js](https://nodejs.org/) for [pyright](https://github.com/microsoft/pyright) (version pinned in [`.tool-versions`](.tool-versions))
* [libxml2](http://xmlsoft.org/) for testing our RSS output

[^4]: On a Mac - I'm not sure what you might use on other platforms.

On a Mac, you can install most of these with [homebrew](https://brew.sh/) and [asdf](https://asdf-vm.com/).

```sh
brew install uv xc gh awscli asdf colima libxml2  # And follow any additional setup instructions brew gives you
asdf plugin add terraform
asdf plugin add nodejs
asdf install
```

## Design

The application is a [Flask](https://flask.palletsprojects.com/) async web app deployed as an 
[AWS Lambda](https://aws.amazon.com/lambda/) function running within the 
[Lambda Web Adapter](https://github.com/awslabs/aws-lambda-web-adapter). 

Good places to start investigating the code are:

* [web.py](src/rss_agg/web.py), the application entry point.
* [routes.py](src/rss_agg/routes.py), the Flask route definitions.

On each request, [RSSService](src/rss_agg/services/rss_service.py) orchestrates the full pipeline:

* A [FeedsService](src/rss_agg/services/feeds_services/base_feeds_service.py) implementation reads a list of feed paths 
  and constructs full Guardian RSS URLs.
    * [FileFeedsService](src/rss_agg/services/feeds_services/file_feeds_service.py) reads from from 
      [feeds.txt](feeds.txt), OR
    * [S3FeedsService](src/rss_agg/services/feeds_services/s3_feeds_service.py) reads from an 
      [S3](https://aws.amazon.com/s3/) object using [boto3](https://docs.aws.amazon.com/boto3/latest/).
* [Fetcher](src/rss_agg/services/fetcher.py) retrieves all feeds concurrently using 
  [httpx](https://www.python-httpx.org/) with HTTP/2 and connection pooling.
* [RSSParser](src/rss_agg/services/rss_parser.py) parses the responses with 
  [defusedxml](https://github.com/tiran/defusedxml) and de-duplicates items by GUID.
* [RSSGenerator](src/rss_agg/services/rss_generator.py) sorts by date, applies a configurable item limit, and emits a 
  fresh RSS feed.

Services are wired together with [wireup](https://maldoinc.github.io/wireup/) for 
[dependency injection](https://martinfowler.com/articles/injection.html), with configuration sourced from environment 
variables as per [the twelve-factor app](https://12factor.net/). 
[AWS API Gateway](https://aws.amazon.com/api-gateway/) provides the public HTTP endpoint, backed by 
[Terraform](https://developer.hashicorp.com/terraform)-managed 
[infrastructure-as-code](https://infrastructure-as-code.com/) located in [terraform/](terraform/).

## Configuration

Configuration is sourced from environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `FEEDS_SERVICE` | Feeds service implementation: `FileFeedsService` or `S3FeedsService` | `FileFeedsService` |
| `FEEDS_FILE` | Path to the feeds list file (used by `FileFeedsService`) | `feeds.txt` |
| `MAX_ITEMS` | Maximum number of items in the output feed | `50` |
| `MAX_CONNECTIONS` | Maximum number of concurrent HTTP connections | `16` |
| `MAX_KEEPALIVE_CONNECTIONS` | Maximum number of keep-alive HTTP connections | `16` |
| `KEEPALIVE_EXPIRY` | Keep-alive connection expiry in seconds | `5` |
| `RETRIES` | Number of HTTP retry attempts per feed | `3` |
| `TIMEOUT` | HTTP request timeout in seconds | `3` |
| `LOG_LEVEL` | Log verbosity: `ERROR`, `WARNING`, `INFO`, or `DEBUG` | `INFO` |

The following are additionally required when `FEEDS_SERVICE=S3FeedsService`:

| Variable | Description | Default |
|----------|-------------|---------|
| `FEEDS_BUCKET_NAME` | S3 bucket name containing the feeds list | `brunns-rss-agg-feeds` |
| `FEEDS_OBJECT_NAME` | S3 object key for the feeds list | `feeds.txt` |
| `AWS_DEFAULT_REGION` | AWS region for S3 access | boto3 default |
| `AWS_ACCESS_KEY_ID` | AWS access key ID for S3 access | boto3 default |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key for S3 access | boto3 default |
| `S3_ENDPOINT` | Custom S3-compatible endpoint URL, e.g. for local testing | AWS S3 |

## Tasks

These tasks can be run using [xc](https://xcfile.dev/).

### pc

Precommit tasks

Requires: test, lint
RunDeps: async

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
RunDeps: async

### unit

Unit tests

```sh
uv run pytest tests/unit/ --durations=10 --cov-report term-missing --cov-fail-under 100 --cov src/rss_agg
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

Inputs: IMAGE_NAME

Environment: IMAGE_NAME=deployment_package.zip

```sh
rm -rf build/ terraform/"$IMAGE_NAME"
uv export --no-dev --python 3.14 --format requirements-txt --output-file requirements.txt
uv pip install -r requirements.txt --target build --python 3.14
cp -r src/rss_agg build/
cp run.sh build/
cp feeds.txt build/
chmod +x build/run.sh
cd build
zip -r ../terraform/"$IMAGE_NAME" .
cd ..
```

### terraform-init

Initialise terraform

Directory: ./terraform

```sh
terraform init
```

### plan

Plan infrastructure changes

Requires: build, terraform-init

RunDeps: async

Directory: ./terraform

```sh
terraform plan
```

### push

Push to origin, and monitor CI workflow 

Requires: pc

Inputs: WORKFLOW

Environment: WORKFLOW=ci.yml

```sh
git push
sleep 5
RUN_ID=$(gh run list --workflow="$WORKFLOW" --limit=1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN_ID" --exit-status
```

### deploy

Run deployment workflow

Inputs: WORKFLOW

Environment: WORKFLOW=cd.yml

```sh
gh workflow run "$WORKFLOW"
sleep 5
RUN_ID=$(gh run list --workflow="$WORKFLOW" --limit=1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN_ID" --exit-status
```

### healthcheck

Check feed is running and returning XML

Inputs: API_URL

Environment: API_URL=http://0.0.0.0:8080

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

Inputs: DURATION

Environment: DURATION=1h

```sh
aws logs tail /aws/lambda/rss_aggregator --since "$DURATION" --format short
```

### create-s3-bucket

One-off commands to set up the [AWS S3](https://aws.amazon.com/s3/) bucket that terraform will use to store
infrastructure state. Run `aws configure` first to authenticate if necessary.

```sh
aws s3 mb s3://brunns-rss-agg-terraform-state --region eu-west-2
aws s3api put-bucket-versioning --bucket brunns-rss-agg-terraform-state --versioning-configuration Status=Enabled
```

### upload-feeds

Upload feeds.txt (by default) to the S3 feeds bucket

Inputs: FEEDS_FILE, BUCKET, OBJECT

Environment: FEEDS_FILE=feeds.txt

Environment: BUCKET=brunns-rss-agg-feeds

Environment: OBJECT=feeds.txt

```sh
aws s3 cp "$FEEDS_FILE" s3://"$BUCKET"/"$OBJECT"
```

## Initial setup steps

Use [brunns-python-template](https://github.com/brunns/brunns-python-template) or similar.
