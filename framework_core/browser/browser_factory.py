"""Playwright browser/context/page lifecycle management.

Provides a single place that knows how to launch the correct Playwright
browser engine (Chromium, Firefox, WebKit) driven purely by `BrowserConfig`
(Constitution I, IX) — no application-specific logic lives here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from framework_core.config.settings import BrowserConfig

if TYPE_CHECKING:
    from playwright.sync_api import Browser, Playwright

_ENGINE_ATTRS = {
    "chromium": "chromium",
    "firefox": "firefox",
    "webkit": "webkit",
}


def launch_browser(playwright: Playwright, config: BrowserConfig) -> Browser:
    """Launch the Playwright browser engine selected by `config.engine`.

    Args:
        playwright: An active `Playwright` driver instance.
        config: The resolved `BrowserConfig` (engine + headless mode).

    Returns:
        A launched Playwright `Browser` instance.

    """
    browser_type = getattr(playwright, _ENGINE_ATTRS[config.engine])
    return browser_type.launch(headless=config.headless)
