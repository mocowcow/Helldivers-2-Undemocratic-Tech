"""Resolve stored key names to Windows scan codes and keypad identities."""

import keyboard


TOGGLE_BINDINGS_KEY = "scroll lock"


# Standard Windows keyboard scan codes. Names describe physical keys,
# so numpad identities remain stable when Num Lock changes.
NUMPAD_CODES = {
    "0": 82, "1": 79, "2": 80, "3": 81, "4": 75,
    "5": 76, "6": 77, "7": 71, "8": 72, "9": 73,
    ".": 83, "+": 78, "-": 74, "*": 55, "/": 53,
    "enter": 28,
}
NUMPAD_NAMES = {code: name for name, code in NUMPAD_CODES.items()}
MAIN_CODES = {
    **{str(number): number + 1 for number in range(1, 10)},
    "0": 11,
    "page up": 73, "page down": 81, "home": 71, "end": 79,
    "insert": 82, "delete": 83,
    "left": 75, "right": 77, "up": 72, "down": 80,
    "enter": 28, "/": 53, "-": 12, ".": 52,
}


def resolve_key(key):
    """Return all (scan_code, is_keypad) identities matched by a key name."""
    name = key.strip().lower()
    # keyboard.normalize_name collapses "num 3" to "3" and "num enter"
    # to "enter", so preserve our keypad prefix before normalizing aliases.
    if name.startswith("num ") and name != "num lock":
        suffix = name[4:]
        if suffix not in NUMPAD_CODES:
            raise ValueError(f"不支援的數字鍵盤按鍵：{key}")
        return ((NUMPAD_CODES[suffix], True),)
    name = keyboard.normalize_name(name)
    if name == "num lock":
        return ((69, True),)
    if name in MAIN_CODES:
        return ((MAIN_CODES[name], False),)
    return tuple((code, False) for code in keyboard.key_to_scan_codes(name))
