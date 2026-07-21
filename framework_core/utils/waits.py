"""Resilient wait/retry helpers built on Playwright's web-first assertions.

These helpers give Page Objects a documented, reusable way to wait for a
condition without ever resorting to a hardcoded time delay (FR-007,
Constitution V).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import expect

if TYPE_CHECKING:
    from playwright.sync_api import Locator

DEFAULT_TIMEOUT_MS = 30_000


def wait_for_visible(locator: Locator, *, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
    """Wait until `locator` is visible, using a Playwright web-first assertion."""
    expect(locator).to_be_visible(timeout=timeout_ms)


def wait_for_hidden(locator: Locator, *, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
    """Wait until `locator` is hidden or detached from the DOM."""
    expect(locator).to_be_hidden(timeout=timeout_ms)


def wait_for_text(locator: Locator, text: str, *, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
    """Wait until `locator` contains the expected text."""
    expect(locator).to_contain_text(text, timeout=timeout_ms)


def wait_for_enabled(locator: Locator, *, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
    """Wait until `locator` is enabled (not disabled)."""
    expect(locator).to_be_enabled(timeout=timeout_ms)
