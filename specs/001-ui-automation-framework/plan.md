# Implementation Plan: Reusable UI Automation Framework

**Branch**: `001-ui-automation-framework` | **Date**: 2026-07-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-ui-automation-framework/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command; its definition describes the execution workflow.

## Summary

Build a plug-and-play, enterprise-grade UI automation framework using
Playwright + pytest, organized so a reusable "core" (config loading, browser
session management, base Page Object, logging, reporting, failure-artifact
capture, pytest fixtures) is fully decoupled from "application-specific" code
(Page Objects, locators, test data, tests) per application. The framework
supports environment selection (DEV/TEST/STAGE/PROD) and browser selection
(Chromium/Firefox/WebKit) purely via CLI flags/environment variables, runs in
parallel via `pytest-xdist`, and automatically captures screenshots, video,
and console logs on failure into timestamped `output/` run folders alongside
an HTML report, Playwright report, and structured logs. Secrets are supplied
via `.env`/environment variables/GitHub Secrets, never hardcoded. A sample
Login Page/Test demonstrates the full pattern, and GitHub Actions runs the
suite on PRs, pushes to `main`, and manual dispatch.

## Technical Context

**Language/Version**: Python 3.13+

**Primary Dependencies**: `playwright` (Python), `pytest`, `pytest-xdist`,
`pytest-html`, `pytest-base-url`, `python-dotenv` (or `pydantic-settings`) for
config/secrets loading, `ruff` for linting/formatting

**Storage**: N/A — no database; configuration lives in per-environment files
(`.env` + YAML/TOML profiles), test data lives in versioned Python/JSON
fixtures, generated artifacts (logs/reports/screenshots/videos) are written
to the filesystem under `output/`

**Testing**: pytest (the framework's own quality gate for its core modules is
also pytest + Ruff; the deliverable itself is a test-automation framework, so
"testing" and "the product" overlap — the sample Login test also serves as an
end-to-end validation of the framework)

**Target Platform**: Cross-platform execution (Linux GitHub Actions runners
primarily; Windows/macOS/Linux for local development) driving Chromium,
Firefox, and WebKit against any HTTP/HTTPS web application

