from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from resources import resource_path
from stratagems import STRATAGEMS


HUD_SCALE = 0.75


class HUDOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stratagem HUD")
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.drag_offset = None
        self.moved_by_user = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setStyleSheet("background: #252525; color: white;")
        font = self.font()
        if font.pointSizeF() > 0:
            font.setPointSizeF(font.pointSizeF() * HUD_SCALE)
        else:
            font.setPixelSize(max(1, round(font.pixelSize() * HUD_SCALE)))
        self.setFont(font)
        self.row = QHBoxLayout(self)
        margin = round(8 * HUD_SCALE)
        self.row.setContentsMargins(margin, margin, margin, margin)
        self.row.setSpacing(round(6 * HUD_SCALE))

    def update_bindings(self, bindings):
        while self.row.count():
            widget = self.row.takeAt(0).widget()
            widget.hide()
            widget.deleteLater()
        for binding in bindings:
            if binding.action != "stratagem" or not binding.key:
                continue
            stratagem = STRATAGEMS[binding.value]
            item = QWidget(self)
            item.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            column = QVBoxLayout(item)
            column.setContentsMargins(0, 0, 0, 0)
            column.setSpacing(round(4 * HUD_SCALE))
            key_label = QLabel(binding.key.upper(), item)
            key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            column.addWidget(key_label)
            visual = None
            if stratagem.svg_name:
                path = resource_path("stratagems-svg") / stratagem.svg_name
                if path.is_file():
                    svg = QSvgWidget(str(path), item)
                    if svg.renderer().isValid():
                        visual = svg
                    else:
                        svg.hide()
                        svg.deleteLater()
            if visual is None:
                visual = QLabel(stratagem.name, item)
                visual.setWordWrap(True)
                visual.setAlignment(Qt.AlignmentFlag.AlignCenter)
                visual.setStyleSheet(f"font-size: {round(9 * HUD_SCALE)}px;")
            icon_size = round(48 * HUD_SCALE)
            visual.setFixedSize(icon_size, icon_size)
            column.addWidget(visual, 0, Qt.AlignmentFlag.AlignHCenter)
            self.row.addWidget(item)
        if not self.row.count():
            placeholder = QLabel("尚未綁定 Stratagem", self)
            placeholder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.row.addWidget(placeholder)
        self.row.activate()
        self.adjustSize()
        self.position_hud()

    def position_hud(self):
        if self.moved_by_user:
            return
        area = self.screen().geometry()
        self.move(
            area.x(),
            area.y() + area.height() - self.height(),
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.position_hud()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            self.moved_by_user = True
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def hideEvent(self, event):
        self.drag_offset = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().hideEvent(event)
