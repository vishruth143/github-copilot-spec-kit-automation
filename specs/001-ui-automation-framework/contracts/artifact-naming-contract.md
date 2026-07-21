# Contract: Output Artifact & Naming Convention

**Feature**: [../spec.md](../spec.md) | **Plan**: [../plan.md](../plan.md)

Defines the on-disk contract for every generated artifact so tooling, CI
uploads, and humans can reliably locate results (FR-010, FR-011, FR-012).

## Directory layout (per run)

```text
output/
└── <run_timestamp>/            # DD-MM-YY-HH-MM-SS, created once at session start
    ├── logs/
    │   └── <test_name>__<browser>__<environment>__<timestamp>.log
    ├── screenshots/
    │   └── <test_name>__<browser>__<environment>__<timestamp>.png
    ├── videos/
    │   └── <test_name>__<browser>__<environment>__<timestamp>.webm
    └── html-report/
        ├── report.html          # pytest-html summary for the whole run
        └── traces/
            └── <test_name>__<browser>__<environment>__<timestamp>.zip  # Playwright trace
```

## Naming convention

```text
<test_name>__<browser>__<environment>__<DD-MM-YY-HH-MM-SS>.<ext>
```

- `test_name`: the pytest node id with `::` and `/` replaced by `_` (e.g.,
  `tests_internet_herokuapp_test_scenarios.py_test_login_with_valid_credentials`).
- `browser`: one of `chromium`, `firefox`, `webkit`.
- `environment`: one of `dev`, `test`, `stage`, `prod` (lowercase).
- Timestamp: capture moment formatted `DD-MM-YY-HH-MM-SS`, e.g.
  `21-07-26-14-05-32`.
- `ext`: `png` (screenshot), `webm` (video), `log` (structured log), `zip`
  (Playwright trace).

## Generation rules

- Artifacts are generated **only on failure** (screenshot, video, console
  log, trace) — passing tests do not produce these files, keeping `output/`
  uncluttered.
- The structured per-test log (`logs/`) captures, at minimum: test start,
  test end, each executed step (via `BasePage._log_step`), any exception with
  stack trace, and locator failures — for both passing and failing tests, so
  a reviewer can audit a passing run too (Constitution XI); only the
  *filename-tagged, timestamped* per-failure log variant above is guaranteed
  solely on failure.
- The `html-report/report.html` file is always generated once per run
  (pass, fail, or mixed), summarizing executed/passed/failed/skipped counts
  and duration per test.
- If Playwright cannot produce a video or console log for a given browser
  engine, the corresponding file is simply absent and the structured log
  records `"video capture unavailable for <browser>"` /
  `"console capture unavailable for <browser>"` — this is not an error.

## Consumption contract (CI)

- The CI workflow uploads the entire `output/<run_timestamp>/` folder as a
  single build artifact via `actions/upload-artifact`, with
  `if: always()` so both passing and failing runs publish it.
- No tooling should assume a fixed number of runs retained on disk locally;
  each local run gets its own new `<run_timestamp>` folder and old ones are
  left for the developer to clean up (documented in README, excluded from
  git via `.gitignore`).
