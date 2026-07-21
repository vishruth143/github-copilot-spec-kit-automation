# Phase 0 Research: Reusable UI Automation Framework

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

All unknowns from the feature request were resolvable from the request
itself, the ratified constitution, and established Playwright/pytest
ecosystem practice — no items remain marked `NEEDS CLARIFICATION`. This
document records the decisions made and the alternatives rejected.

## 1. Configuration & secrets loading

- **Decision**: Use `python-dotenv` to load a local `.env` file into process
  environment variables for local development, and read all configuration
  (environment name, browser, headless flag, base URLs, credentials) through
  a single typed `Settings`/`EnvironmentProfile` loader in
  `framework_core/config/`. In CI, the same environment variables are
  injected via GitHub Actions Secrets/`env:` — no code path difference
  between local and CI.
- **Rationale**: Keeps one consistent access pattern (`os.environ` +
  validation) regardless of where the process runs; avoids a second
  configuration format to maintain. Fail-fast validation (raise
  `ConfigurationError` naming the missing variable) satisfies FR-014 and
  Constitution VIII.
- **Alternatives considered**: `pydantic-settings` (richer validation, but an
  extra dependency for marginal benefit at this scope — documented as a
  future upgrade option, not required for v1); raw `os.getenv()` scattered
  across modules (rejected — violates FR-013/Constitution IX isolation of
  environment-specific values from business logic).

## 2. Environment profile selection (DEV/TEST/STAGE/PROD)

- **Decision**: Each environment is a named profile (a small dataclass) with
  `base_url` and any environment-specific overrides, stored in
  `framework_core/config/environments.py`. The active profile is selected by
  an `ENV` (or `--env` pytest CLI option) value that looks up the matching
  profile; an unknown/misspelled name raises a fail-fast, descriptive error
  rather than silently defaulting.
- **Rationale**: Satisfies FR-004/SC-004 (config-only switching) and directly
  answers the "unsupported environment name" edge case from spec.md.
- **Alternatives considered**: One `.env` file per environment loaded by
  filename convention (`.env.dev`, `.env.stage`) — viable and documented as a
  supported pattern in README, but the profile registry remains the single
  source of truth so both approaches funnel through the same validated
  loader.

## 3. Browser & execution-mode selection

- **Decision**: Add custom pytest CLI options (`--browser=chromium|firefox|
  webkit`, `--headed`) resolved through `pytest-playwright`'s standard
  fixture-override mechanism plus the framework's own `browser_factory`.
  Default is `chromium`, headless.
- **Rationale**: `pytest-playwright`-style flags are the ecosystem-standard,
  well-documented way to parameterize browser/headed mode without custom
  plumbing, satisfying FR-005 with minimal custom code (Constitution III —
  KISS).
- **Alternatives considered**: Environment-variable-only browser selection
  (rejected as sole mechanism — CLI flags are more discoverable for local
  ad-hoc runs; both are supported since the loader reads CLI first, env var
  as fallback).

## 4. Parallel execution strategy

- **Decision**: Use `pytest-xdist` (`-n auto` or `-n <count>`) for parallel
  execution; every fixture that touches browser/page state is function-scoped
  so each worker/test gets an isolated `BrowserContext`/`Page`. Failure
  artifact filenames embed the test name + timestamp (down to the second) to
  avoid collisions across parallel workers (spec.md edge case).
- **Rationale**: `pytest-xdist` is the standard, well-maintained parallel
  runner for pytest; function-scoped Playwright contexts are Playwright's own
  documented recommendation for test isolation, satisfying FR-006, FR-022,
  Constitution V/VI.
- **Alternatives considered**: Process-per-browser custom orchestration
  (rejected — reinvents what `pytest-xdist` already provides reliably).

## 5. Locator strategy priority

- **Decision**: Enforce, via code review guidance and `BasePage` helper
  method naming (`get_by_role_action`, etc.), the priority order: (1)
  `get_by_role`, (2) `get_by_test_id`, (3) label/text locators, (4) CSS/XPath
  only with an inline justification comment.
- **Rationale**: Matches Playwright's own recommended locator priority for
  resilience to DOM/styling changes, directly satisfying FR-008.
- **Alternatives considered**: XPath-first (rejected — brittle, explicitly
  discouraged by both the user request and Playwright best practice).

## 6. Failure diagnostics capture (screenshot, video, console logs, structured logs)

