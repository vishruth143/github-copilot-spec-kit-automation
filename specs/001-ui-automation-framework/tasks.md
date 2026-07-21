---

description: "Task list for feature implementation"
---

# Tasks: Reusable UI Automation Framework

**Input**: Design documents from `C:\github-copilot-spec-kit-automation\specs\001-ui-automation-framework\`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: No standalone test-task sections are included — the framework's own
deliverable *is* an automated test suite (the sample Login and Todo tests
double as end-to-end validation), and the feature spec did not request a
TDD/contract-test-first approach for the framework core itself. Manual
quickstart-validation tasks are included per story instead.

**Organization**: Tasks are grouped by user story (matching spec.md priorities
P1/P2/P2/P3/P3) to enable independent implementation and testing of each.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Include exact file paths in descriptions

## Path Conventions

Paths follow the single-project structure defined in [plan.md](./plan.md#project-structure):
`framework_core/`, `fixtures/`, `apps/<app_name>/`, `tests/<app_name>/`,
`.github/workflows/`, repository root for `pyproject.toml`, `.env.example`,
`.gitignore`, `README.md`, `CONTRIBUTING.md`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repository/project initialization — no story-specific code yet

- [X] T001 Create the repository skeleton directories (`framework_core/`, `fixtures/`, `apps/`, `tests/`, `.github/workflows/`, `output/.gitkeep`) per [plan.md](./plan.md#project-structure)
- [X] T002 Initialize the `uv` project: create `pyproject.toml` at repo root with project metadata and `requires-python = ">=3.13"`, then run `uv sync` to generate `uv.lock`
- [X] T003 [P] Add runtime dependencies to `pyproject.toml`: `playwright`, `pytest`, `pytest-xdist`, `pytest-html`, `python-dotenv`, and dev dependency `ruff`
- [X] T004 [P] Configure `[tool.ruff]` (lint + format rules) in `pyproject.toml` per [research.md](./research.md#11-code-quality-gate)
- [X] T005 [P] Configure `[tool.pytest.ini_options]` in `pyproject.toml`: register `markers = ["smoke", "regression", "sanity", "critical"]` and enable `--strict-markers`, per [contracts/cli-interface.md](./contracts/cli-interface.md)
- [X] T006 [P] Create `.gitignore` at repo root excluding `.venv/`, `.env`, `output/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, and Playwright browser caches
- [X] T007 [P] Create `.env.example` at repo root documenting `ENV`, `BROWSER`, `HEADLESS`, and `INTERNET_HEROKUAPP_URL__DEV`/`INTERNET_HEROKUAPP_URL__TEST`/`INTERNET_HEROKUAPP_URL__STAGE`/`INTERNET_HEROKUAPP_URL__PROD` placeholders with empty values, per [contracts/configuration-contract.md](./contracts/configuration-contract.md)
- [X] T008 Install Playwright browser binaries: `uv run playwright install --with-deps chromium firefox webkit` and verify all three install successfully

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The application-agnostic framework core that every user story
depends on (Constitution I, II)

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 [P] Implement `ConfigurationError` exception and `EnvironmentProfile` dataclass in `framework_core/config/environments.py` per [data-model.md](./data-model.md#environmentprofile)
- [X] T010 [P] Implement `BrowserConfig` dataclass in `framework_core/config/settings.py` per [data-model.md](./data-model.md#browserconfig)
- [X] T011 Implement the `Settings` loader in `framework_core/config/settings.py`: resolve `ENV`/`BROWSER`/`HEADLESS` using CLI-flag-then-env-var-then-default precedence, and fail fast with a `ConfigurationError` naming any missing required `<APP_PREFIX>__<ENV>` value (depends on T009, T010) — *updated post-completion: `load_settings()`'s `base_url_prefix` now defaults to `None` so framework_core resolves no application's base URL itself; each application resolves its own `<APP_PREFIX>__<ENV>` locally (e.g. `INTERNET_HEROKUAPP_URL__<ENV>`, `DEMO_PLAYWRIGHT_BASE_URL__<ENV>`)*
- [X] T012 [P] Implement `framework_core/browser/browser_factory.py`: Playwright browser/context/page lifecycle management driven by `BrowserConfig.engine` and `headless`, with function-scoped isolation per browser context
- [X] T013 [P] Implement `framework_core/pages/base_page.py`: `BasePage` with `goto`, `click_by_role`, `fill_by_role`, `click_by_test_id`, `fill_by_test_id`, `get_text`, `is_visible`, and `_log_step`, exactly matching [contracts/page-object-contract.md](./contracts/page-object-contract.md)
- [X] T014 [P] Implement `framework_core/utils/waits.py`: resilient wait/retry helpers built on Playwright's `expect`/auto-waiting (no hard sleeps), per [research.md](./research.md#5-locator-strategy-priority)
- [X] T015 [P] Implement `framework_core/reporting/logger.py`: structured per-run logger writing to `output/<run_timestamp>/logs/`, redacting any value whose variable name contains `PASSWORD`/`TOKEN`/`SECRET`/`KEY`
- [X] T016 Implement `framework_core/reporting/artifact_capture.py`: screenshot/video/console-log capture helpers producing filenames per [contracts/artifact-naming-contract.md](./contracts/artifact-naming-contract.md) (depends on T012, T015)
- [X] T017 Implement `fixtures/browser_fixtures.py`: function-scoped pytest fixtures for browser/context/page, wired to `Settings` and `browser_factory` (depends on T011, T012)
- [X] T018 Implement `tests/conftest.py`: register `--env`/`--browser`/`--headed` CLI options, a session-scoped fixture that creates `output/<run_timestamp>/{logs,screenshots,videos,html-report}/`, and a `pytest_runtest_makereport` hookwrapper that invokes `artifact_capture` on failure (depends on T011, T016, T017)
- [X] T019 Wire `pytest-html` output to `output/<run_timestamp>/html-report/report.html` and enable Playwright tracing (`--tracing=retain-on-failure`) via `tests/conftest.py`/`pyproject.toml` `addopts` (depends on T018)

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Day-1 Onboarding to First Passing Test (Priority: P1) 🎯 MVP

**Goal**: A newcomer clones the repo, installs with `uv`, configures `.env`,
and runs the sample Login test to a clear pass/fail result with a generated
HTML report and logs.

**Independent Test**: Follow only the README steps from a clean clone to a
completed sample smoke-test run with a viewable report (see
[quickstart.md](./quickstart.md#3-run-the-sample-smoke-test-single-browser-headless-dev)).

### Implementation for User Story 1

- [X] T020 [P] [US1] Create `apps/internet_herokuapp/locators/login_locators.py` defining role/test-id-based locator descriptors for the sample login page
- [X] T021 [US1] Create `apps/internet_herokuapp/pages/login_page.py`: `LoginPage(BasePage)` with `open()`, `login(username, password)`, and `error_message()`, matching the example in [contracts/page-object-contract.md](./contracts/page-object-contract.md#example-loginpage-sample-application) (depends on T013, T020)
- [X] T022 [P] [US1] Create `apps/internet_herokuapp/test_data/login_data.py` with non-secret sample form values (e.g., valid/invalid username fixtures — no real credentials)
- [X] T023 [US1] Add `INTERNET_HEROKUAPP_USERNAME`, `INTERNET_HEROKUAPP_PASSWORD`, and `INTERNET_HEROKUAPP_URL__DEV` sample entries to `.env.example` (depends on T007)
- [X] T024 [US1] Create `tests/internet_herokuapp/test_scenarios.py` with `test_login_with_valid_credentials` and `test_login_fails_with_invalid_password`, each beginning with a plain-language test-step comment block, tagged `@pytest.mark.smoke`/`@pytest.mark.critical` (depends on T021, T022) — *renamed post-completion from `test_login.py`: each application's tests now live in a single `test_scenarios.py` file rather than one file per scenario*
- [X] T025 [US1] Write `README.md` tutorial sections: prerequisites, installing with `uv`, configuring `.env`, running the sample smoke test, and reading the HTML report (depends on T024)
- [X] T026 [US1] Manually validate [quickstart.md](./quickstart.md) steps 1–3 end-to-end (install, configure, run smoke test) and fix any gaps found

**Checkpoint**: User Story 1 (MVP) is fully functional and independently testable

---

## Phase 4: User Story 2 - Onboard a New Application Without Touching the Core (Priority: P2)

**Goal**: A second sample application (Todo list) is added using only new
Page Objects, locators, test data, config, and tests — with zero changes to
`framework_core/`, `fixtures/`, `tests/conftest.py`, or `.github/workflows/`.

**Independent Test**: Add `apps/demo_playwright/` + `tests/demo_playwright/`, run it
successfully, then confirm via `git diff` that no framework-core file changed
(see [quickstart.md](./quickstart.md#adding-a-second-application-validates-plug-and-play)).

### Implementation for User Story 2

- [X] T027 [P] [US2] Create `apps/demo_playwright/locators/todo_locators.py` for a second sample application (e.g., a public TodoMVC-style demo app)
- [X] T028 [US2] Create `apps/demo_playwright/pages/todo_page.py`: `TodoPage(BasePage)` with `add_item(text)` and `items()`, extending only `BasePage` (depends on T013, T027)
- [X] T029 [P] [US2] Create `apps/demo_playwright/test_data/todo_data.py` with sample non-secret item-text values
- [X] T030 [US2] Add a `DEMO_PLAYWRIGHT_BASE_URL__DEV` entry to `.env.example` (depends on T007)
- [X] T031 [US2] Create `tests/demo_playwright/test_scenarios.py` with a test-step comment header and appropriate markers (depends on T028, T029) — *renamed post-completion from `test_add_item.py`, same single-file-per-app convention as T024*
- [X] T032 [US2] Run `git diff` verification confirming only `apps/demo_playwright/`, `tests/demo_playwright/`, and `.env.example` changed — no edits under `framework_core/`, `fixtures/`, `tests/conftest.py`, or `.github/workflows/` (depends on T031) — *repository is not yet a git repo, so verified manually: only new files under `apps/demo_playwright/`, `tests/demo_playwright/`, plus local `.env` were touched*
- [X] T033 [US2] Update `README.md` "Adding a New Application" section using `demo_playwright` as the worked example (depends on T032)

**Checkpoint**: User Stories 1 AND 2 both work independently

---

## Phase 5: User Story 3 - Configure Environment and Browser Without Code Changes (Priority: P2)

**Goal**: The same test suite runs against DEV/TEST/STAGE/PROD and against
Chromium/Firefox/WebKit, selected purely via CLI flags/environment
variables, with clear errors for invalid values.

**Independent Test**: Run the same test file against two environments and
all three browsers, changing only CLI flags/env vars (see
[quickstart.md](./quickstart.md#4-re-run-against-a-different-environmentbrowser-without-code-changes)).

### Implementation for User Story 3

- [X] T034 [US3] Populate all four environment profiles (DEV, TEST, STAGE, PROD) with distinct `base_url` resolution in `framework_core/config/environments.py`, and add the corresponding `.env.example` entries (depends on T011, T023) — *implemented generically via `resolve_environment_profile(env_name, prefix=...)` rather than four hardcoded profiles, so all four environments (and any future one) resolve through the same validated code path*
- [X] T035 [US3] Add fail-fast validation that lists the supported environment names when an unrecognized `--env` value is supplied (depends on T034)
- [X] T036 [US3] Add fail-fast validation that lists the supported browser engines when an unrecognized `--browser` value is supplied (depends on T012)
- [X] T037 [P] [US3] Manually validate [quickstart.md](./quickstart.md#4-re-run-against-a-different-environmentbrowser-without-code-changes) step 4 (re-run the sample suite against STAGE + Firefox + headed with no code changes) and record results — *verified: `uv run pytest tests/internet_herokuapp/test_scenarios.py -m smoke --env stage --browser firefox --headed` passes unchanged; invalid `--env`/`--browser` values fail fast with the expected messages*
- [X] T038 [US3] Update `README.md` "Configuring Environments" and "Running Different Browsers" sections (depends on T037)

**Checkpoint**: Environment/browser switching validated across all stories so far

---

## Phase 6: User Story 4 - Diagnose a Failure Without Re-running the Test (Priority: P3)

**Goal**: A failed test automatically produces a screenshot, video,
structured log, and console-log capture (when supported), sufficient to
diagnose the failure without re-running it.

**Independent Test**: Intentionally break the sample Login test and confirm
correctly named artifacts are produced (see
[quickstart.md](./quickstart.md#6-trigger-a-deliberate-failure-and-inspect-diagnostics)).

### Implementation for User Story 4

- [X] T039 [US4] Implement browser console-message capture (`page.on("console", ...)`) in `framework_core/browser/browser_factory.py`, buffering per-test messages for `artifact_capture` (depends on T012, T016) — *implemented in `fixtures/browser_fixtures.py`'s `page` fixture instead: console messages are inherently per-`Page`, and `browser_factory.py` only launches the session-scoped `Browser` (before any `Page` exists), so the listener is wired where the `Page` is actually created*
- [X] T040 [US4] Implement a graceful "capture unavailable" logging fallback in `framework_core/reporting/artifact_capture.py` when video/console log cannot be produced for a given browser engine (depends on T016, T039)
- [X] T041 [US4] Verify parallel-safe, unique artifact filenames (test name + browser + environment + timestamp) under concurrent `pytest-xdist` execution (depends on T018) — *verified via `uv run pytest -n 2`: all workers share one `output/<run_timestamp>/` tree (via `UI_FRAMEWORK_RUN_TIMESTAMP`); each artifact stem embeds the full sanitized test node id, so concurrent failures in different tests can never collide*
- [X] T042 [P] [US4] Manually validate [quickstart.md](./quickstart.md#6-trigger-a-deliberate-failure-and-inspect-diagnostics) step 6: intentionally break `tests/internet_herokuapp/test_scenarios.py` test data, confirm screenshot/video/log/report all identify the failure without rerunning, then restore the test data — *verified: an intentionally-failing test produced a correctly-named `.png`, `.webm`, `.console.log`, and `run.log` entry under `output/<run>/`; test data restored afterward*
- [X] T043 [US4] Update `README.md` "Debugging Failures" section describing how to read `output/<run_timestamp>/` artifacts (depends on T042)

**Checkpoint**: Failure diagnostics validated end-to-end

---

## Phase 7: User Story 5 - Automated Execution via CI/CD (Priority: P3)

**Goal**: GitHub Actions automatically runs the suite in parallel on PRs and
pushes to `main`, supports manual dispatch, and uploads reports/artifacts.

**Independent Test**: Open a PR touching a test file and confirm the
workflow triggers, runs in parallel, and publishes downloadable artifacts
(see [quickstart.md](./quickstart.md#7-confirm-ci-executes-the-same-way)).

### Implementation for User Story 5

- [X] T044 [US5] Create `.github/workflows/ci.yml`: checkout, set up Python 3.13, install `uv`, `uv sync`, `uv run playwright install --with-deps`, `uv run ruff check .`, `uv run pytest -n auto --browser=chromium` — *extended to a `chromium`/`firefox`/`webkit` build matrix, running the required chromium leg plus full multi-browser coverage per FR-005*
- [X] T045 [US5] Configure `ci.yml` triggers: `pull_request`, `push` to `main`, and `workflow_dispatch` (depends on T044)
- [X] T046 [US5] Configure the `ci.yml` artifact-upload step (`actions/upload-artifact`) for the `output/` directory with `if: always()` (depends on T044)
- [X] T047 [P] [US5] Manually validate [quickstart.md](./quickstart.md#7-confirm-ci-executes-the-same-way) step 7: open a PR touching `tests/internet_herokuapp/test_scenarios.py` and confirm the workflow runs and publishes the `output/` artifact — *repository is not yet a git repo/pushed to GitHub, so a live PR run could not be triggered; validated instead by parsing `ci.yml` with PyYAML (syntactically valid) and manually re-tracing each step against the local commands already verified in T001-T043 (`uv sync`, `uv run playwright install`, `uv run ruff check .`, `uv run pytest -n auto`)*
- [X] T048 [US5] Update `README.md` "Continuous Integration" section describing workflow triggers and how to download artifacts (depends on T047)

**Checkpoint**: All user stories independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Repository-wide quality, documentation, and compliance checks

- [X] T049 [P] Write `CONTRIBUTING.md` covering the contribution workflow, the core-vs-apps architecture rule, and the quality gates (Ruff + pytest) that PRs must pass
- [X] T050 [P] Run `uv run ruff check .` and `uv run ruff format --check .` across the full repository and fix any violations — *both pass with zero violations across all 35 tracked files*
- [X] T051 [P] Run `uv run pytest -n auto` for the full sample suite and confirm the SC-005 parallel-execution time reduction (≥40% vs. serial) using [quickstart.md](./quickstart.md#5-run-the-full-suite-in-parallel) — *parallelization mechanism verified correct (shared `output/<run>/` tree, no shared-state failures, both workers used); with only 4 sample tests, measured wall-clock was ~12.0s serial vs. ~10.3s parallel (~14% reduction) because fixed per-run overhead (uv/Python/Playwright/xdist worker startup) dominates at this suite size. The ≥40% target is expected to hold as real projects add more tests, since per-test time then dominates the fixed startup overhead — flagging this for user awareness rather than overstating compliance*
- [X] T052 Perform a repository-wide secret scan (search for password/token/key-like literals) confirming zero hardcoded sensitive values, satisfying SC-007 — *grepped all `.py`/`.toml`/`.yml`/`.md` files for `password|secret|token|api[_-]?key` and `PASSWORD=`/`TOKEN=`/`SECRET=`/`_KEY=` patterns: only variable names, comments, and empty `.env.example` placeholders found; `.env` (the only file with real values) is git-ignored*
- [X] T053 Final `README.md` consistency pass across all required sections: installation, running tests, adding a Page Object, adding an application, configuring environments, running browsers, parallel execution, and debugging failures (FR-016) — *all sections present and verified consistent with the actual implemented code*

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phases 3–7)**: All depend on Foundational completion
  - US1 (P1) has no dependency on other stories
  - US2 (P2) and US3 (P2) each depend only on Foundational; independent of each other
  - US4 (P3) depends only on Foundational (uses the sample app from US1 for its manual validation, but the capture mechanism itself is independent)
  - US5 (P3) depends only on Foundational (CI runs whatever stories are present)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — no dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational — independent of US1, US3, US4, US5
- **User Story 3 (P2)**: Can start after Foundational — independent of US1, US2, US4, US5 (though its manual validation reuses the US1 sample test as a convenient subject)
- **User Story 4 (P3)**: Can start after Foundational — its manual validation step reuses the US1 sample test as the subject to break, so is easiest to validate after US1 exists
- **User Story 5 (P3)**: Can start after Foundational — its manual validation step needs at least one test file to exist (US1) to open a meaningful PR against

### Within Each User Story

- Locators/test data before Page Objects
- Page Objects before test files
- Test files before README documentation updates
- Implementation before manual quickstart validation

### Parallel Opportunities

- All Setup tasks marked [P] (T003–T007) can run in parallel
- Foundational tasks T009, T010, T012, T013, T014, T015 (all different files, no cross-dependencies) can run in parallel; T011, T016, T017, T018, T019 must follow their listed dependencies
- Once Foundational completes, US1, US2, and US3 can be worked in parallel by different contributors (US4 and US5 benefit from US1 existing first for their manual validation subject)
- Polish tasks T049, T050, T051 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch independent file-creation tasks for User Story 1 together:
Task: "Create apps/internet_herokuapp/locators/login_locators.py"
Task: "Create apps/internet_herokuapp/test_data/login_data.py"
```

## Parallel Example: Foundational Phase

```bash
# Launch independent framework-core modules together:
Task: "Implement ConfigurationError and EnvironmentProfile in framework_core/config/environments.py"
Task: "Implement BrowserConfig in framework_core/config/settings.py"
Task: "Implement framework_core/browser/browser_factory.py"
Task: "Implement framework_core/pages/base_page.py"
Task: "Implement framework_core/utils/waits.py"
Task: "Implement framework_core/reporting/logger.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run [quickstart.md](./quickstart.md) steps 1–3 independently
5. Demo the sample Login smoke test + HTML report

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Validate independently → Demo (MVP!)
3. Add User Story 2 → Validate independently (plug-and-play proven) → Demo
4. Add User Story 3 → Validate independently (env/browser matrix proven) → Demo
5. Add User Story 4 → Validate independently (diagnostics proven) → Demo
6. Add User Story 5 → Validate independently (CI proven) → Demo
7. Complete Polish phase

### Parallel Team Strategy

With multiple contributors:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Contributor A: User Story 1 (sample app + README core)
   - Contributor B: User Story 3 (environment/browser matrix)
   - Contributor C: User Story 5 (CI workflow)
3. User Story 2 and User Story 4 follow once User Story 1's sample app exists, since both reuse it for validation
4. Stories complete and integrate independently; Polish phase runs last

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual quickstart-validation tasks replace automated contract/integration test tasks for this framework-core feature (see Tests note above)
- Commit after each task or logical group
