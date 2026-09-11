from dataclasses import dataclass
from functools import partial

import keyboard

from actions import call_stratagem, send_chat
from stratagems import STRATAGEMS


def bind_key(key, callback):
    return keyboard.add_hotkey(
        key, callback, suppress=True, trigger_on_release=True,
    )


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
    def __init__(self, open_chat):
        self.open_chat = open_chat
        self._bindings = {}
        self._removers = {}

    @property
    def bindings(self):
        return tuple(self._bindings.values())

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
        callback = self._callback(binding)
        # Validate syntax before removing an existing registration.
        keyboard.parse_hotkey_combinations(key)
        previous = self._bindings.get(key)
        self.unbind(key)
        try:
            remover = bind_key(key, callback)
        except Exception:
            if previous is not None:
                self._removers[key] = bind_key(key, self._callback(previous))
                self._bindings[key] = previous
            raise
        self._removers[key] = remover
        self._bindings[key] = binding

    def unbind(self, key):
        key = key.strip().lower()
        remover = self._removers.get(key)
        if remover is not None:
            remover()
            del self._removers[key]
            del self._bindings[key]

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
