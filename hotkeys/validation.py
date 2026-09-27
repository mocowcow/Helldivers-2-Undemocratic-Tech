from hotkeys.keys import TOGGLE_BINDINGS_KEY, resolve_key

from stratagems import STRATAGEMS


def validate_bindings(bindings):
    keys = set()
    reserved = set(resolve_key(TOGGLE_BINDINGS_KEY))
    open_chat_count = 0
    recognize_terminal_count = 0
    for binding in bindings:
        if binding.action not in ("stratagem", "chat", "open_chat", "recognize_terminal"):
            raise ValueError(f"未知的綁定動作：{binding.action}")
        if binding.action == "stratagem" and binding.value not in STRATAGEMS:
            raise ValueError(f"未知的戰略配備：{binding.value}")
        if binding.action == "open_chat":
            open_chat_count += 1
            if open_chat_count > 1:
                raise ValueError("開啟聊天視窗只能設定一個快捷鍵。")
        if binding.action == "recognize_terminal":
            recognize_terminal_count += 1
            if recognize_terminal_count > 1:
                raise ValueError("Terminal 辨識只能設定一個快捷鍵。")
        if not binding.key:
            continue
        if binding.action == "chat" and not binding.value.strip():
            raise ValueError("聊天文字不可空白。")
        try:
            scan_codes = set(resolve_key(binding.key))
        except (ValueError, KeyError) as error:
            raise ValueError(f"不支援的單一按鍵：{binding.key}") from error
        if not scan_codes:
            raise ValueError(f"不支援的快捷鍵：{binding.key}")
        if reserved.intersection(scan_codes):
            raise ValueError("Scroll Lock 保留用於切換啟用狀態，不能設定為其他快捷鍵。")
        if keys.intersection(scan_codes):
            raise ValueError(f"快捷鍵重複：{binding.key.upper()}")
        keys.update(scan_codes)


def effective_bindings(bindings):
    bindings = tuple(bindings)
    validate_bindings(bindings)
    return tuple(binding for binding in bindings if binding.key)
