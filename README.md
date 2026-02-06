# RSS aggregator

Aggregate, de-duplicate and republish RSS feeds.

Includes deployment to [AWS Lambda](https://aws.amazon.com/lambda/).

Requires [uv](https://docs.astral.sh/uv/), [xc](https://xcfile.dev/), and [terraform](https://developer.hashicorp.com/terraform):

```sh
brew install uv xc colima terraform
```

## Tasks

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
uv run gunicorn -b 0.0.0.0:8080 rss_agg.web:app
```

### test

Run tests

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

### healthcheck

Check feed is running and returning XML

Inputs: API_URL

```shell
echo "Testing API at: $API_URL"

trap "rm -f response.xml" EXIT

for i in {1..6}; do
    HTTP_RESPONSE=$(curl -s -w "HTTP_STATUS:%{http_code}" "$API_URL")
    HTTP_STATUS=$(echo "$HTTP_RESPONSE" | tr -d '\n' | sed -e 's/.*HTTP_STATUS://')
    BODY=$(echo "$HTTP_RESPONSE" | sed -e 's/HTTP_STATUS:.*//')
    
    if [ "$HTTP_STATUS" -eq 200 ]; then
      echo "$BODY" > response.xml
      
      if xmllint --noout response.xml; then
        echo "Success: API returned valid XML"
        exit 0
      else
        echo "Error: API returned 200 but the body is NOT valid XML"
        cat response.xml
        exit 1
      fi
    fi
    
    echo "Attempt $i: API returned $HTTP_STATUS, retrying in 5s..."
    sleep 5
done

echo "Error: API failed to respond with 200 after 6 attempts"
exit 1
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
