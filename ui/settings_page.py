import logging

from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from config.settings import SETTINGS_PATH
from hotkeys.models import Binding
from ui.key_input import KeyInput
from game.cooldowns import COOLDOWN_UPGRADES
from ui.labels import modifier_label
from localization import available_languages, current_language, error_text, tr


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
        open_path_button = QPushButton(tr('settings.open_folder'))
        open_path_button.clicked.connect(self.open_settings_folder)
        path_row.addWidget(open_path_button)
        save_button = QPushButton(tr('settings.save'))
        save_button.clicked.connect(lambda checked=False: self.save_requested.emit())
        path_row.addWidget(save_button)
        form.addRow(tr('settings.path'), path_row)
        self.language_combo = QComboBox()
        for code, name in available_languages().items():
            self.language_combo.addItem(name, code)
        self.language_combo.setCurrentIndex(self.language_combo.findData(current_language()))
        form.addRow(tr('settings.language'), self.language_combo)
        current_key = next((b.key for b in bindings if b.action == "open_chat"), "")
        self.open_chat_key = KeyInput(current_key)
        chat_key_row = QHBoxLayout()
        chat_key_row.addWidget(self.open_chat_key)
        self.clear_key = QPushButton(tr('settings.clear'))
        self.clear_key.clicked.connect(self.open_chat_key.clear_binding)
        chat_key_row.addWidget(self.clear_key)
        form.addRow(tr('settings.chat_key'), chat_key_row)
        terminal_key = next((b.key for b in bindings if b.action == "recognize_terminal"), "")
        self.terminal_key = KeyInput(terminal_key)
        self.terminal_key.setToolTip(tr('settings.terminal_hint'))
        terminal_key_row = QHBoxLayout()
        terminal_key_row.addWidget(self.terminal_key)
        self.clear_terminal_key = QPushButton(tr('settings.clear'))
        self.clear_terminal_key.clicked.connect(self.terminal_key.clear_binding)
        terminal_key_row.addWidget(self.clear_terminal_key)
        form.addRow(tr('settings.terminal_key'), terminal_key_row)
        hint = QLabel(
            tr('settings.cooldown_hint')
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
            checkbox = QCheckBox(modifier_label(upgrade.key))
            checkbox.setChecked(cooldown_modifiers.get(upgrade.key, upgrade.default_enabled))
            checkbox.toggled.connect(self.emit_cooldown_upgrades)
            self.upgrade_checkboxes[upgrade.key] = checkbox
            upgrades_layout.addWidget(checkbox)
        upgrades_layout.addStretch()
        upgrades_scroll.setWidget(upgrades_content)
        form.addRow(upgrades_scroll)

    def language(self):
        return self.language_combo.currentData() or current_language()

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
        self.terminal_key.setEnabled(editable)
        self.clear_terminal_key.setEnabled(editable)

    def draft(self):
        return tuple(
            Binding(key, action)
            for key, action in (
                (self.open_chat_key.key, "open_chat"),
                (self.terminal_key.key, "recognize_terminal"),
            )
            if key
        )

    def open_settings_folder(self):
        folder = SETTINGS_PATH.parent
        try:
            folder.mkdir(parents=True, exist_ok=True)
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder))):
                raise OSError(tr('settings.folder_unavailable'))
        except OSError as error:
            logging.getLogger(__name__).exception("開啟設定檔資料夾失敗")
            QMessageBox.warning(self, tr('settings.folder_failed'), error_text(error))
