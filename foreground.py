import ctypes
from ctypes import wintypes
from pathlib import PureWindowsPath

from PySide6.QtCore import QObject, Qt, Signal, Slot


GAME_EXECUTABLE = "helldivers2.exe"
EVENT_SYSTEM_FOREGROUND = 0x0003
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
WinEventProc = ctypes.WINFUNCTYPE(
    None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,
    wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD,
)
user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.SetWinEventHook.argtypes = [
    wintypes.DWORD, wintypes.DWORD, wintypes.HMODULE, WinEventProc,
    wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
]
user32.SetWinEventHook.restype = wintypes.HANDLE
user32.UnhookWinEvent.argtypes = [wintypes.HANDLE]
user32.UnhookWinEvent.restype = wintypes.BOOL
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD),
]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL


def is_game_foreground():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return False
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not process:
        return False
    try:
        size = wintypes.DWORD(32768)
        path = ctypes.create_unicode_buffer(size.value)
        if not kernel32.QueryFullProcessImageNameW(process, 0, path, ctypes.byref(size)):
            return False
        return (
            PureWindowsPath(path.value).name.lower() == GAME_EXECUTABLE
            and user32.GetForegroundWindow() == hwnd
        )
    finally:
        kernel32.CloseHandle(process)


class ForegroundMonitor(QObject):
    changed = Signal()

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.hook = None
        self.callback = WinEventProc(self.on_event)
        self.changed.connect(self.refresh, Qt.ConnectionType.QueuedConnection)

    def start(self):
        if self.hook:
            return
        # Receive all foreground transitions, including this application's windows.
        self.hook = user32.SetWinEventHook(
            EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_FOREGROUND,
            None, self.callback, 0, 0, 0,
        )
        if not self.hook:
            raise ctypes.WinError(ctypes.get_last_error())
        self.refresh()

    def on_event(self, hook, event, hwnd, object_id, child_id, thread_id, timestamp):
        self.changed.emit()

    @Slot()
    def refresh(self):
        if not self.hook:
            return
        if is_game_foreground():
            try:
                self.manager.enable()
            except Exception as error:
                self.manager.disable()
                print(f"啟用快捷鍵失敗：{error}", flush=True)
        else:
            self.manager.disable()

    def stop(self):
        if self.hook:
            user32.UnhookWinEvent(self.hook)
            self.hook = None
        self.manager.disable()
