"""
cc_color.py - Color/Palette Manager for NsCDE Control Center.

Provides palette selection, color preview, and integration with
GTK/Qt/Kvantum/Firefox themes via nscde-wayland-theme.
"""

import os
import sys
import subprocess
import configparser
import shutil

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QListWidget, QListWidgetItem, QPushButton, QCheckBox,
    QGroupBox, QGridLayout, QColorDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

script_dir = os.path.dirname(os.path.abspath(__file__))
bin_dir = os.path.join(os.path.dirname(script_dir), "bin")
sys.path.insert(0, script_dir)

from nscde_cde import (
    load_all_palette_colors, get_palette_list, find_default_palette,
    load_palette_colors, build_dialog_stylesheet
)


def _run_tool(name, args, timeout=10):
    """Run a wayland tool and return (returncode, stdout, stderr)."""
    tool = os.path.join(bin_dir, name)
    if not os.path.exists(tool):
        tool = shutil.which(name)
        if not tool:
            return -1, "", f"{name} not found"
    try:
        r = subprocess.run(
            [tool] + args,
            capture_output=True, text=True, timeout=timeout
        )
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)


def _apply_labwc_theme(palette_path):
    """Generate and apply labwc theme from palette."""
    theme_dir = os.path.expanduser("~/.config/labwc")
    themerc = os.path.join(theme_dir, "themerc")
    rc, out, err = _run_tool("nscde-wayland-theme", [palette_path])
    if rc == 0 and out:
        os.makedirs(theme_dir, exist_ok=True)
        with open(themerc, 'w') as f:
            f.write(out)
        return True
    return False


def _apply_kvantum(palette_path):
    """Generate and apply Kvantum theme."""
    kv_dir = os.path.expanduser("~/.config/Kvantum")
    rc, out, err = _run_tool(
        "nscde-wayland-theme", ["--kvantum-dir", kv_dir, palette_path]
    )
    return rc == 0


def _apply_gtk4(palette_path):
    """Generate and apply GTK4 CSS."""
    gtk4_dir = os.path.expanduser("~/.config/gtk-4.0")
    os.makedirs(gtk4_dir, exist_ok=True)
    rc, out, err = _run_tool("nscde-wayland-theme", ["--gtk4", palette_path])
    if rc == 0 and out:
        css_path = os.path.join(gtk4_dir, "gtk.css")
        with open(css_path, 'w') as f:
            f.write(out)
        return True
    return False


def _apply_firefox(palette_path):
    """Generate and install Firefox CSS theme."""
    rc, out, err = _run_tool(
        "nscde-wayland-theme", ["--install-firefox", palette_path]
    )
    return rc == 0


