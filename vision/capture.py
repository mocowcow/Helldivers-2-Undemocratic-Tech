"""Hotkey-safe screen capture, recognition, and Terminal direction input."""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from threading import Event, Lock, Thread, Timer
from time import monotonic

import numpy as np
import pydirectinput as pdi
from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtGui import QGuiApplication, QImage
from PySide6.QtWidgets import QMessageBox

from game.actions import DIRECTION_KEYS
from config.settings import SETTINGS_PATH

from .detection import recognize_screenshot
from .deadline import check_deadline, recognition_deadline
from .terminal import RecognitionError, _write_image


logger = logging.getLogger(__name__)
RECOGNITION_TIMEOUT = 2.0


@dataclass
class _Request:
    deadline: float
    lock: object = field(default_factory=Lock)
    state: str = "pending"
    timer: object = None
    image: object = None
    failure_reason: str = ""
    failure_timestamp: str = ""
    save_started: bool = False


class TerminalRecognition(QObject):
    """Create on the Qt GUI thread; request() may be used as a keyboard callback.

    Captures the primary screen and sends recognized directions using the game's
    direction mapping. Failed requests preserve their original screenshots.
    """

    capture_requested = Signal(object)
    failed = Signal(object, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._busy = Lock()
        self._closed = Event()
        self._request = None
        self._popup = None
        self.capture_requested.connect(self._capture, Qt.ConnectionType.QueuedConnection)
        self.failed.connect(self._show_failure, Qt.ConnectionType.QueuedConnection)

    def request(self):
        """Queue a capture; return False if closing or already processing."""
        if self._closed.is_set():
            return False
        if not self._busy.acquire(blocking=False):
            logger.info("Terminal 辨識仍在執行，略過重複請求")
            return False
        job = _Request(monotonic() + RECOGNITION_TIMEOUT)
        self._request = job
        try:
            if self._closed.is_set():
                self._busy.release()
                return False
            job.timer = Timer(max(0, job.deadline - monotonic()), self._expire, args=(job,))
            job.timer.daemon = True
            job.timer.start()
            self.capture_requested.emit(job)
        except Exception as error:
            logger.exception("Terminal 辨識請求失敗")
            self._fail(job, f"辨識請求失敗：{type(error).__name__}: {error}")
            self._finish(job)
            self._busy.release()
            raise
        return True

    @Slot(object)
    def _capture(self, job):
        # QScreen/QPixmap operations stay on the GUI thread. Only the independent
        # NumPy buffer is passed to the recognition worker.
        if self._closed.is_set():
            self._finish(job)
            self._busy.release()
            return
        try:
            check_deadline(job.deadline)
            if self._popup is not None:
                self._popup.hide()
            screen = QGuiApplication.primaryScreen()
            if screen is None:
                raise RuntimeError("沒有可擷取的主螢幕")
            pixmap = screen.grabWindow(0)
            if pixmap.isNull():
                raise RuntimeError("螢幕截圖失敗")
            image = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
            pixels = np.frombuffer(image.bits(), dtype=np.uint8).reshape(
                image.height(), image.bytesPerLine())
            rgba = pixels[:, :image.width()*4].reshape(image.height(), image.width(), 4)
            bgr = rgba[:, :, [2, 1, 0]].copy()
            with job.lock:
                job.image = bgr.copy()
            # The watchdog may have expired while capture was still running.
            self._save_failure(job)
            check_deadline(job.deadline)
            logger.info("Terminal 開始辨識 screen=%s size=%sx%s",
                        screen.name(), image.width(), image.height())
            Thread(target=self._recognize, args=(bgr, job), name="terminal-recognition", daemon=True).start()
        except TimeoutError:
            self._expire(job)
            self._finish(job)
            self._busy.release()
        except Exception as error:
            logger.exception("Terminal 截圖或啟動辨識失敗")
            self._fail(job, f"截圖或啟動辨識失敗：{type(error).__name__}: {error}")
            self._finish(job)
            self._busy.release()

    def _recognize(self, image, job):
        try:
            with recognition_deadline(job.deadline):
                sequence, roi = recognize_screenshot(image)
            if not self._closed.is_set():
                logger.info("Terminal 辨識結果 sequence=%s roi=%s",
                            json.dumps(sequence), roi)
                # Validate the entire sequence before sending its first key.
                keys = [DIRECTION_KEYS[direction] for direction in sequence]
                # Atomically choose timeout or input. A late result can never
                # start sending, even if the watchdog thread ran late.
                with job.lock:
                    check_deadline(job.deadline)
                    if job.state != "pending":
                        return
                    job.state = "sending"
                    job.timer.cancel()
                for key in keys:
                    if self._closed.is_set():
                        return
                    pdi.press(key)
                logger.info("Terminal 方向按鍵送出完成 count=%s", len(keys))
        except TimeoutError:
            self._expire(job)
        except RecognitionError as error:
            if not self._closed.is_set():
                logger.warning("Terminal 無法可靠辨識：%s", error)
                self._fail(job, f"無法可靠辨識：{error}")
        except Exception as error:
            logger.exception("Terminal 辨識或方向按鍵輸入發生錯誤")
            self._fail(job, f"辨識或方向按鍵輸入失敗：{type(error).__name__}: {error}")
        finally:
            self._finish(job)
            self._busy.release()

    def _expire(self, job):
        with job.lock:
            if job.state != "pending" or self._closed.is_set():
                return
            job.state = "expired"
            job.failure_reason = f"辨識超時_超過{RECOGNITION_TIMEOUT:g}秒"
            job.failure_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        logger.warning("Terminal 超時：超過 %g 秒，取消後續按鍵輸入", RECOGNITION_TIMEOUT)
        self.failed.emit(job, f"截圖與辨識超過 {RECOGNITION_TIMEOUT:g} 秒，已取消後續按鍵輸入。")
        self._save_failure(job)

    def _fail(self, job, message):
        with job.lock:
            if self._closed.is_set() or job.state not in ("pending", "sending"):
                return
            job.state = "failed"
            job.failure_reason = message
            job.failure_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            if job.timer is not None:
                job.timer.cancel()
        self.failed.emit(job, message)
        self._save_failure(job)

    @staticmethod
    def _save_failure(job):
        with job.lock:
            if job.image is None or not job.failure_reason or job.save_started:
                return
            job.save_started = True
            image = job.image
            reason = job.failure_reason
            timestamp = job.failure_timestamp

        def save():
            try:
                # SETTINGS_PATH points to bindings.json, not a directory.
                folder = SETTINGS_PATH.parent / "failed"
                folder.mkdir(parents=True, exist_ok=True)
                name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", reason.split(";", 1)[0])
                name = name[:80].strip(" .") or "辨識失敗"
                path = folder / f"{name}_{timestamp}.png"
                _write_image(path, image)
                logger.info("Terminal 失敗截圖已儲存 path=%s reason=%s", path, reason)
            except Exception:
                logger.exception("Terminal 失敗截圖儲存失敗 reason=%s", reason)

        try:
            # Saving must not delay the popup or run in the GUI thread.
            Thread(target=save, name="terminal-failure-save", daemon=False).start()
        except Exception:
            logger.exception("Terminal 無法啟動失敗截圖儲存")

    @staticmethod
    def _finish(job):
        with job.lock:
            if job.state != "expired":
                job.state = "finished"
            if job.timer is not None:
                job.timer.cancel()

    @Slot(object, str)
    def _show_failure(self, job, message):
        if self._closed.is_set() or job is not self._request:
            return
        if self._popup is None:
            self._popup = QMessageBox()
            self._popup.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self._popup.setIcon(QMessageBox.Icon.Warning)
            self._popup.setStandardButtons(QMessageBox.StandardButton.Ok)
            self._popup.setModal(False)
            self._popup.setTextFormat(Qt.TextFormat.PlainText)
        self._popup.setWindowTitle("Terminal 辨識失敗")
        summary = message.split(";", 1)[0][:300]
        self._popup.setText(summary)
        self._popup.setDetailedText(message if summary != message else "")
        self._popup.show()
        self._popup.raise_()

    def close(self):
        """Stop accepting requests; active daemon work does not delay app exit."""
        self._closed.set()
        if self._request is not None:
            self._finish(self._request)
        if self._popup is not None:
            self._popup.close()
