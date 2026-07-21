"""Shared, reusable pytest fixtures for browser/context/page lifecycle.

These fixtures are application-agnostic: any application's tests use the
same `page` fixture regardless of which application they target
(Constitution I, II, VI).
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from framework_core.browser.browser_factory import launch_browser
from framework_core.config.settings import BrowserConfig, Settings
from framework_core.reporting.artifact_capture import (
    FAILED_STASH_KEY,
    artifact_stem,
    capture_screenshot,
    finalize_video,
    write_console_log,
)
from playwright.sync_api import sync_playwright

if TYPE_CHECKING:
    from playwright.sync_api import Browser, Page, Playwright

TIMESTAMP_FORMAT = "%d-%m-%y-%H-%M-%S"


@pytest.fixture(scope="session")
def playwright_instance() -> Iterator[Playwright]:
    """Start and stop a single Playwright driver instance for the session."""
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, browser_config: BrowserConfig) -> Iterator[Browser]:
    """Launch one `Browser` instance per session, per the active `BrowserConfig`."""
    browser_instance = launch_browser(playwright_instance, browser_config)
    yield browser_instance
    browser_instance.close()


@pytest.fixture
def page(
    browser: Browser,
    run_paths: object,
    settings: Settings,
    request: pytest.FixtureRequest,
) -> Iterator[Page]:
    """Provide a fresh, isolated `Page` per test.

    Creates an isolated `BrowserContext` with video recording and tracing
    enabled. On teardown, if the test's setup/call phase failed (per
    `FAILED_STASH_KEY`, set by the `pytest_runtest_makereport` hook in
    `tests/conftest.py`), captures a screenshot, finalized video, console
    log, and Playwright trace using the naming convention from
    specs/001-ui-automation-framework/contracts/artifact-naming-contract.md.
    """
    videos_dir = run_paths.videos_dir  # type: ignore[attr-defined]
    raw_video_dir = videos_dir / "_raw"
    raw_video_dir.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(record_video_dir=str(raw_video_dir))
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    console_messages: list[str] = []
    current_page = context.new_page()
    current_page.on(
        "console",
        lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"),
    )

    yield current_page

    failed = request.node.stash.get(FAILED_STASH_KEY, False)
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    stem = artifact_stem(
        request.node.nodeid,
        settings.browser.engine,
        settings.environment.name,
        timestamp,
    )

    report_dir = run_paths.report_dir  # type: ignore[attr-defined]
    screenshots_dir = run_paths.screenshots_dir  # type: ignore[attr-defined]
    logs_dir = run_paths.logs_dir  # type: ignore[attr-defined]

    if failed:
        capture_screenshot(current_page, screenshots_dir / f"{stem}.png")
        context.tracing.stop(path=str(report_dir / "traces" / f"{stem}.zip"))
    else:
        context.tracing.stop()

    video = current_page.video
    context.close()

    if failed and video is not None:
        finalize_video(current_page, videos_dir / f"{stem}.webm")
        write_console_log(console_messages, logs_dir / f"{stem}.console.log")

    # Discard the raw, GUID-named recording now that we've either renamed it
    # into place (on failure) or decided we don't need it (on pass) — only
    # failure videos are meant to be kept (Constitution VII).
    if video is not None:
        try:
            raw_path = Path(video.path())
        except Exception:  # pragma: no cover - best-effort cleanup
            raw_path = None
        if raw_path is not None and raw_path.exists():
            raw_path.unlink(missing_ok=True)
