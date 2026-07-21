"""App-specific fixtures for internet_herokuapp tests (not part of the framework core).

Kept local to `tests/internet_herokuapp/` so onboarding a new application
never requires touching `framework_core/`, `fixtures/`, or
`tests/conftest.py` (Constitution I, II).
"""

from __future__ import annotations

import os

import pytest
from framework_core.config.environments import ConfigurationError, resolve_environment_profile
from framework_core.config.settings import Settings


@pytest.fixture(scope="session")
def internet_herokuapp_credentials() -> dict[str, str]:
    """Resolve the internet_herokuapp test account credentials, failing fast if unset."""
    username = os.environ.get("INTERNET_HEROKUAPP_USERNAME", "").strip()
    password = os.environ.get("INTERNET_HEROKUAPP_PASSWORD", "").strip()
    if not username or not password:
        raise ConfigurationError(
            "Missing required environment variable(s): "
            "INTERNET_HEROKUAPP_USERNAME / INTERNET_HEROKUAPP_PASSWORD"
        )
    return {"username": username, "password": password}


@pytest.fixture(scope="session")
def internet_herokuapp_base_url(settings: Settings) -> str:
    """Resolve the internet_herokuapp base URL for the currently active environment."""
    profile = resolve_environment_profile(
        settings.environment.name,
        prefix="INTERNET_HEROKUAPP_URL",
    )
    return profile.base_url
