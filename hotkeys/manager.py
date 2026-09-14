from functools import partial
import logging

import keyboard

from game.actions import call_stratagem, send_chat
from stratagems import STRATAGEMS
from hotkeys.models import Binding
from hotkeys.keys import resolve_key


_scan_hooks = {}
logger = logging.getLogger(__name__)


def _subscribe_scan_code(code, handler):
    entry = _scan_hooks.get(code)
    if entry is None:
        handlers = []

        def dispatch(event):
            return all(callback(event) for callback in tuple(handlers))

        remove_hook = keyboard.hook_key(code, dispatch, suppress=True)
        entry = (handlers, remove_hook)
        _scan_hooks[code] = entry
    handlers, remove_hook = entry
    handlers.append(handler)

    def unsubscribe():
        if handler not in handlers:
            return
        handlers.remove(handler)
        if not handlers:
            remove_hook()
            del _scan_hooks[code]

    return unsubscribe


def bind_key(key, callback):
    identities = set(resolve_key(key))

    def handler(event):
        if (event.scan_code, event.is_keypad) not in identities:
            return True
        if event.event_type == keyboard.KEY_UP:
            try:
                logger.info("快捷鍵開始 key=%s", key)
                callback()
                logger.info("快捷鍵回呼完成 key=%s", key)
            except Exception:
                logger.exception("快捷鍵執行失敗 key=%s", key)
        return False

    removers = []
    try:
        for code in sorted({code for code, _ in identities}):
            removers.append(_subscribe_scan_code(code, handler))
    except Exception:
        for remove in removers:
            remove()
        raise

    def unbind():
        for remove in removers:
            remove()

    return unbind


def bind_stragem(key, stratagem):
    return bind_key(key, partial(call_stratagem, stratagem))


def bind_chat(key, text):
    return bind_key(key, partial(send_chat, text))


class BindingManager:
    def __init__(self, open_chat):
        self.open_chat = open_chat
        self._enabled = False
        self._bindings = {}
        self._removers = {}

    @property
    def bindings(self):
        return tuple(self._bindings.values())

    def _register(self, binding):
        callback = self._callback(binding)

        def invoke():
            if self._enabled:
                callback()

        return bind_key(binding.key, invoke)

    def enable(self):
        if self._enabled:
            return
        try:
            for binding in self._bindings.values():
                self._removers[binding.key] = self._register(binding)
        except Exception:
            self.disable()
            raise
        self._enabled = True
        logger.info("已啟用綁定 count=%s", len(self._removers))

    def disable(self):
        count = len(self._removers)
        self._enabled = False
        for key in tuple(self._removers):
            self._removers[key]()
            del self._removers[key]
        if count:
            logger.info("已解除綁定 count=%s", count)

    def _callback(self, binding):
        if binding.action == "stratagem":
            return partial(call_stratagem, STRATAGEMS[binding.value])
        if binding.action == "chat":
            return partial(send_chat, binding.value)
        if binding.action == "open_chat":
            return partial(self.open_chat)
        raise ValueError(f"Unknown binding action: {binding.action}")

    def bind(self, binding):
        """Register or replace a key; restore the old binding if registration fails."""
        key = binding.key.strip().lower()
        if not key:
            raise ValueError("Hotkey must not be empty")
        binding = Binding(key, binding.action, binding.value)
        self._callback(binding)
        # Validate the single key before removing an existing registration.
        resolve_key(key)
        previous = self._bindings.get(key)
        self.unbind(key)
        try:
            if self._enabled:
                self._removers[key] = self._register(binding)
        except Exception:
            if previous is not None:
                if self._enabled:
                    self._removers[key] = self._register(previous)
                self._bindings[key] = previous
            raise
        self._bindings[key] = binding

    def unbind(self, key):
        key = key.strip().lower()
        remover = self._removers.get(key)
        if remover is not None:
            remover()
            del self._removers[key]
        self._bindings.pop(key, None)

    def clear(self):
        for key in tuple(self._bindings):
            self.unbind(key)

    def replace(self, bindings):
        """Replace the complete set, restoring previous registrations on failure."""
        normalized = []
        keys = set()
        for binding in bindings:
            key = binding.key.strip().lower()
            identities = set(resolve_key(key)) if key else set()
            if not identities or keys.intersection(identities):
                raise ValueError(f"Empty or duplicate hotkey: {key}")
            self._callback(binding)
            keys.update(identities)
            normalized.append(Binding(key, binding.action, binding.value))

        previous = self.bindings
        try:
            self.clear()
            for binding in normalized:
                self.bind(binding)
        except Exception:
            self.clear()
            for binding in previous:
                self.bind(binding)
            raise
