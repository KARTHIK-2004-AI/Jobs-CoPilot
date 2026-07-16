"""Tests for the base exceptions implementation."""

from ultron_jobs.core.exceptions import UltronJobsError


def test_ultron_jobs_error_construction() -> None:
    """Test default values, custom codes, and standard error string serialization."""
    # Test default code and empty context
    err = UltronJobsError("Something failed")
    assert err.message == "Something failed"
    assert err.error_code == "ULTRON_JOBS_ERROR"
    assert err.context == {}
    assert str(err) == "[ULTRON_JOBS_ERROR] Something failed"
    assert err.to_dict() == {
        "error_code": "ULTRON_JOBS_ERROR",
        "message": "Something failed",
        "context": {},
    }


def test_ultron_jobs_error_explicit_params() -> None:
    """Test explicit arguments for error code and context metadata."""
    context = {"user_id": 42, "details": ["a", "b"]}
    err = UltronJobsError("Custom error", error_code="MY_CODE", context=context)
    assert err.message == "Custom error"
    assert err.error_code == "MY_CODE"
    assert err.context == context
    assert str(err) == "[MY_CODE] Custom error"
    assert err.to_dict() == {
        "error_code": "MY_CODE",
        "message": "Custom error",
        "context": context,
    }


def test_subclassing_outside_module() -> None:
    """Verify that subclassing UltronJobsError outside the module behaves properly."""
    class CustomOutsideError(UltronJobsError):
        pass

    err = CustomOutsideError("Outside failure")
    assert err.error_code == "CUSTOM_OUTSIDE_ERROR"
    assert str(err) == "[CUSTOM_OUTSIDE_ERROR] Outside failure"
