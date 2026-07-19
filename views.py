"""
SecureSteg — views.py
All application views (pages), one class per section of the sidebar.
"""

import os
import numpy as np
from PIL import Image

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QScrollArea, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QClipboard

import core
import history
import theme
from widgets import (
    DropZone, MeterRow, StatBox, TechButtonGroup, HistogramCanvas,
    Panel, panel_head, view_header, numpy_to_pixmap
)


TECH_OPTIONS = [
    ('logistic', 'Logistic map'),
    ('tent', 'Tent map'),
    ('sign', 'SIGN method'),
]


def load_image_as_array(path):
    """Load any image format, return HxWx4 uint8 RGBA numpy array."""
    img = Image.open(path).convert('RGBA')
    return np.array(img)


def scroll_wrap(inner_widget):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(inner_widget)
    return scroll


# =====================================================
# 01 — ENCODE
# =====================================================

class EncodeView(QWidget):

    def __init__(self, on_message_changed=None, on_view_binary=None,
                 on_view_psnr=None, on_view_histogram=None):
        super().__init__()
        self.arr = None
        self.width_ = 0
        self.height_ = 0
        self.on_message_changed = on_message_changed
        self.on_view_binary = on_view_binary
        self.on_view_psnr = on_view_psnr
        self.on_view_histogram = on_view_histogram

        outer = QVBoxLayout()
        outer.setContentsMargins(40, 30, 40, 40)
        outer.setSpacing(14)

        outer.addLayout(view_header(
            "01 — Workspace", "Encode a message",
            "Hide text inside an image's pixel data using least-significant-bit substitution."
        ))

        grid = QHBoxLayout()
        grid.setSpacing(14)

        # --- Panel 1: Source image
        p1 = Panel()
        p1.add(panel_head(1, "Source image"))

        self.drop = DropZone(sub="PNG · JPG · WebP · BMP — auto-converts")
        self.drop.fileSelected.connect(self.load_image)
        p1.add(self.drop)

        stats_row = QHBoxLayout()
        self.stat_px = StatBox("—", "pixels")
        self.stat_cap = StatBox("—", "max chars")
        self.stat_dim = StatBox("—", "dimensions")
        for s in (self.stat_px, self.stat_cap, self.stat_dim):
            stats_row.addWidget(s)
        p1.add(stats_row)

        self.cap_meter = MeterRow("Capacity usage")
        p1.add(self.cap_meter)

        grid.addWidget(p1, 1)

        # --- Panel 2: Key
        p2 = Panel()
        p2.add(panel_head(2, "Key"))

        seed_label = QLabel("Numeric seed")
        seed_label.setObjectName("FieldLabel")
        p2.add(seed_label)

        self.seed_input = QLineEdit()
        self.seed_input.setPlaceholderText("e.g. 42, 0.7, 137")
        self.seed_input.textChanged.connect(self.update_key)
        p2.add(self.seed_input)

        tech_label = QLabel("Generation technique")
        tech_label.setObjectName("FieldLabel")
        p2.add(tech_label)

        self.tech_group = TechButtonGroup(TECH_OPTIONS)
        self.tech_group.changed.connect(lambda _: self.update_key())
        p2.add(self.tech_group)

        key_label = QLabel("Derived key")
        key_label.setObjectName("FieldLabel")
        p2.add(key_label)

        self.key_display = QLabel("Enter a seed to derive a key")
        self.key_display.setObjectName("KeyDisplay")
        self.key_display.setWordWrap(True)
        p2.add(self.key_display)

        self.strength_meter = MeterRow("Key strength")
        p2.add(self.strength_meter)

        grid.addWidget(p2, 1)

        outer.addLayout(grid)

        # --- Panel 3: Message
        p3 = Panel()
        p3.add(panel_head(3, "Message"))

        self.msg_input = QTextEdit()
        self.msg_input.setPlaceholderText("Type the message to hide...")
        self.msg_input.setFixedHeight(100)
        self.msg_input.textChanged.connect(self.update_char_count)
        p3.add(self.msg_input)

        foot = QHBoxLayout()
        self.char_count_label = QLabel("0 / — characters")
        self.char_count_label.setStyleSheet(f"color:{theme.TEXT_3}; font-size:11.5px;")
        foot.addWidget(self.char_count_label)
        foot.addStretch()

        self.view_binary_btn = QPushButton("\u229f View binary breakdown")
        self.view_binary_btn.setObjectName("LinkBtn")
        self.view_binary_btn.setCursor(Qt.PointingHandCursor)
        self.view_binary_btn.clicked.connect(self._go_view_binary)
        foot.addWidget(self.view_binary_btn)

        p3.add(foot)

        self.progress_meter = MeterRow("Encoding progress")
        self.progress_meter.hide()
        p3.add(self.progress_meter)

        self.encode_btn = QPushButton("\u2193 Encode && save PNG")
        self.encode_btn.setObjectName("PrimaryBtn")
        self.encode_btn.setCursor(Qt.PointingHandCursor)
        self.encode_btn.setFixedHeight(42)
        self.encode_btn.clicked.connect(self.do_encode)
        p3.add(self.encode_btn)

        self.result_label = QLabel("")
        self.result_label.setObjectName("AlertSuccess")
        self.result_label.setWordWrap(True)
        self.result_label.hide()
        p3.add(self.result_label)

        result_tools = QHBoxLayout()
        self.psnr_shortcut_btn = QPushButton("\u25a3 PSNR analysis")
        self.psnr_shortcut_btn.setObjectName("GhostBtn")
        self.psnr_shortcut_btn.setCursor(Qt.PointingHandCursor)
        self.psnr_shortcut_btn.clicked.connect(self._go_view_psnr)

        self.histogram_shortcut_btn = QPushButton("\u25a4 Histogram viewer")
        self.histogram_shortcut_btn.setObjectName("GhostBtn")
        self.histogram_shortcut_btn.setCursor(Qt.PointingHandCursor)
        self.histogram_shortcut_btn.clicked.connect(self._go_view_histogram)

        result_tools.addWidget(self.psnr_shortcut_btn)
        result_tools.addWidget(self.histogram_shortcut_btn)
        result_tools.addStretch()

        self.result_tools_widget = QWidget()
        self.result_tools_widget.setLayout(result_tools)
        self.result_tools_widget.hide()
        p3.add(self.result_tools_widget)

        self.error_label = QLabel("")
        self.error_label.setObjectName("AlertError")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        p3.add(self.error_label)

        outer.addWidget(p3)
        outer.addStretch()

        self.setLayout(outer)

    # -------------------------
    def load_image(self, path):
        try:
            self.arr = load_image_as_array(path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load image: {e}")
            return

        self.height_, self.width_ = self.arr.shape[0], self.arr.shape[1]
        self.drop.mark_has_image()
        self.drop.text_label.setText(os.path.basename(path))

        px = self.width_ * self.height_
        cap = core.capacity_chars(self.width_, self.height_)
        self.stat_px.set_value(f"{px:,}")
        self.stat_cap.set_value(f"{cap:,}")
        self.stat_dim.set_value(f"{self.width_} \u00d7 {self.height_}")

        self.update_char_count()

    def update_key(self):
        seed_text = self.seed_input.text().strip()
        if not seed_text:
            self.key_display.setText("Enter a seed to derive a key")
            self.strength_meter.set_value(0, theme.TEXT_3, "—")
            return
        try:
            seed = float(seed_text)
        except ValueError:
            self.key_display.setText("Invalid seed")
            return

        key = core.generate_key(seed, self.tech_group.current)
        self.key_display.setText(key)

        pct, label = core.key_strength(key)
        color = theme.RED if pct < 40 else (theme.AMBER if pct < 75 else theme.GREEN)
        self.strength_meter.set_value(pct, color, f"{label} ({pct}%)")

    def update_char_count(self):
        msg = self.msg_input.toPlainText()
        cap = core.capacity_chars(self.width_, self.height_) if self.arr is not None else None

        if cap:
            self.char_count_label.setText(f"{len(msg)} / {cap:,} characters")
            pct = min(100, round((len(msg) / cap) * 100))
            color = theme.RED if pct > 90 else (theme.AMBER if pct > 70 else theme.ACCENT)
            self.cap_meter.set_value(pct, color, f"{pct}% capacity used")
        else:
            self.char_count_label.setText(f"{len(msg)} / — characters")

        if self.on_message_changed:
            self.on_message_changed(msg)

    def do_encode(self):
        self.result_label.hide()
        self.result_tools_widget.hide()
        self.error_label.hide()

        seed_text = self.seed_input.text().strip()
        msg = self.msg_input.toPlainText()

        if self.arr is None:
            self._show_error("\u26a0  Upload an image first.")
            return
        if not seed_text:
            self._show_error("\u26a0  Enter a numeric seed.")
            return
        if not msg.strip():
            self._show_error("\u26a0  Type a secret message.")
            return

        try:
            seed = float(seed_text)
            self.progress_meter.show()
            self.progress_meter.set_value(30, theme.ACCENT, "Encoding...")

            encoded = core.encode_message(self.arr, seed, self.tech_group.current, msg)

            self.progress_meter.set_value(90, theme.ACCENT, "Saving...")

            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save encoded image", "securesteg_encoded.png", "PNG Image (*.png)"
            )
            if not save_path:
                self.progress_meter.hide()
                return

            Image.fromarray(encoded, 'RGBA').save(save_path, 'PNG')

            self.progress_meter.set_value(100, theme.GREEN, "Done")

            tech = self.tech_group.current
            self.result_label.setText(
                f"\u2713 Encoded! Saved to {os.path.basename(save_path)}. "
                f"Use seed \"{seed_text}\" with {tech} to decode."
            )
            self.result_label.show()
            self.result_tools_widget.show()

            history.save_history('encode', msg, seed_text, tech)

        except Exception as e:
            self._show_error(f"\u2717 Encoding failed: {e}")
            self.progress_meter.hide()

    def _go_view_binary(self):
        if self.on_view_binary:
            self.on_view_binary(self.msg_input.toPlainText())

    def _go_view_psnr(self):
        if self.on_view_psnr:
            self.on_view_psnr()

    def _go_view_histogram(self):
        if self.on_view_histogram:
            self.on_view_histogram()

    def _show_error(self, text):
        self.error_label.setText(text)
        self.error_label.show()


