"""Locator descriptors for the demo_playwright Todo list page.

Named here (rather than scattered inline in the Page Object) so they stay
easy to find and update if the target application's markup changes
(Constitution IV).
"""

NEW_TODO_INPUT_PLACEHOLDER = "What needs to be done?"

# The demo app exposes each todo item's label with data-testid="todo-title" —
# a stable, purpose-built test id (tier 2 of FR-008's locator priority order).
TODO_ITEM_TEST_ID = "todo-title"
