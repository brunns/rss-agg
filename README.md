# RSS aggregator

Aggregate, de-duplicate and republish RSS feeds.

Includes deployment to [AWS Lambda](https://aws.amazon.com/lambda/).

Requires [uv](https://docs.astral.sh/uv/), [xc](https://xcfile.dev/), [colima](https://github.com/abiosoft/colima) and [terraform](https://developer.hashicorp.com/terraform):

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

### run

Run CLI - outputs RSS to stdout

```sh
uv run cli -vv
```

### web

Run web server

```sh
uv run flask --app rss_agg/web.py run
```

### test

Run tests

```sh
if command -v colima > /dev/null; then colima status || colima start; fi
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

### build

Build lambda image locally

```sh
uv export --no-dev --python 3.14 --format requirements-txt --output-file requirements.txt
uv pip install -r requirements.txt --target build --python 3.14
cp -r rss_agg build/
cp lambda_function.py build/
cp feeds.txt build/
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

### create-s3-bucket

One-off commands to set up the [AWS S3](https://aws.amazon.com/s3/) bucket that terraform will use to store 
infrastructure state. Run `aws configure` first to autenticate if necessary.

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

For future reference...

```sh 
PACKAGE="rss-agg"
DESCRIPTION="Aggregate, de-duplicate and republish RSS feeds."

uv init --package $PACKAGE --description $DESCRIPTION
cd $PACKAGE
mkdir -p tests/{unit,integration} terraform .github/workflows
touch tests/{unit,integration}/__init__.py tests/conftest.py tests/integration/conftest.py terraform/main.tf .github/workflows/ci.yml

curl https://www.toptal.com/developers/gitignore/api/python,flask,node,emacs,terraform,dotenv,macos > .gitignore
cat <<EOF >> .gitignore

# Custom

.idea/
requirements.txt
terraform/.terraform.lock.hcl
terraform/deployment_package.zip
EOF

cat <<EOF >> README.md
# ${PACKAGE}

${DESCRIPTION}
EOF

uv sync
uv add "flask[async]" httpx yarl defusedxml python-json-logger aws-wsgi
uv add ruff pyright pytest pytest-asyncio pytest-cov pytest-docker feedparser pyhamcrest mbtest respx brunns-matchers pyfakefs --dev

git add .  && git commit -m"Initial commit."
idea .
```
