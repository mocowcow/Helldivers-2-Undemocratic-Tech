import pydirectinput as pdi
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from actions import send_chat
from binding_panel import BindingPanel
from bindings import BindingManager
from chat_input import ChatInput
from defaults import INPUT_PAUSE
from settings import DEFAULT_STRATAGEM_BINDINGS, effective_bindings, load_bindings


def main():
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    chat_input = ChatInput(send_chat)
    bindings = BindingManager(chat_input.request)
    load_error = ""
    try:
        saved_bindings = load_bindings()
    except (OSError, ValueError) as error:
        saved_bindings = DEFAULT_STRATAGEM_BINDINGS
        load_error = str(error)

    try:
        bindings.replace(effective_bindings(saved_bindings))
        pdi.PAUSE = INPUT_PAUSE
        panel = BindingPanel(bindings, saved_bindings, load_error)
        panel.show()
        # Initialize chat focus after the control panel has been shown.
        QTimer.singleShot(250, chat_input.initialize)
        return app.exec()
    finally:
        bindings.clear()


if __name__ == "__main__":
    raise SystemExit(main())
