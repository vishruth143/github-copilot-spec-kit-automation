# Contract: Configuration & Secrets Interface

**Feature**: [../spec.md](../spec.md) | **Plan**: [../plan.md](../plan.md)

Defines every environment variable / `.env` key the framework core
recognizes, and the fail-fast behavior when a required one is missing. This
is the contract application onboarders and CI pipeline authors must follow.

## Required variables (framework core)

| Variable | Required? | Example | Purpose |
|---|---|---|---|
| `ENV` | No (CLI `--env` may supply it) | `stage` | Selects the active `EnvironmentProfile` |
| `BROWSER` | No (CLI `--browser` may supply it) | `firefox` | Selects the active browser engine |
| `HEADLESS` | No | `true` / `false` | Overrides default headless mode |

framework_core never requires or resolves any application's base URL
directly — `load_settings()`'s `base_url_prefix` defaults to `None`, so the
shared, session-scoped `settings` fixture only validates `ENV` and never
hardcodes an application's name or URL (Constitution I, II). Each
application resolves its own base URL locally (see below).

## Application-specific variables (per `apps/<app_name>/`)

Each application under test documents its own required variables, including
its own `<APP_PREFIX>__<ENV>` base-url variables, resolved locally by a
fixture in its `tests/<app_name>/conftest.py` that calls
`resolve_environment_profile(settings.environment.name, prefix="<APP_PREFIX>")`.
For example, for `apps/internet_herokuapp/`:

| Variable | Required? | Example | Purpose |
|---|---|---|---|
| `INTERNET_HEROKUAPP_URL__<ENV>` | Yes, for whichever `<ENV>` is active | `INTERNET_HEROKUAPP_URL__STAGE=https://stage.example.com` | Base URL for that environment; looked up dynamically by active environment name |
| `INTERNET_HEROKUAPP_USERNAME` | Yes for login tests | `automation_user@example.com` | Non-production test account username |
| `INTERNET_HEROKUAPP_PASSWORD` | Yes for login tests | *(secret — never committed)* | Non-production test account password |

Another onboarded application, `apps/demo_playwright/`, follows the same
pattern with its own prefix: `DEMO_PLAYWRIGHT_BASE_URL__<ENV>`.

## `.env.example` contract

- MUST list every variable name above (framework + all onboarded apps) with
  an empty or placeholder value — never a real secret.
- MUST be kept in sync whenever a new required variable is introduced (PR
  review checklist item).

## Fail-fast behavior

- The settings loader (`framework_core/config/settings.py`) MUST resolve
  `ENV`/`BROWSER`/`HEADLESS` at the start of the pytest session (in the
  session-scoped `settings` fixture), before any browser is launched. Each
  application's own local fixture (e.g. `internet_herokuapp_base_url`,
  `demo_playwright_base_url`) MUST resolve that application's required
  variables just as eagerly (session-scoped), so a missing variable still
  fails fast before any test using that application runs.
- If any required variable is missing or empty, the loader MUST raise a
  `ConfigurationError` whose message names the exact missing variable
  (e.g., `"Missing required environment variable: INTERNET_HEROKUAPP_URL__STAGE"`),
  causing the session to abort with a clear, actionable message instead of
  failing deep inside a test.

## Secrecy guarantees

- Values resolved from secret-like variables (anything containing
  `PASSWORD`, `TOKEN`, `SECRET`, `KEY`) MUST NOT be written to: structured
  logs, the HTML report, the Playwright report/trace, screenshots, or
  exception messages. The logger MUST redact such values if they are ever
  passed to a log call (defense in depth).
- `.env` MUST be listed in `.gitignore` and MUST NOT be committed.
- CI supplies the same variable names via GitHub Actions Secrets
  (`env:` block referencing `${{ secrets.* }}`) — no code branch differs
  between local `.env` and CI secrets injection.
