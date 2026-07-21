"""Environment profile definitions for the UI automation framework.

An `EnvironmentProfile` represents one named deployment target (DEV, TEST,
STAGE, PROD) with its own base URL, resolved from environment variables so
no environment-specific value is ever hardcoded in source code (FR-004,
FR-013, Constitution VIII/IX).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

SUPPORTED_ENVIRONMENTS: tuple[str, ...] = ("dev", "test", "stage", "prod")


class ConfigurationError(RuntimeError):
    """Raised when required configuration/secrets are missing or invalid."""


@dataclass(frozen=True)
class EnvironmentProfile:
    """A named, validated configuration profile for one deployment target."""

    name: str
    base_url: str
    default_timeout_ms: int = 30_000
    extra_settings: dict[str, str] = field(default_factory=dict)


def base_url_env_var(env_name: str, prefix: str) -> str:
    """Build the expected environment-variable name for an environment's base URL."""
    return f"{prefix}__{env_name.upper()}"


def resolve_environment_profile(
    env_name: str,
    *,
    prefix: str | None = None,
    default_timeout_ms: int = 30_000,
) -> EnvironmentProfile:
    """Resolve a validated `EnvironmentProfile` for `env_name`, failing fast if invalid.

    Args:
        env_name: Requested environment name (case-insensitive), e.g. "dev".
        prefix: Base-url environment-variable prefix, e.g.
            "INTERNET_HEROKUAPP_URL" or "DEMO_PLAYWRIGHT_BASE_URL". Each
            application resolves its own base URL by passing its own prefix,
            so multiple applications can each be configured independently
            and framework_core never hardcodes an application name. If
            `None` (the framework-core default), only `env_name` is
            validated and `base_url` is left empty — use this for the
            generic, application-agnostic `settings` fixture.
        default_timeout_ms: Default Playwright action/navigation timeout.

    Returns:
        A validated, immutable `EnvironmentProfile`.

    Raises:
        ConfigurationError: If `env_name` is not one of
            `SUPPORTED_ENVIRONMENTS`, or (when `prefix` is given) the
            corresponding base-url environment variable is missing or
            empty.

    """
    normalized = env_name.strip().lower()
    if normalized not in SUPPORTED_ENVIRONMENTS:
        supported = ", ".join(SUPPORTED_ENVIRONMENTS)
        raise ConfigurationError(
            f"Unsupported environment '{env_name}'. Supported environments: {supported}."
        )

    if prefix is None:
        return EnvironmentProfile(
            name=normalized, base_url="", default_timeout_ms=default_timeout_ms
        )

    var_name = base_url_env_var(normalized, prefix=prefix)
    base_url = os.environ.get(var_name, "").strip()
    if not base_url:
        raise ConfigurationError(f"Missing required environment variable: {var_name}")

    return EnvironmentProfile(
        name=normalized,
        base_url=base_url,
        default_timeout_ms=default_timeout_ms,
    )
