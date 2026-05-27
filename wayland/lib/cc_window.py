"""
cc_window.py - Window Manager configuration for NsCDE Control Center.

Edits labwc rc.xml for window behavior, theme, placement, and keyboard settings.
"""

import os
import sys
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTabWidget, QCheckBox, QComboBox, QSpinBox,
    QPushButton, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from nscde_cde import reconfigure_labwc

LABWC_RC = os.path.expanduser("~/.config/nscde-wayland/labwc/rc.xml")

DEFAULT_RC_XML = """<?xml version="1.0" encoding="UTF-8"?>
<labwc_config>
  <core>
    <decoration>server</decoration>
    <gap>0</gap>
  </core>
  <focus>
    <followMouse>no</followMouse>
    <followMouseRequiresMovement>yes</followMouseRequiresMovement>
    <raiseOnFocus>no</raiseOnFocus>
  </focus>
  <theme>
    <name>NsCDE-Wayland</name>
    <titleLayout>LIMC</titleLayout>
  </theme>
  <placement>
    <policy>center</policy>
  </placement>
  <windowSwitcher>
    <show>yes</show>
  </windowSwitcher>
</labwc_config>
"""


def _load_rc_xml():
    """Load or create labwc rc.xml."""
    if not os.path.exists(LABWC_RC):
        os.makedirs(os.path.dirname(LABWC_RC), exist_ok=True)
        with open(LABWC_RC, 'w') as f:
            f.write(DEFAULT_RC_XML)
    try:
        return ET.parse(LABWC_RC)
    except ET.ParseError:
        with open(LABWC_RC, 'w') as f:
            f.write(DEFAULT_RC_XML)
        return ET.parse(LABWC_RC)


