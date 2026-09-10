import keyboard
import pydirectinput as pdi


def send_chat(text):
    pdi.press("enter")
    keyboard.write(text)
    pdi.press("enter")


keyboard.add_hotkey(
    "f1", lambda: send_chat("sorry"),
    suppress=True, trigger_on_release=True,
)

pdi.PAUSE = 0
keyboard.wait()
