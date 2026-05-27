"""
cc_font.py - Font Manager for NsCDE Control Center.

Provides font selection with preview, fontset management,
and GTK/Qt integration.
"""

import os
import configparser

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QComboBox, QGroupBox, QGridLayout, QFontDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Font categories matching NsCDE FontMgr
FONT_CATEGORIES = [
    ("Variable Regular", "variable_regular"),
    ("Variable Bold", "variable_bold"),
    ("Variable Italic", "variable_italic"),
    ("Monospaced Regular", "mono_regular"),
    ("Monospaced Bold", "mono_bold"),
]

# Size groups
SIZE_GROUPS = {
    "Small": {"variable_regular": 10, "variable_bold": 10, "variable_italic": 10,
              "mono_regular": 10, "mono_bold": 10},
    "Medium": {"variable_regular": 12, "variable_bold": 12, "variable_italic": 12,
               "mono_regular": 12, "mono_bold": 12},
    "Large": {"variable_regular": 14, "variable_bold": 14, "variable_italic": 14,
              "mono_regular": 14, "mono_bold": 14},
}


def _get_fontsets_dir():
    d = os.path.expanduser("~/.config/nscde-wayland/fontsets")
    os.makedirs(d, exist_ok=True)
    return d


def _list_fontsets():
    """List available fontset files."""
    d = _get_fontsets_dir()
    fontsets = []
    for f in sorted(os.listdir(d)):
        if f.endswith(".fontset"):
            fontsets.append(f[:-8])  # strip .fontset
    return fontsets


def _load_fontset(name):
    """Load a fontset file. Returns dict of category -> font string."""
    path = os.path.join(_get_fontsets_dir(), f"{name}.fontset")
    result = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"')
                    for cat_label, cat_key in FONT_CATEGORIES:
                        if cat_key in key:
                            result[cat_key] = val
    except Exception:
        pass
    return result


def _save_fontset(name, fonts_dict):
    """Save a fontset file."""
    safe_name = name.replace('/', '_').replace('\\', '_').replace('..', '_')
    path = os.path.join(_get_fontsets_dir(), f"{safe_name}.fontset")
    with open(path, 'w') as f:
        f.write(f"# NsCDE-Wayland fontset: {name}\n")
        for cat_label, cat_key in FONT_CATEGORIES:
            val = fonts_dict.get(cat_key, "sans-serif 12")
            f.write(f"{cat_key} = \"{val}\"\n")
    return path


def _apply_font_integration(fonts_dict):
    """Write font settings to GTK/Qt config files."""
    # Build GTK font string (use variable_regular)
    var_font = fonts_dict.get("variable_regular", "sans-serif 12")
    mono_font = fonts_dict.get("mono_regular", "monospace 12")

    # GTK3 settings.ini
    gtk3_dir = os.path.expanduser("~/.config/gtk-3.0")
    os.makedirs(gtk3_dir, exist_ok=True)
    gtk3_path = os.path.join(gtk3_dir, "settings.ini")
    config = configparser.ConfigParser()
    config.read(gtk3_path)
    if not config.has_section("Settings"):
        config.add_section("Settings")
    config.set("Settings", "gtk-font-name", var_font)
    with open(gtk3_path, 'w') as f:
        config.write(f)

    # GTK4 settings (via gtk.css @define not applicable, use settings.ini if exists)
    gtk4_dir = os.path.expanduser("~/.config/gtk-4.0")
    os.makedirs(gtk4_dir, exist_ok=True)

    # Qt5ct
    qt5_dir = os.path.expanduser("~/.config/qt5ct")
    os.makedirs(qt5_dir, exist_ok=True)
    qt5_path = os.path.join(qt5_dir, "qt5ct.conf")
    config = configparser.ConfigParser()
    config.read(qt5_path)
    if not config.has_section("Fonts"):
        config.add_section("Fonts")
    config.set("Fonts", "general", var_font)
    config.set("Fonts", "fixed", mono_font)
    with open(qt5_path, 'w') as f:
        config.write(f)

    # Qt6ct
    qt6_dir = os.path.expanduser("~/.config/qt6ct")
    os.makedirs(qt6_dir, exist_ok=True)
    qt6_path = os.path.join(qt6_dir, "qt6ct.conf")
    config = configparser.ConfigParser()
    config.read(qt6_path)
    if not config.has_section("Fonts"):
        config.add_section("Fonts")
    config.set("Fonts", "general", var_font)
    config.set("Fonts", "fixed", mono_font)
    with open(qt6_path, 'w') as f:
        config.write(f)

    # Save to settings.ini
    settings_path = os.path.expanduser("~/.config/nscde-wayland/settings.ini")
    config = configparser.ConfigParser()
    config.read(settings_path)
    if not config.has_section("Font"):
        config.add_section("Font")
    config.set("Font", "current_fontset", "")
    for cat_label, cat_key in FONT_CATEGORIES:
        config.set("Font", cat_key, fonts_dict.get(cat_key, ""))
    with open(settings_path, 'w') as f:
        config.write(f)


def _read_current_fonts():
    """Read current font settings from settings.ini."""
    settings_path = os.path.expanduser("~/.config/nscde-wayland/settings.ini")
    config = configparser.ConfigParser()
    config.read(settings_path)
    result = {}
    for cat_label, cat_key in FONT_CATEGORIES:
        val = config.get("Font", cat_key, fallback="")
        if not val:
            # Set reasonable defaults
            if "mono" in cat_key:
                val = "monospace 12"
            else:
                val = "sans-serif 12"
        result[cat_key] = val
    return result