# =====================================================
# 02 — DECODE
# =====================================================

class DecodeView(QWidget):

    def __init__(self):
        super().__init__()
        self.arr = None

        outer = QVBoxLayout()
        outer.setContentsMargins(40, 30, 40, 40)
        outer.setSpacing(14)

        outer.addLayout(view_header(
            "02 — Workspace", "Decode a message",
            "Extract a hidden message from a previously encoded image."
        ))

        p1 = Panel()
        p1.add(panel_head(1, "Encoded image"))
        self.drop = DropZone(sub="Select the image that has a hidden message")
        self.drop.fileSelected.connect(self.load_image)
        p1.add(self.drop)
        outer.addWidget(p1)

        p2 = Panel()
        p2.add(panel_head(2, "Key"))

        seed_label = QLabel("Numeric seed")
        seed_label.setObjectName("FieldLabel")
        p2.add(seed_label)

        self.seed_input = QLineEdit()
        self.seed_input.setPlaceholderText("Same seed used to encode")
        p2.add(self.seed_input)

        tech_label = QLabel("Generation technique")
        tech_label.setObjectName("FieldLabel")
        p2.add(tech_label)

        self.tech_group = TechButtonGroup(TECH_OPTIONS)
        p2.add(self.tech_group)

        self.decode_btn = QPushButton("\u2193 Decode message")
        self.decode_btn.setObjectName("PrimaryBtn")
        self.decode_btn.setCursor(Qt.PointingHandCursor)
        self.decode_btn.setFixedHeight(42)
        self.decode_btn.clicked.connect(self.do_decode)
        p2.add(self.decode_btn)

        self.error_label = QLabel("")
        self.error_label.setObjectName("AlertError")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        p2.add(self.error_label)

        self.decoded_box = QFrame()
        self.decoded_box.setObjectName("DecodedBox")
        db_layout = QVBoxLayout()
        db_layout.setContentsMargins(16, 14, 16, 14)

        dlabel = QLabel("DECODED MESSAGE")
        dlabel.setObjectName("DecodedLabel")

        self.decoded_text = QLabel("")
        self.decoded_text.setObjectName("DecodedText")
        self.decoded_text.setWordWrap(True)

        self.copy_btn = QPushButton("\u29c9 Copy to clipboard")
        self.copy_btn.setObjectName("LinkBtn")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_decoded)

        db_layout.addWidget(dlabel)
        db_layout.addWidget(self.decoded_text)
        db_layout.addWidget(self.copy_btn, alignment=Qt.AlignLeft)
        self.decoded_box.setLayout(db_layout)
        self.decoded_box.hide()
        p2.add(self.decoded_box)

        outer.addWidget(p2)
        outer.addStretch()
        self.setLayout(outer)

    def load_image(self, path):
        try:
            self.arr = load_image_as_array(path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load image: {e}")
            return
        self.drop.mark_has_image()
        self.drop.text_label.setText(os.path.basename(path))

    def do_decode(self):
        self.error_label.hide()
        self.decoded_box.hide()

        seed_text = self.seed_input.text().strip()

        if self.arr is None:
            self._show_error("\u26a0  Upload an encoded image first.")
            return
        if not seed_text:
            self._show_error("\u26a0  Enter the numeric seed.")
            return

        try:
            seed = float(seed_text)
            message = core.decode_message(self.arr, seed, self.tech_group.current)

            if message is None:
                self._show_error("\u2717  Could not decode — wrong seed or technique.")
                return

            self.decoded_text.setText(message)
            self.decoded_box.show()
            history.save_history('decode', message, seed_text, self.tech_group.current)

        except Exception as e:
            self._show_error(f"\u2717  Decode failed: {e}")

    def copy_decoded(self):
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(self.decoded_text.text())
        orig = self.copy_btn.text()
        self.copy_btn.setText("\u2713 Copied")
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1800, lambda: self.copy_btn.setText(orig))

    def _show_error(self, text):
        self.error_label.setText(text)
        self.error_label.show()


