from localization import tr
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QLineEdit

from hotkeys.keys import NUMPAD_NAMES, resolve_key


KEY_NAMES = {
    Qt.Key.Key_Return: "enter", Qt.Key.Key_Enter: "enter",
    Qt.Key.Key_Space: "space", Qt.Key.Key_Backspace: "backspace",
    Qt.Key.Key_Delete: "delete", Qt.Key.Key_Insert: "insert",
    Qt.Key.Key_PageUp: "page up", Qt.Key.Key_PageDown: "page down",
    Qt.Key.Key_Control: "ctrl", Qt.Key.Key_Shift: "shift",
    Qt.Key.Key_Alt: "alt", Qt.Key.Key_Meta: "windows",
    Qt.Key.Key_CapsLock: "caps lock", Qt.Key.Key_NumLock: "num lock",
    Qt.Key.Key_ScrollLock: "scroll lock", Qt.Key.Key_Print: "print screen",
}


class KeyInput(QLineEdit):
    changed = Signal()

    def __init__(self, key=""):
        super().__init__()
        self.key = key
        self.capturing = False
        self.pressed = set()
        self.candidate = ""
        self.setReadOnly(True)
        self.setMinimumWidth(150)
        self.setToolTip(tr('key_input.hint'))
        self.show_key()

    def show_key(self):
        self.setText(self.key.upper() if self.key else tr('key_input.unbound'))

    def begin_capture(self):
        self.capturing = True
        self.pressed.clear()
        self.candidate = ""
        self.setText(tr('key_input.capture'))

    def cancel_capture(self):
        self.capturing = False
        self.pressed.clear()
        self.candidate = ""
        self.show_key()

    def clear_binding(self):
        previous = self.key
        self.key = ""
        self.cancel_capture()
        if previous:
            self.changed.emit()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.begin_capture()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.begin_capture()

    def focusOutEvent(self, event):
        self.cancel_capture()
        super().focusOutEvent(event)

    def event(self, event):
        # Handle Tab here so QWidget does not move focus before capture.
        if getattr(self, "capturing", False):
            if event.type() == QEvent.Type.ShortcutOverride:
                event.accept()
                return True
            if event.type() == QEvent.Type.KeyPress:
                self.keyPressEvent(event)
                return True
            if event.type() == QEvent.Type.KeyRelease:
                self.keyReleaseEvent(event)
                return True
        return super().event(event)

    def keyPressEvent(self, event):
        event.accept()
        if not self.capturing or event.isAutoRepeat():
            return
        if event.key() == Qt.Key.Key_Escape:
            self.clear_binding()
            return
        self.pressed.add(event.key())
        modifiers = event.modifiers() & ~Qt.KeyboardModifier.KeypadModifier
        own_modifier = {
            Qt.Key.Key_Control: Qt.KeyboardModifier.ControlModifier,
            Qt.Key.Key_Shift: Qt.KeyboardModifier.ShiftModifier,
            Qt.Key.Key_Alt: Qt.KeyboardModifier.AltModifier,
            Qt.Key.Key_Meta: Qt.KeyboardModifier.MetaModifier,
        }.get(event.key(), Qt.KeyboardModifier.NoModifier)
        if len(self.pressed) > 1 or modifiers & ~own_modifier:
            self.candidate = ""
            self.setText(tr('key_input.single_only'))
            return
        name = KEY_NAMES.get(event.key())
        if name is None:
            name = QKeySequence(event.key()).toString(QKeySequence.SequenceFormat.PortableText).lower()
        if (event.modifiers() & Qt.KeyboardModifier.KeypadModifier
                and event.key() != Qt.Key.Key_NumLock):
            # Use the physical scan code rather than the Num Lock-dependent name.
            keypad_name = NUMPAD_NAMES.get(event.nativeScanCode() & 0xff)
            name = f"num {keypad_name}" if keypad_name is not None else ""
        try:
            if not name or not resolve_key(name):
                raise ValueError("Unsupported key")
        except (ValueError, KeyError):
            self.candidate = ""
            self.setText(tr('key_input.unsupported'))
            return
        self.candidate = name
        self.setText(name.upper())

    def keyReleaseEvent(self, event):
        event.accept()
        if not self.capturing or event.isAutoRepeat():
            return
        self.pressed.discard(event.key())
        if self.pressed or not self.candidate:
            return
        previous = self.key
        self.key = self.candidate
        self.cancel_capture()
        if self.key != previous:
            self.changed.emit()
