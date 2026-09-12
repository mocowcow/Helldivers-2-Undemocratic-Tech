import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from config.defaults import DEFAULT_BINDINGS
from hotkeys.models import Binding
from hotkeys.validation import validate_bindings


SETTINGS_PATH = Path(os.environ["LOCALAPPDATA"]) / "HD2" / "bindings.json"


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
