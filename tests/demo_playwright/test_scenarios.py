"""Sample test scenarios demonstrating plug-and-play onboarding of a second
application (User Story 2), independent of internet_herokuapp's login flow.

All test scenarios for the demo_playwright application live in this single
file (one `test_scenarios.py` per application, rather than splitting
scenarios across multiple files) so an application's test suite has one
obvious entry point. These tests target Playwright's public TodoMVC demo
(https://demo.playwright.dev/todomvc/).
"""

from __future__ import annotations

import pytest
from apps.demo_playwright.pages.todo_page import TodoPage
from apps.demo_playwright.test_data.todo_data import SAMPLE_ITEMS


@pytest.mark.smoke
def test_add_single_item(page, demo_playwright_base_url):
    # Test steps:
    # 1. Open the Todo application.
    # 2. Add a single new todo item.
    # 3. Verify the item appears in the todo list.
    todo_page = TodoPage(page, base_url=demo_playwright_base_url)
    todo_page.open()

    todo_page.add_item(SAMPLE_ITEMS[0])

    assert SAMPLE_ITEMS[0] in todo_page.items()


@pytest.mark.regression
def test_add_multiple_items(page, demo_playwright_base_url):
    # Test steps:
    # 1. Open the Todo application.
    # 2. Add several new todo items one after another.
    # 3. Verify all items appear in the todo list, in order.
    todo_page = TodoPage(page, base_url=demo_playwright_base_url)
    todo_page.open()

    for item in SAMPLE_ITEMS:
        todo_page.add_item(item)

    assert todo_page.items() == SAMPLE_ITEMS
