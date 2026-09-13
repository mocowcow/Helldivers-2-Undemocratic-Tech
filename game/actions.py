import time

import keyboard
import pydirectinput as pdi


CHAT_CHUNK_LIMIT = 10
DIRECTION_KEYS = {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
}


def send_chat(text):
    pdi.press("enter")
    for start in range(0, len(text), CHAT_CHUNK_LIMIT):
        keyboard.write(text[start:start + CHAT_CHUNK_LIMIT])
        time.sleep(0.05)
    pdi.press("enter")


def call_stratagem(stratagem):
    pdi.press("ctrl")
    for direction in stratagem.sequence:
        pdi.press(DIRECTION_KEYS.get(direction, direction))
