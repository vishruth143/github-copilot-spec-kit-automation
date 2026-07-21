# Quickstart: Validate the UI Automation Framework

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

This is a runnable validation guide, not a full README. It proves the
framework works end-to-end using the sample Login application (User Story 1
in [spec.md](./spec.md#user-story-1---day-1-onboarding-to-first-passing-test-priority-p1)).
Full onboarding documentation belongs in the eventual `README.md`
(tasks phase); this guide only validates the design.

## Prerequisites

- Python 3.13+ available on PATH
- [`uv`](https://docs.astral.sh/uv/) installed
- Git access to this repository

## 1. Install dependencies

```bash
uv sync
uv run playwright install --with-deps chromium firefox webkit
```

**Expected outcome**: `uv sync` completes with a populated `.venv/` and
`uv.lock` unchanged (or updated on first run); Playwright reports all three
browser engines installed successfully.

## 2. Configure required values

```bash
cp .env.example .env
# then edit .env and set, at minimum:
#   ENV=dev
#   INTERNET_HEROKUAPP_URL__DEV=<sample app URL>
#   INTERNET_HEROKUAPP_USERNAME=<non-production test account>
#   INTERNET_HEROKUAPP_PASSWORD=<non-production test account password>
```

**Expected outcome**: `.env` exists locally and is *not* tracked by git
(verify with `git status` — it must not appear).

## 3. Run the sample smoke test (single browser, headless, DEV)

```bash
uv run pytest -m smoke --env dev --browser chromium
```

**Expected outcome**: Test session completes with a clear PASS/FAIL summary;
an `output/<run_timestamp>/html-report/report.html` file is created; on pass,
no failure artifacts are produced; on failure, matching screenshot/video/log
files appear under that run's `screenshots/`, `videos/`, and `logs/`
subfolders, named per
[contracts/artifact-naming-contract.md](./contracts/artifact-naming-contract.md).

## 4. Re-run against a different environment/browser without code changes

```bash
uv run pytest -m smoke --env stage --browser firefox --headed
```

**Expected outcome**: Same test file executes unchanged, now targeting the
`STAGE` base URL in Firefox, in a headed window — confirming FR-004/FR-005/
SC-004 (config-only switching).

## 5. Run the full suite in parallel

```bash
uv run pytest -n auto
```

**Expected outcome**: Tests distribute across workers with no shared-state
failures; total wall-clock time is measurably lower than a serial
(`uv run pytest -p no:xdist`) run of the same suite, validating SC-005.

## 6. Trigger a deliberate failure and inspect diagnostics

Temporarily break the sample login test (e.g., wrong password in test data),
run step 3 again, then open the newest `output/<run_timestamp>/` folder:

- `screenshots/…png` shows the failing screen state.
- `videos/…webm` plays back the full interaction leading to failure.
- `logs/…log` shows step-by-step execution ending in the exception.
- `html-report/report.html` marks the test as failed with a link/reference to
  the same artifacts.

**Expected outcome**: The failure can be fully diagnosed from these files
alone, without re-running the test — validating User Story 4.

## 7. Confirm CI executes the same way

Open a pull request that modifies `tests/internet_herokuapp/test_scenarios.py`
(or push to `main`), then check the GitHub Actions run for this repository.

**Expected outcome**: The workflow triggers automatically, runs in parallel,
and the completed run has a downloadable artifact containing the same
`output/` structure as the local run — validating User Story 5 / SC-006.

## Adding a second application (validates plug-and-play)

1. Create `apps/<new_app>/{pages,locators,test_data}/`.
2. Create `apps/<new_app>/pages/<page>_page.py` extending
   `framework_core.pages.base_page.BasePage` per
   [contracts/page-object-contract.md](./contracts/page-object-contract.md).
3. Add the new environment's base URL variable(s) to `.env.example` and your
   local `.env`, following
   [contracts/configuration-contract.md](./contracts/configuration-contract.md).
4. Create `tests/<new_app>/test_scenarios.py` (all of this application's test
   scenarios in one file).
5. Run `uv run pytest tests/<new_app>/`.

**Expected outcome**: The new suite runs successfully, and `git diff` shows
changes only under `apps/<new_app>/`, `tests/<new_app>/`, and `.env.example`
— zero changes to `framework_core/`, `fixtures/`, `tests/conftest.py`, or
`.github/workflows/`, validating User Story 2 / SC-002.
