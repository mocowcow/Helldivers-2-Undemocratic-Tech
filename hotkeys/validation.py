from messages import UserFacingError
from hotkeys.keys import TOGGLE_BINDINGS_KEY, resolve_key

from stratagems import STRATAGEMS


def validate_bindings(bindings):
    keys = set()
    reserved = set(resolve_key(TOGGLE_BINDINGS_KEY))
    open_chat_count = 0
    recognize_terminal_count = 0
    for binding in bindings:
        if binding.action not in ("stratagem", "chat", "open_chat", "recognize_terminal"):
            raise UserFacingError('errors.unknown_action', action=binding.action)
        if binding.action == "stratagem" and binding.value not in STRATAGEMS:
            raise UserFacingError('errors.unknown_stratagem', stratagem=binding.value)
        if binding.action == "open_chat":
            open_chat_count += 1
            if open_chat_count > 1:
                raise UserFacingError('errors.chat_key_count')
        if binding.action == "recognize_terminal":
            recognize_terminal_count += 1
            if recognize_terminal_count > 1:
                raise UserFacingError('errors.terminal_key_count')
        if not binding.key:
            continue
        if binding.action == "chat" and not binding.value.strip():
            raise UserFacingError('errors.empty_chat')
        try:
            scan_codes = set(resolve_key(binding.key))
        except (ValueError, KeyError) as error:
            raise UserFacingError('errors.unsupported_key', key_name=binding.key) from error
        if not scan_codes:
            raise UserFacingError('errors.unsupported_hotkey', key_name=binding.key)
        if reserved.intersection(scan_codes):
            raise UserFacingError('errors.reserved_key')
        if keys.intersection(scan_codes):
            raise UserFacingError('errors.duplicate_key', key_name=binding.key.upper())
        keys.update(scan_codes)


def effective_bindings(bindings):
    bindings = tuple(bindings)
    validate_bindings(bindings)
    return tuple(binding for binding in bindings if binding.key)
