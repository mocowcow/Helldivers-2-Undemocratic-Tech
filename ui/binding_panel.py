import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QHBoxLayout, QMessageBox,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from config.settings import save_settings
from hotkeys.models import Binding
from hotkeys.validation import effective_bindings
from stratagems import STRATAGEMS
from ui.binding_table import BindingTable
from ui.settings_page import SettingsPage
from ui.hud_overlay import HUDOverlay
from localization import error_text, tr


logger = logging.getLogger(__name__)


class BindingPanel(QWidget):
    toggle_requested = Signal()

    def __init__(self, manager, bindings, cooldown_modifiers=None):
        super().__init__()
        self.manager = manager
        self.hud_overlay = HUDOverlay()
        bindings = tuple(bindings)
        self.setWindowTitle(tr('bindings.title'))
        self.resize(720, 440)
        layout = QVBoxLayout(self)
        navigation = QHBoxLayout()
        self.navigation = QButtonGroup(self)
        for index, title in enumerate((tr('bindings.stratagem_tab'), tr('bindings.chat_tab'), tr('bindings.settings_tab'))):
            button = QPushButton(title)
            button.setCheckable(True)
            self.navigation.addButton(button, index)
            navigation.addWidget(button)
        self.navigation.button(0).setChecked(True)
        layout.addLayout(navigation)

        buttons = QHBoxLayout()
        self.add_button = QPushButton(tr('bindings.add'))
        self.delete_button = QPushButton(tr('bindings.delete'))
        for button, callback in (
            (self.add_button, self.add_row),
            (self.delete_button, self.delete_rows),
        ):
            button.clicked.connect(callback)
            buttons.addWidget(button)
        self.enable_checkbox = QCheckBox(tr('bindings.enable'))
        self.enable_checkbox.setToolTip(
            tr('bindings.toggle_hint')
        )
        self.enable_checkbox.toggled.connect(self.toggle_bindings)
        self.toggle_requested.connect(
            self.enable_checkbox.toggle, Qt.ConnectionType.QueuedConnection)
        buttons.addWidget(self.enable_checkbox)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.pages = QStackedWidget()
        self.stratagem_table = BindingTable("stratagem", bindings)
        self.chat_table = BindingTable("chat", bindings)
        for table in (self.stratagem_table, self.chat_table):
            self.pages.addWidget(table)

        self.settings_page = SettingsPage(bindings, cooldown_modifiers)
        self.settings_page.cooldown_upgrades_changed.connect(
            self.manager.set_cooldown_upgrades)
        self.settings_page.emit_cooldown_upgrades()
        self.settings_page.save_requested.connect(self.save)
        self.pages.addWidget(self.settings_page)
        layout.addWidget(self.pages)
        self.navigation.idClicked.connect(self.select_page)

    def select_page(self, index):
        self.pages.setCurrentIndex(index)
        editable = not self.enable_checkbox.isChecked() and index < 2
        self.add_button.setEnabled(editable)
        self.delete_button.setEnabled(editable)

    def set_bindings_editable(self, editable):
        self.stratagem_table.setEnabled(editable)
        self.chat_table.setEnabled(editable)
        self.settings_page.set_bindings_editable(editable)
        self.select_page(self.pages.currentIndex())

    def draft(self):
        bindings = self.stratagem_table.draft() + self.chat_table.draft()
        return bindings + self.settings_page.draft()

    def add_row(self):
        table = self.pages.currentWidget()
        if not isinstance(table, BindingTable):
            return
        value = next(iter(STRATAGEMS)) if table.action == "stratagem" else ""
        table.append_binding(Binding("", table.action, value))
        table.selectRow(table.rowCount() - 1)
        table.scrollToBottom()

    def delete_rows(self):
        table = self.pages.currentWidget()
        if not isinstance(table, BindingTable):
            return
        rows = table.selectionModel().selectedRows()
        if not rows:
            return
        for index in sorted(rows, key=lambda item: item.row(), reverse=True):
            table.removeRow(index.row())

    def toggle_bindings(self, enabled):
        if not enabled:
            self.manager.disable()
            self.hud_overlay.set_cooldown_enabled(False)
            self.hud_overlay.hide()
            self.set_bindings_editable(True)
            return
        try:
            desired = effective_bindings(self.draft())
            self.manager.replace(desired)
            self.hud_overlay.update_bindings(desired)
            self.hud_overlay.set_cooldown_enabled(True)
            self.manager.enable()
            self.hud_overlay.show()
        except Exception as error:
            logger.exception("啟用綁定失敗")
            self.manager.disable()
            self.enable_checkbox.setChecked(False)
            QMessageBox.warning(self, tr('bindings.enable_failed_title'), error_text(error))
            return
        self.set_bindings_editable(False)

    def save(self):
        try:
            save_settings(
                self.draft(), self.settings_page.cooldown_modifiers(),
                language=self.settings_page.language())
        except Exception as error:
            logger.exception("儲存設定失敗")
            QMessageBox.warning(self, tr('bindings.save_failed_title'), error_text(error))
            return

    def closeEvent(self, event):
        self.hud_overlay.close()
        event.accept()
        QApplication.instance().quit()
