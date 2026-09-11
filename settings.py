import json
import os
import keyboard
from pathlib import Path
from tempfile import NamedTemporaryFile

from bindings import Binding
from defaults import DEFAULT_BINDINGS
from stratagems import STRATAGEMS


SETTINGS_PATH = Path(os.environ["LOCALAPPDATA"]) / "HD2" / "bindings.json"


def validate_bindings(bindings):
    keys = set()
    open_chat_count = 0
    for binding in bindings:
        if binding.action not in ("stratagem", "chat", "open_chat"):
            raise ValueError(f"未知的綁定動作：{binding.action}")
        if binding.action == "stratagem" and binding.value not in STRATAGEMS:
            raise ValueError(f"未知的戰略配備：{binding.value}")
        if binding.action == "open_chat":
            open_chat_count += 1
            if open_chat_count > 1:
                raise ValueError("開啟聊天視窗只能設定一個快捷鍵。")
        if not binding.key:
            continue
        if binding.action == "chat" and not binding.value.strip():
            raise ValueError("聊天文字不可空白。")
        try:
            scan_codes = set(keyboard.key_to_scan_codes(binding.key))
        except (ValueError, KeyError) as error:
            raise ValueError(f"不支援的單一按鍵：{binding.key}") from error
        if not scan_codes:
            raise ValueError(f"不支援的快捷鍵：{binding.key}")
        if keys.intersection(scan_codes):
            raise ValueError(f"快捷鍵重複：{binding.key.upper()}")
        keys.update(scan_codes)


def effective_bindings(bindings):
    bindings = tuple(bindings)
    validate_bindings(bindings)
    return tuple(binding for binding in bindings if binding.key)


def load_bindings(path=SETTINGS_PATH):
    if not path.exists():
        return DEFAULT_BINDINGS
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 2:
        raise ValueError("不支援的綁定設定格式。")
    data = data.get("bindings")
    if not isinstance(data, list):
        raise ValueError("bindings 必須是清單。")
    bindings = []
    for item in data:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("key"), str)
            or not isinstance(item.get("action"), str)
            or not isinstance(item.get("value"), str)
        ):
            raise ValueError("綁定欄位格式錯誤。")
        bindings.append(Binding(item["key"], item["action"], item["value"]))
    validate_bindings(bindings)
    return tuple(bindings)


def save_bindings(bindings, path=SETTINGS_PATH):
    bindings = tuple(bindings)
    validate_bindings(bindings)
    data = {
        "version": 2,
        "bindings": [
            {"key": binding.key, "action": binding.action, "value": binding.value}
            for binding in bindings
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix="bindings-", suffix=".tmp", delete=False,
        ) as output:
            temporary = Path(output.name)
            json.dump(data, output, ensure_ascii=False, indent=2)
            output.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
