from dataclasses import dataclass
from functools import partial

import keyboard

from actions import call_stratagem, send_chat
from stratagems import STRATAGEMS


def bind_key(key, callback):
    def handler(event):
        if event.event_type == keyboard.KEY_UP:
            callback()
        return False

    return keyboard.hook_key(key, handler, suppress=True)


def bind_stragem(key, stratagem):
    return bind_key(key, partial(call_stratagem, stratagem))


def bind_chat(key, text):
    return bind_key(key, partial(send_chat, text))


@dataclass(frozen=True)
class Binding:
    key: str
    action: str
    value: str = ""


class BindingManager:
    def __init__(self, open_chat, can_trigger=None):
        self.open_chat = open_chat
        self.can_trigger = can_trigger
        self._enabled = False
        self._bindings = {}
        self._removers = {}

    @property
    def bindings(self):
        return tuple(self._bindings.values())

    def _register(self, binding):
        callback = self._callback(binding)

        def invoke():
            if self._enabled and (self.can_trigger is None or self.can_trigger()):
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

    def disable(self):
        self._enabled = False
        for key in tuple(self._removers):
            self._removers[key]()
            del self._removers[key]

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
        # Validate syntax before removing an existing registration.
        keyboard.parse_hotkey_combinations(key)
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
            if not key or key in keys:
                raise ValueError(f"Empty or duplicate hotkey: {key}")
            self._callback(binding)
            keyboard.parse_hotkey_combinations(key)
            keys.add(key)
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
