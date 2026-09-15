import logging
import sys

import pydirectinput as pdi
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from config.defaults import DEFAULT_BINDINGS, INPUT_PAUSE
from config.settings import load_settings
from game.actions import send_chat
from hotkeys.manager import BindingManager
from hotkeys.validation import effective_bindings
from resources import resource_path
from ui.binding_panel import BindingPanel
from ui.chat_input import ChatInput
from diagnostics import configure_logging, LOG_PATH


logger = logging.getLogger(__name__)


def main():
    app = QApplication([])
    app.setWindowIcon(QIcon(str(resource_path("icon.ico"))))
    app.setQuitOnLastWindowClosed(False)
    chat_input = ChatInput(send_chat)
    bindings = BindingManager(chat_input.request)
    load_error = ""
    cooldown_modifiers = None
    try:
        saved_bindings, cooldown_modifiers = load_settings()
    except (OSError, ValueError) as error:
        logger.exception("設定載入失敗，使用預設綁定")
        saved_bindings = DEFAULT_BINDINGS
        load_error = str(error)

    try:
        bindings.replace(effective_bindings(saved_bindings))
        pdi.PAUSE = INPUT_PAUSE
        panel = BindingPanel(bindings, saved_bindings, load_error, cooldown_modifiers)
        bindings.on_stratagem_trigger = panel.hud_overlay.cooldown_requested.emit
        panel.show()
        return app.exec()
    finally:
        try:
            bindings.disable()
        finally:
            bindings.clear()


if __name__ == "__main__":
    configure_logging()
    logger.info(
        "啟動 frozen=%s executable=%s python=%s log=%s",
        getattr(sys, "frozen", False), sys.executable, sys.version, LOG_PATH,
    )
    try:
        exit_code = main()
    except Exception:
        logger.exception("程式異常結束")
        raise SystemExit(1)
    else:
        logger.info("程式結束 exit_code=%s", exit_code)
        raise SystemExit(exit_code)