**Project Type**: Single project — reusable test-automation framework (core
library modules + a sample application's tests), not a client/server or
mobile split

**Performance Goals**: Parallel execution (`pytest-xdist`) MUST reduce total
wall-clock suite time by ≥40% vs. serial execution (SC-005); per-test
framework overhead (fixture setup/teardown, logging) must stay negligible
relative to actual browser interaction time

**Constraints**: No hardcoded secrets/environment URLs anywhere in source
(FR-013); zero framework-core modifications when onboarding a new
application (FR-002, SC-002); all synchronization via Playwright auto-wait/
web-first assertions, no hard sleeps (FR-007); tests must be order-independent
and parallel-safe (FR-022)

**Scale/Scope**: v1 ships framework core + one fully-worked sample
application (Login page/flow) across 4 environment profiles and 3 browser
engines; architecture must allow additional applications and future test
types (API, mobile, accessibility, visual) to be added as new modules without
touching the core (FR-021)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Constitution Principle | Plan Compliance |
|---|---|
| I. Modular Architecture (NON-NEGOTIABLE) | `framework_core/` contains only app-agnostic modules (config, browser, base page, reporting, utils); `apps/<app_name>/` holds all app-specific Page Objects/locators/test data. Core never imports from `apps/`. |
| II. Plug-and-Play Design (NON-NEGOTIABLE) | New applications are onboarded by adding an `apps/<new_app>/` package + an environment profile entry + `tests/<new_app>/`; no edits to `framework_core/`, `conftest.py` plugin wiring, or CI workflows are needed. |
| III. Clean Code & Maintainability (NON-NEGOTIABLE) | Ruff (lint + format) enforced via CI gate; public classes/functions carry type hints + docstrings; each module has a single, clearly named responsibility. |
| IV. Page Object Model | `BasePage` in `framework_core/pages/` provides shared, logged, exception-wrapped actions; all app Page Objects extend it and expose business-level methods only; tests never touch locators directly. |
| V. Reliable Test Automation (NON-NEGOTIABLE) | All waits use Playwright `expect(...)`/auto-waiting; no `time.sleep`; retry-safe navigation helpers in `framework_core/utils/`. |
| VI. Test Independence | Fixtures are function-scoped per test (fresh browser context/page); no shared mutable module-level state; `pytest-xdist` group-safe by design. |
| VII. Failure Diagnostics | `conftest.py` hook captures screenshot + video + console log + structured log entry on failure, written to the run's `output/<timestamp>/` tree with the FR-010 naming convention. |
| VIII. Secure Configuration (NON-NEGOTIABLE) | Settings loader reads `.env`/environment variables only; secrets never logged, never written to reports; missing required values raise a fail-fast `ConfigurationError` before any browser launches. |
| IX. Configuration Management | `framework_core/config/` exposes environment, browser, headless/headed, and parallelism settings entirely through env vars/CLI, isolated from business logic. |
| X. Code Quality | CI gate runs Ruff + full pytest suite; PRs cannot merge on failure. |
| XI. Logging & Reporting | `pytest-html` summary + Playwright trace/report + structured per-test log files, all under one run's `output/` folder, clearly enumerating pass/fail/skip counts and durations. |
| XII. Documentation | README.md (tutorial-style) + CONTRIBUTING.md cover install, config, running tests, adding Page Objects/apps, debugging failures. |
| XIII. Extensibility | Root layout reserves sibling space for future `api_core/`, `mobile_core/`, etc., without touching `framework_core/` for UI testing. |
| XIV. Dependency Management | `uv` + `pyproject.toml` + committed `uv.lock` give reproducible installs; dependency set kept minimal and pinned. |
| XV. Continuous Integration | `.github/workflows/ci.yml` runs on PR, push to `main`, and `workflow_dispatch`, executing Ruff + parallel pytest and uploading `output/` as a build artifact. |

**Initial gate result**: PASS — no violations requiring Complexity Tracking entries.

## Project Structure

### Documentation (this feature)

```text
specs/001-ui-automation-framework/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
pyproject.toml           # uv-managed project + dependency manifest
uv.lock                  # reproducible dependency lockfile (committed)
.env.example              # documents every required config/secret name
.gitignore
README.md                 # tutorial-style onboarding guide
CONTRIBUTING.md

.github/
└── workflows/
    └── ci.yml            # PR, push-to-main, and workflow_dispatch triggers

framework_core/            # reusable, application-agnostic framework core
├── __init__.py
├── config/
│   ├── __init__.py
│   ├── settings.py        # env/browser/parallelism settings loader (fail-fast)
│   └── environments.py    # DEV/TEST/STAGE/PROD profile definitions
├── browser/
│   ├── __init__.py
│   └── browser_factory.py # Playwright browser/context/page lifecycle
├── pages/
│   ├── __init__.py
│   └── base_page.py       # BasePage: shared, logged, exception-wrapped actions
├── reporting/
│   ├── __init__.py
│   ├── logger.py           # structured per-run logging setup
│   └── artifact_capture.py # screenshot/video/console-log capture on failure
└── utils/
    ├── __init__.py
    └── waits.py            # resilient wait/retry helpers (no hard sleeps)

fixtures/                   # shared, reusable pytest fixtures (framework-level)
├── __init__.py
└── browser_fixtures.py     # browser/page/context fixtures wired into conftest

apps/                        # application-specific code (one subfolder per app)
└── internet_herokuapp/       # sample application used by FR-018
    ├── __init__.py
    ├── pages/
    │   ├── __init__.py
    │   └── login_page.py
    ├── locators/
    │   ├── __init__.py
    │   └── login_locators.py
    └── test_data/
        ├── __init__.py
        └── login_data.py

tests/
├── conftest.py              # root fixture wiring, CLI options, failure hook
└── internet_herokuapp/
    └── test_scenarios.py    # all sample Login test scenarios (step-comment header, markers)

output/                       # generated at runtime, gitignored
└── <run-timestamp>/
    ├── logs/
    ├── screenshots/
    ├── videos/
    └── html-report/
```

**Structure Decision**: Single project. `framework_core/` and `fixtures/` are
the only modules imported by `conftest.py`/tests directly and MUST remain
application-agnostic (Constitution I, II). Each application under test gets
its own `apps/<app_name>/` package (Page Objects, locators, test data) and
`tests/<app_name>/` test package; onboarding a new application never touches
`framework_core/`, `fixtures/`, `tests/conftest.py`, or `.github/workflows/`.
`output/` is fully generated/gitignored and organized per run for easy
diagnosis (Constitution VII, XI).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — the Constitution Check above passes for every principle with
the structure chosen. This section intentionally has no entries.

## Post-Design Constitution Check

*Re-evaluated after Phase 1 (research.md, data-model.md, contracts/,
quickstart.md).*

Every design artifact produced in Phase 0/1 reinforces the same table above:
`data-model.md` keeps `EnvironmentProfile`/`BrowserConfig`/`TestExecutionRun`/
`FailureArtifact` free of any application-specific fields (Principle I, II);
`contracts/page-object-contract.md` codifies the `BasePage` boundary
(Principle IV); `contracts/configuration-contract.md` codifies fail-fast,
secret-safe configuration (Principle VIII, IX); `contracts/
artifact-naming-contract.md` codifies the diagnostics/reporting layout
(Principle VII, XI); `research.md` §10–11 codify the CI and code-quality gate
(Principle XIV, XV, X). No new violations were introduced by the detailed
design.

**Post-design gate result**: PASS — no Complexity Tracking entries required.
