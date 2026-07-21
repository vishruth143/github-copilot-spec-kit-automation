# Contract: CLI / pytest Invocation Interface

**Feature**: [../spec.md](../spec.md) | **Plan**: [../plan.md](../plan.md)

This defines the command-line contract that any user (local developer or CI)
uses to run the framework. This is the framework's primary "external
interface" since it has no network API.

## Base command

```bash
uv run pytest [OPTIONS] [PATH]
```

## Custom options (added by `tests/conftest.py`)

| Option | Values | Default | Maps to |
|---|---|---|---|
| `--env` | `dev` \| `test` \| `stage` \| `prod` (case-insensitive) | `dev` (or `ENV` env var if set) | `EnvironmentProfile.name` |
| `--browser` | `chromium` \| `firefox` \| `webkit` | `chromium` (or `BROWSER` env var if set) | `BrowserConfig.engine` |
| `--headed` | flag (presence = `True`) | `False` (headless) | `BrowserConfig.headless` |
| `-n` / `--numprocesses` (from `pytest-xdist`) | integer or `auto` | `1` (serial) | `BrowserConfig.parallel_workers` |
| `-m` (standard pytest marker selection) | e.g. `-m smoke`, `-m "regression and not sanity"` | none (all tests) | pytest marker filtering |

## Precedence rules

1. Explicit CLI flag (`--env`, `--browser`, `--headed`) always wins.
2. If a CLI flag is omitted, the corresponding environment variable (`ENV`,
   `BROWSER`, `HEADLESS`) is used.
3. If neither is set, the documented default applies.
4. An unrecognized `--env` or `--browser` value MUST cause immediate
   collection-time failure with a message listing the supported values —
   tests MUST NOT silently fall back to a default when an explicit but
   invalid value was supplied.

## Registered pytest markers

Declared in `pyproject.toml` under `[tool.pytest.ini_options]` /
`markers = [...]` so `--strict-markers` can be enabled safely:

- `smoke` — minimal, fast, must-pass-always subset
- `regression` — full regression coverage
- `sanity` — quick post-deploy sanity subset
- `critical` — business-critical flows

A test MAY carry more than one marker (e.g., `@pytest.mark.smoke` and
`@pytest.mark.critical` together); marker selection with `-m` follows
standard pytest boolean expression rules. A test with no marker is still
collected and runs as part of an unfiltered (`pytest` with no `-m`) run, but
is excluded from any marker-filtered run.

## Example invocations

```bash
# Smoke suite, Chromium, headless, DEV, serial
uv run pytest -m smoke --env dev --browser chromium

# Full regression, parallel, Firefox, headed, STAGE
uv run pytest -m regression --env stage --browser firefox --headed -n auto

# Single test file
uv run pytest tests/internet_herokuapp/test_scenarios.py --env test
```

## Exit codes

Standard pytest exit codes apply (0 = all passed, 1 = tests failed, 2 =
usage error, etc.). CI treats any non-zero exit code as a failed run that
still uploads `output/` artifacts (`if: always()`).
