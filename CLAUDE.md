# CLAUDE.md
2
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RSS aggregator that fetches, de-duplicates, and republishes RSS feeds from theguardian.com. Deployed as an AWS Lambda function behind API Gateway, using Python 3.14.

## Build and Development Commands

This project uses [xc](https://xcfile.dev/) for task running. All commands are defined in `README.md`.

### Essential commands:
- `xc test` - Run all tests (unit + integration)
- `xc unit` - Run unit tests with coverage (requires 100% coverage)
- `xc integration` - Run integration tests (requires Colima/Docker)
- `xc lint` - Lint code (ruff + pyright)
- `xc format` - Format code with ruff
- `xc cli` - Run CLI locally (outputs RSS to stdout)
- `xc web` - Run web server locally on port 8080 (**always terminate after use** — gunicorn workers show as `python3.x` processes, use `lsof -i :8080` to find and kill any that remain)
- `xc build` - Build Lambda deployment package
- `xc plan` - Plan Terraform changes (runs build first)

### Before committing:
Always run `xc pc` before any commit. This runs the full test suite and linter.

### Running a single test:
```sh
uv run pytest tests/unit/test_specific.py::test_name -vv
```

### Running a single integration test:
```sh
uv run pytest tests/integration/test_specific.py::test_name -s
```

## Architecture

### Application Flow

The application has two entry points:

1. **CLI mode** (`cli.py`): Fetches feeds and outputs RSS to stdout
2. **Web mode** (`web.py`): Flask app serving RSS via HTTP (used in Lambda)

Both modes follow the same flow:
1. Read feed paths from `feeds.txt`
2. Construct full URLs by combining `base_url` (theguardian.com) + path + "/rss"
3. Fetch all feeds concurrently via `Fetcher` (using httpx with HTTP/2)
4. Parse feeds with `RSSParser` (using defusedxml)
5. De-duplicate items by GUID
6. Sort by date and limit to `max_items`
7. Generate new RSS feed with `RSSGenerator`

### Dependency Injection

Uses [wireup](https://github.com/maldoinc/wireup) for dependency injection:
- Services are marked with `@injectable` decorator
- Configuration values injected with `Annotated[Type, Inject(config="key")]`
- Container created from environment variables (web) or CLI args (cli)
- Container held in `WireupFlask.container` for web mode

See `README.md` for the full service descriptions and configuration reference.

## Lambda Deployment

### Architecture
- Lambda function uses Python 3.14 runtime
- Uses AWS Lambda Web Adapter layer to run Flask app in Lambda
- Handler is `run.sh` which starts gunicorn
- API Gateway provides public HTTP endpoint
- State stored in S3 backend for Terraform
- SnapStart is configured but currently disabled (`apply_on = "None"` in `terraform/modules/lambda/main.tf`)

### Deployment Process

**Always deploy via GitHub Actions CD workflow**, not locally:

1. Commit and push your changes to GitHub
2. Trigger the workflow:
   - Via GitHub UI: Go to Actions → Deploy → Run workflow
   - Via CLI: `xc deploy`
3. The workflow will:
   - Run tests and linting
   - Build deployment package (`xc build`)
   - Run `terraform init` and `terraform apply -auto-approve`
   - Run healthcheck to verify deployment

**Terraform modules** in `terraform/modules/`:
- `lambda/`: Lambda function, IAM role, CloudWatch logs, "live" alias
- `api_gateway/`: API Gateway REST API with Lambda integration
- `s3_feeds/`: S3 bucket for feeds list (versioned, private)

## Git Commits

- Never add `Co-Authored-By` trailers to commit messages.
- Always use `xc push` to push code (runs full test suite + linter before pushing and monitors CI).

## Tool Preferences

- **JSON parsing**: Use `jq` instead of `python -c` for parsing JSON output
- **Task runner**: Always use `xc` tasks rather than running the underlying commands directly.
- **Python tool & package management**: Use `uv` and `uvx` where appropriate.
- **Command-line tools**: Prefer standard Unix tools when available

## Code Style

- Ruff with strict settings (`select = ["ALL"]`)
- Max line length: 120
- Max cyclomatic complexity: 5
- Pyright for type checking
- Tests excluded from some linting rules (see `pyproject.toml`)
- Coverage omits `cli.py` and `web.py` (entry points)

## Testing

- **Unit tests**: `tests/unit/` - Pure Python, no I/O, requires 100% coverage
- **Integration tests**: `tests/integration/` - Use Docker/Colima for external services
- Test frameworks: pytest, pytest-asyncio, pyhamcrest, mockito (not unittest.mock), respx
- Use `pyfakefs` for filesystem mocking
- Run tests using `xc` tasks

## Dependencies

- **Flask**: Async support required (`flask[async]`)
- **httpx**: HTTP client with HTTP/2 support (`httpx[http2]`)
- **defusedxml**: Safe XML parsing (prevents XML bombs)
- **wireup**: Dependency injection
- **yarl**: URL handling
- **gunicorn**: WSGI server for Lambda
- **boto3**: AWS asset access
