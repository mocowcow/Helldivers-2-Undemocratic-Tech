from threading import Event
import logging

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import QLineEdit

from game.windows import activate_foreground, get_foreground_window, set_foreground_window


logger = logging.getLogger(__name__)


class ChatInput(QLineEdit):
    open_requested = Signal(object)

    def __init__(self, send_chat):
        super().__init__()
        self.send_chat = send_chat
        self.on_open = None
        self.on_finished = None
        self._closing = False
        self._pending_text = ""
        self._delivery_timer = QTimer(self)
        self._delivery_timer.setSingleShot(True)
        self._delivery_timer.timeout.connect(lambda: self.deliver(self._pending_text))
        self.active = Event()
        self.target = None
        self.composing = False
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(200, 50)
        self.open_requested.connect(
            self.open_input, Qt.ConnectionType.QueuedConnection)

    def request(self):
        # Global keyboard callbacks must not manipulate Qt widgets directly.
        if not self._closing and not self.active.is_set():
            self.active.set()
            try:
                self.open_requested.emit(get_foreground_window())
            except Exception:
                self.active.clear()
                raise

    @Slot(object)
    def open_input(self, target):
        if self._closing:
            self.active.clear()
            return
        self.active.set()
        try:
            if self.on_open:
                self.on_open()
            self._open_input(target)
        except Exception:
            logger.exception("開啟聊天視窗失敗")
            self.hide()
            self._finish_input()

    def _open_input(self, target):
        logger.info("開啟聊天視窗 target=%s", target)
        self.target = target
        self.composing = False
        self.clear()
        screen = QGuiApplication.screenAt(
            QCursor.pos()) or QGuiApplication.primaryScreen()
        area = screen.availableGeometry()
        self.move(
            area.x() + area.width() - self.width() - 12,
            area.y() + area.height() - self.height() - 12,
        )
        self.show_and_focus()

    def show_and_focus(self):
        self.active.set()
        self.show()
        self.raise_()
        self.activateWindow()
        activate_foreground(int(self.winId()))
        if get_foreground_window() == int(self.winId()):
            self.setFocus(Qt.FocusReason.OtherFocusReason)

    def inputMethodEvent(self, event):
        self.composing = bool(event.preeditString())
        super().inputMethodEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancel()
            event.accept()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not self.composing:
            self.submit()
            event.accept()
        else:
            super().keyPressEvent(event)

    def cancel(self):
        logger.info("取消聊天輸入")
        self._delivery_timer.stop()
        self.hide()
        try:
            if self.target and not self._closing:
                set_foreground_window(self.target)
        finally:
            self._finish_input()

    def _finish_input(self):
        was_active = self.active.is_set()
        self.active.clear()
        if was_active and not self._closing and self.on_finished:
            self.on_finished()

    def submit(self):
        text = self.text()
        if not text.strip():
            self.cancel()
            return
        self.hide()
        if self.target:
            set_foreground_window(self.target)
        self._pending_text = text
        self._delivery_timer.start(150)

    def deliver(self, text):
        if self._closing or not self.active.is_set():
            return
        if not self.target or get_foreground_window() != self.target:
            logger.warning("無法切回原視窗，文字尚未送出 target=%s", self.target)
            self.show_and_focus()
            return
        try:
            self.send_chat(text)
        except Exception:
            logger.exception("聊天輸入中斷，請確認遊戲聊天狀態")
            self.show_and_focus()
        else:
            self._finish_input()

    def shutdown(self):
        """Stop pending delivery without restoring bindings during app exit."""
        self._closing = True
        self._delivery_timer.stop()
        self.hide()
        self.active.clear()

    def closeEvent(self, event):
        self.cancel()
        event.accept()
