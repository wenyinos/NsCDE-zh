"""
cc_defaultapps.py - Default Applications page for NsCDE Control Center.

Manages 8 default application categories via ~/.config/nscde-wayland/settings.ini.
"""

import os
import configparser

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QComboBox, QPushButton, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt

# Application categories and their settings keys
APP_CATEGORIES = [
    ("Terminal Emulator", "terminal", ["foot", "alacritty", "kitty", "wezterm",
                                        "gnome-terminal", "konsole", "xfce4-terminal",
                                        "qterminal", "lxterminal", "xterm"]),
    ("Text Editor", "xeditor", ["kate", "gedit", "mousepad", "pluma",
                                 "xed", "code", "sublime_text", "nano", "vim"]),
    ("File Manager", "filemgr", ["pcmanfm-qt", "nautilus", "dolphin", "thunar",
                                  "nemo", "caja", "ranger"]),
    ("Web Browser", "browser", ["firefox", "chromium", "google-chrome",
                                 "brave-browser", "vivaldi", "epiphany"]),
    ("Mail Reader", "mailreader", ["thunderbird", "evolution", "geary",
                                    "claws-mail", "mutt"]),
    ("Task Manager", "taskmgr", ["foot -e htop", "foot -e btop",
                                  "gnome-system-monitor", "ksysguard"]),
    ("Calculator", "calculator", ["gnome-calculator", "kcalc", "galculator",
                                   "qalculate-gtk", "bc"]),
    ("Print Manager", "printmgr", ["system-config-printer", "hp-toolbox",
                                     "gtklp"]),
]


def _find_installed_apps():
    """Discover installed applications from .desktop files and PATH."""
    import shutil
    installed = {}
    for cat_name, key, defaults in APP_CATEGORIES:
        found = []
        for app in defaults:
            cmd = app.split()[0]
            if shutil.which(cmd):
                found.append(app)
        installed[key] = found
    return installed


def _read_current_apps():
    """Read current settings from ~/.config/nscde-wayland/settings.ini."""
    config_path = os.path.expanduser("~/.config/nscde-wayland/settings.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    current = {}
    for cat_name, key, defaults in APP_CATEGORIES:
        val = config.get("DefaultApps", key, fallback="")
        if not val and defaults:
            val = defaults[0]
        current[key] = val
    return current


def _save_settings(apps_dict):
    """Save application settings to settings.ini."""
    config_path = os.path.expanduser("~/.config/nscde-wayland/settings.ini")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.has_section("DefaultApps"):
        config.add_section("DefaultApps")
    for key, val in apps_dict.items():
        config.set("DefaultApps", key, val)
    with open(config_path, 'w') as f:
        config.write(f)


class DefaultAppsPage(QWidget):
    """Default applications configuration page."""

    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self.combos = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        # Title
        title = QLabel("Default Applications")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {self.colors['bs']}")
        layout.addWidget(sep)

        # Description
        desc = QLabel("Select the default application for each category.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        layout.addSpacing(8)

        # Grid of category + combobox
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        installed = _find_installed_apps()
        current = _read_current_apps()

        for row, (cat_name, key, defaults) in enumerate(APP_CATEGORIES):
            lbl = QLabel(f"{cat_name}:")
            lbl.setStyleSheet(f"font: bold 12px; color: {self.colors['fg']}")
            grid.addWidget(lbl, row, 0, Qt.AlignmentFlag.AlignVCenter)

            combo = QComboBox()
            combo.setMinimumWidth(250)

            # Build list: current value + installed + defaults
            choices = []
            cur = current.get(key, "")
            if cur and cur not in choices:
                choices.append(cur)
            for app in installed.get(key, []):
                if app not in choices:
                    choices.append(app)
            for app in defaults:
                if app not in choices:
                    choices.append(app)

            combo.addItems(choices)
            if cur:
                idx = combo.findText(cur)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            combo.setEditable(True)
            self.combos[key] = combo
            grid.addWidget(combo, row, 1)

        layout.addLayout(grid)
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(apply_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self._on_close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        # Status label
        self.status = QLabel("")
        self.status.setStyleSheet(f"color: {self.colors['sel']}; font: italic 11px")
        layout.addWidget(self.status)

    def _on_apply(self):
        """Save current selections."""
        apps = {}
        for key, combo in self.combos.items():
            apps[key] = combo.currentText().strip()
        _save_settings(apps)
        self.status.setText("Settings saved to ~/.config/nscde-wayland/settings.ini")

    def _on_close(self):
        """Close the parent window."""
        window = self.window()
        if window:
            window.close()
