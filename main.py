import keyboard
import pydirectinput as pdi
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from chat_input import ChatInput
from stratagems import STRATAGEMS


def send_chat(text):
    pdi.press("enter")
    keyboard.write(text)
    pdi.press("enter")


def bind_key(key, callback):
    return keyboard.add_hotkey(
        key, callback, suppress=True, trigger_on_release=True,
    )


def bind_stragem(key, stratagem):
    def wrapper():
        pdi.press("ctrl")
        for x in stratagem.sequence:
            match x:
                case 'up':
                    x = 'w'
                case 'down':
                    x = 's'
                case 'left':
                    x = 'a'
                case 'right':
                    x = 'd'
            pdi.press(x)
    return bind_key(key, wrapper)


def bind_chat(key, text):
    return bind_key(key, lambda: send_chat(text))


app = QApplication([])
app.setQuitOnLastWindowClosed(False)
chat_input = ChatInput(send_chat)
chat_input.initialize()

bind_stragem("f1", STRATAGEMS["Reinforce"])
bind_stragem("f2", STRATAGEMS["B-1 Supply Pack"])
bind_stragem("f3", STRATAGEMS["M-103 Supply FRV"])
bind_stragem("f4", STRATAGEMS["NUX-223 Hellbomb"])

bind_stragem("f5", STRATAGEMS["Orbital Napalm Barrage"])
bind_stragem("f6", STRATAGEMS["Orbital 120mm HE Barrage"])
bind_stragem("f7", STRATAGEMS["Orbital 380mm HE Barrage"])
bind_stragem("f8", STRATAGEMS["A/FLAM-40 Flame Sentry"])

bind_chat("f12", "sorry")
bind_key("\\", chat_input.request)

pdi.PAUSE = 0.017
try:
    app.exec()
finally:
    keyboard.unhook_all()
