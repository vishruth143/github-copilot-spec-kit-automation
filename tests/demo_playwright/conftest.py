"""App-specific fixtures for demo_playwright tests (not part of the framework core).

Kept local to `tests/demo_playwright/` so onboarding this second application
never required touching `framework_core/`, `fixtures/`, or
`tests/conftest.py` (Constitution I, II).
"""

from __future__ import annotations

import pytest
from framework_core.config.environments import resolve_environment_profile
from framework_core.config.settings import Settings


@pytest.fixture(scope="session")
def demo_playwright_base_url(settings: Settings) -> str:
    """Resolve the demo_playwright base URL for the currently active environment."""
    profile = resolve_environment_profile(
        settings.environment.name,
        prefix="DEMO_PLAYWRIGHT_BASE_URL",
    )
    return profile.base_url
