import ctypes
from ctypes import wintypes


user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
user32.AttachThreadInput.restype = wintypes.BOOL
user32.SetFocus.argtypes = [wintypes.HWND]
user32.SetFocus.restype = wintypes.HWND
kernel32.GetCurrentThreadId.restype = wintypes.DWORD


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
