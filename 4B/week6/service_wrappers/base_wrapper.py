import time
import logging
from typing import Callable, TypeVar, Tuple

T = TypeVar("T")

logger = logging.getLogger(__name__)


class RetryableServiceError(Exception):
    """Raised when a temporary service error occurs."""


class NonRetryableServiceError(Exception):
    """Raised when a permanent service error occurs."""


def with_retry(
    func: Callable[[], T],
    retries: int = 3,
    delay: float = 1.0,
    retry_exceptions: Tuple[type, ...] = (Exception,),
) -> T:
    """
    Runs a function with retry logic.

    Args:
        func: Zero-argument callable to execute.
        retries: Number of attempts.
        delay: Delay between retries in seconds.
        retry_exceptions: Exceptions that should trigger retry.

    Returns:
        Result of func()

    Raises:
        Exception: Final exception if all retries fail.
    """
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            return func()
        except retry_exceptions as exc:
            last_error = exc
            logger.warning("Attempt %s/%s failed: %s", attempt, retries, str(exc))

            if attempt < retries:
                time.sleep(delay)

    raise last_error