"""
SecureSteg — widgets.py
Reusable custom widgets shared across views.
"""

from PyQt5.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap

import theme


# =====================================================
# Drop Zone — click or drag & drop an image
# =====================================================

class DropZone(QFrame):

    fileSelected = pyqtSignal(str)

    def __init__(self, icon="\u25a6", text="Drop an image or click to browse",
                 sub="PNG · JPG · WebP · BMP"):
        super().__init__()
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("hasimage", "false")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 26, 16, 26)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(4)

        self.icon_label = QLabel(icon)
        self.icon_label.setObjectName("DropIcon")
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.text_label = QLabel(text)
        self.text_label.setObjectName("DropText")
        self.text_label.setAlignment(Qt.AlignCenter)

        self.sub_label = QLabel(sub)
        self.sub_label.setObjectName("DropSub")
        self.sub_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addWidget(self.sub_label)
        self.setLayout(layout)

    def mark_has_image(self):
        self.setProperty("hasimage", "true")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select an image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            self.fileSelected.emit(path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path:
                self.fileSelected.emit(path)


# =====================================================
# Meter bar — capacity bar / strength bar / progress bar / suspicion meter
# =====================================================

class MeterBar(QWidget):

    def __init__(self, height=6):
        super().__init__()
        self._pct = 0
        self._color = QColor(theme.TEXT_3)
        self.setFixedHeight(height)

    def set_value(self, pct, color_hex=None):
        self._pct = max(0, min(100, pct))
        if color_hex:
            self._color = QColor(color_hex)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bg_rect = QRectF(0, 0, self.width(), self.height())
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(theme.RAISED))
        painter.drawRoundedRect(bg_rect, self.height() / 2, self.height() / 2)

        fill_w = self.width() * (self._pct / 100)
        if fill_w > 0:
            fill_rect = QRectF(0, 0, fill_w, self.height())
            painter.setBrush(self._color)
            painter.drawRoundedRect(fill_rect, self.height() / 2, self.height() / 2)


class MeterRow(QWidget):
    """Label + MeterBar + percentage text, stacked."""

    def __init__(self, label_text, height=6):
        super().__init__()
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        self.label = QLabel(label_text)
        self.label.setObjectName("FieldLabel")

        self.bar = MeterBar(height=height)

        self.value_label = QLabel("0%")
        self.value_label.setStyleSheet(f"color:{theme.TEXT_3}; font-size:11px;")

        outer.addWidget(self.label)
        outer.addWidget(self.bar)
        outer.addWidget(self.value_label)
        self.setLayout(outer)

    def set_value(self, pct, color_hex, text=None):
        self.bar.set_value(pct, color_hex)
        self.value_label.setText(text if text else f"{pct}%")
        self.value_label.setStyleSheet(f"color:{color_hex}; font-size:11px;")


# =====================================================
# Stat display — value + label
# =====================================================

class StatBox(QWidget):

    def __init__(self, value="—", label=""):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.value_label = QLabel(value)
        self.value_label.setObjectName("StatVal")

        self.text_label = QLabel(label)
        self.text_label.setObjectName("StatLbl")

        layout.addWidget(self.value_label)
        layout.addWidget(self.text_label)
        self.setLayout(layout)

    def set_value(self, value):
        self.value_label.setText(str(value))


# =====================================================
# Technique button group (single-select toggle row)
# =====================================================

class TechButtonGroup(QWidget):

    changed = pyqtSignal(str)

    def __init__(self, options):
        """options: list of (key, label) tuples"""
        super().__init__()
        self.options = options
        self.buttons = {}
        self.current = options[0][0]

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)

        for key, label in options:
            btn = QPushButton(label)
            btn.setObjectName("TechBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("active", "true" if key == self.current else "false")
            btn.clicked.connect(lambda checked, k=key: self.select(k))
            layout.addWidget(btn)
            self.buttons[key] = btn

        layout.addStretch()
        self.setLayout(layout)

    def select(self, key):
        self.current = key
        for k, btn in self.buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.changed.emit(key)


# =====================================================
# Histogram canvas — overlaid bar chart for two images
# =====================================================

class HistogramCanvas(QWidget):

    def __init__(self, color_a="rgba(229,72,77,0.65)", color_b="rgba(215,220,229,0.45)"):
        super().__init__()
        self.hist_a = None
        self.hist_b = None
        self.color_a = QColor(229, 72, 77, 165)
        self.color_b = QColor(215, 220, 229, 115)
        self.setMinimumHeight(120)
        self.setStyleSheet(f"background:{theme.RAISED}; border-radius:6px;")

    def set_data(self, hist_a, hist_b):
        self.hist_a = hist_a
        self.hist_b = hist_b
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        if self.hist_a is None or self.hist_b is None:
            return

        max_val = max(self.hist_a.max(), self.hist_b.max(), 1)
        bar_w = w / 256

        painter.setPen(Qt.NoPen)
        for i in range(256):
            bh = (self.hist_a[i] / max_val) * h
            painter.setBrush(self.color_a)
            painter.drawRect(int(i * bar_w), int(h - bh), max(1, int(bar_w) + 1), int(bh))

        for i in range(256):
            bh = (self.hist_b[i] / max_val) * h
            painter.setBrush(self.color_b)
            painter.drawRect(int(i * bar_w), int(h - bh), max(1, int(bar_w) + 1), int(bh))


# =====================================================
# Panel — bordered card container
# =====================================================

class Panel(QFrame):

    def __init__(self):
        super().__init__()
        self.setObjectName("Panel")
        self.layout_ = QVBoxLayout()
        self.layout_.setContentsMargins(20, 18, 20, 18)
        self.layout_.setSpacing(12)
        self.setLayout(self.layout_)

    def add(self, widget_or_layout):
        if isinstance(widget_or_layout, QWidget):
            self.layout_.addWidget(widget_or_layout)
        else:
            self.layout_.addLayout(widget_or_layout)


def panel_head(step_num, title_text):
    row = QHBoxLayout()
    row.setSpacing(10)

    step = QLabel(str(step_num))
    step.setObjectName("PanelStep")
    step.setFixedSize(22, 22)
    step.setAlignment(Qt.AlignCenter)

    title = QLabel(title_text)
    title.setObjectName("PanelHead")

    row.addWidget(step)
    row.addWidget(title)
    row.addStretch()
    return row


def view_header(eyebrow, title_text, subtitle):
    box = QVBoxLayout()
    box.setSpacing(6)

    e = QLabel(eyebrow)
    e.setObjectName("ViewEyebrow")

    t = QLabel(title_text)
    t.setObjectName("ViewTitle")

    s = QLabel(subtitle)
    s.setObjectName("ViewSub")
    s.setWordWrap(True)

    box.addWidget(e)
    box.addWidget(t)
    box.addWidget(s)
    return box


def numpy_to_pixmap(arr):
    """Convert an HxWx3 or HxWx4 uint8 numpy array to a QPixmap."""
    from PyQt5.QtGui import QImage
    import numpy as np

    arr = np.ascontiguousarray(arr)
    h, w = arr.shape[0], arr.shape[1]

    if arr.ndim == 2:
        qimg = QImage(arr.data, w, h, w, QImage.Format_Grayscale8)
    elif arr.shape[2] == 3:
        qimg = QImage(arr.data, w, h, w * 3, QImage.Format_RGB888)
    else:
        qimg = QImage(arr.data, w, h, w * 4, QImage.Format_RGBA8888)

    return QPixmap.fromImage(qimg.copy())
