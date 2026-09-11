import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from bindings import Binding
from defaults import DEFAULT_BINDINGS
from stratagems import STRATAGEMS


BINDING_KEYS = tuple(f"f{number}" for number in range(1, 13)) + ("\\",)
SETTINGS_PATH = Path(os.environ["LOCALAPPDATA"]) / "HD2" / "bindings.json"
DEFAULT_STRATAGEM_BINDINGS = tuple(
    binding for binding in DEFAULT_BINDINGS if binding.action == "stratagem"
)


def validate_bindings(bindings):
    keys = set()
    for binding in bindings:
        if binding.action != "stratagem" or binding.value not in STRATAGEMS:
            raise ValueError(f"未知的戰略配備：{binding.value}")
        if binding.key not in BINDING_KEYS:
            raise ValueError(f"不支援的快捷鍵：{binding.key}")
        if binding.key in keys:
            raise ValueError(f"快捷鍵重複：{binding.key.upper()}")
        keys.add(binding.key)


def effective_bindings(bindings):
    bindings = tuple(bindings)
    validate_bindings(bindings)
    used_keys = {binding.key for binding in bindings}
    return bindings + tuple(
        binding for binding in DEFAULT_BINDINGS
        if binding.action != "stratagem" and binding.key not in used_keys
    )


def load_bindings(path=SETTINGS_PATH):
    if not path.exists():
        return DEFAULT_STRATAGEM_BINDINGS
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("綁定設定必須是清單。")
    bindings = []
    for item in data:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("key"), str)
            or not isinstance(item.get("stratagem"), str)
        ):
            raise ValueError("每筆綁定必須包含 key 與 stratagem 字串。")
        bindings.append(Binding(item["key"], "stratagem", item["stratagem"]))
    validate_bindings(bindings)
    return tuple(bindings)


def save_bindings(bindings, path=SETTINGS_PATH):
    bindings = tuple(bindings)
    validate_bindings(bindings)
    data = [{"key": binding.key, "stratagem": binding.value} for binding in bindings]
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
