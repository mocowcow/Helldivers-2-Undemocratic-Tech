from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QHeaderView, QHBoxLayout,
    QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from bindings import Binding
from settings import BINDING_KEYS, SETTINGS_PATH, effective_bindings, save_bindings
from stratagems import STRATAGEMS


class BindingPanel(QWidget):
    def __init__(self, manager, bindings, load_error=""):
        super().__init__()
        self.manager = manager
        self.setWindowTitle("HD2 Undemocratic Tech")
        self.resize(720, 440)
        layout = QVBoxLayout(self)
        buttons = QHBoxLayout()
        for title, callback in (
            ("增加", self.add_row), ("刪除", self.delete_rows), ("套用", self.apply),
        ):
            button = QPushButton(title)
            button.clicked.connect(callback)
            buttons.addWidget(button)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Stratagem", "快捷鍵"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)
        note = QLabel("未分配給戰略配備時：F12 發送 sorry；\\ 開啟聊天輸入框。")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        for binding in bindings:
            self.append_row(binding)
        if self.table.rowCount():
            self.table.selectRow(0)
        self.status.setText(
            f"設定讀取失敗，暫用預設值：{load_error}"
            if load_error else f"按「套用」才更新並儲存至：{SETTINGS_PATH}"
        )

    def append_row(self, binding):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for column, values, current in (
            (0, STRATAGEMS, binding.value),
            (1, BINDING_KEYS, binding.key),
        ):
            self.table.setItem(row, column, QTableWidgetItem())
            combo = QComboBox()
            for value in values:
                combo.addItem(value if column == 0 else value.upper(), value)
            combo.setCurrentIndex(combo.findData(current))
            combo.currentIndexChanged.connect(self.mark_dirty)
            combo.activated.connect(lambda index, widget=combo: self.select_widget_row(widget))
            self.table.setCellWidget(row, column, combo)

    def select_widget_row(self, widget):
        for row in range(self.table.rowCount()):
            if widget in (self.table.cellWidget(row, 0), self.table.cellWidget(row, 1)):
                self.table.selectRow(row)
                return

    def mark_dirty(self, *args):
        self.status.setText("尚未套用；目前快捷鍵與已儲存設定保持不變。")

    def add_row(self):
        used = {
            self.table.cellWidget(row, 1).currentData()
            for row in range(self.table.rowCount())
        }
        if self.table.rowCount() >= len(BINDING_KEYS):
            self.status.setText("最多可設定 13 筆綁定。")
            return
        key = next(key for key in BINDING_KEYS if key not in used)
        self.append_row(Binding(key, "stratagem", next(iter(STRATAGEMS))))
        self.table.selectRow(self.table.rowCount() - 1)
        self.table.scrollToBottom()
        self.mark_dirty()

    def delete_rows(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self.status.setText("請先選取要刪除的列。")
            return
        for index in sorted(rows, key=lambda item: item.row(), reverse=True):
            self.table.removeRow(index.row())
        self.mark_dirty()

    def apply(self):
        draft = tuple(
            Binding(
                self.table.cellWidget(row, 1).currentData(),
                "stratagem", self.table.cellWidget(row, 0).currentData(),
            )
            for row in range(self.table.rowCount())
        )
        previous = self.manager.bindings
        try:
            desired = effective_bindings(draft)
            self.manager.replace(desired)
            try:
                save_bindings(draft)
            except Exception:
                self.manager.replace(previous)
                raise
        except Exception as error:
            self.status.setText(f"套用失敗：{error}")
            QMessageBox.warning(self, "套用失敗", str(error))
            return
        self.status.setText(f"已套用並儲存 {len(draft)} 筆綁定。")

    def closeEvent(self, event):
        event.accept()
        QApplication.instance().quit()
