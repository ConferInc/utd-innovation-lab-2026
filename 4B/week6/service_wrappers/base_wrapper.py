import time
import logging
from dataclasses import dataclass
from typing import Callable, TypeVar, Tuple

T = TypeVar("T")

logger = logging.getLogger(__name__)


class RetryableServiceError(Exception):
    """Raised when a temporary service error occurs."""


class NonRetryableServiceError(Exception):
    """Raised when a permanent service error occurs."""


class CircuitBreakerOpenError(Exception):
    """Raised when the circuit breaker is open and calls should fail fast."""


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    reset_timeout: float = 30.0
    failure_count: int = 0
    opened_at: float | None = None

    def is_open(self) -> bool:
        if self.opened_at is None:
            return False

        if (time.time() - self.opened_at) >= self.reset_timeout:
            self.failure_count = 0
            self.opened_at = None
            return False

        return True

    def record_success(self) -> None:
        self.failure_count = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.opened_at = time.time()


def with_retry(
    func: Callable[[], T],
    operation_name: str,
    service_name: str,
    retries: int = 3,
    delay: float = 1.0,
    retry_exceptions: Tuple[type, ...] = (Exception,),
    circuit_breaker: CircuitBreaker | None = None,
) -> T:
    if circuit_breaker and circuit_breaker.is_open():
        logger.error(
            "%s.%s blocked by open circuit breaker",
            service_name,
            operation_name,
        )
        raise CircuitBreakerOpenError(
            f"{service_name}.{operation_name} blocked by circuit breaker"
        )

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            logger.info(
                "%s.%s attempt=%s/%s starting",
                service_name,
                operation_name,
                attempt,
                retries,
            )
            result = func()
            if circuit_breaker:
                circuit_breaker.record_success()
            logger.info(
                "%s.%s attempt=%s succeeded",
                service_name,
                operation_name,
                attempt,
            )
            return result
        except retry_exceptions as exc:
            last_error = exc
            logger.warning(
                "%s.%s attempt=%s failed error_type=%s error=%s",
                service_name,
                operation_name,
                attempt,
                type(exc).__name__,
                str(exc),
            )
            if circuit_breaker:
                circuit_breaker.record_failure()
            if attempt < retries:
                time.sleep(delay)

    logger.error(
        "%s.%s exhausted retries=%s final_error_type=%s final_error=%s",
        service_name,
        operation_name,
        retries,
        type(last_error).__name__,
        str(last_error),
    )
    raise last_error