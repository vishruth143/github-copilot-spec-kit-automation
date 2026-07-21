"""Failure-artifact capture: screenshot, video, console log.

Filenames follow `<test_name>__<browser>__<environment>__<timestamp>.<ext>`
per specs/001-ui-automation-framework/contracts/artifact-naming-contract.md
(FR-009, FR-010, Constitution VII).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = logging.getLogger("framework_core.reporting")

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9_.-]+")

#: Stash key set (True) on a test item by the `pytest_runtest_makereport`
#: hook whenever that test's setup or call phase failed. Fixtures read this
#: during teardown to decide whether to capture failure artifacts.
FAILED_STASH_KEY = pytest.StashKey[bool]()


def sanitize_test_name(node_id: str) -> str:
    """Sanitize a pytest node id into a filesystem-safe test name."""
    return _UNSAFE_CHARS.sub("_", node_id)


def artifact_stem(test_name: str, browser: str, environment: str, timestamp: str) -> str:
    """Build the shared filename stem used by every artifact type for one failure."""
    safe_name = sanitize_test_name(test_name)
    return f"{safe_name}__{browser}__{environment}__{timestamp}"


@dataclass
class FailureArtifact:
    """Diagnostic files captured for a single failed test."""

    test_name: str
    browser: str
    environment: str
    timestamp: str
    screenshot_path: Path | None = None
    video_path: Path | None = None
    console_log_path: Path | None = None
    exception_summary: str = ""


def capture_screenshot(page: Page, destination: Path) -> Path | None:
    """Capture a full-page screenshot, returning the path, or `None` on failure."""
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(destination), full_page=True)
        return destination
    except Exception as exc:  # pragma: no cover - best-effort diagnostics
        logger.warning("Screenshot capture unavailable: %s", exc)
        return None


def finalize_video(page: Page, destination: Path) -> Path | None:
    """Save the page's recorded video to `destination`, if one exists."""
    try:
        video = page.video
        if video is None:
            logger.info("Video capture unavailable for this page/browser.")
            return None
        destination.parent.mkdir(parents=True, exist_ok=True)
        video.save_as(str(destination))
        return destination
    except Exception as exc:  # pragma: no cover - best-effort diagnostics
        logger.warning("Video capture unavailable: %s", exc)
        return None


def write_console_log(console_messages: list[str], destination: Path) -> Path | None:
    """Write buffered console messages to `destination`, if any were captured."""
    if not console_messages:
        logger.info("Console log capture unavailable or produced no output.")
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(console_messages), encoding="utf-8")
    return destination
