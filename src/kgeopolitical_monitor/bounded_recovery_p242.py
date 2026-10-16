"""Bounded NO_SEND recovery invocation. No daemon, providers or activation."""
import fcntl
import os
import time
from .research_durable_cursor_v1 import recover_durable


def run(root, *, allowed_consumers, observed_at_utc, attempts=3,
        budget_seconds=10, max_items=10, clock=time.monotonic):
    if type(attempts) is not int or not 1 <= attempts <= 3:
        raise ValueError("invalid attempts")
    if type(budget_seconds) not in (int, float) or not 0 < budget_seconds <= 60:
        raise ValueError("invalid budget")
    import math
    if not math.isfinite(budget_seconds):
        raise ValueError("invalid budget")
    if type(max_items) is not int or not 1 <= max_items <= 100:
        raise ValueError("invalid bound")
    from .research_storage_v1 import initialize
    root = initialize(root)
    fd = os.open(root / ".p242-invocation.lock",
                 os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    started = clock()
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {"status": "BUSY", "attempts": 0, "send": False}
        for number in range(1, attempts + 1):
            if clock() - started >= budget_seconds:
                return {"status": "DEADLINE", "attempts": number - 1, "send": False}
            try:
                report = recover_durable(root, allowed_consumers=allowed_consumers,
                    observed_at_utc=observed_at_utc, max_items=max_items)
            except PermissionError:
                raise
            except OSError:
                if number == attempts:
                    return {"status": "IO_FAILURE", "attempts": number, "send": False}
                continue
            status = "FAIL_CLOSED" if report["errors"] else "COMPLETE"
            if clock() - started >= budget_seconds:
                status = "DEADLINE"
            return {"status": status, "attempts": number, "report": report, "send": False}
    finally:
        os.close(fd)
