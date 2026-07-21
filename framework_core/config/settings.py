"""Framework-wide settings loader: environment, browser, and execution mode.

Resolves configuration using the precedence: explicit CLI flag > environment
variable > documented default. Fails fast with `ConfigurationError` when a
required value is missing or invalid, before any browser is launched
(Constitution VIII).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from framework_core.config.environments import (
    ConfigurationError,
    EnvironmentProfile,
    resolve_environment_profile,
)

SUPPORTED_BROWSERS: tuple[str, ...] = ("chromium", "firefox", "webkit")


@dataclass(frozen=True)
class BrowserConfig:
    """The selected browser engine and execution mode for a test run."""

    engine: str
    headless: bool = True


def resolve_browser_config(
    engine: str | None = None,
    headless: bool | None = None,
) -> BrowserConfig:
    """Resolve a validated `BrowserConfig` using CLI-arg > env var > default.

    Raises:
        ConfigurationError: If the resolved engine is not one of
            `SUPPORTED_BROWSERS`.

    """
    resolved_engine = (engine or os.environ.get("BROWSER") or "chromium").strip().lower()
    if resolved_engine not in SUPPORTED_BROWSERS:
        supported = ", ".join(SUPPORTED_BROWSERS)
        raise ConfigurationError(
            f"Unsupported browser '{resolved_engine}'. Supported browsers: {supported}."
        )

    if headless is not None:
        resolved_headless = headless
    else:
        env_value = os.environ.get("HEADLESS")
        resolved_headless = True if env_value is None else env_value.strip().lower() != "false"

    return BrowserConfig(engine=resolved_engine, headless=resolved_headless)


@dataclass(frozen=True)
class Settings:
    """Aggregated, validated settings for one test-execution run."""

    environment: EnvironmentProfile
    browser: BrowserConfig


def load_settings(
    env_name: str | None = None,
    browser_engine: str | None = None,
    headless: bool | None = None,
    *,
    base_url_prefix: str | None = None,
) -> Settings:
    """Load and validate `Settings` for a test run, failing fast on errors.

    `base_url_prefix` is intentionally `None` by default so framework_core
    never hardcodes any application's name or base URL — each application
    resolves its own base URL locally (see e.g.
    `tests/internet_herokuapp/conftest.py`, `tests/demo_playwright/conftest.py`)
    by calling `resolve_environment_profile(settings.environment.name, prefix=...)`
    with its own prefix.
    """
    resolved_env_name = (env_name or os.environ.get("ENV") or "dev").strip()
    environment = resolve_environment_profile(resolved_env_name, prefix=base_url_prefix)
    browser = resolve_browser_config(browser_engine, headless)
    return Settings(environment=environment, browser=browser)


__all__ = [
    "BrowserConfig",
    "ConfigurationError",
    "Settings",
    "SUPPORTED_BROWSERS",
    "load_settings",
    "resolve_browser_config",
]
