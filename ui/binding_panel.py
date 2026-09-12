from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from config.settings import save_bindings
from hotkeys.models import Binding
from hotkeys.validation import effective_bindings
from stratagems import STRATAGEMS
from ui.binding_table import BindingTable
from ui.settings_page import SettingsPage


class BindingPanel(QWidget):
    def __init__(self, manager, bindings, load_error=""):
        super().__init__()
        self.manager = manager
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
        apply_button = QPushButton("套用")
        for button, callback in (
            (self.add_button, self.add_row),
            (self.delete_button, self.delete_rows),
            (apply_button, self.apply),
        ):
            button.clicked.connect(callback)
            buttons.addWidget(button)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.pages = QStackedWidget()
        self.stratagem_table = BindingTable("stratagem", bindings)
        self.chat_table = BindingTable("chat", bindings)
        for table in (self.stratagem_table, self.chat_table):
            self.pages.addWidget(table)
            table.changed.connect(self.mark_dirty)

        self.settings_page = SettingsPage(bindings)
        self.settings_page.changed.connect(self.mark_dirty)
        self.settings_page.save_requested.connect(self.save)
        self.pages.addWidget(self.settings_page)
        layout.addWidget(self.pages)
        self.navigation.idClicked.connect(self.select_page)

        layout.addWidget(QLabel("「套用」更新所有分頁的綁定；Settings 的「儲存」寫入設定檔。"))
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        if load_error:
            self.status.setText(f"設定讀取失敗，暫用預設值：{load_error}")

    def select_page(self, index):
        self.pages.setCurrentIndex(index)
        self.add_button.setEnabled(index < 2)
        self.delete_button.setEnabled(index < 2)

    def mark_dirty(self, *args):
        self.status.setText("內容已修改；請按「套用」更新綁定，按「儲存」保存設定。")

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
        self.mark_dirty()

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
        self.mark_dirty()

    def apply(self):
        try:
            desired = effective_bindings(self.draft())
            self.manager.replace(desired)
        except Exception as error:
            self.status.setText(f"套用失敗：{error}")
            QMessageBox.warning(self, "套用失敗", str(error))
            return
        self.status.setText(f"已套用 {len(desired)} 筆綁定；設定檔未更新。")

    def save(self):
        try:
            save_bindings(self.draft())
        except Exception as error:
            self.status.setText(f"儲存失敗：{error}")
            QMessageBox.warning(self, "儲存失敗", str(error))
            return
        self.status.setText("已儲存所有分頁設定；目前生效的綁定未變更。")

    def closeEvent(self, event):
        event.accept()
        QApplication.instance().quit()
