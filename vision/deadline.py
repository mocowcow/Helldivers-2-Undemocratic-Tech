"""Cooperative recognition deadline, isolated per worker context."""

from contextlib import contextmanager
from contextvars import ContextVar
from time import monotonic


_deadline = ContextVar("terminal_recognition_deadline", default=None)


def check_deadline(deadline=None):
    limit = _deadline.get() if deadline is None else deadline
    if limit is not None and monotonic() >= limit:
        raise TimeoutError("Terminal 截圖與辨識超過截止時間，取消按鍵輸入。")


@contextmanager
def recognition_deadline(deadline):
    token = _deadline.set(deadline)
    try:
        check_deadline()
        yield
        check_deadline()
    finally:
        _deadline.reset(token)
