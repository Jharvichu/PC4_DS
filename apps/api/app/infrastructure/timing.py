"""RNF 1.1 / RNF 2.2: measure elapsed time of critical operations and warn on budget overrun."""

import logging
import time
from contextlib import asynccontextmanager

logger = logging.getLogger("app.timing")


@asynccontextmanager
async def log_slow_operation(operation_name: str, budget_seconds: float):
    """Log how long the wrapped block took; warn if it exceeded `budget_seconds`."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        if elapsed > budget_seconds:
            logger.warning("%s exceeded budget: %.3fs > %.1fs", operation_name, elapsed, budget_seconds)
        else:
            logger.info("%s completed in %.3fs (budget %.1fs)", operation_name, elapsed, budget_seconds)
