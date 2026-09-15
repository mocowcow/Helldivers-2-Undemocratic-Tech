import logging

from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from config.settings import SETTINGS_PATH
from hotkeys.models import Binding
from ui.key_input import KeyInput
from game.cooldowns import COOLDOWN_UPGRADES


class SettingsPage(QWidget):
    save_requested = Signal()
    cooldown_upgrades_changed = Signal(object)

    def __init__(self, bindings, cooldown_modifiers=None):
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
        chat_key_row = QHBoxLayout()
        chat_key_row.addWidget(self.open_chat_key)
        self.clear_key = QPushButton("清除")
        self.clear_key.clicked.connect(self.open_chat_key.clear_binding)
        chat_key_row.addWidget(self.clear_key)
        form.addRow("開啟聊天視窗快捷鍵", chat_key_row)
        hint = QLabel(
            "冷卻修正：各效果逐一相乘，於下次熱鍵觸發時計算；不改變已開始的倒數。"
        )
        hint.setWordWrap(True)
        form.addRow(hint)
        upgrades_scroll = QScrollArea()
        upgrades_scroll.setWidgetResizable(True)
        upgrades_scroll.setMinimumHeight(140)
        upgrades_content = QWidget()
        upgrades_layout = QVBoxLayout(upgrades_content)
        self.upgrade_checkboxes = {}
        cooldown_modifiers = cooldown_modifiers if cooldown_modifiers is not None else {}
        for upgrade in COOLDOWN_UPGRADES:
            checkbox = QCheckBox(f"{upgrade.name}\n{upgrade.description}")
            checkbox.setChecked(cooldown_modifiers.get(upgrade.key, upgrade.default_enabled))
            checkbox.toggled.connect(self.emit_cooldown_upgrades)
            self.upgrade_checkboxes[upgrade.key] = checkbox
            upgrades_layout.addWidget(checkbox)
        upgrades_layout.addStretch()
        upgrades_scroll.setWidget(upgrades_content)
        form.addRow(upgrades_scroll)

    def cooldown_modifiers(self):
        return {
            key: checkbox.isChecked()
            for key, checkbox in self.upgrade_checkboxes.items()
        }

    def emit_cooldown_upgrades(self, *args):
        enabled = frozenset(key for key, checked in self.cooldown_modifiers().items() if checked)
        self.cooldown_upgrades_changed.emit(enabled)

    def set_bindings_editable(self, editable):
        self.open_chat_key.setEnabled(editable)
        self.clear_key.setEnabled(editable)

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
            logging.getLogger(__name__).exception("開啟設定檔資料夾失敗")
            QMessageBox.warning(self, "開啟儲存路徑失敗", str(error))