class FontPreview(QLabel):
    """Preview label that displays text in a specific font."""

    def set_font_string(self, font_str):
        """Parse a font string like 'Noto Sans 12' and apply it."""
        try:
            font = QFont(font_str)
            if font.family() == font_str and ' ' in font_str:
                # QFont couldn't parse, try manual parse
                parts = font_str.rsplit(' ', 1)
                if len(parts) == 2:
                    try:
                        size = int(parts[1])
                        font = QFont(parts[0], size)
                    except ValueError:
                        font = QFont(font_str)
            self.setFont(font)
        except Exception:
            pass
        self.setText("The quick brown fox 狐狸 跳过了 懒狗 ABCDEF abcdef 012345")


class FontPage(QWidget):
    """Font management page."""

    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self.font_previews = {}
        self._build_ui()
        self._load_initial()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        # Title
        title = QLabel("Font Manager")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {self.colors['bs']}")
        layout.addWidget(sep)

        # Fontset selector
        fs_layout = QHBoxLayout()
        fs_layout.addWidget(QLabel("Fontset:"))
        self.fontset_combo = QComboBox()
        self.fontset_combo.setMinimumWidth(200)
        self.fontset_combo.currentTextChanged.connect(self._on_fontset_changed)
        fs_layout.addWidget(self.fontset_combo)

        save_btn = QPushButton("Save As...")
        save_btn.clicked.connect(self._on_save_fontset)
        fs_layout.addWidget(save_btn)
        fs_layout.addStretch()
        layout.addLayout(fs_layout)

        # Font categories with previews
        cat_group = QGroupBox("Font Categories")
        cat_layout = QVBoxLayout(cat_group)

        self.font_buttons = {}
        for cat_label, cat_key in FONT_CATEGORIES:
            row = QHBoxLayout()

            lbl = QLabel(f"{cat_label}:")
            lbl.setFixedWidth(140)
            lbl.setStyleSheet(f"font: bold 11px; color: {self.colors['fg']}")
            row.addWidget(lbl)

            # Font display / pick button
            font_btn = QPushButton("sans-serif 12")
            font_btn.setMinimumWidth(250)
            font_btn.clicked.connect(lambda checked, k=cat_key, b=font_btn: self._pick_font(k, b))
            row.addWidget(font_btn)
            self.font_buttons[cat_key] = font_btn

            cat_layout.addLayout(row)

            # Preview label
            preview = FontPreview()
            preview.setStyleSheet(f"""
                border: 1px solid {self.colors['bs']};
                padding: 4px;
                background-color: {self.colors['btn_bg']};
                color: {self.colors['btn_fg']};
            """)
            preview.setFixedHeight(36)
            cat_layout.addWidget(preview)
            self.font_previews[cat_key] = preview

        layout.addWidget(cat_group)

        # Buttons
        btn_layout = QHBoxLayout()

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

    def _load_initial(self):
        """Load fontsets and current font configuration."""
        # Populate fontset combo
        self.fontset_combo.blockSignals(True)
        self.fontset_combo.addItem("(Custom)")
        for name in _list_fontsets():
            self.fontset_combo.addItem(name)
        self.fontset_combo.blockSignals(False)

        # Load current fonts
        current = _read_current_fonts()
        for cat_label, cat_key in FONT_CATEGORIES:
            font_str = current.get(cat_key, "sans-serif 12")
            self.font_buttons[cat_key].setText(font_str)
            self.font_previews[cat_key].set_font_string(font_str)

    def _on_fontset_changed(self, name):
        """Load a fontset when selected."""
        if name == "(Custom)":
            return
        fonts = _load_fontset(name)
        if fonts:
            for cat_label, cat_key in FONT_CATEGORIES:
                font_str = fonts.get(cat_key, "sans-serif 12")
                self.font_buttons[cat_key].setText(font_str)
                self.font_previews[cat_key].set_font_string(font_str)

    def _pick_font(self, cat_key, btn):
        """Open font picker dialog."""
        current_text = btn.text()
        try:
            current_font = QFont(current_text)
        except Exception:
            current_font = QFont()

        font, ok = QFontDialog.getFont(current_font, self, f"Select {cat_key}")
        if ok:
            font_str = font.toString()
            # Simplify to "Family Size" format
            family = font.family()
            size = font.pointSize()
            if size > 0:
                font_str = f"{family} {size}"
            btn.setText(font_str)
            self.font_previews[cat_key].set_font_string(font_str)
            self.fontset_combo.setCurrentText("(Custom)")

    def _on_save_fontset(self):
        """Save current font configuration as a fontset."""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Save Fontset", "Fontset name:")
        if ok and name:
            safe_name = name.replace('/', '_').replace('\\', '_').replace('..', '_')
            fonts = {}
            for cat_label, cat_key in FONT_CATEGORIES:
                fonts[cat_key] = self.font_buttons[cat_key].text()
            _save_fontset(safe_name, fonts)
            # Refresh combo
            self.fontset_combo.blockSignals(True)
            if self.fontset_combo.findText(safe_name) < 0:
                self.fontset_combo.addItem(safe_name)
            self.fontset_combo.setCurrentText(safe_name)
            self.fontset_combo.blockSignals(False)
            self.status.setText(f"Fontset '{name}' saved")

    def _on_apply(self):
        """Apply current font settings."""
        fonts = {}
        for cat_label, cat_key in FONT_CATEGORIES:
            fonts[cat_key] = self.font_buttons[cat_key].text()
        _apply_font_integration(fonts)
        self.status.setText("Font settings applied to GTK/Qt")

    def _on_close(self):
        self.window().close()