- **Decision**: Implement a pytest `hookimpl(hookwrapper=True)` for
  `pytest_runtest_makereport` in `tests/conftest.py` that, on failure, pulls
  the current test's `page`/`context` from the fixture, saves a screenshot
  (`page.screenshot(path=...)`), finalizes the context's video recording
  (Playwright's built-in `record_video_dir` context option), and dumps
  buffered console messages (collected via a `page.on("console", ...)`
  listener registered per test) into the same run folder. A dedicated
  `framework_core/reporting/logger.py` configures a per-run structured logger
  (Python `logging` with a run-scoped file handler).
- **Rationale**: Uses Playwright's native, supported capture mechanisms
  (no custom video/screenshot pipeline) — satisfies FR-009, FR-010, FR-011,
  Constitution VII, and the spec's WebKit-console-limitation edge case
  (framework logs "console capture unavailable" instead of failing when the
  listener yields nothing).
- **Alternatives considered**: Third-party video-capture tools (rejected —
  Playwright already provides this natively with no extra dependency).

## 7. Reporting

- **Decision**: `pytest-html` for the human-readable HTML report plus
  Playwright's own trace viewer output (`--tracing=retain-on-failure`) as the
  "Playwright report," both written into the run's `output/<timestamp>/`
  folder.
- **Rationale**: Both are first-class, actively maintained tools already
  implied by the user request ("HTML Report" + "Playwright Report");
  satisfies FR-012 without introducing a heavier reporting service.
- **Alternatives considered**: Allure (richer but adds a Java dependency and
  extra CI complexity) — documented in the constitution's assumptions as an
  optional future upgrade, not required for v1.

## 8. Output/artifact folder organization & naming

- **Decision**: One folder per run: `output/<DD-MM-YY-HH-MM-SS>/` created at
  session start (a pytest `session`-scoped autouse fixture), containing
  `logs/`, `screenshots/`, `videos/`, `html-report/`. Failure artifact
  filenames follow `<test_name>__<browser>__<environment>__<DD-MM-YY-HH-MM-SS>.
  <ext>`.
- **Rationale**: Matches FR-010 exactly and keeps every artifact type
  co-located and easy to browse for a human (Constitution XI).
- **Alternatives considered**: Flat `output/` with no per-run subfolder
  (rejected — successive runs would overwrite or clutter, harder to browse).

## 9. Dependency & environment management

- **Decision**: `uv` manages the virtual environment and `pyproject.toml`
  dependencies exclusively (`uv sync`, `uv run pytest ...`,
  `uv run playwright install --with-deps`); `uv.lock` is committed for
  reproducibility.
- **Rationale**: Explicitly mandated by the user request and Constitution
  XIV (single standardized workflow, reproducible builds).
- **Alternatives considered**: `pip` + `requirements.txt` (rejected — not
  reproducible/lockfile-based by default); `poetry` (rejected — user
  explicitly requested `uv`).

## 10. CI/CD workflow design

- **Decision**: One GitHub Actions workflow (`.github/workflows/ci.yml`)
  triggered on `pull_request`, `push` to `main`, and `workflow_dispatch`; job
  steps: checkout → set up Python 3.13 → install `uv` → `uv sync` →
  `uv run playwright install --with-deps` → `uv run ruff check .` →
  `uv run pytest -n auto --browser=chromium` → upload `output/` as a build
  artifact (`actions/upload-artifact`, `if: always()` so failures still
  publish diagnostics).
- **Rationale**: Satisfies FR-015, SC-006, and Constitution XV in one
  workflow instead of three separate ones, minimizing duplication (DRY).
- **Alternatives considered**: Separate workflows per trigger (rejected —
  duplicates steps; a single workflow with multiple `on:` triggers is
  simpler and easier to maintain, per Constitution III KISS).

## 11. Code quality gate

- **Decision**: `ruff check` (linting) and `ruff format --check` (formatting)
  run as an explicit CI step before tests; both are configured in
  `pyproject.toml` under `[tool.ruff]`.
- **Rationale**: User explicitly requested Ruff; single tool covering both
  lint + format keeps tooling minimal (Constitution III, X).
- **Alternatives considered**: `flake8` + `black` + `isort` combo (rejected —
  three tools where Ruff alone covers the same ground faster).

## Outstanding Clarifications

None. All technical decisions above are considered final for Phase 1 design.