def _reconfigure_labwc():
    """Signal labwc to reconfigure."""
    try:
        subprocess.Popen(
            ["labwc", "-r"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception:
        pass


def _read_integration_prefs():
    """Read integration checkbox states from settings.ini."""
    config_path = os.path.expanduser("~/.config/nscde-wayland/settings.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    return {
        'labwc': config.getboolean("ColorIntegration", "labwc", fallback=True),
        'kvantum': config.getboolean("ColorIntegration", "kvantum", fallback=False),
        'gtk4': config.getboolean("ColorIntegration", "gtk4", fallback=True),
        'firefox': config.getboolean("ColorIntegration", "firefox", fallback=False),
    }


def _save_integration_prefs(prefs):
    """Save integration checkbox states."""
    config_path = os.path.expanduser("~/.config/nscde-wayland/settings.ini")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.has_section("ColorIntegration"):
        config.add_section("ColorIntegration")
    for k, v in prefs.items():
        config.set("ColorIntegration", k, str(v))
    with open(config_path, 'w') as f:
        config.write(f)


class ColorSwatch(QPushButton):
    """A single color preview button."""

    def __init__(self, color, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.setFixedSize(48, 48)
        self.set_color(color)

    def set_color(self, color):
        self._color = color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-top: 2px solid #ffffff;
                border-left: 2px solid #ffffff;
                border-right: 2px solid #444444;
                border-bottom: 2px solid #444444;
            }}
            QPushButton:pressed {{
                border-top: 2px solid #444444;
                border-left: 2px solid #444444;
                border-right: 2px solid #ffffff;
                border-bottom: 2px solid #ffffff;
            }}
        """)
        self.setToolTip(f"Color {self.index}: {color}")

    def get_color(self):
        return self._color


class ColorPage(QWidget):
    """Color/Palette management page."""

    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self.swatches = []
        self._current_palette_path = None
        self._build_ui()
        self._load_palettes()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        # Title
        title = QLabel("Color Manager")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {self.colors['bs']}")
        layout.addWidget(sep)

        # Main content: palette list + color swatches
        main_layout = QHBoxLayout()

        # Left: palette list
        left = QVBoxLayout()
        left.addWidget(QLabel("Palettes:"))
        self.palette_list = QListWidget()
        self.palette_list.setMinimumWidth(200)
        self.palette_list.currentItemChanged.connect(self._on_palette_selected)
        left.addWidget(self.palette_list)
        main_layout.addLayout(left)

        # Right: color swatches + options
        right = QVBoxLayout()

        # Color swatches
        swatch_group = QGroupBox("Palette Colors")
        swatch_layout = QGridLayout(swatch_group)
        swatch_layout.setSpacing(4)
        for i in range(8):
            swatch = ColorSwatch("#888888", i + 1)
            swatch.clicked.connect(lambda checked, idx=i: self._on_color_click(idx))
            row, col = divmod(i, 4)
            swatch_layout.addWidget(swatch, row, col)
            self.swatches.append(swatch)
        right.addWidget(swatch_group)

        # Integration options
        integ_group = QGroupBox("Integration Options")
        integ_layout = QVBoxLayout(integ_group)
        prefs = _read_integration_prefs()

        self.cb_labwc = QCheckBox("labwc/Openbox theme")
        self.cb_labwc.setChecked(prefs.get('labwc', True))
        integ_layout.addWidget(self.cb_labwc)

        self.cb_gtk4 = QCheckBox("GTK4 CSS")
        self.cb_gtk4.setChecked(prefs.get('gtk4', True))
        integ_layout.addWidget(self.cb_gtk4)

        self.cb_kvantum = QCheckBox("Qt5/Qt6 Kvantum theme")
        self.cb_kvantum.setChecked(prefs.get('kvantum', False))
        integ_layout.addWidget(self.cb_kvantum)

        self.cb_firefox = QCheckBox("Firefox CSS theme")
        self.cb_firefox.setChecked(prefs.get('firefox', False))
        integ_layout.addWidget(self.cb_firefox)

        right.addWidget(integ_group)
        right.addStretch()
        main_layout.addLayout(right)

        layout.addLayout(main_layout)

        # Buttons
        btn_layout = QHBoxLayout()

        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self._on_preview)
        btn_layout.addWidget(preview_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(apply_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self._on_close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        # Status
        self.status = QLabel("")
        self.status.setStyleSheet(f"color: {self.colors['sel']}; font: italic 11px")
        layout.addWidget(self.status)

    def _load_palettes(self):
        """Load available palettes into the list."""
        palettes = get_palette_list()
        current_palette = find_default_palette()
        for name, path in palettes:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.palette_list.addItem(item)
            if path == current_palette:
                self.palette_list.setCurrentItem(item)

    def _on_palette_selected(self, current, previous):
        if not current:
            return
        path = current.data(Qt.ItemDataRole.UserRole)
        self._current_palette_path = path
        self._update_swatches(path)

    def _update_swatches(self, palette_path):
        """Update color swatch buttons from palette."""
        all_colors = load_all_palette_colors(palette_path)
        for i, swatch in enumerate(self.swatches):
            cs = all_colors.get(i + 1)
            if cs:
                swatch.set_color(cs['bg'])

    def _on_color_click(self, index):
        """Open color picker for a single color."""
        swatch = self.swatches[index]
        color = QColorDialog.getColor(
            QColor(swatch.get_color()), self,
            f"Edit Color {index + 1}"
        )
        if color.isValid():
            swatch.set_color(color.name())

    def _on_preview(self):
        """Temporarily apply theme for preview."""
        if not self._current_palette_path:
            self.status.setText("Select a palette first")
            return
        self.status.setText("Applying preview...")
        QApplication.processEvents()

        if self.cb_labwc.isChecked():
            _apply_labwc_theme(self._current_palette_path)
            _reconfigure_labwc()

        self.status.setText("Preview applied")

    def _on_apply(self):
        """Apply theme permanently."""
        if not self._current_palette_path:
            self.status.setText("Select a palette first")
            return

        # Save integration preferences
        prefs = {
            'labwc': self.cb_labwc.isChecked(),
            'gtk4': self.cb_gtk4.isChecked(),
            'kvantum': self.cb_kvantum.isChecked(),
            'firefox': self.cb_firefox.isChecked(),
        }
        _save_integration_prefs(prefs)

        # Copy palette to user config
        user_palette = os.path.expanduser("~/.config/nscde-wayland/palette.dp")
        os.makedirs(os.path.dirname(user_palette), exist_ok=True)
        shutil.copy2(self._current_palette_path, user_palette)

        self.status.setText("Applying theme...")
        QApplication.processEvents()

        results = []

        # Apply each enabled integration
        if prefs['labwc']:
            if _apply_labwc_theme(self._current_palette_path):
                results.append("labwc theme")
                _reconfigure_labwc()
            else:
                results.append("labwc theme (FAILED)")

        if prefs['gtk4']:
            if _apply_gtk4(self._current_palette_path):
                results.append("GTK4 CSS")
            else:
                results.append("GTK4 CSS (FAILED)")

        if prefs['kvantum']:
            if _apply_kvantum(self._current_palette_path):
                results.append("Kvantum")
            else:
                results.append("Kvantum (FAILED)")

        if prefs['firefox']:
            if _apply_firefox(self._current_palette_path):
                results.append("Firefox CSS")
            else:
                results.append("Firefox CSS (FAILED)")

        self.status.setText(f"Applied: {', '.join(results)}")

    def _on_close(self):
        self.window().close()
