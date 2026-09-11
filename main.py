import pydirectinput as pdi
from PySide6.QtWidgets import QApplication

from actions import send_chat
from bindings import BindingManager
from chat_input import ChatInput
from defaults import DEFAULT_BINDINGS, INPUT_PAUSE


def main():
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    chat_input = ChatInput(send_chat)
    bindings = BindingManager(chat_input.request)

    try:
        chat_input.initialize()
        for binding in DEFAULT_BINDINGS:
            bindings.bind(binding)
        pdi.PAUSE = INPUT_PAUSE
        return app.exec()
    finally:
        bindings.clear()


if __name__ == "__main__":
    raise SystemExit(main())