# =====================================================
# 03 — SCAN
# =====================================================

class ScanView(QWidget):

    def __init__(self):
        super().__init__()
        outer = QVBoxLayout()
        outer.setContentsMargins(40, 30, 40, 40)
        outer.setSpacing(14)

        outer.addLayout(view_header(
            "03 — Workspace", "Scan an image",
            "Quickly inspect an image's steganographic capacity and pixel data."
        ))

        p1 = Panel()
        p1.add(panel_head(1, "Image to scan"))
        self.drop = DropZone(sub="Any image — inspect capacity and dimensions")
        self.drop.fileSelected.connect(self.load_image)
        p1.add(self.drop)
        outer.addWidget(p1)

        self.results_panel = Panel()
        self.results_panel.add(panel_head(2, "Scan results"))

        stats_row = QHBoxLayout()
        self.stat_px = StatBox("—", "pixels")
        self.stat_cap = StatBox("—", "max chars")
        self.stat_w = StatBox("—", "width")
        self.stat_h = StatBox("—", "height")
        for s in (self.stat_px, self.stat_cap, self.stat_w, self.stat_h):
            stats_row.addWidget(s)
        self.results_panel.add(stats_row)
        self.results_panel.hide()

        outer.addWidget(self.results_panel)
        outer.addStretch()
        self.setLayout(outer)

    def load_image(self, path):
        try:
            arr = load_image_as_array(path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load image: {e}")
            return

        self.drop.mark_has_image()
        self.drop.text_label.setText(os.path.basename(path))

        h, w = arr.shape[0], arr.shape[1]
        px = w * h
        cap = core.capacity_chars(w, h)

        self.stat_px.set_value(f"{px:,}")
        self.stat_cap.set_value(f"{cap:,}")
        self.stat_w.set_value(f"{w}px")
        self.stat_h.set_value(f"{h}px")
        self.results_panel.show()


# =====================================================
# 04 — PSNR
# =====================================================

class PSNRView(QWidget):

    def __init__(self):
        super().__init__()
        self.arr_a = None
        self.arr_b = None

        outer = QVBoxLayout()
        outer.setContentsMargins(40, 30, 40, 40)
        outer.setSpacing(14)

        outer.addLayout(view_header(
            "04 — Tool", "PSNR analysis",
            "Measure the Peak Signal-to-Noise Ratio between an original and an encoded image."
        ))

        grid = QHBoxLayout()
        grid.setSpacing(14)

        p_a = Panel()
        p_a.add(panel_head("A", "Original image"))
        self.drop_a = DropZone(sub="Upload the untouched original")
        self.drop_a.fileSelected.connect(lambda p: self.load_image(p, 'a'))
        p_a.add(self.drop_a)
        grid.addWidget(p_a)

        p_b = Panel()
        p_b.add(panel_head("B", "Encoded image"))
        self.drop_b = DropZone(sub="Upload the image with hidden data")
        self.drop_b.fileSelected.connect(lambda p: self.load_image(p, 'b'))
        p_b.add(self.drop_b)
        grid.addWidget(p_b)

        outer.addLayout(grid)

        self.calc_btn = QPushButton("Calculate PSNR")
        self.calc_btn.setObjectName("PrimaryBtn")
        self.calc_btn.setCursor(Qt.PointingHandCursor)
        self.calc_btn.setFixedHeight(42)
        self.calc_btn.clicked.connect(self.calculate)
        outer.addWidget(self.calc_btn)

        self.error_label = QLabel("")
        self.error_label.setObjectName("AlertError")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        outer.addWidget(self.error_label)

        self.result_panel = Panel()
        big_row = QHBoxLayout()
        self.psnr_num = QLabel("—")
        self.psnr_num.setObjectName("PsnrNum")
        unit = QLabel("dB")
        unit.setObjectName("PsnrUnit")
        big_row.addWidget(self.psnr_num)
        big_row.addWidget(unit)
        big_row.addStretch()
        self.result_panel.add(big_row)

        self.psnr_verdict = QLabel("")
        self.psnr_verdict.setObjectName("PsnrVerdict")
        self.psnr_verdict.setWordWrap(True)
        self.result_panel.add(self.psnr_verdict)

        stats_row = QHBoxLayout()
        self.stat_mse = StatBox("—", "MSE")
        self.stat_diff_px = StatBox("—", "different pixels")
        self.stat_diff_pct = StatBox("—", "% changed")
        for s in (self.stat_mse, self.stat_diff_px, self.stat_diff_pct):
            stats_row.addWidget(s)
        self.result_panel.add(stats_row)
        self.result_panel.hide()

        outer.addWidget(self.result_panel)
        outer.addStretch()
        self.setLayout(outer)

    def load_image(self, path, side):
        try:
            arr = load_image_as_array(path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load image: {e}")
            return

        if side == 'a':
            self.arr_a = arr
            self.drop_a.mark_has_image()
            self.drop_a.text_label.setText(os.path.basename(path))
        else:
            self.arr_b = arr
            self.drop_b.mark_has_image()
            self.drop_b.text_label.setText(os.path.basename(path))

    def calculate(self):
        self.error_label.hide()
        self.result_panel.hide()

        if self.arr_a is None:
            self._show_error("\u26a0  Upload original image (slot A).")
            return
        if self.arr_b is None:
            self._show_error("\u26a0  Upload encoded image (slot B).")
            return

        try:
            res = core.calculate_psnr(self.arr_a, self.arr_b)
        except ValueError as e:
            self._show_error(f"\u26a0  {e}")
            return

        psnr_display = "\u221e" if res['psnr'] == float('inf') else f"{res['psnr']:.2f}"
        self.psnr_num.setText(psnr_display)
        self.psnr_verdict.setText(res['verdict'])
        self.stat_mse.set_value("0" if res['mse'] == 0 else f"{res['mse']:.6f}")
        self.stat_diff_px.set_value(f"{res['diff_px']:,}")
        self.stat_diff_pct.set_value(f"{res['pct']:.3f}%")
        self.result_panel.show()

    def _show_error(self, text):
        self.error_label.setText(text)
        self.error_label.show()


# =====================================================
# 05 — BINARY VISUALIZER
# =====================================================

class BinaryView(QWidget):

    def __init__(self):
        super().__init__()
        outer = QVBoxLayout()
        outer.setContentsMargins(40, 30, 40, 40)
        outer.setSpacing(14)

        outer.addLayout(view_header(
            "05 — Tool", "Binary visualizer",
            "See how text is converted into bits before being hidden in an image."
        ))

        p1 = Panel()
        p1.add(panel_head(1, "Text input"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type or paste text to see its binary breakdown...")
        self.text_input.setFixedHeight(80)
        self.text_input.textChanged.connect(self.render_binary)
        p1.add(self.text_input)

        stats_row = QHBoxLayout()
        self.stat_bits = StatBox("0", "bits")
        self.stat_px = StatBox("0", "pixels needed")
        self.stat_bytes = StatBox("0", "characters")
        for s in (self.stat_bits, self.stat_px, self.stat_bytes):
            stats_row.addWidget(s)
        p1.add(stats_row)
        outer.addWidget(p1)

        p2 = Panel()
        p2.add(panel_head(2, "Character \u2192 binary table"))

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Char", "Code", "Binary"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setFixedHeight(280)
        p2.add(self.table)

        self.empty_label = QLabel("Type some text above to see its binary breakdown here.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(f"color:{theme.TEXT_3}; padding:28px;")
        p2.add(self.empty_label)

        outer.addWidget(p2)
        outer.addStretch()
        self.setLayout(outer)
        self.render_binary()

    def render_binary(self):
        text = self.text_input.toPlainText()

        if not text:
            self.table.setRowCount(0)
            self.table.hide()
            self.empty_label.show()
            self.stat_bits.set_value("0")
            self.stat_px.set_value("0")
            self.stat_bytes.set_value("0")
            return

        self.empty_label.hide()
        self.table.show()
        self.table.setRowCount(len(text))

        all_bits = 0
        for i, ch in enumerate(text):
            code = ord(ch)
            bin_str = format(code, '08b')
            all_bits += 8

            display = "\u2423" if ch == ' ' else ("\u21b5" if ch == '\n' else ch)

            self.table.setItem(i, 0, QTableWidgetItem(display))
            self.table.setItem(i, 1, QTableWidgetItem(str(code)))
            self.table.setItem(i, 2, QTableWidgetItem(bin_str))

        self.stat_bits.set_value(all_bits)
        self.stat_px.set_value(f"{-(-all_bits // 3):,}")
        self.stat_bytes.set_value(len(text))


# =====================================================
# 06 — HISTOGRAM VIEWER
# =====================================================

class HistogramView(QWidget):

    def __init__(self):
        super().__init__()
        self.arr_a = None
        self.arr_b = None

        outer = QVBoxLayout()
        outer.setContentsMargins(40, 30, 40, 40)
        outer.setSpacing(14)

        outer.addLayout(view_header(
            "06 — Tool", "Histogram viewer",
            "Compare the color-channel distributions of two images side by side."
        ))

        grid = QHBoxLayout()
        grid.setSpacing(14)

        p_a = Panel()
        p_a.add(panel_head("A", "Original"))
        self.drop_a = DropZone(sub="Upload the original image")
        self.drop_a.fileSelected.connect(lambda p: self.load_image(p, 'a'))
        p_a.add(self.drop_a)
        grid.addWidget(p_a)

        p_b = Panel()
        p_b.add(panel_head("B", "Encoded"))
        self.drop_b = DropZone(sub="Upload the encoded image")
        self.drop_b.fileSelected.connect(lambda p: self.load_image(p, 'b'))
        p_b.add(self.drop_b)
        grid.addWidget(p_b)

        outer.addLayout(grid)

        self.hist_panels = {}
        for ch, label in (('r', 'Red channel'), ('g', 'Green channel'), ('b', 'Blue channel')):
            p = Panel()
            p.add(panel_head(label[0], label))
            canvas = HistogramCanvas()
            p.add(canvas)
            p.hide()
            self.hist_panels[ch] = (p, canvas)
            outer.addWidget(p)

        info = QLabel(
            "Red bars = image A, silver bars = image B. Large discrepancies in the "
            "distribution can indicate the presence of hidden data."
        )
        info.setObjectName("InfoBox")
        info.setWordWrap(True)
        info.hide()
        self.info_box = info
        outer.addWidget(info)

        outer.addStretch()
        self.setLayout(outer)

    def load_image(self, path, side):
        try:
            arr = load_image_as_array(path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load image: {e}")
            return

        if side == 'a':
            self.arr_a = arr
            self.drop_a.mark_has_image()
            self.drop_a.text_label.setText(os.path.basename(path))
        else:
            self.arr_b = arr
            self.drop_b.mark_has_image()
            self.drop_b.text_label.setText(os.path.basename(path))

        if self.arr_a is not None and self.arr_b is not None:
            self.draw_histograms()

    def draw_histograms(self):
        for ch in ('r', 'g', 'b'):
            hist_a = core.build_histogram(self.arr_a, ch)
            hist_b = core.build_histogram(self.arr_b, ch)
            panel, canvas = self.hist_panels[ch]
            canvas.set_data(hist_a, hist_b)
            panel.show()
        self.info_box.show()


# =====================================================
# 07 — STEGANALYSIS
# =====================================================

class SteganalysisView(QWidget):

    def __init__(self):
        super().__init__()
        outer = QVBoxLayout()
        outer.setContentsMargins(40, 30, 40, 40)
        outer.setSpacing(14)

        outer.addLayout(view_header(
            "07 — Tool", "Steganalysis detector",
            "Analyze LSB patterns in an image to detect whether hidden data is likely present."
        ))

        p1 = Panel()
        p1.add(panel_head(1, "Image to analyze"))
        self.drop = DropZone(sub="Checks LSB randomness, chi-square score, and bit uniformity")
        self.drop.fileSelected.connect(self.analyze)
        p1.add(self.drop)
        outer.addWidget(p1)

        self.results_panel = Panel()
        self.results_panel.add(panel_head(2, "Analysis results"))

        self.verdict_label = QLabel("")
        self.verdict_label.setWordWrap(True)
        self.results_panel.add(self.verdict_label)

        stats_row = QHBoxLayout()
        self.stat_chi = StatBox("—", "Chi-square score")
        self.stat_ratio = StatBox("—", "LSB 1-ratio")
        self.stat_entropy = StatBox("—", "LSB entropy")
        self.stat_pairs = StatBox("—", "Pair match %")
        for s in (self.stat_chi, self.stat_ratio, self.stat_entropy, self.stat_pairs):
            stats_row.addWidget(s)
        self.results_panel.add(stats_row)

        self.suspicion_meter = MeterRow("Suspicion level", height=10)
        self.results_panel.add(self.suspicion_meter)

        info = QLabel(
            "How it works: Natural images have non-uniform LSB distributions. Hidden data "
            "tends to randomize LSBs, making the distribution unusually close to 50/50. A "
            "chi-square score near 1.0 and LSB ratio near 50% both suggest possible "
            "steganographic content."
        )
        info.setObjectName("InfoBox")
        info.setWordWrap(True)
        self.results_panel.add(info)

        self.results_panel.hide()
        outer.addWidget(self.results_panel)
        outer.addStretch()
        self.setLayout(outer)

    def analyze(self, path):
        try:
            arr = load_image_as_array(path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load image: {e}")
            return

        self.drop.mark_has_image()
        self.drop.text_label.setText(os.path.basename(path))

        res = core.analyze_steg(arr)

        obj_map = {'clean': 'StegVerdictClean', 'suspect': 'StegVerdictSuspect', 'likely': 'StegVerdictLikely'}
        self.verdict_label.setObjectName(obj_map[res['vclass']])
        self.verdict_label.setStyleSheet("")
        self.verdict_label.setText(res['verdict'])
        self.verdict_label.style().unpolish(self.verdict_label)
        self.verdict_label.style().polish(self.verdict_label)

        self.stat_chi.set_value(f"{res['chi']:.2f}")
        self.stat_ratio.set_value(f"{res['lsb_ratio']:.2f}%")
        self.stat_entropy.set_value(f"{res['entropy']:.4f}")
        self.stat_pairs.set_value(f"{res['pair_match']:.1f}%")

        susp = res['suspicion']
        color = theme.GREEN if susp < 30 else (theme.AMBER if susp < 65 else theme.RED)
        self.suspicion_meter.set_value(susp, color, f"{susp}% suspicion score")

        self.results_panel.show()


# =====================================================
# 08 — BIT PLANE VIEWER
# =====================================================

class BitplaneView(QWidget):

    def __init__(self):
        super().__init__()
        self.arr = None
        self.channel = 'r'

        outer = QVBoxLayout()
        outer.setContentsMargins(40, 30, 40, 40)
        outer.setSpacing(14)

        outer.addLayout(view_header(
            "08 — Tool", "Bit plane viewer",
            "View each of the 8 bit planes of an image independently. LSB steganography "
            "shows noise in bit plane 0."
        ))

        p1 = Panel()
        p1.add(panel_head(1, "Image"))
        self.drop = DropZone(sub="Plane 0 = LSB \u00b7 Plane 7 = MSB")
        self.drop.fileSelected.connect(self.load_image)
        p1.add(self.drop)
        outer.addWidget(p1)

        self.channel_panel = Panel()
        self.channel_panel.add(panel_head(2, "Channel"))
        self.channel_group = TechButtonGroup([('r', 'Red'), ('g', 'Green'), ('b', 'Blue')])
        self.channel_group.changed.connect(self.render_bitplanes)
        self.channel_panel.add(self.channel_group)
        self.channel_panel.hide()
        outer.addWidget(self.channel_panel)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(12)
        self.grid_widget.setLayout(self.grid_layout)
        self.grid_widget.hide()
        outer.addWidget(self.grid_widget)

        info = QLabel(
            "What to look for: In an unmodified image, bit plane 0 (LSB) looks like random "
            "noise. After LSB steganography, it may show subtle structured patterns where "
            "message bits have replaced natural pixel variation."
        )
        info.setObjectName("InfoBox")
        info.setWordWrap(True)
        info.hide()
        self.info_box = info
        outer.addWidget(info)

        outer.addStretch()
        self.setLayout(outer)

    def load_image(self, path):
        try:
            self.arr = load_image_as_array(path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load image: {e}")
            return

        self.drop.mark_has_image()
        self.drop.text_label.setText(os.path.basename(path))
        self.channel_panel.show()
        self.grid_widget.show()
        self.info_box.show()
        self.render_bitplanes('r')

    def render_bitplanes(self, channel):
        if self.arr is None:
            return
        self.channel = channel

        # clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for plane in range(8):
            gray = core.bitplane_gray(self.arr, channel, plane)
            pixmap = numpy_to_pixmap(gray)
            pixmap = pixmap.scaledToWidth(160, Qt.SmoothTransformation)

            card = QFrame()
            card.setObjectName("BitplaneCard")
            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.setSpacing(0)

            suffix = " (LSB)" if plane == 0 else (" (MSB)" if plane == 7 else "")
            lbl = QLabel(f"Plane {plane}{suffix}")
            lbl.setObjectName("BitplaneLabel")

            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignCenter)

            card_layout.addWidget(lbl)
            card_layout.addWidget(img_label)
            card.setLayout(card_layout)

            self.grid_layout.addWidget(card, plane // 4, plane % 4)


# =====================================================
# 09 — HISTORY
# =====================================================

class HistoryView(QWidget):

    def __init__(self):
        super().__init__()
        outer = QVBoxLayout()
        outer.setContentsMargins(40, 30, 40, 40)
        outer.setSpacing(14)

        outer.addLayout(view_header(
            "09 — Workspace", "History",
            "Recent encode and decode operations — stored locally on this computer only."
        ))

        head_row = QHBoxLayout()
        head_row.addStretch()
        clear_btn = QPushButton("\u232b Clear all")
        clear_btn.setObjectName("GhostBtn")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_all)
        head_row.addWidget(clear_btn)
        outer.addLayout(head_row)

        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(9)
        list_widget = QWidget()
        list_widget.setLayout(self.list_layout)
        outer.addWidget(list_widget)

        self.empty_label = QLabel("No history yet — encode or decode a message to see it here.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(f"color:{theme.TEXT_3}; padding:40px;")
        outer.addWidget(self.empty_label)

        outer.addStretch()
        self.setLayout(outer)

    def refresh(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        items = history.get_history()

        if not items:
            self.empty_label.show()
            return
        self.empty_label.hide()

        for idx, entry in enumerate(items):
            self.list_layout.addWidget(self._build_item(idx, entry))

    def _build_item(self, idx, entry):
        box = QFrame()
        box.setObjectName("HistoryItem")
        row = QHBoxLayout()
        row.setContentsMargins(14, 12, 14, 12)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        meta = QLabel(f"{entry['time']}  \u00b7  seed:{entry['seed']}  \u00b7  {entry['tech']}")
        meta.setObjectName("HistoryMeta")

        msg = QLabel(entry['message'])
        msg.setObjectName("HistoryMsg")
        msg.setWordWrap(True)

        text_col.addWidget(meta)
        text_col.addWidget(msg)

        badge = QLabel(entry['type'].upper())
        badge.setObjectName("BadgeEncode" if entry['type'] == 'encode' else "BadgeDecode")
        badge.setAlignment(Qt.AlignCenter)

        del_btn = QPushButton("\u2715")
        del_btn.setObjectName("DeleteBtn")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda: self.delete_item(idx))

        row.addLayout(text_col, 1)
        row.addWidget(badge)
        row.addWidget(del_btn)
        box.setLayout(row)
        return box

    def delete_item(self, idx):
        history.delete_entry(idx)
        self.refresh()

    def clear_all(self):
        reply = QMessageBox.question(
            self, "Clear history", "Clear all history?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            history.clear_history()
            self.refresh()


# =====================================================
# 10 — LEARN
# =====================================================

class LearnView(QWidget):

    def __init__(self):
        super().__init__()
        outer = QVBoxLayout()
        outer.setContentsMargins(40, 30, 40, 40)
        outer.setSpacing(14)

        outer.addLayout(view_header(
            "10 — Reference", "Learn the technique",
            "Core concepts behind how SecureSteg hides and protects messages."
        ))

        topics = [
            ("Steganography",
             "The practice of concealing the existence of a message, rather than just its "
             "content. Unlike encryption, which scrambles a message so it is unreadable but "
             "obviously present, steganography hides the message inside an ordinary-looking "
             "file so an observer has no reason to suspect anything is there at all."),
            ("LSB substitution",
             "Every pixel in an image is made of color channels — red, green, and blue — each "
             "stored as an 8-bit number from 0 to 255. The least significant bit (LSB) is the "
             "final bit of that number. Flipping it changes the color value by at most 1, an "
             "amount no human eye can perceive. SecureSteg replaces the LSB of each channel "
             "with one bit of the secret message."),
        ]

        for title, body in topics:
            outer.addWidget(self._learn_panel(title, body))

        # Chaotic maps panel with formula cards
        p = Panel()
        p.add(panel_head("\u2699", "Chaotic maps"))
        intro = QLabel(
            "A chaotic map is a simple mathematical formula that produces a sequence of "
            "numbers which looks random but is fully determined by its starting value, or "
            "seed. The same seed always reproduces the exact same sequence."
        )
        intro.setObjectName("LearnBody")
        intro.setWordWrap(True)
        p.add(intro)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(10)
        for title, formula, body in [
            ("Logistic map", "x = r \u00b7 x \u00b7 (1 \u2212 x)",
             "A population-growth model repurposed for its chaotic behavior at r \u2248 3.99."),
            ("Tent map", "x = u\u00b7x or u\u00b7(1\u2212x)",
             "A piecewise linear function shaped like a tent, simple to compute and highly "
             "sensitive to its seed."),
            ("SIGN method", "x = sin(t) mod 1",
             "Mixes the seed with each step index inside a sine function to avoid periodic "
             "repeats."),
        ]:
            cards_row.addWidget(self._formula_card(title, formula, body))
        p.add(cards_row)

        outer.addWidget(p)

        more_topics = [
            ("Fisher\u2013Yates shuffle",
             "An algorithm that reorders a list so every position appears exactly once. "
             "SecureSteg uses the chaotic sequence to drive this shuffle across all pixel "
             "indices, guaranteeing no pixel is written to twice and none are skipped."),
            ("XOR encryption",
             "An exclusive-or operation compares each bit of the message against the key. "
             "Applying XOR twice with the same key perfectly reverses it — the same generated "
             "key both encrypts and decrypts the message before it is hidden."),
            ("PSNR \u2014 Peak Signal-to-Noise Ratio",
             "A measurement in decibels of how different two images are. Higher means a "
             "smaller, less detectable change. Well-implemented LSB steganography typically "
             "scores above 50 dB."),
            ("Steganalysis",
             "The science of detecting hidden data. Key indicators include unusually uniform "
             "LSB distributions (natural images are non-uniform), high chi-square scores "
             "between observed and expected LSB patterns, and suspiciously high LSB entropy."),
            ("Bit planes",
             "An image can be separated into 8 layers, one per bit position. Bit plane 0 "
             "contains only the LSBs of every pixel. In clean images this plane looks like "
             "random noise; steganographic content may introduce visible structure or "
             "unusually regular patterns into plane 0."),
        ]
        for title, body in more_topics:
            outer.addWidget(self._learn_panel(title, body))

        outer.addStretch()
        self.setLayout(outer)

    def _learn_panel(self, title, body):
        p = Panel()
        t = QLabel(title)
        t.setObjectName("LearnTitle")
        b = QLabel(body)
        b.setObjectName("LearnBody")
        b.setWordWrap(True)
        p.add(t)
        p.add(b)
        return p

    def _formula_card(self, title, formula, body):
        card = QFrame()
        card.setObjectName("LearnCard")
        layout = QVBoxLayout()
        layout.setContentsMargins(13, 13, 13, 13)
        layout.setSpacing(6)

        t = QLabel(title)
        t.setObjectName("LearnCardTitle")

        f = QLabel(formula)
        f.setObjectName("LearnCardFormula")

        b = QLabel(body)
        b.setObjectName("LearnCardBody")
        b.setWordWrap(True)

        layout.addWidget(t)
        layout.addWidget(f, alignment=Qt.AlignLeft)
        layout.addWidget(b)
        card.setLayout(layout)
        return card
