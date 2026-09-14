import math
import time

from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QIcon
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget, QToolButton

from resources import resource_path
from stratagems import STRATAGEMS


HUD_SCALE = 0.75


class HUDOverlay(QWidget):
    cooldown_requested = Signal(str, float)

    def __init__(self):
        super().__init__()
        self.cooldown_enabled = False
        self.enabled_since = 0.0
        self.deadlines = {}
        self.countdown_labels = {}
        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(100)
        self.countdown_timer.timeout.connect(self.refresh_countdowns)
        self.cooldown_requested.connect(self.start_cooldown, Qt.ConnectionType.QueuedConnection)
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
        self.locked = False
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
        self.lock_button = QToolButton(self)
        self.lock_button.setCheckable(True)
        self.lock_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lock_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lock_button.setIconSize(QSize(24, 24))
        self.lock_button.setFixedSize(30, 30)
        self.lock_button.toggled.connect(self.set_locked)
        self.row.addWidget(self.lock_button, 0, Qt.AlignmentFlag.AlignVCenter)
        self.set_locked(True)

    def set_locked(self, locked):
        self.locked = locked
        self.drag_offset = None
        filename = "lock_on.svg" if locked else "lock_off.svg"
        self.lock_button.setIcon(QIcon(str(resource_path("ui") / filename)))
        self.lock_button.setToolTip("已鎖定，點擊解鎖" if locked else "已解鎖，點擊鎖定")
        self.lock_button.setAccessibleName("解鎖 HUD" if locked else "鎖定 HUD")
        self.setCursor(Qt.CursorShape.ArrowCursor if locked else Qt.CursorShape.OpenHandCursor)

    def update_bindings(self, bindings):
        self.countdown_labels.clear()
        while self.row.count() > 1:
            widget = self.row.takeAt(1).widget()
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
            countdown = QLabel(visual)
            countdown.setGeometry(0, (icon_size - 20) // 2, icon_size, 20)
            countdown.setAlignment(Qt.AlignmentFlag.AlignCenter)
            countdown.setStyleSheet(
                "background-color: rgba(0, 0, 0, 150); color: white; "
                "font-size: 12px; font-weight: bold;"
            )
            countdown.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            countdown.hide()
            self.countdown_labels.setdefault(binding.value, []).append(countdown)
            column.addWidget(visual, 0, Qt.AlignmentFlag.AlignHCenter)
            self.row.addWidget(item)
        if self.row.count() == 1:
            placeholder = QLabel("尚未綁定 Stratagem", self)
            placeholder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.row.addWidget(placeholder)
        self.row.activate()
        self.adjustSize()
        self.position_hud()
        self.refresh_countdowns()

    def set_cooldown_enabled(self, enabled, clear=True):
        if not enabled and clear:
            self.clear_countdowns()
        if enabled == self.cooldown_enabled:
            return
        self.cooldown_enabled = enabled
        if enabled:
            self.enabled_since = time.monotonic()

    def clear_countdowns(self):
        self.countdown_timer.stop()
        self.deadlines.clear()
        for labels in self.countdown_labels.values():
            for label in labels:
                label.clear()
                label.hide()

    @Slot(str, float)
    def start_cooldown(self, name, triggered_at):
        # Discard queued triggers from before the latest enabling of both options.
        if not self.cooldown_enabled or triggered_at < self.enabled_since:
            return
        stratagem = STRATAGEMS.get(name)
        if stratagem is None or stratagem.cooldown <= 0:
            return
        self.deadlines[name] = triggered_at + stratagem.cooldown
        self.refresh_countdowns()
        if self.deadlines:
            self.countdown_timer.start()

    def refresh_countdowns(self):
        now = time.monotonic()
        for name, deadline in tuple(self.deadlines.items()):
            if deadline <= now:
                del self.deadlines[name]
        for name, labels in self.countdown_labels.items():
            remaining = max(0, math.ceil(self.deadlines.get(name, now) - now))
            for label in labels:
                if remaining:
                    minutes, seconds = divmod(remaining, 60)
                    label.setText(f"{minutes}:{seconds:02d}")
                    label.show()
                    label.raise_()
                else:
                    label.clear()
                    label.hide()
        if not self.deadlines:
            self.countdown_timer.stop()

    def position_hud(self, reset=False):
        if reset:
            self.moved_by_user = False
            self.drag_offset = None
        elif self.locked or self.moved_by_user:
            return
        area = self.screen().geometry()
        self.move(
            area.x(),
            area.y() + area.height() - self.height(),
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.position_hud(reset=True)

    def mousePressEvent(self, event):
        if not self.locked and event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.locked and self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            self.moved_by_user = True
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = None
            self.setCursor(Qt.CursorShape.ArrowCursor if self.locked else Qt.CursorShape.OpenHandCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def hideEvent(self, event):
        self.drag_offset = None
        self.setCursor(Qt.CursorShape.ArrowCursor if self.locked else Qt.CursorShape.OpenHandCursor)
        super().hideEvent(event)
