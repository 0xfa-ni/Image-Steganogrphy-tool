"""
SecureSteg — main.py
Main window: sidebar navigation wiring all views together, and the app entry point.
"""

import sys
import os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QColor

import theme
from views import (
    EncodeView, DecodeView, ScanView, PSNRView, BinaryView,
    HistogramView, SteganalysisView, BitplaneView, HistoryView, LearnView
)

NAV_GROUPS = [
    ("Workspace", [
        ("encode", "01", "Encode"),
        ("decode", "02", "Decode"),
        ("scan", "03", "Scan"),
    ]),
    ("Tools", [
        ("psnr", "04", "PSNR analysis"),
        ("binary", "05", "Binary visualizer"),
        ("histogram", "06", "Histogram viewer"),
        ("steganalysis", "07", "Steganalysis"),
        ("bitplane", "08", "Bit plane viewer"),
        ("history", "09", "History"),
    ]),
    ("Reference", [
        ("learn", "10", "Learn"),
    ]),
]


def resource_path(filename):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecureSteg — Image Steganography Lab")
        self.resize(1180, 780)

        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central = QWidget()
        for w in (central,):
            palette = w.palette()
            palette.setColor(QPalette.Window, QColor(theme.BG))
            w.setAutoFillBackground(True)
            w.setPalette(palette)

        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---------------- Sidebar ----------------
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(248)
        side_layout = QVBoxLayout()
        side_layout.setContentsMargins(18, 26, 18, 18)
        side_layout.setSpacing(0)

        brand_row = QHBoxLayout()
        brand_mark = QLabel("::")
        brand_mark.setObjectName("BrandMark")
        brand_text_col = QVBoxLayout()
        brand_text_col.setSpacing(0)
        brand_name = QLabel("SecureSteg")
        brand_name.setObjectName("BrandName")
        brand_tag = QLabel("image steganography lab")
        brand_tag.setObjectName("BrandTag")
        brand_text_col.addWidget(brand_name)
        brand_text_col.addWidget(brand_tag)
        brand_row.addWidget(brand_mark)
        brand_row.addLayout(brand_text_col)
        brand_row.addStretch()

        brand_wrap = QWidget()
        brand_wrap.setLayout(brand_row)
        side_layout.addWidget(brand_wrap)
        side_layout.addSpacing(24)

        self.nav_buttons = {}

        for group_name, items in NAV_GROUPS:
            label = QLabel(group_name.upper())
            label.setObjectName("NavLabel")
            side_layout.addWidget(label)
            side_layout.addSpacing(4)

            for key, num, text in items:
                btn = QPushButton(f"  {num}   {text}")
                btn.setObjectName("NavBtn")
                btn.setCursor(Qt.PointingHandCursor)
                btn.setProperty("active", "false")
                btn.clicked.connect(lambda checked, k=key: self.switch_view(k))
                side_layout.addWidget(btn)
                self.nav_buttons[key] = btn

            side_layout.addSpacing(20)

        side_layout.addStretch()

        foot = QLabel("\u25cf  Runs 100% on your computer\nno server, no upload")
        foot.setObjectName("SidebarFoot")
        foot.setWordWrap(True)
        side_layout.addWidget(foot)

        sidebar.setLayout(side_layout)
        root.addWidget(sidebar)

        # ---------------- Main content ----------------
        self.stack = QStackedWidget()
        stack_palette = self.stack.palette()
        stack_palette.setColor(QPalette.Window, QColor(theme.BG))
        self.stack.setAutoFillBackground(True)
        self.stack.setPalette(stack_palette)

        self.encode_view = EncodeView(
            on_message_changed=self._sync_binary_view,
            on_view_binary=self._go_view_binary,
            on_view_psnr=lambda: self.switch_view("psnr"),
            on_view_histogram=lambda: self.switch_view("histogram"),
        )
        self.decode_view = DecodeView()
        self.scan_view = ScanView()
        self.psnr_view = PSNRView()
        self.binary_view = BinaryView()
        self.histogram_view = HistogramView()
        self.steganalysis_view = SteganalysisView()
        self.bitplane_view = BitplaneView()
        self.history_view = HistoryView()
        self.learn_view = LearnView()

        self.views = {
            "encode": self.encode_view,
            "decode": self.decode_view,
            "scan": self.scan_view,
            "psnr": self.psnr_view,
            "binary": self.binary_view,
            "histogram": self.histogram_view,
            "steganalysis": self.steganalysis_view,
            "bitplane": self.bitplane_view,
            "history": self.history_view,
            "learn": self.learn_view,
        }

        for key, view in self.views.items():
            view.setObjectName("PageRoot")
            view.setAttribute(Qt.WA_StyledBackground, True)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(view)
            scroll.setFrameShape(QScrollArea.NoFrame)

            # IMPORTANT: don't use setStyleSheet() on the scroll area or its
            # viewport — a stylesheet set on either one breaks QSS inheritance
            # for every widget inside it (buttons/panels/labels render with no
            # background or wrong color at all). Use the palette instead, which
            # paints the background without interfering with the app-level
            # stylesheet cascade.
            for w in (scroll, scroll.viewport()):
                palette = w.palette()
                palette.setColor(QPalette.Window, QColor(theme.BG))
                w.setAutoFillBackground(True)
                w.setPalette(palette)

            self.stack.addWidget(scroll)
            self.views[key] = (view, scroll)

        root.addWidget(self.stack, 1)

        central.setLayout(root)
        self.setCentralWidget(central)

        self.switch_view("encode")

    def _sync_binary_view(self, message):
        # Keep the binary visualizer's text box mirroring the encode message
        # only if the user hasn't typed something else there manually — simple
        # convenience sync, matching the "View binary breakdown" link behavior.
        pass

    def _go_view_binary(self, message):
        self.binary_view.text_input.setPlainText(message)
        self.switch_view("binary")

    def switch_view(self, key):
        for k, btn in self.nav_buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        view, scroll = self.views[key]
        self.stack.setCurrentWidget(scroll)

        if key == "history":
            self.history_view.refresh()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(theme.GLOBAL_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
