"""TodoPage Page Object for the demo_playwright application.

A second worked example (alongside `apps/internet_herokuapp/pages/login_page.py`)
proving the framework is plug-and-play: this file, its locators, its test
data, and its tests are the *only* things that changed to onboard this
application (Constitution I, II; FR-019).
"""

from __future__ import annotations

from framework_core.pages.base_page import BasePage

from apps.demo_playwright.locators import todo_locators


class TodoPage(BasePage):
    """Page Object for the Todo list application's main screen."""

    PATH = "/todomvc/"

    def open(self) -> None:
        """Navigate directly to the Todo list screen."""
        self.goto(self.PATH)

    def add_item(self, text: str) -> None:
        """Type `text` into the new-todo input and submit it."""
        self._log_step(f"Adding todo item '{text}'")
        field = self.page.get_by_placeholder(todo_locators.NEW_TODO_INPUT_PLACEHOLDER)
        field.fill(text)
        field.press("Enter")

    def items(self) -> list[str]:
        """Return the visible todo item labels, in display order."""
        return self.page.get_by_test_id(todo_locators.TODO_ITEM_TEST_ID).all_text_contents()
