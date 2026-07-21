# Contract: Page Object Base Interface

**Feature**: [../spec.md](../spec.md) | **Plan**: [../plan.md](../plan.md)

Defines the interface every application-specific Page Object MUST implement
by extending `framework_core.pages.base_page.BasePage`. This is the contract
that keeps the framework "plug-and-play" (Constitution I, II, IV).

## `BasePage` contract

```python
class BasePage:
    """Shared, logged, exception-safe browser interactions for all pages."""

    def __init__(self, page: "playwright.sync_api.Page") -> None: ...

    # --- Navigation ---
    def goto(self, path: str = "") -> None:
        """Navigate to `base_url + path`, waiting for the page to be ready."""

    # --- Resilient interaction helpers (locator-priority aware) ---
    def click_by_role(self, role: str, name: str, **kwargs) -> None: ...
    def fill_by_role(self, role: str, name: str, value: str, **kwargs) -> None: ...
    def click_by_test_id(self, test_id: str) -> None: ...
    def fill_by_test_id(self, test_id: str, value: str) -> None: ...
    def get_text(self, locator: "playwright.sync_api.Locator") -> str: ...
    def is_visible(self, locator: "playwright.sync_api.Locator") -> bool: ...

    # --- Diagnostics ---
    def _log_step(self, message: str) -> None:
        """Write a structured log entry for the current test step."""
```

## Rules for subclasses (application Page Objects)

1. **MUST** call `super().__init__(page)` and store only what is needed
   (no direct access to framework-internal reporting/config modules beyond
   what `BasePage` exposes).
2. **MUST** expose only business-meaningful public methods (e.g.,
   `login(username: str, password: str) -> None`,
   `error_message() -> str | None`) — never return raw `Locator` objects from
   public methods, and never require the caller to know a locator string.
3. **MUST NOT** import from another application's `apps/<other_app>/`
   package, and **MUST NOT** import anything from `tests/`.
4. **MUST** use the locator priority order from
   [../research.md](../research.md#5-locator-strategy-priority): role → test-id
   → label/text → CSS/XPath (last resort, with justification comment).
5. **MUST** let exceptions raised by `BasePage` helpers propagate with their
   enriched context (step name, locator description) rather than catching and
   discarding them.
6. **SHOULD** keep one Page Object per page/reusable component, named
   `<PageName>Page` in `apps/<app_name>/pages/<page_name>_page.py`.

## Example: `LoginPage` (sample application)

```python
class LoginPage(BasePage):
    """Page Object for the sample application's login screen."""

    PATH = "/login"

    def open(self) -> None:
        """Navigate directly to the login screen."""
        self.goto(self.PATH)

    def login(self, username: str, password: str) -> None:
        """Fill credentials and submit the login form."""
        self.fill_by_role("textbox", "Username", username)
        self.fill_by_role("textbox", "Password", password)
        self.click_by_role("button", "Log in")

    def error_message(self) -> str | None:
        """Return the visible login error message, if any."""
        locator = self.page.get_by_role("alert")
        return self.get_text(locator) if self.is_visible(locator) else None
```

## Versioning

Changes to the `BasePage` public method signatures are breaking changes for
every application's Page Objects and MUST be treated as a MINOR/MAJOR change
requiring a review of all `apps/*/pages/` for compatibility before merge.
