---
description: Run all UI tests, auto-heal failing locators and assertions, re-run healed tests, and summarize every change made
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (e.g., `--browser firefox`, `--env stage`, or a
specific app like `tests/internet_herokuapp/`). If empty, run all apps on the default browser and env.

---

## Goal

Run the full UI test suite, detect failures caused by stale locators or changed UI text, heal the root
cause by patching `*_locators.py` or `test_data` files, re-run to confirm fixes, and produce a
structured change summary — all without human intervention.

---

## Step 1 — Run Full Test Suite

Create the output directory if it does not exist, then run the complete suite with JUnit XML output:

```bash
mkdir -p output/heal-run
uv run pytest --junit-xml=output/heal-run/results.xml -v --tb=long $ARGUMENTS
```

> On Windows use: `New-Item -ItemType Directory -Force output/heal-run`

Read `output/heal-run/results.xml` after the run.

Parse every `<testcase>` node and build a **failures list**. For each failure record:

- `test_node_id` — `classname` + `::` + `name`
- `failure_message` — full text of the `<failure>` or `<error>` child element

If the failures list is empty, skip to Step 6 (summary: all passed).

---

## Step 2 — Classify Each Failure

For each failed test, apply these rules **in order** and assign one classification:

| Pattern in failure message | Classification | Healable? |
|---|---|---|
| `TimeoutError` + locator expression | **Stale Locator** | ✅ Yes |
| `ElementActionError: Failed to click` or `Failed to fill` | **Missing Element** | ✅ Yes |
| `AssertionError` with a quoted or compared string | **Changed UI Text** | ✅ Yes |
| `ConfigurationError` | **Config / Env** | ⚠️ Warn only |
| `ImportError` or `SyntaxError` | **Code Error** | ❌ No — report only |

For each **healable** failure:

1. Read the test file to find which Page Object class it instantiates.
2. Read the Page Object file to find which locator constant is referenced by the failing action.
3. Read the `apps/<app>/locators/*_locators.py` file to see the current value of that constant.

---

## Step 3 — Capture Live DOM for Each Failing Page

For each healable failure, determine the page URL:

- Find the `PATH` constant on the Page Object class (e.g. `PATH = "/login"`).
- Find the app's base URL environment variable name from `tests/<app>/conftest.py`
  (e.g. `resolve_environment_profile(..., prefix="INTERNET_HEROKUAPP_URL")`).
- Read `.env` to get the resolved base URL value for the active environment.

Run a Playwright DOM snapshot:

```bash
uv run python -c "
import os; from dotenv import load_dotenv; from playwright.sync_api import sync_playwright
load_dotenv()
base = os.environ.get('<BASE_URL_VAR>__DEV', '')
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto(base + '<PAGE_PATH>', wait_until='domcontentloaded')
    open('output/heal-run/dom_<page_name>.html', 'w', encoding='utf-8').write(pg.content())
    b.close()
print('DOM captured')
"
```

Replace `<BASE_URL_VAR>`, `<PAGE_PATH>`, and `<page_name>` with actual values.

Read the saved HTML file.

---

## Step 4 — Heal Each Failure

### Stale Locator / Missing Element

Using the DOM snapshot:

1. Search for the element that was targeted (by its role, label, accessible name, or surrounding context).
2. Determine the most resilient replacement value. Follow the **locator priority** (high → low):
   - ARIA role + accessible name (`get_by_role`)
   - `data-testid` attribute (`get_by_test_id`)
   - Label text (`get_by_label`)
   - Visible text (`get_by_text`)
   - CSS selector — **last resort only**, add a comment explaining why no higher-priority option exists
3. Edit `apps/<app>/locators/*_locators.py`: update **only** the failing constant's value. Leave all
   other constants untouched.
4. Record: `{ file, constant_name, old_value, new_value, reason }`.

### Changed UI Text (AssertionError)

1. Identify the expected string from the assertion in the test or from a `test_data/` variable.
2. Read the DOM snapshot to find the actual current text rendered on the page.
3. If the expected value lives in `apps/<app>/test_data/*.py`, edit that file to update it.
   If it is hardcoded inside the test file, edit the test file only.
4. Record: `{ file, variable_or_line, old_value, new_value, reason }`.

### Healing constraints — MUST follow

- **NEVER** change the locator strategy (e.g. do not downgrade from `get_by_role` to CSS) unless the
  DOM genuinely provides no role/label/test-id that unambiguously targets the element.
- **NEVER** modify `framework_core/`, `fixtures/`, or `tests/conftest.py`.
- **ONLY** edit files under `apps/<app>/locators/` and `apps/<app>/test_data/`.
- If no valid alternative locator exists in the DOM, mark the failure as **UNRESOLVED** and document
  exactly what was tried.

---

## Step 5 — Re-run Previously Failed Tests

After all heals are applied, re-run only the tests that were in the failures list:

```bash
uv run pytest <space-separated test node IDs> -v --tb=short
```

For each re-run result classify as:

- ✅ **HEALED** — test now passes
- ❌ **UNRESOLVED** — test still fails (preserve original error + what was attempted)

---

## Step 6 — Produce Change Summary

Print the following structured report to the terminal:

```
╔══════════════════════════════════════════════════════════════╗
║              UI TEST AUTO-HEAL SUMMARY                      ║
╚══════════════════════════════════════════════════════════════╝

Run date   : <ISO timestamp>
Browser    : <browser used>
Environment: <env used>

TEST RESULTS
  Total     : <N>
  Passed    : <N>   (initial run)
  Failed    : <N>   (initial run)
  Healed    : <N>   ✅
  Unresolved: <N>   ❌

──────────────────────────────────────────────────────────────
CHANGES MADE
──────────────────────────────────────────────────────────────
  File     : apps/<app>/locators/<file>.py
  Constant : <CONSTANT_NAME>
  Before   : "<old value>"
  After    : "<new value>"
  Reason   : <e.g. "Button label changed from 'Login' to 'Sign In' in live DOM">

  (repeat block for every change)

──────────────────────────────────────────────────────────────
UNRESOLVED FAILURES
──────────────────────────────────────────────────────────────
  Test     : <test node id>
  Error    : <original error>
  Tried    : <what healing was attempted>
  Action   : Manual investigation required

  (repeat block for every unresolved failure)

──────────────────────────────────────────────────────────────
FINAL RESULT: ✅ All tests passing  /  ⚠️ <N> unresolved failures remain
──────────────────────────────────────────────────────────────
```

---

## Done When

- [ ] Full test suite executed and `output/heal-run/results.xml` parsed
- [ ] Every failure classified (Stale Locator / Missing Element / Changed UI Text / Unresolvable)
- [ ] DOM snapshot captured for each healable failing page
- [ ] `*_locators.py` and/or `test_data` files patched where a fix was found
- [ ] All previously failed tests re-run; healed/unresolved status confirmed
- [ ] Change summary printed to terminal
