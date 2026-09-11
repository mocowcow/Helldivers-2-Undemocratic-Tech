import ctypes
from ctypes import wintypes
from threading import Event

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import QLineEdit


user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.GetForegroundWindow.restype = wintypes.HWND
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
user32.AttachThreadInput.restype = wintypes.BOOL
user32.SetFocus.argtypes = [wintypes.HWND]
user32.SetFocus.restype = wintypes.HWND
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.GetCurrentThreadId.restype = wintypes.DWORD


def activate_foreground(hwnd):
    user32.SetForegroundWindow(hwnd)
    if user32.GetForegroundWindow() == hwnd:
        user32.SetFocus(hwnd)
        return

    foreground = user32.GetForegroundWindow()
    foreground_thread = user32.GetWindowThreadProcessId(foreground, None)
    current_thread = kernel32.GetCurrentThreadId()
    if not foreground_thread or foreground_thread == current_thread:
        return
    attached = user32.AttachThreadInput(current_thread, foreground_thread, True)
    if not attached:
        return
    try:
        user32.SetForegroundWindow(hwnd)
        if user32.GetForegroundWindow() == hwnd:
            user32.SetFocus(hwnd)
    finally:
        user32.AttachThreadInput(current_thread, foreground_thread, False)


class ChatInput(QLineEdit):
    open_requested = Signal(object)

    def __init__(self, send_chat):
        super().__init__()
        self.send_chat = send_chat
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
        if not self.active.is_set():
            self.active.set()
            self.open_requested.emit(user32.GetForegroundWindow())

    @Slot(object)
    def open_input(self, target):
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
        if user32.GetForegroundWindow() == int(self.winId()):
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
        self.hide()
        if self.target:
            user32.SetForegroundWindow(self.target)
        self.active.clear()

    def submit(self):
        text = self.text()
        if not text.strip():
            self.cancel()
            return
        self.hide()
        if self.target:
            user32.SetForegroundWindow(self.target)
        QTimer.singleShot(150, lambda: self.deliver(text))

    def deliver(self, text):
        if not self.target or user32.GetForegroundWindow() != self.target:
            print("無法切回原視窗，文字尚未送出。", flush=True)
            self.show_and_focus()
            return
        try:
            self.send_chat(text)
        except Exception as error:
            print(f"輸入中斷，請確認遊戲聊天狀態：{error}", flush=True)
            self.show_and_focus()
        else:
            self.active.clear()

    def closeEvent(self, event):
        self.cancel()
        event.accept()
