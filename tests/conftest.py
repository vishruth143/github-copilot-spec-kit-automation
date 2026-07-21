"""Root pytest configuration for the UI automation framework.

Registers the framework's CLI options (`--env`, `--browser`, `--headed`),
creates the per-run `output/<timestamp>/` directory tree, wires up
`pytest-html`/Playwright tracing output paths, and marks failed tests via a
stash key so fixtures can react during teardown (see
fixtures/browser_fixtures.py). See
specs/001-ui-automation-framework/contracts/cli-interface.md and
specs/001-ui-automation-framework/contracts/artifact-naming-contract.md.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from dotenv import load_dotenv
from framework_core.config.settings import Settings, load_settings
from framework_core.reporting.artifact_capture import FAILED_STASH_KEY
from framework_core.reporting.logger import configure_run_logger

if TYPE_CHECKING:
    pass

load_dotenv()

pytest_plugins = ("fixtures.browser_fixtures",)

TIMESTAMP_FORMAT = "%d-%m-%y-%H-%M-%S"
RUN_TIMESTAMP_ENV_VAR = "UI_FRAMEWORK_RUN_TIMESTAMP"


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register the framework's environment/browser/execution-mode CLI options."""
    group = parser.getgroup("ui-automation-framework")
    group.addoption(
        "--env",
        action="store",
        default=None,
        help="Target environment: dev | test | stage | prod (default: $ENV or 'dev')",
    )
    group.addoption(
        "--browser",
        action="store",
        default=None,
        help="Browser engine: chromium | firefox | webkit (default: $BROWSER or 'chromium')",
    )
    group.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browsers in headed mode (default: headless)",
    )


@dataclass(frozen=True)
class RunPaths:
    """Filesystem paths for one test-execution run's output tree."""

    run_timestamp: str
    output_dir: Path
    logs_dir: Path
    screenshots_dir: Path
    videos_dir: Path
    report_dir: Path


def _resolve_run_timestamp() -> str:
    """Resolve the run timestamp shared across `pytest-xdist` workers.

    The first process to run `pytest_configure` (the xdist master, or the
    single process in a non-parallel run) generates the timestamp and
    publishes it via an environment variable, which spawned xdist worker
    processes inherit — guaranteeing every worker writes into the same
    `output/<timestamp>/` tree.
    """
    existing = os.environ.get(RUN_TIMESTAMP_ENV_VAR)
    if existing:
        return existing
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    os.environ[RUN_TIMESTAMP_ENV_VAR] = timestamp
    return timestamp


def pytest_configure(config: pytest.Config) -> None:
    """Create the run's output directory tree and configure reporting."""
    run_timestamp = _resolve_run_timestamp()
    output_dir = Path("output") / run_timestamp
    run_paths = RunPaths(
        run_timestamp=run_timestamp,
        output_dir=output_dir,
        logs_dir=output_dir / "logs",
        screenshots_dir=output_dir / "screenshots",
        videos_dir=output_dir / "videos",
        report_dir=output_dir / "html-report",
    )
    for path in (
        run_paths.logs_dir,
        run_paths.screenshots_dir,
        run_paths.videos_dir,
        run_paths.report_dir,
    ):
        path.mkdir(parents=True, exist_ok=True)

    configure_run_logger(run_paths.logs_dir)
    config.stash[_RUN_PATHS_STASH_KEY] = run_paths

    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "")
    report_name = f"report_{worker_id}.html" if worker_id else "report.html"
    config.option.htmlpath = str(run_paths.report_dir / report_name)
    config.option.self_contained_html = True


_RUN_PATHS_STASH_KEY = pytest.StashKey[RunPaths]()


@pytest.fixture(scope="session")
def run_paths(pytestconfig: pytest.Config) -> RunPaths:
    """Expose the current run's output directory tree to fixtures/tests."""
    return pytestconfig.stash[_RUN_PATHS_STASH_KEY]


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    """Load and validate `Settings` once per session, failing fast on errors."""
    return load_settings(
        env_name=pytestconfig.getoption("--env"),
        browser_engine=pytestconfig.getoption("--browser"),
        headless=False if pytestconfig.getoption("--headed") else None,
    )


@pytest.fixture(scope="session")
def browser_config(settings: Settings):
    """Expose just the `BrowserConfig` portion of the session's `Settings`."""
    return settings.browser


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Mark `item` as failed (via stash) whenever its setup/call phase fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when in ("setup", "call") and report.failed:
        item.stash[FAILED_STASH_KEY] = True
