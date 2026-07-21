# Contributing

Thank you for improving this UI automation framework. This document covers
the contribution workflow, the core-vs-apps architecture rule, and the
quality gates every pull request must pass.

## Getting started

```bash
uv sync
uv run playwright install chromium firefox webkit
cp .env.example .env   # then fill in local values
```

See the [README](README.md) for full usage instructions.

## The core-vs-apps architecture rule

This is the single most important rule in this repository (Constitution I,
II — [.specify/memory/constitution.md](.specify/memory/constitution.md)):

- **`framework_core/`, `fixtures/`, `tests/conftest.py`, `.github/workflows/`
  are application-agnostic.** They MUST NEVER contain a hardcoded
  application name, URL, selector, or credential.
- **All application-specific code lives under `apps/<app_name>/` and
  `tests/<app_name>/`.** Onboarding a new application must never require
  editing any of the framework-core paths above.
- Every Page Object **must** extend `framework_core.pages.base_page.BasePage`
  and expose only business-meaningful methods (no raw locators leaking to
  tests).
- Prefer the locator priority order — role → test id → label/text →
  CSS/XPath (last resort, with a justifying comment) — see
  [contracts/page-object-contract.md](specs/001-ui-automation-framework/contracts/page-object-contract.md).

If a change to "core" code is genuinely required (e.g., a new shared
capability), explain why in the pull request description.

## Adding tests

- New test files live under `tests/<app_name>/`.
- Every test starts with a plain-language, numbered "Test steps:" comment
  block describing what it does, independent of the code.
- Tag tests with the appropriate marker(s): `smoke`, `regression`, `sanity`,
  `critical` (see `pyproject.toml`).
- Never hardcode credentials, tokens, or environment URLs in test code or
  test data — read them from environment variables (see
  [contracts/configuration-contract.md](specs/001-ui-automation-framework/contracts/configuration-contract.md)).
- Any new required environment variable must be added to `.env.example`
  (placeholder value only) in the same pull request.

## Quality gates (must pass before merge)

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -n auto
```

CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs the same
checks across the Chromium/Firefox/WebKit matrix on every pull request.

## Pull request checklist

- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass with zero
      violations.
- [ ] `uv run pytest -n auto` passes locally.
- [ ] No hardcoded secrets, credentials, or environment-specific URLs were
      introduced (search your diff for anything that should come from
      `.env`/CI secrets instead).
- [ ] Any new required environment variable is documented in `.env.example`.
- [ ] New/changed Page Objects extend `BasePage` and use the locator
      priority order.
- [ ] New tests include a "Test steps:" comment block and appropriate
      marker(s).
- [ ] `README.md` is updated if user-facing behavior changed.
