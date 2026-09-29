"""JSON-backed UI translation; independent of Qt and stored binding values."""

import json
import logging

import i18n

from resources import resource_path


DEFAULT_LANGUAGE = "zh_TW"
_configured = False


def available_languages():
    languages = {}
    for path in sorted(resource_path("locales").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            metadata = data.get("_meta", {})
            name = metadata.get("language_name") if isinstance(metadata, dict) else None
            languages[path.stem] = name if isinstance(name, str) and name else path.stem
        except (OSError, ValueError):
            logging.getLogger(__name__).warning("無法讀取語系檔 path=%s", path)
    return languages


def current_language():
    return i18n.get("locale") if _configured else DEFAULT_LANGUAGE


def configure_i18n(language=DEFAULT_LANGUAGE):
    global _configured
    directory = str(resource_path("locales"))
    if directory not in i18n.load_path:
        i18n.load_path.append(directory)
    i18n.set("file_format", "json")
    i18n.set("filename_format", "{locale}.{format}")
    i18n.set("skip_locale_root_data", True)
    i18n.set("fallback", DEFAULT_LANGUAGE)
    i18n.set("enable_memoization", True)
    i18n.set("locale", language)
    _configured = True


def tr(key, **values):
    if not _configured:
        configure_i18n()
    return i18n.t(key, **values)


def error_text(error):
    from messages import UserFacingError

    if isinstance(error, UserFacingError):
        values = {key: error_text(value) if isinstance(value, UserFacingError) else value
                  for key, value in error.values.items()}
        return tr(error.message_key, **values)
    return str(error)
