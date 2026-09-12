import ctypes

from PySide6.QtCore import QObject, Qt, Signal, Slot

from game.windows import EVENT_SYSTEM_FOREGROUND, WinEventProc, is_game_foreground, user32


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
