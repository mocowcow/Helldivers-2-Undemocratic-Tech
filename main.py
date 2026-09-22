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
from vision.capture import TerminalRecognition


logger = logging.getLogger(__name__)
_terminal_recognition = None


def request_terminal_recognition():
    """Hotkey callback: capture primary screen, recognize and send directions.

    After main() initializes the service, register using:
        unbind = bind_key(key, request_terminal_recognition)
    The caller owns that hotkey registration and its returned unbind callback.
    """
    service = _terminal_recognition
    if service is None:
        logger.warning("Terminal 辨識服務尚未初始化或已關閉")
        return False
    return service.request()


def main():
    global _terminal_recognition
    app = QApplication([])
    app.setWindowIcon(QIcon(str(resource_path("icon.ico"))))
    app.setQuitOnLastWindowClosed(False)
    chat_input = ChatInput(send_chat)
    bindings = BindingManager(chat_input.request, recognize_terminal=request_terminal_recognition)
    chat_input.on_open = bindings.suspend
    app.aboutToQuit.connect(bindings.disable)
    app.aboutToQuit.connect(chat_input.shutdown)
    load_error = ""
    cooldown_modifiers = None
    try:
        saved_bindings, cooldown_modifiers = load_settings()
    except (OSError, ValueError) as error:
        logger.exception("設定載入失敗，使用預設綁定")
        saved_bindings = DEFAULT_BINDINGS
        load_error = str(error)

    try:
        _terminal_recognition = TerminalRecognition(app)
        bindings.replace(effective_bindings(saved_bindings))
        pdi.PAUSE = INPUT_PAUSE
        panel = BindingPanel(bindings, saved_bindings, load_error, cooldown_modifiers)

        def resume_after_chat():
            try:
                bindings.resume()
            except Exception:
                logger.exception("聊天結束後恢復快捷鍵失敗，已停用綁定")
                bindings.disable()
                panel.enable_checkbox.setChecked(False)
                # Clear the suspension now that no hooks need restoring.
                bindings.resume()
                panel.status.setText("恢復快捷鍵失敗，已停用；請重新勾選啟用。")

        chat_input.on_finished = resume_after_chat
        bindings.on_stratagem_trigger = panel.hud_overlay.cooldown_requested.emit
        panel.show()
        return app.exec()
    finally:
        chat_input.shutdown()
        if _terminal_recognition is not None:
            _terminal_recognition.close()
            _terminal_recognition = None
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
