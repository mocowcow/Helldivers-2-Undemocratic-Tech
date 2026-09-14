import time
import logging

import keyboard
import pydirectinput as pdi


CHAT_CHUNK_LIMIT = 10
logger = logging.getLogger(__name__)
DIRECTION_KEYS = {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
}


def send_chat(text):
    logger.info("聊天輸入開始 characters=%s", len(text))
    pdi.press("enter")
    for start in range(0, len(text), CHAT_CHUNK_LIMIT):
        keyboard.write(text[start:start + CHAT_CHUNK_LIMIT])
        time.sleep(0.05)
    pdi.press("enter")
    logger.info("聊天輸入事件送出完成 characters=%s", len(text))


def call_stratagem(stratagem):
    logger.info("戰略指令開始 name=%s", stratagem.name)
    pdi.press("ctrl")
    for direction in stratagem.sequence:
        pdi.press(DIRECTION_KEYS.get(direction, direction))
    logger.info("戰略指令完成 name=%s", stratagem.name)
