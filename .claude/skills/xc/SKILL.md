---
name: xc
description: Run project workflows using the xc task runner. Use when testing, linting, formatting, committing, pushing, or deploying. Always prefer xc tasks over running underlying commands directly.
---

Run the requested workflow using `xc`. If $ARGUMENTS is provided, focus on that workflow (test, lint, commit, push, deploy). Otherwise, follow the appropriate workflow for the current task.

## Available Tasks

### Testing
- `xc unit` — Unit tests with 100% coverage requirement
- `xc integration` — Integration tests (starts Colima/Docker if needed)
- `xc test` — All tests concurrently (unit + integration)

### Code Quality
- `xc format` — Format with ruff (run before linting)
- `xc lint` — Lint with ruff + pyright

### Pre-commit & Push
- `xc pc` — Pre-commit: runs test + lint concurrently (required before every commit)
- `xc push` — Runs `pc`, then pushes and watches CI workflow

### Deploy
- `xc deploy` — Triggers CD workflow via GitHub Actions and watches it

## Workflows

### Making a commit
1. `xc pc` — run full test suite + linter
2. `git add <specific files>` — stage only the files you changed (never `git add -A` or `git add .`)
3. `git commit -m "..."` — write a clear, concise commit message
4. Optionally: `xc push` to push and monitor CI

### Pushing to origin
Use `xc push` instead of `git push` directly — it runs `xc pc` first, then pushes and watches the CI run.

### Deploying
Deploy only via GitHub Actions, never locally:
1. Ensure changes are pushed (`xc push`)
2. `xc deploy` — triggers the CD workflow and watches it complete

## Rules
- **Always use `xc` tasks** — never run the underlying commands (pytest, ruff, etc.) directly
- **Never `git add -A` or `git add .`** — add specific files only to avoid accidentally staging secrets or binaries
- **No `Co-Authored-By` trailers** in commit messages
- **`xc web` must be killed after use** — gunicorn workers persist; use `lsof -i :8080` to find and kill them
- Integration tests need Docker/Colima — `xc integration` handles starting Colima automatically
