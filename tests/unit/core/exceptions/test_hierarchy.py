"""Tests for the exception classes hierarchy structure and import logic."""

import sys
from ultron_jobs.core.exceptions import (
    ApplicationError,
    BootstrapError,
    ConfigurationError,
    DependencyInjectionError,
    ExternalServiceError,
    InfrastructureError,
    InvalidConfigError,
    MissingConfigError,
    ModelProviderError,
    PersistenceError,
    UseCaseError,
    UltronJobsError,
    ValidationError,
)


def test_exception_classes_exist() -> None:
    """Verify that all expected exception classes are defined and importable."""
    classes = [
        UltronJobsError,
        ConfigurationError,
        InvalidConfigError,
        MissingConfigError,
        InfrastructureError,
        PersistenceError,
        ExternalServiceError,
        ModelProviderError,
        ApplicationError,
        ValidationError,
        UseCaseError,
        BootstrapError,
        DependencyInjectionError,
    ]
    for cls in classes:
        assert issubclass(cls, Exception)


def test_exception_parentage() -> None:
    """Verify that the exception hierarchy matches the specification tree."""
    assert issubclass(ConfigurationError, UltronJobsError)
    assert issubclass(MissingConfigError, ConfigurationError)
    assert issubclass(InvalidConfigError, ConfigurationError)

    assert issubclass(InfrastructureError, UltronJobsError)
    assert issubclass(PersistenceError, InfrastructureError)
    assert issubclass(ExternalServiceError, InfrastructureError)
    assert issubclass(ModelProviderError, ExternalServiceError)

    assert issubclass(ApplicationError, UltronJobsError)
    assert issubclass(ValidationError, ApplicationError)
    assert issubclass(UseCaseError, ApplicationError)

    assert issubclass(BootstrapError, UltronJobsError)
    assert issubclass(DependencyInjectionError, BootstrapError)


def test_all_trace_to_base_recursively() -> None:
    """Recursively check that all classes registered in subclasses subclass UltronJobsError."""
    def get_all_subclasses(cls: type) -> list[type]:
        all_subclasses = []
        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(get_all_subclasses(subclass))
        return all_subclasses

    all_subs = get_all_subclasses(UltronJobsError)

    expected_leaves = [
        MissingConfigError,
        InvalidConfigError,
        PersistenceError,
        ModelProviderError,
        ValidationError,
        UseCaseError,
        DependencyInjectionError,
    ]
    for leaf in expected_leaves:
        assert leaf in all_subs


def test_no_cross_layer_imports() -> None:
    """Check that core exceptions don't import from outer application/infrastructure layers."""
    for name, module in list(sys.modules.items()):
        if name.startswith("ultron_jobs.core.exceptions"):
            for val in getattr(module, "__dict__", {}).values():
                if hasattr(val, "__module__") and val.__module__:
                    mod_name = val.__module__
                    assert not any(
                        forbidden in mod_name
                        for forbidden in [
                            "ultron_jobs.domain",
                            "ultron_jobs.application",
                            "ultron_jobs.infrastructure",
                            "ultron_jobs.interface",
                        ]
                    ), f"Forbidden cross-layer import detected: {mod_name} in {name}"
                    
                    # Also assert standard string checks to prevent imports
                    # checking in raw source code lines:
                    source = getattr(module, "__file__", None)
                    if source:
                        with open(source, "r", encoding="utf-8") as f:
                            content = f.read()
                            assert "ultron_jobs.domain" not in content
                            assert "ultron_jobs.application" not in content
                            assert "ultron_jobs.infrastructure" not in content
                            assert "ultron_jobs.interface" not in content
