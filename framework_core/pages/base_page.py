"""Base Page Object providing shared, logged, exception-safe UI actions.

Every application-specific Page Object MUST extend `BasePage` and MUST NOT
expose raw Playwright locators/primitives to callers — see
specs/001-ui-automation-framework/contracts/page-object-contract.md
(Constitution IV).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page

logger = logging.getLogger("framework_core.pages")


class ElementActionError(RuntimeError):
    """Raised when a Page Object action fails, with enriched step context."""


class BasePage:
    """Shared, logged, exception-safe browser interactions for all pages."""

    def __init__(self, page: Page, base_url: str = "") -> None:
        """Store the Playwright `page` and the active environment's base URL."""
        self.page = page
        self.base_url = base_url.rstrip("/")

    def _log_step(self, message: str) -> None:
        """Write a structured log entry describing the current test step."""
        logger.info(message)

    def goto(self, path: str = "") -> None:
        """Navigate to `base_url + path`, waiting for the page to be ready."""
        normalized_path = path if path.startswith("/") or not path else f"/{path}"
        url = f"{self.base_url}{normalized_path}"
        self._log_step(f"Navigating to {url}")
        try:
            self.page.goto(url, wait_until="domcontentloaded")
        except Exception as exc:
            raise ElementActionError(f"Failed to navigate to '{url}': {exc}") from exc

    def click_by_role(self, role: str, name: str, **kwargs: object) -> None:
        """Click the element found by ARIA role and accessible name."""
        self._log_step(f"Click role='{role}' name='{name}'")
        locator = self.page.get_by_role(role, name=name, **kwargs)  # type: ignore[arg-type]
        try:
            locator.click()
        except Exception as exc:
            raise ElementActionError(f"Failed to click role='{role}' name='{name}': {exc}") from exc

    def fill_by_role(self, role: str, name: str, value: str, **kwargs: object) -> None:
        """Fill the element found by ARIA role and accessible name."""
        self._log_step(f"Fill role='{role}' name='{name}'")
        locator = self.page.get_by_role(role, name=name, **kwargs)  # type: ignore[arg-type]
        try:
            locator.fill(value)
        except Exception as exc:
            raise ElementActionError(f"Failed to fill role='{role}' name='{name}': {exc}") from exc

    def click_by_test_id(self, test_id: str) -> None:
        """Click the element found by its `data-testid` attribute."""
        self._log_step(f"Click test_id='{test_id}'")
        locator = self.page.get_by_test_id(test_id)
        try:
            locator.click()
        except Exception as exc:
            raise ElementActionError(f"Failed to click test_id='{test_id}': {exc}") from exc

    def fill_by_test_id(self, test_id: str, value: str) -> None:
        """Fill the element found by its `data-testid` attribute."""
        self._log_step(f"Fill test_id='{test_id}'")
        locator = self.page.get_by_test_id(test_id)
        try:
            locator.fill(value)
        except Exception as exc:
            raise ElementActionError(f"Failed to fill test_id='{test_id}': {exc}") from exc

    def get_text(self, locator: Locator) -> str:
        """Return the visible text content of `locator`."""
        try:
            return locator.inner_text()
        except Exception as exc:
            raise ElementActionError(f"Failed to read text from locator: {exc}") from exc

    def is_visible(self, locator: Locator) -> bool:
        """Return whether `locator` is currently visible (never raises)."""
        try:
            return locator.is_visible()
        except Exception:
            return False
