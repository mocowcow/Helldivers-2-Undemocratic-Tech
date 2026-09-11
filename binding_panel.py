from PySide6.QtCore import QEvent, QItemSelectionModel, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QButtonGroup, QComboBox, QFormLayout,
    QHeaderView, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton,
    QStackedWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from bindings import Binding
from key_input import KeyInput
from settings import SETTINGS_PATH, effective_bindings, save_bindings
from stratagems import STRATAGEMS


class BindingTable(QTableWidget):
    changed = Signal()

    def __init__(self, action, bindings):
        super().__init__(0, 2)
        self.action = action
        self.setHorizontalHeaderLabels([
            "Stratagem" if action == "stratagem" else "Chat message", "快捷鍵",
        ])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        for binding in bindings:
            if binding.action == action:
                self.append_binding(binding)
        if self.rowCount():
            self.selectRow(0)

    def append_binding(self, binding):
        row = self.rowCount()
        self.insertRow(row)
        if self.action == "stratagem":
            field = QComboBox()
            for name in STRATAGEMS:
                field.addItem(name, name)
            field.setCurrentIndex(field.findData(binding.value))
            field.currentIndexChanged.connect(lambda _: self.changed.emit())
        else:
            field = QLineEdit(binding.value)
            field.textChanged.connect(lambda _: self.changed.emit())
        key = KeyInput(binding.key)
        key.changed.connect(self.changed.emit)
        for column, widget in enumerate((field, key)):
            self.setItem(row, column, QTableWidgetItem())
            self.setCellWidget(row, column, widget)
            widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.FocusIn:
            for row in range(self.rowCount()):
                if watched in (self.cellWidget(row, 0), self.cellWidget(row, 1)):
                    # Select without moving the current index or re-entering focus handling.
                    self.selectionModel().select(
                        self.model().index(row, 0),
                        QItemSelectionModel.SelectionFlag.ClearAndSelect
                        | QItemSelectionModel.SelectionFlag.Rows,
                    )
                    break
        return super().eventFilter(watched, event)

    def draft(self):
        return tuple(
            Binding(
                self.cellWidget(row, 1).key, self.action,
                self.cellWidget(row, 0).currentData()
                if self.action == "stratagem" else self.cellWidget(row, 0).text(),
            )
            for row in range(self.rowCount())
        )


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

        settings_page = QWidget()
        form = QFormLayout(settings_page)
        path = QLineEdit(str(SETTINGS_PATH))
        path.setReadOnly(True)
        path_row = QHBoxLayout()
        path_row.addWidget(path, 1)
        open_path_button = QPushButton("開啟儲存路徑")
        open_path_button.clicked.connect(self.open_settings_folder)
        path_row.addWidget(open_path_button)
        save_button = QPushButton("儲存")
        save_button.clicked.connect(self.save)
        path_row.addWidget(save_button)
        form.addRow("設定檔儲存位置", path_row)
        current_key = next((b.key for b in bindings if b.action == "open_chat"), "")
        self.open_chat_key = KeyInput(current_key)
        self.open_chat_key.changed.connect(self.mark_dirty)
        chat_key_row = QHBoxLayout()
        chat_key_row.addWidget(self.open_chat_key)
        clear_key = QPushButton("清除")
        clear_key.clicked.connect(self.open_chat_key.clear_binding)
        chat_key_row.addWidget(clear_key)
        form.addRow("開啟聊天視窗快捷鍵", chat_key_row)
        self.pages.addWidget(settings_page)
        layout.addWidget(self.pages)
        self.navigation.idClicked.connect(self.select_page)

        layout.addWidget(QLabel("「套用」更新所有分頁的綁定；Settings 的「儲存」寫入設定檔。"))
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        if load_error:
            self.status.setText(f"設定讀取失敗，暫用預設值：{load_error}")

    def open_settings_folder(self):
        folder = SETTINGS_PATH.parent
        try:
            folder.mkdir(parents=True, exist_ok=True)
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder))):
                raise OSError("無法開啟設定檔資料夾。")
        except OSError as error:
            QMessageBox.warning(self, "開啟儲存路徑失敗", str(error))

    def select_page(self, index):
        self.pages.setCurrentIndex(index)
        self.add_button.setEnabled(index < 2)
        self.delete_button.setEnabled(index < 2)

    def mark_dirty(self, *args):
        self.status.setText("內容已修改；請按「套用」更新綁定，按「儲存」保存設定。")

    def draft(self):
        bindings = self.stratagem_table.draft() + self.chat_table.draft()
        key = self.open_chat_key.key
        if key:
            bindings += (Binding(key, "open_chat"),)
        return bindings

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
