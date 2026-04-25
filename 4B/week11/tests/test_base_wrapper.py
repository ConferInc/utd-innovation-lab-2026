import pytest

from service_wrappers.base_wrapper import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    with_retry,
)


def test_circuit_breaker_opens_after_threshold():
    breaker = CircuitBreaker(failure_threshold=2, reset_timeout=60)

    with pytest.raises(ValueError):
        with_retry(
            lambda: (_ for _ in ()).throw(ValueError("boom")),
            operation_name="test_op",
            service_name="test_service",
            retries=1,
            retry_exceptions=(ValueError,),
            circuit_breaker=breaker,
        )

    with pytest.raises(ValueError):
        with_retry(
            lambda: (_ for _ in ()).throw(ValueError("boom")),
            operation_name="test_op",
            service_name="test_service",
            retries=1,
            retry_exceptions=(ValueError,),
            circuit_breaker=breaker,
        )

    with pytest.raises(CircuitBreakerOpenError):
        with_retry(
            lambda: "ok",
            operation_name="test_op",
            service_name="test_service",
            retries=1,
            circuit_breaker=breaker,
        )


def test_circuit_breaker_resets_on_success():
    breaker = CircuitBreaker(failure_threshold=3, reset_timeout=60)

    breaker.record_failure()
    breaker.record_failure()
    assert not breaker.is_open()

    breaker.record_success()
    assert breaker.failure_count == 0
    assert breaker.opened_at is None


def test_with_retry_succeeds_on_first_try():
    result = with_retry(
        lambda: 42,
        operation_name="op",
        service_name="svc",
        retries=3,
    )
    assert result == 42


def test_with_retry_exhausts_retries():
    call_count = {"n": 0}

    def failing():
        call_count["n"] += 1
        raise ValueError("fail")

    with pytest.raises(ValueError, match="fail"):
        with_retry(
            failing,
            operation_name="op",
            service_name="svc",
            retries=3,
            delay=0.0,
            retry_exceptions=(ValueError,),
        )

    assert call_count["n"] == 3
