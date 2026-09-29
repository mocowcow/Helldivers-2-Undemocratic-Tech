import json
import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from messages import UserFacingError
from localization import DEFAULT_LANGUAGE, available_languages

from config.defaults import DEFAULT_BINDINGS
from game.cooldowns import COOLDOWN_UPGRADES
from hotkeys.models import Binding
from hotkeys.validation import validate_bindings


SETTINGS_PATH = Path(os.environ["LOCALAPPDATA"]) / "HD2" / "bindings.json"
logger = logging.getLogger(__name__)


def load_settings(path=SETTINGS_PATH):
    modifiers = {modifier.key: modifier.default_enabled for modifier in COOLDOWN_UPGRADES}
    if not path.exists():
        logger.info("設定檔不存在，使用預設綁定 path=%s", path)
        return DEFAULT_BINDINGS, modifiers, DEFAULT_LANGUAGE
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 2:
        raise UserFacingError('errors.settings_format')
    language = data.get("language", DEFAULT_LANGUAGE)
    if not isinstance(language, str) or language not in available_languages():
        language = DEFAULT_LANGUAGE
    saved_modifiers = data.get("cooldown_modifiers", {})
    if not isinstance(saved_modifiers, dict) or any(
        not isinstance(value, bool) for value in saved_modifiers.values()
    ):
        raise UserFacingError('errors.modifier_types')
    modifiers.update({key: saved_modifiers[key] for key in modifiers if key in saved_modifiers})
    data = data.get("bindings")
    if not isinstance(data, list):
        raise UserFacingError('errors.bindings_list')
    bindings = []
    for item in data:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("key"), str)
            or not isinstance(item.get("action"), str)
            or not isinstance(item.get("value"), str)
        ):
            raise UserFacingError('errors.binding_fields')
        bindings.append(Binding(item["key"], item["action"], item["value"]))
    validate_bindings(bindings)
    logger.info("設定載入完成 path=%s count=%s", path, len(bindings))
    return tuple(bindings), modifiers, language


def save_settings(bindings, cooldown_modifiers, path=SETTINGS_PATH, *, language=DEFAULT_LANGUAGE):
    bindings = tuple(bindings)
    validate_bindings(bindings)
    if not isinstance(cooldown_modifiers, dict) or any(
        not isinstance(cooldown_modifiers.get(modifier.key), bool)
        for modifier in COOLDOWN_UPGRADES
    ):
        raise UserFacingError('errors.modifier_missing')
    data = {
        "version": 2,
        "language": language,
        "cooldown_modifiers": {
            modifier.key: cooldown_modifiers[modifier.key]
            for modifier in COOLDOWN_UPGRADES
        },
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
        logger.info("設定儲存完成 path=%s count=%s", path, len(bindings))
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
