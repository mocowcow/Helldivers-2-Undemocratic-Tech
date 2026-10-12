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

GR8_FAST_RELOAD_T1_MS = 1550
GR8_FAST_RELOAD_T2_MS = 1800

RELOAD_ARMOR_MULTIPLIERS = {
    "standard": 1.0,
    "TR-8": 0.8,  # says increases by 30%, but NOT actually how it works.
}


def GR8_fast_reload(time_multiplier=1, cancel=None):
    """Run R/C twice; multiplier scales both waits (0.9 means 10% shorter)."""
    from threading import Event

    cancel = cancel if cancel is not None else Event()
    if time_multiplier < 0:
        raise ValueError("Reload time multiplier must not be negative")
    logger.info("GR8 fast reload started multiplier=%s", time_multiplier)
    for delay_ms in (GR8_FAST_RELOAD_T1_MS, GR8_FAST_RELOAD_T2_MS):
        if cancel.is_set():
            return
        pdi.press("r", _pause=False)
        if cancel.wait(delay_ms * time_multiplier / 1000):
            return
        pdi.press("c")
    logger.info("GR8 fast reload completed")


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
