from PySide6.QtCore import QEvent, QItemSelectionModel, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QHeaderView, QLineEdit, QTableWidget, QTableWidgetItem,
)

from hotkeys.models import Binding
from ui.key_input import KeyInput
from ui.stratagem_picker import StratagemButton


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
            field = StratagemButton(binding.value)
            field.changed.connect(self.changed.emit)
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
                self.cellWidget(row, 0).name
                if self.action == "stratagem" else self.cellWidget(row, 0).text(),
            )
            for row in range(self.rowCount())
        )
