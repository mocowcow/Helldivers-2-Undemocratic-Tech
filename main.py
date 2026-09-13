import pydirectinput as pdi
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from config.defaults import DEFAULT_BINDINGS, INPUT_PAUSE
from config.settings import load_bindings
from game.actions import send_chat
from hotkeys.manager import BindingManager
from hotkeys.validation import effective_bindings
from resources import resource_path
from ui.binding_panel import BindingPanel
from ui.chat_input import ChatInput


def main():
    app = QApplication([])
    app.setWindowIcon(QIcon(str(resource_path("icon.ico"))))
    app.setQuitOnLastWindowClosed(False)
    chat_input = ChatInput(send_chat)
    bindings = BindingManager(chat_input.request)
    load_error = ""
    try:
        saved_bindings = load_bindings()
    except (OSError, ValueError) as error:
        saved_bindings = DEFAULT_BINDINGS
        load_error = str(error)

    try:
        bindings.replace(effective_bindings(saved_bindings))
        pdi.PAUSE = INPUT_PAUSE
        panel = BindingPanel(bindings, saved_bindings, load_error)
        panel.show()
        return app.exec()
    finally:
        try:
            bindings.disable()
        finally:
            bindings.clear()


if __name__ == "__main__":
    raise SystemExit(main())
