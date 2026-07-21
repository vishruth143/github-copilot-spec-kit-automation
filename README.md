# Reusable UI Automation Framework

A plug-and-play, enterprise-grade UI automation framework built with
**Playwright**, **pytest**, and the **Page Object Model** design pattern —
managed with **uv**.

- Add a brand-new application under test without touching the framework core.
- Switch environment (`dev`/`test`/`stage`/`prod`) and browser
  (`chromium`/`firefox`/`webkit`) with a CLI flag or environment variable —
  no code changes.
- Run tests in parallel, headless or headed.
- On any failure, automatically get a screenshot, video recording, console
  log, and Playwright trace — no re-running required to diagnose.
- No secrets ever committed: all credentials/URLs come from environment
  variables / `.env` / CI secrets.

This README is a tutorial. For the full design rationale, see
[specs/001-ui-automation-framework/](specs/001-ui-automation-framework/)
(spec, plan, research, data model, contracts) and
[.specify/memory/constitution.md](.specify/memory/constitution.md).

## Table of contents

- [Quick reference](#quick-reference)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running tests](#running-tests)
- [Reading test reports and failure diagnostics](#reading-test-reports-and-failure-diagnostics)
- [Project structure](#project-structure)
- [Adding a Page Object](#adding-a-page-object)
- [Adding a new application](#adding-a-new-application)
- [Configuring environments](#configuring-environments)
- [Configuring browsers](#configuring-browsers)
- [Parallel execution](#parallel-execution)
- [Continuous Integration](#continuous-integration)
- [Code quality](#code-quality)
- [Contributing](#contributing)

## Quick reference

The essential commands, for anyone who just wants to get running:

```bash
# --- One-time setup ---
uv sync                                          # install dependencies
uv run playwright install chromium firefox webkit  # install browser engines
cp .env.example .env                             # then fill in real values

# --- Run tests ---
uv run pytest                                    # everything, using .env defaults
uv run pytest -m smoke                           # smoke suite only
uv run pytest tests/internet_herokuapp/          # one application's tests
uv run pytest tests/internet_herokuapp/test_scenarios.py::test_login_with_valid_credentials  # one test
uv run pytest -n auto                            # parallel, auto worker count

# --- Override environment / browser / mode for a single run ---
uv run pytest --env stage --browser firefox --headed
uv run pytest --env test --browser webkit -m regression -n auto

# --- Code quality (run before every commit) ---
uv run ruff check .
uv run ruff format .

# --- View the last run's results ---
start output/<run-timestamp>/html-report/report.html   # Windows
# open output/<run-timestamp>/html-report/report.html  # macOS
# xdg-open output/<run-timestamp>/html-report/report.html  # Linux
```

See the sections below for full details on each of these.

## Prerequisites

- Python 3.13 or later on `PATH`
- [`uv`](https://docs.astral.sh/uv/) — the only supported package manager for
  this project (do not use `pip install` directly)
- Git

## Installation

```bash
# 1. Clone the repository
git clone <this-repository-url>
cd github-copilot-spec-kit-automation

# 2. Install Python dependencies into a local .venv (managed by uv)
uv sync

# 3. Install the Playwright browser engines
uv run playwright install chromium firefox webkit
```

`uv sync` reads `pyproject.toml`/`uv.lock` and creates/updates `.venv/` with
exactly the pinned dependency versions — no `requirements.txt`, no global
installs.

## Configuration

All environment-specific values and secrets are supplied via environment
variables, loaded from a local `.env` file that is **never committed** (see
[.gitignore](.gitignore)).

```bash
cp .env.example .env
```

Edit `.env` and fill in real values for your machine, for example:

```dotenv
ENV=dev
BROWSER=chromium
HEADLESS=true

INTERNET_HEROKUAPP_URL__DEV=https://the-internet.herokuapp.com
INTERNET_HEROKUAPP_USERNAME=tomsmith
INTERNET_HEROKUAPP_PASSWORD=SuperSecretPassword!
```

- `ENV` / `BROWSER` / `HEADLESS` are optional defaults — every one of them
  can also be overridden per-run with a CLI flag (see below).
- `framework_core` never hardcodes any application's name or base URL: each
  application resolves its own `<APP_PREFIX>__<ENV>` base-url variable
  locally (e.g. `INTERNET_HEROKUAPP_URL__DEV`, `DEMO_PLAYWRIGHT_BASE_URL__DEV`)
  via a fixture in its own `tests/<app_name>/conftest.py` (see
  [Configuring environments](#configuring-environments)).
- Never put real secrets in `.env.example` — only empty placeholders. Real
  values live in your local `.env` (gitignored) or, in CI, in GitHub Actions
  Secrets.

## Running tests

```bash
# Run everything using the defaults from .env
uv run pytest

# Run only the smoke suite
uv run pytest -m smoke

# Override environment / browser / headed mode for a single run
uv run pytest -m smoke --env stage --browser firefox --headed

# Run a specific application's tests
uv run pytest tests/internet_herokuapp/

# Run a specific test file or test
uv run pytest tests/internet_herokuapp/test_scenarios.py::test_login_with_valid_credentials
```

Available markers (see `pyproject.toml`): `smoke`, `regression`, `sanity`,
`critical`. Combine with pytest's `-m` expression syntax, e.g.
`-m "smoke and not regression"`.

Available CLI flags (registered in `tests/conftest.py`):

| Flag | Values | Overrides |
|---|---|---|
| `--env` | `dev` \| `test` \| `stage` \| `prod` | `ENV` env var |
| `--browser` | `chromium` \| `firefox` \| `webkit` | `BROWSER` env var |
| `--headed` | (flag) | `HEADLESS` env var (forces headed mode) |

## Reading test reports and failure diagnostics

Every test run creates a fresh, timestamped folder:

```text
output/
  <DD-MM-YY-HH-MM-SS>/
    html-report/report.html   # pytest-html report for the whole run
    logs/run.log               # structured, secret-redacted run log
    screenshots/                # full-page PNG per *failed* test
    videos/                     # video recording per *failed* test
    logs/<test>.console.log     # browser console output per *failed* test
    html-report/traces/         # Playwright trace .zip per *failed* test
```

Artifact filenames follow
`<test_name>__<browser>__<environment>__<DD-MM-YY-HH-MM-SS>.<ext>` (see
[contracts/artifact-naming-contract.md](specs/001-ui-automation-framework/contracts/artifact-naming-contract.md)),
so you can immediately tell which test, browser, and environment produced a
given artifact — even after running the same suite many times.

To debug a failure:

1. Open `output/<run>/html-report/report.html` and find the failed test.
2. Open the matching screenshot for the failure moment.
3. Play the matching video for the full interaction leading up to it.
4. Open the Playwright trace in `html-report/traces/` with
   `uv run playwright show-trace <path-to-trace.zip>` for a full DOM/network
   timeline.
5. Check `logs/run.log` and the test's `.console.log` for application/browser
   console output (passwords/tokens/secrets are automatically redacted).

Passing tests intentionally do **not** keep a screenshot/video/trace, to keep
`output/` small.

## Project structure

```text
framework_core/     # Application-agnostic framework code (never app-specific)
  config/            # Environment & browser configuration resolution
  browser/           # Playwright browser/context lifecycle
  pages/             # BasePage — the mandatory parent for every Page Object
  utils/              # Resilient wait helpers
  reporting/          # Logging + failure-artifact capture
fixtures/            # Shared pytest fixtures (browser/context/page lifecycle)
apps/<app_name>/     # One folder per application under test
  locators/           # Locator descriptors (role/test-id/label — no brittle CSS/XPath)
  pages/              # Page Objects extending BasePage
  test_data/          # Non-secret sample test data
tests/<app_name>/    # Test files + app-specific fixtures/conftest.py
output/              # Timestamped run artifacts (gitignored, except .gitkeep)
.github/workflows/   # CI pipeline definitions
```

## Adding a Page Object

Every Page Object **must** extend
`framework_core.pages.base_page.BasePage` and expose only
business-meaningful methods — never raw locators — to tests. See
[apps/internet_herokuapp/pages/login_page.py](apps/internet_herokuapp/pages/login_page.py)
for a complete example:

```python
from framework_core.pages.base_page import BasePage
from apps.internet_herokuapp.locators import login_locators


class LoginPage(BasePage):
    PATH = "/login"

    def open(self) -> None:
        self.goto(self.PATH)

    def login(self, username: str, password: str) -> None:
        self.page.get_by_label(login_locators.USERNAME_FIELD_LABEL).fill(username)
        self.page.get_by_label(login_locators.PASSWORD_FIELD_LABEL).fill(password)
        self.click_by_role(login_locators.LOGIN_BUTTON_ROLE, login_locators.LOGIN_BUTTON_NAME)
```

Locator priority (most to least resilient) — see
[contracts/page-object-contract.md](specs/001-ui-automation-framework/contracts/page-object-contract.md):

1. **Role** — `get_by_role(...)` (via `BasePage.click_by_role`/`fill_by_role`)
2. **Test id** — `get_by_test_id(...)` (via `BasePage.click_by_test_id`/`fill_by_test_id`)
3. **Label / text** — `get_by_label(...)`, `get_by_text(...)`
4. **CSS / XPath** — last resort only, with a comment justifying why no
   higher-priority locator was available

## Adding a new application

The framework is plug-and-play: onboarding a new application never requires
changing `framework_core/`, `fixtures/`, `tests/conftest.py`, or
`.github/workflows/`.

1. Create the app's folders:

   ```bash
   mkdir -p apps/<new_app>/{locators,pages,test_data}
   mkdir -p tests/<new_app>
   ```

   Every application's `tests/<new_app>/` directory MUST include an empty
   `__init__.py` (as must `tests/` itself). Since every application uses the
   same `test_scenarios.py` filename, pytest needs each `tests/<app>/` to be
   an importable package so it can tell `tests.internet_herokuapp.test_scenarios`
   apart from `tests.demo_playwright.test_scenarios` — without it, pytest
   fails with an `import file mismatch` error the first time a second app is
   added.

2. Add `apps/<new_app>/locators/<page>_locators.py` with named locator
   constants.
3. Add `apps/<new_app>/pages/<page>_page.py` with a Page Object extending
   `BasePage`.
4. Add `apps/<new_app>/test_data/<page>_data.py` with non-secret sample
   values.
5. Add the app's base URL(s) to `.env.example` (placeholders) and your local
   `.env` (real values), following an `<APP_PREFIX>__<ENV>` naming
   convention of your choosing (e.g. `<NEW_APP>_URL__<ENV>`) — see
   [contracts/configuration-contract.md](specs/001-ui-automation-framework/contracts/configuration-contract.md).
6. Add `tests/<new_app>/test_scenarios.py` — all of this application's test
   scenarios live in this one file (do not split scenarios across multiple
   files, e.g. one per feature) — plus a local `conftest.py` for any
   app-specific fixtures — e.g. credentials, and a `<new_app>_base_url`
   fixture that resolves your chosen prefix via
   `resolve_environment_profile(settings.environment.name, prefix="<APP_PREFIX>")`
   (see `tests/internet_herokuapp/conftest.py` or
   `tests/demo_playwright/conftest.py` for worked examples) — keep these out
   of the shared `tests/conftest.py`.
7. Run `uv run pytest tests/<new_app>/`.

See [apps/demo_playwright/](apps/demo_playwright/) and
[tests/demo_playwright/](tests/demo_playwright/) for a second, fully worked
example.

## Configuring environments

Each environment (`dev`, `test`, `stage`, `prod`) is resolved as a name by
`framework_core` (with no per-environment code branching anywhere in the
framework); each application then resolves its own base URL for that
environment from its own `<APP_PREFIX>__<ENV>` environment variables (e.g.
`INTERNET_HEROKUAPP_URL__STAGE`, `DEMO_PLAYWRIGHT_BASE_URL__STAGE`).

```bash
uv run pytest --env stage
# or
ENV=stage uv run pytest
```

If the resolved environment's base URL variable is missing or blank, the
framework fails fast with a clear `ConfigurationError` naming the missing
variable — it never silently falls back to another environment.

```text
$ uv run pytest --env bogus
ConfigurationError: Unsupported environment 'bogus'. Supported environments: dev, test, stage, prod.
```

## Configuring browsers

```bash
uv run pytest --browser firefox
uv run pytest --browser webkit --headed
# or
BROWSER=webkit HEADLESS=false uv run pytest
```

Supported engines: `chromium`, `firefox`, `webkit`. An unsupported engine
name fails fast with a `ConfigurationError`.

```text
$ uv run pytest --browser edge
ConfigurationError: Unsupported browser 'edge'. Supported browsers: chromium, firefox, webkit.
```

## Parallel execution

```bash
# Auto-detect CPU count
uv run pytest -n auto

# Explicit worker count
uv run pytest -n 4
```

Powered by `pytest-xdist`. Each test gets its own isolated `BrowserContext`/
`Page`, and all workers in a run share the same `output/<run_timestamp>/`
folder so artifacts from a parallel run stay together.

## Continuous Integration

GitHub Actions runs the suite automatically on pull requests, pushes to
`main`, and on-demand via `workflow_dispatch` — see
[.github/workflows/ci.yml](.github/workflows/ci.yml). The workflow:

- Installs `uv`, syncs dependencies, and installs the matching Playwright
  browser for each matrix leg.
- Runs a `chromium` / `firefox` / `webkit` build matrix, each running the
  suite in parallel via `pytest -n auto`.
- Runs `ruff check` and `ruff format --check` as a quality gate before tests.
- Reads all secrets (credentials, base URLs) from GitHub Actions Secrets
  (`Settings → Secrets and variables → Actions`) — never from committed
  files. Required secrets: `INTERNET_HEROKUAPP_URL__DEV`,
  `INTERNET_HEROKUAPP_USERNAME`, `INTERNET_HEROKUAPP_PASSWORD`,
  `DEMO_PLAYWRIGHT_BASE_URL__DEV`.
- Uploads each matrix leg's `output/` folder (HTML report, screenshots,
  videos, logs, traces) as a downloadable workflow artifact
  (`test-output-<browser>`), on every run, pass or fail
  (`if: always()`) — open the workflow run in the **Actions** tab and
  download the artifact from the run summary page.

## Code quality

```bash
uv run ruff check .
uv run ruff format .
```

Ruff enforces linting (pyflakes, isort, pyupgrade, bugbear, simplify,
pydocstyle) and formatting across the whole repository — run both before
committing.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding conventions, how to add
tests, and the pull request checklist.
