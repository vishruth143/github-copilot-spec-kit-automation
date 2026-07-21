"""LoginPage Page Object for the internet_herokuapp application.

Demonstrates the full framework pattern end-to-end (FR-018): extends
`BasePage`, exposes only business-meaningful methods, and uses the locator
priority order documented in
specs/001-ui-automation-framework/contracts/page-object-contract.md.
"""

from __future__ import annotations

from framework_core.pages.base_page import BasePage

from apps.internet_herokuapp.locators import login_locators


class LoginPage(BasePage):
    """Page Object for the sample application's login screen."""

    PATH = "/login"

    def open(self) -> None:
        """Navigate directly to the login screen."""
        self.goto(self.PATH)

    def login(self, username: str, password: str) -> None:
        """Fill credentials and submit the login form."""
        self._log_step(f"Filling login form for user '{username}'")
        # No data-testid is exposed by this demo application's fields, but
        # each input has an associated <label>; label text is the
        # "label/text" tier of FR-008's locator priority order.
        self.page.get_by_label(login_locators.USERNAME_FIELD_LABEL).fill(username)
        self.page.get_by_label(login_locators.PASSWORD_FIELD_LABEL).fill(password)
        self.click_by_role(login_locators.LOGIN_BUTTON_ROLE, login_locators.LOGIN_BUTTON_NAME)

    def flash_message(self) -> str | None:
        """Return the visible flash banner message, if any."""
        locator = self.page.locator(login_locators.FLASH_MESSAGE_SELECTOR)
        return self.get_text(locator) if self.is_visible(locator) else None

    def is_login_successful(self) -> bool:
        """Return whether the login redirected to the authenticated secure area."""
        return "/secure" in self.page.url
