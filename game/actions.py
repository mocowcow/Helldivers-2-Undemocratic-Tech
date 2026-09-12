import keyboard
import pydirectinput as pdi


DIRECTION_KEYS = {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
}


def send_chat(text):
    pdi.press("enter")
    keyboard.write(text)
    pdi.press("enter")


def call_stratagem(stratagem):
    pdi.press("ctrl")
    for direction in stratagem.sequence:
        pdi.press(DIRECTION_KEYS.get(direction, direction))
