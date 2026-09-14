import logging

from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from config.settings import save_bindings
from hotkeys.models import Binding
from hotkeys.validation import effective_bindings
from stratagems import STRATAGEMS
from ui.binding_table import BindingTable
from ui.settings_page import SettingsPage
from ui.hud_overlay import HUDOverlay


logger = logging.getLogger(__name__)


class BindingPanel(QWidget):
    def __init__(self, manager, bindings, load_error=""):
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
        self.enable_checkbox = QCheckBox("啟用")
        self.enable_checkbox.toggled.connect(self.toggle_bindings)
        buttons.addWidget(self.enable_checkbox)
        self.hud_overlay_checkbox = QCheckBox("HUD overlay")
        self.hud_overlay_checkbox.toggled.connect(self.toggle_hud_overlay)
        buttons.addWidget(self.hud_overlay_checkbox)
        self.cooldown_checkbox = QCheckBox("預估cd")
        self.cooldown_checkbox.setToolTip("依熱鍵觸發時間預估冷卻，不確認遊戲是否成功呼叫。")
        self.cooldown_checkbox.toggled.connect(self.update_cooldown_enabled)
        buttons.addWidget(self.cooldown_checkbox)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.pages = QStackedWidget()
        self.stratagem_table = BindingTable("stratagem", bindings)
        self.chat_table = BindingTable("chat", bindings)
        for table in (self.stratagem_table, self.chat_table):
            self.pages.addWidget(table)
        self.stratagem_table.changed.connect(self.refresh_hud_overlay)

        self.settings_page = SettingsPage(bindings)
        self.settings_page.save_requested.connect(self.save)
        self.pages.addWidget(self.settings_page)
        layout.addWidget(self.pages)
        self.navigation.idClicked.connect(self.select_page)

        layout.addWidget(QLabel("勾選「啟用」綁定快捷鍵，取消勾選解除綁定；Settings 的「儲存」寫入設定檔。"))
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        if load_error:
            self.status.setText(f"設定讀取失敗，暫用預設值：{load_error}")

    def toggle_hud_overlay(self, enabled):
        logger.info("HUD 顯示狀態 enabled=%s", enabled)
        self.update_cooldown_enabled()
        if enabled:
            self.hud_overlay.update_bindings(self.stratagem_table.draft())
            self.hud_overlay.show()
        else:
            self.hud_overlay.hide()

    def update_cooldown_enabled(self, *args):
        self.hud_overlay.set_cooldown_enabled(
            self.hud_overlay_checkbox.isChecked() and self.cooldown_checkbox.isChecked(),
            clear=not self.cooldown_checkbox.isChecked(),
        )

    def select_page(self, index):
        self.pages.setCurrentIndex(index)
        editable = not self.enable_checkbox.isChecked() and index < 2
        self.add_button.setEnabled(editable)
        self.delete_button.setEnabled(editable)

    def refresh_hud_overlay(self):
        if self.hud_overlay_checkbox.isChecked():
            self.hud_overlay.update_bindings(self.stratagem_table.draft())

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
        self.refresh_hud_overlay()

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
        self.refresh_hud_overlay()

    def toggle_bindings(self, enabled):
        if not enabled:
            self.manager.disable()
            self.set_bindings_editable(True)
            self.status.setText("已解除快捷鍵綁定。")
            return
        try:
            desired = effective_bindings(self.draft())
            self.manager.replace(desired)
            self.manager.enable()
        except Exception as error:
            logger.exception("啟用綁定失敗")
            self.manager.disable()
            self.enable_checkbox.setChecked(False)
            self.status.setText(f"啟用失敗：{error}")
            QMessageBox.warning(self, "啟用失敗", str(error))
            return
        self.set_bindings_editable(False)
        self.status.setText(f"已啟用 {len(desired)} 筆綁定；取消勾選後可修改。設定檔未更新。")

    def save(self):
        try:
            save_bindings(self.draft())
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
