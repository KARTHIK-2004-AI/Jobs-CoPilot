"""Import smoke tests for the ULTRON Jobs package scaffold."""

import importlib


def test_ultron_jobs_package_imports() -> None:
    """The package and top-level layer packages import without side effects."""
    modules = (
        "ultron_jobs",
        "ultron_jobs.domain",
        "ultron_jobs.application",
        "ultron_jobs.infrastructure",
        "ultron_jobs.interface",
        "ultron_jobs.core",
    )

    for module in modules:
        assert importlib.import_module(module)
