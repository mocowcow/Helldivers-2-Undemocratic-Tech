from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QGroupBox, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from stratagems import STRATAGEMS


SVG_DIRECTORY = Path(__file__).resolve().parent / "stratagems-svg"
TILE_SIZE = 84
COLUMNS = 10


class StratagemPicker(QDialog):
    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.selected_name = current_name
        self.setWindowTitle("選擇 Stratagem")
        available = self.screen().availableGeometry()
        self.resize(min(980, available.width()), min(760, available.height()))
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        content = QWidget()
        groups_layout = QVBoxLayout(content)

        groups = {}
        for name, stratagem in STRATAGEMS.items():
            groups.setdefault(stratagem.category, {}).setdefault(
                stratagem.subcategory, [],
            ).append((name, stratagem))

        for category, subcategories in groups.items():
            group = QGroupBox(category)
            category_layout = QVBoxLayout(group)
            for subcategory, entries in subcategories.items():
                category_layout.addWidget(QLabel(subcategory))
                grid = QGridLayout()
                grid.setAlignment(Qt.AlignmentFlag.AlignLeft)
                grid.setSpacing(6)
                for column in range(COLUMNS):
                    grid.setColumnMinimumWidth(column, TILE_SIZE)
                for index, (name, stratagem) in enumerate(entries):
                    tile = self.make_tile(name, stratagem, name == current_name)
                    grid.addWidget(tile, index // COLUMNS, index % COLUMNS)
                category_layout.addLayout(grid)
            groups_layout.addWidget(group)
        groups_layout.addStretch()
        scroll.setWidget(content)

    def make_tile(self, name, stratagem, selected):
        tile = QPushButton()
        tile.setFixedSize(TILE_SIZE, TILE_SIZE)
        tile.setCheckable(True)
        tile.setChecked(selected)
        tile.setAutoDefault(False)
        tile.setToolTip(name)
        tile.setAccessibleName(name)
        tile.setStyleSheet(
            "QPushButton { background: #252525; color: white; "
            "border: 2px solid #666; border-radius: 4px; }"
            "QPushButton:hover, QPushButton:focus { border-color: #ffe45c; }"
            "QPushButton:checked { border-color: #ffe45c; background: #454025; }"
        )
        tile_layout = QVBoxLayout(tile)
        tile_layout.setContentsMargins(6, 6, 6, 6)
        visual = None
        if stratagem.svg_name:
            svg_path = SVG_DIRECTORY / stratagem.svg_name
            if svg_path.is_file():
                svg = QSvgWidget(str(svg_path), tile)
                if svg.renderer().isValid():
                    visual = svg
                else:
                    svg.deleteLater()
        if visual is None:
            visual = QLabel(name, tile)
            visual.setWordWrap(True)
            visual.setAlignment(Qt.AlignmentFlag.AlignCenter)
            visual.setStyleSheet("color: white; background: transparent; font-size: 10px;")
        visual.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        tile_layout.addWidget(visual)
        tile.clicked.connect(lambda checked=False: self.choose(name))
        return tile

    def choose(self, name):
        self.selected_name = name
        self.accept()


class StratagemButton(QPushButton):
    changed = Signal()

    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.setToolTip("點擊選擇 Stratagem")
        self.clicked.connect(self.choose)

    def choose(self):
        picker = StratagemPicker(self.name, self.window())
        try:
            if picker.exec() == QDialog.DialogCode.Accepted:
                if picker.selected_name != self.name:
                    self.name = picker.selected_name
                    self.setText(self.name)
                    self.changed.emit()
        finally:
            picker.deleteLater()
