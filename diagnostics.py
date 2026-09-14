"""Console and persistent UTF-8 application logging."""

import logging
import os
from pathlib import Path
import sys
import threading


LOG_PATH = Path(os.environ["LOCALAPPDATA"]) / "HD2" / "output.log"


def configure_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handlers = [logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")]
    if sys.stderr is not None:
        handlers.append(logging.StreamHandler(sys.stderr))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(process)d:%(threadName)s] %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )

    def report_exception(exc_type, exc_value, traceback):
        logging.getLogger(__name__).error(
            "未處理的例外", exc_info=(exc_type, exc_value, traceback),
        )

    def report_thread_exception(args):
        report_exception(args.exc_type, args.exc_value, args.exc_traceback)

    sys.excepthook = report_exception
    threading.excepthook = report_thread_exception

