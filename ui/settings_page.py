from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFormLayout, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QWidget,
)

from config.settings import SETTINGS_PATH
from hotkeys.models import Binding
from ui.key_input import KeyInput


class SettingsPage(QWidget):
    changed = Signal()
    save_requested = Signal()

    def __init__(self, bindings):
        super().__init__()
        form = QFormLayout(self)
        path = QLineEdit(str(SETTINGS_PATH))
        path.setReadOnly(True)
        path_row = QHBoxLayout()
        path_row.addWidget(path, 1)
        open_path_button = QPushButton("開啟儲存路徑")
        open_path_button.clicked.connect(self.open_settings_folder)
        path_row.addWidget(open_path_button)
        save_button = QPushButton("儲存")
        save_button.clicked.connect(lambda checked=False: self.save_requested.emit())
        path_row.addWidget(save_button)
        form.addRow("設定檔儲存位置", path_row)
        current_key = next((b.key for b in bindings if b.action == "open_chat"), "")
        self.open_chat_key = KeyInput(current_key)
        self.open_chat_key.changed.connect(self.changed.emit)
        chat_key_row = QHBoxLayout()
        chat_key_row.addWidget(self.open_chat_key)
        clear_key = QPushButton("清除")
        clear_key.clicked.connect(self.open_chat_key.clear_binding)
        chat_key_row.addWidget(clear_key)
        form.addRow("開啟聊天視窗快捷鍵", chat_key_row)

    def draft(self):
        key = self.open_chat_key.key
        return (Binding(key, "open_chat"),) if key else ()

    def open_settings_folder(self):
        folder = SETTINGS_PATH.parent
        try:
            folder.mkdir(parents=True, exist_ok=True)
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder))):
                raise OSError("無法開啟設定檔資料夾。")
        except OSError as error:
            QMessageBox.warning(self, "開啟儲存路徑失敗", str(error))
