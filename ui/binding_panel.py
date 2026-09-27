import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from config.settings import save_settings
from hotkeys.models import Binding
from hotkeys.validation import effective_bindings
from stratagems import STRATAGEMS
from ui.binding_table import BindingTable
from ui.settings_page import SettingsPage
from ui.hud_overlay import HUDOverlay


logger = logging.getLogger(__name__)


class BindingPanel(QWidget):
    toggle_requested = Signal()

    def __init__(self, manager, bindings, load_error="", cooldown_modifiers=None):
        super().__init__()
        self.manager = manager
        self.hud_overlay = HUDOverlay()
        bindings = tuple(bindings)
        self.setWindowTitle("HD2 Undemocratic Tech")
        self.resize(720, 440)
        layout = QVBoxLayout(self)
        navigation = QHBoxLayout()
        self.navigation = QButtonGroup(self)
        for index, title in enumerate(("Stratagem binding", "Chat binding", "Settings")):
            button = QPushButton(title)
            button.setCheckable(True)
            self.navigation.addButton(button, index)
            navigation.addWidget(button)
        self.navigation.button(0).setChecked(True)
        layout.addLayout(navigation)

        buttons = QHBoxLayout()
        self.add_button = QPushButton("增加")
        self.delete_button = QPushButton("刪除")
        for button, callback in (
            (self.add_button, self.add_row),
            (self.delete_button, self.delete_rows),
        ):
            button.clicked.connect(callback)
            buttons.addWidget(button)
        self.enable_checkbox = QCheckBox("啟用 (scrlk 啟用/停用)")
        self.enable_checkbox.setToolTip(
            "按 Scroll Lock 同時啟用／停用快捷鍵、HUD 與預估倒數。\n"
            "倒數依熱鍵觸發時間估算，不確認遊戲是否成功呼叫。"
        )
        self.enable_checkbox.toggled.connect(self.toggle_bindings)
        self.toggle_requested.connect(self.enable_checkbox.toggle, Qt.ConnectionType.QueuedConnection)
        buttons.addWidget(self.enable_checkbox)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.pages = QStackedWidget()
        self.stratagem_table = BindingTable("stratagem", bindings)
        self.chat_table = BindingTable("chat", bindings)
        for table in (self.stratagem_table, self.chat_table):
            self.pages.addWidget(table)

        self.settings_page = SettingsPage(bindings, cooldown_modifiers)
        self.settings_page.cooldown_upgrades_changed.connect(self.manager.set_cooldown_upgrades)
        self.settings_page.emit_cooldown_upgrades()
        self.settings_page.save_requested.connect(self.save)
        self.pages.addWidget(self.settings_page)
        layout.addWidget(self.pages)
        self.navigation.idClicked.connect(self.select_page)

        layout.addWidget(QLabel("「啟用」統一控制快捷鍵、HUD 與預估倒數；停用時清除倒數。Settings 的「儲存」寫入設定檔。"))
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        if load_error:
            self.status.setText(f"設定讀取失敗，暫用預設值：{load_error}")

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
            self.status.setText("請先選取要刪除的列。")
            return
        for index in sorted(rows, key=lambda item: item.row(), reverse=True):
            table.removeRow(index.row())

    def toggle_bindings(self, enabled):
        if not enabled:
            self.manager.disable()
            self.set_bindings_editable(True)
            self.status.setText("已停用快捷鍵與 HUD，並清除倒數。")
            return
        try:
            desired = effective_bindings(self.draft())
            self.manager.replace(desired)
            self.hud_overlay.update_bindings(desired)
            self.hud_overlay.set_cooldown_enabled(True)
            self.manager.enable()
            self.hud_overlay.set_bindings_enabled(True)
            self.hud_overlay.show()
        except Exception as error:
            logger.exception("啟用綁定失敗")
            self.manager.disable()
            self.enable_checkbox.setChecked(False)
            self.status.setText(f"啟用失敗：{error}")
            QMessageBox.warning(self, "啟用失敗", str(error))
            return
        self.set_bindings_editable(False)
        self.status.setText(f"已啟用 {len(desired)} 筆綁定、HUD 與預估倒數；停用後可修改。設定檔未更新。")

    def save(self):
        try:
            save_settings(self.draft(), self.settings_page.cooldown_modifiers())
        except Exception as error:
            logger.exception("儲存設定失敗")
            self.status.setText(f"儲存失敗：{error}")
            QMessageBox.warning(self, "儲存失敗", str(error))
            return
        self.status.setText("已儲存所有分頁設定；目前生效的綁定未變更。")

    def closeEvent(self, event):
        self.hud_overlay.close()
        event.accept()
        QApplication.instance().quit()
