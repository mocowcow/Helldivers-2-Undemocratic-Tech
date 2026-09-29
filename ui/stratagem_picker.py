from localization import tr
from PySide6.QtCore import Qt, Signal, QSize, QRect
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QGroupBox, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from stratagems import STRATAGEMS
from resources import resource_path
from ui.labels import category_label, stratagem_label


SVG_DIRECTORY = resource_path("stratagems-svg")
TILE_SIZE = 84
COLUMNS = 10


class StratagemPicker(QDialog):
    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.selected_id = current_name
        self.setWindowTitle(tr('picker.title'))
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
            group = QGroupBox(category_label(category))
            category_layout = QVBoxLayout(group)
            for subcategory, entries in subcategories.items():
                category_layout.addWidget(QLabel(category_label(subcategory)))
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
        tile.setToolTip(stratagem_label(name))
        tile.setAccessibleName(stratagem_label(name))
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
            visual = QLabel(stratagem_label(name), tile)
            visual.setWordWrap(True)
            visual.setAlignment(Qt.AlignmentFlag.AlignCenter)
            visual.setStyleSheet("color: white; background: transparent; font-size: 10px;")
        visual.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        tile_layout.addWidget(visual)
        tile.clicked.connect(lambda checked=False: self.choose(name))
        return tile

    def choose(self, name):
        self.selected_id = name
        self.accept()


class StratagemButton(QPushButton):
    changed = Signal()

    def __init__(self, name):
        super().__init__()
        self.stratagem_id = name
        self.setIconSize(QSize(28, 28))
        self.update_visual()
        self.setToolTip(tr('picker.button_hint'))
        self.clicked.connect(self.choose)

    def update_visual(self):
        self.setText(stratagem_label(self.stratagem_id))
        icon = QIcon()
        stratagem = STRATAGEMS.get(self.stratagem_id)
        if stratagem is not None and stratagem.svg_name:
            path = SVG_DIRECTORY / stratagem.svg_name
            if path.is_file():
                source = QIcon(str(path))
                size = self.iconSize()
                ratio = self.devicePixelRatioF()
                background = QPixmap(
                    round(size.width() * ratio), round(size.height() * ratio),
                )
                background.setDevicePixelRatio(ratio)
                background.fill(Qt.GlobalColor.black)
                painter = QPainter(background)
                try:
                    source.paint(painter, QRect(0, 0, size.width(), size.height()))
                finally:
                    painter.end()
                icon = QIcon(background)
                icon.addPixmap(background, QIcon.Mode.Disabled)
        self.setIcon(icon)

    def choose(self):
        picker = StratagemPicker(self.stratagem_id, self.window())
        try:
            if picker.exec() == QDialog.DialogCode.Accepted:
                if picker.selected_id != self.stratagem_id:
                    self.stratagem_id = picker.selected_id
                    self.update_visual()
                    self.changed.emit()
        finally:
            picker.deleteLater()
