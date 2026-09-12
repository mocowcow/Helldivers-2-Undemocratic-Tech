import ctypes
from ctypes import wintypes
from pathlib import PureWindowsPath


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
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
user32.AttachThreadInput.restype = wintypes.BOOL
user32.SetFocus.argtypes = [wintypes.HWND]
user32.SetFocus.restype = wintypes.HWND
kernel32.GetCurrentThreadId.restype = wintypes.DWORD


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


def get_foreground_window():
    return user32.GetForegroundWindow()


def set_foreground_window(hwnd):
    return user32.SetForegroundWindow(hwnd)


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
