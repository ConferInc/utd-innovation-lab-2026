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