def _save_rc_xml(tree):
    """Save rc.xml with proper formatting."""
    os.makedirs(os.path.dirname(LABWC_RC), exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(LABWC_RC, encoding="UTF-8", xml_declaration=True)


def _get_el(root, path, default=""):
    """Get text content of an XML element path."""
    el = root.find(path)
    if el is not None and el.text:
        return el.text.strip()
    return default


def _set_el(root, path, value):
    """Set text content of an XML element path, creating if needed."""
    parts = path.split('/')
    current = root
    for part in parts:
        child = current.find(part)
        if child is None:
            child = ET.SubElement(current, part)
        current = child
    current.text = str(value)


class WindowPage(QWidget):
    """Window manager configuration page with tabs."""

    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self._tree = None
        self._build_ui()
        self._load_config()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        title = QLabel("Window Manager")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {self.colors['bs']}")
        layout.addWidget(sep)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_behavior_tab(), "Behavior")
        self.tabs.addTab(self._build_theme_tab(), "Theme")
        self.tabs.addTab(self._build_placement_tab(), "Placement")
        self.tabs.addTab(self._build_keyboard_tab(), "Keyboard")
        layout.addWidget(self.tabs)

        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(apply_btn)
        defaults_btn = QPushButton("Defaults")
        defaults_btn.clicked.connect(self._on_defaults)
        btn_layout.addWidget(defaults_btn)
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self._on_close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.status = QLabel("")
        self.status.setStyleSheet(f"color: {self.colors['sel']}; font: italic 11px")
        layout.addWidget(self.status)

    def _build_behavior_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        focus_group = QGroupBox("Focus Policy")
        focus_layout = QGridLayout(focus_group)
        self.cb_follow_mouse = QCheckBox("Follow mouse (focus follows pointer)")
        focus_layout.addWidget(self.cb_follow_mouse, 0, 0)
        self.cb_raise_on_focus = QCheckBox("Raise window on focus")
        focus_layout.addWidget(self.cb_raise_on_focus, 1, 0)
        layout.addWidget(focus_group)

        deco_group = QGroupBox("Decoration")
        deco_layout = QGridLayout(deco_group)
        deco_layout.addWidget(QLabel("Style:"), 0, 0)
        self.combo_decoration = QComboBox()
        self.combo_decoration.addItems(["server", "client", "none"])
        deco_layout.addWidget(self.combo_decoration, 0, 1)
        layout.addWidget(deco_group)

        layout.addStretch()
        return tab

    def _build_theme_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        theme_group = QGroupBox("Theme")
        theme_layout = QGridLayout(theme_group)
        theme_layout.addWidget(QLabel("Theme name:"), 0, 0)
        self.combo_theme = QComboBox()
        self.combo_theme.setEditable(True)
        self.combo_theme.addItems(["NsCDE-Wayland", "Clearlooks", "Numix"])
        theme_layout.addWidget(self.combo_theme, 0, 1)
        theme_layout.addWidget(QLabel("Title layout:"), 1, 0)
        self.combo_title_layout = QComboBox()
        self.combo_title_layout.setEditable(True)
        self.combo_title_layout.addItems(["LIMC", "LMIC", "IMLC", "MILC", "LIM", "LIC"])
        theme_layout.addWidget(self.combo_title_layout, 1, 1)
        layout.addWidget(theme_group)

        layout.addStretch()
        return tab

    def _build_placement_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        place_group = QGroupBox("Window Placement")
        place_layout = QGridLayout(place_group)
        place_layout.addWidget(QLabel("Policy:"), 0, 0)
        self.combo_placement = QComboBox()
        self.combo_placement.addItems(["center", "automatic", "cursor", "top_left"])
        place_layout.addWidget(self.combo_placement, 0, 1)
        layout.addWidget(place_group)

        switcher_group = QGroupBox("Window Switcher")
        switcher_layout = QGridLayout(switcher_group)
        self.cb_switcher = QCheckBox("Show window switcher (Alt-Tab)")
        switcher_layout.addWidget(self.cb_switcher, 0, 0)
        layout.addWidget(switcher_group)

        layout.addStretch()
        return tab

    def _build_keyboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info = QLabel(
            "Keyboard shortcuts are configured in labwc rc.xml\n"
            "directly. Common shortcuts:\n\n"
            "  Alt+F4      Close window\n"
            "  Alt+Return  Maximize toggle\n"
            "  Alt+Space   Window menu\n"
            "  Alt+Tab     Window switcher\n"
            "  Super+L     Lock screen\n\n"
            "Edit ~/.config/nscde-wayland/labwc/rc.xml for custom keybinds."
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()
        return tab

    def _load_config(self):
        """Load current labwc configuration into UI."""
        self._tree = _load_rc_xml()
        root = self._tree.getroot()

        self.cb_follow_mouse.setChecked(_get_el(root, 'focus/followMouse') == 'yes')
        self.cb_raise_on_focus.setChecked(_get_el(root, 'focus/raiseOnFocus') == 'yes')

        deco = _get_el(root, 'core/decoration', 'server')
        idx = self.combo_decoration.findText(deco)
        if idx >= 0:
            self.combo_decoration.setCurrentIndex(idx)

        theme = _get_el(root, 'theme/name', 'NsCDE-Wayland')
        self.combo_theme.setCurrentText(theme)

        tl = _get_el(root, 'theme/titleLayout', 'LIMC')
        self.combo_title_layout.setCurrentText(tl)

        policy = _get_el(root, 'placement/policy', 'center')
        self.combo_placement.setCurrentText(policy)

        self.cb_switcher.setChecked(
            _get_el(root, 'windowSwitcher/show', 'yes') == 'yes'
        )

    def _on_defaults(self):
        self.cb_follow_mouse.setChecked(False)
        self.cb_raise_on_focus.setChecked(False)
        self.combo_decoration.setCurrentText("server")
        self.combo_theme.setCurrentText("NsCDE-Wayland")
        self.combo_title_layout.setCurrentText("LIMC")
        self.combo_placement.setCurrentText("center")
        self.cb_switcher.setChecked(True)
        self.status.setText("Reset to defaults")

    def _on_apply(self):
        root = self._tree.getroot()

        _set_el(root, 'focus/followMouse',
                'yes' if self.cb_follow_mouse.isChecked() else 'no')
        _set_el(root, 'focus/raiseOnFocus',
                'yes' if self.cb_raise_on_focus.isChecked() else 'no')
        _set_el(root, 'core/decoration', self.combo_decoration.currentText())
        _set_el(root, 'theme/name', self.combo_theme.currentText())
        _set_el(root, 'theme/titleLayout', self.combo_title_layout.currentText())
        _set_el(root, 'placement/policy', self.combo_placement.currentText())
        _set_el(root, 'windowSwitcher/show',
                'yes' if self.cb_switcher.isChecked() else 'no')

        _save_rc_xml(self._tree)
        reconfigure_labwc()
        self.status.setText("Configuration saved and labwc reconfigured")

    def _on_close(self):
        self.window().close()
