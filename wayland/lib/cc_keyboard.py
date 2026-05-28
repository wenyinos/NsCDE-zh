"""
cc_keyboard.py - Keyboard shortcut configuration for NsCDE Control Center.

Edits labwc rc.xml <keyboard> section for keybind management.
"""

import os
import sys
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QDialog, QFormLayout, QLineEdit,
    QComboBox, QDialogButtonBox, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from nscde_cde import reconfigure_labwc
from cc_window import _load_rc_xml, _save_rc_xml

# Common labwc actions with their parameters
LABWC_ACTIONS = [
    "ToggleMaximize", "Close", "Iconify", "ShowMenu",
    "NextWindow", "PreviousWindow", "GoToDesktop",
    "Execute", "Focus", "Raise", "Move", "Resize",
    "ToggleFullscreen", "ToggleDecorations", "Shade",
    "MoveToEdge", "SnapToEdge", "SendToDesktop",
    "ToggleKeybinds", "Exit",
]

# Modifier key labels
MODIFIERS = {
    "A": "Alt",
    "C": "Ctrl",
    "S": "Shift",
    "W": "Super",
}

# Predefined common shortcuts
PRESETS = [
    ("A-Return", "ToggleMaximize", "", "Maximize toggle"),
    ("A-F4", "Close", "", "Close window"),
    ("A-Space", "ShowMenu", "root-menu", "Window menu"),
    ("A-Tab", "NextWindow", "", "Next window"),
    ("A-S-Tab", "PreviousWindow", "", "Previous window"),
    ("W-Return", "Execute", "foot", "Terminal"),
    ("W-f", "Execute", "pcmanfm-qt", "File manager"),
    ("A-F2", "Execute", "fuzzel", "Run dialog"),
    ("W-l", "Execute", "nscde-wayland-lock", "Lock screen"),
    ("C-A-Delete", "Execute", "nscde-wayland-logout", "Logout dialog"),
]


def _parse_keybinds(root):
    """Extract keybinds from rc.xml root. Returns list of dicts."""
    keybinds = []
    kb_section = root.find('keyboard')
    if kb_section is None:
        return keybinds
    for kb in kb_section.findall('keybind'):
        key = kb.get('key', '')
        actions = []
        for act in kb.findall('action'):
            name = act.get('name', '')
            # Collect all attributes except 'name'
            attrs = {k: v for k, v in act.attrib.items() if k != 'name'}
            # Also get text content if present (for Execute command)
            text = act.text.strip() if act.text else ''
            actions.append({'name': name, 'attrs': attrs, 'text': text})
        keybinds.append({'key': key, 'actions': actions})
    return keybinds


def _format_key_display(key_str):
    """Convert labwc key notation to display string. e.g. 'A-Return' -> 'Alt+Return'."""
    parts = key_str.split('-')
    display_parts = []
    for p in parts[:-1]:
        display_parts.append(MODIFIERS.get(p, p))
    display_parts.append(parts[-1] if parts else '')
    return '+'.join(display_parts)


def _format_action_display(actions):
    """Format action list to display string."""
    parts = []
    for act in actions:
        name = act['name']
        if act['attrs']:
            # Show first attribute value
            val = list(act['attrs'].values())[0]
            parts.append(f"{name}({val})")
        elif act['text']:
            parts.append(f"{name}({act['text']})")
        else:
            parts.append(name)
    return ', '.join(parts)


class KeybindEditDialog(QDialog):
    """Dialog for adding/editing a keybind."""

    def __init__(self, colors, keybind=None, parent=None):
        super().__init__(parent)
        self.colors = colors
        self.keybind = keybind  # None for new, dict for edit
        self.setWindowTitle("Edit Keybind" if keybind else "Add Keybind")
        self.setMinimumWidth(400)
        self._build_ui()
        if keybind:
            self._load_keybind(keybind)

    def _build_ui(self):
        layout = QFormLayout(self)

        # Key combination
        self.edit_key = QLineEdit()
        self.edit_key.setPlaceholderText("e.g. A-F4, W-Return, C-A-Delete")
        layout.addRow("Key combination:", self.edit_key)

        # Preset selector
        self.combo_preset = QComboBox()
        self.combo_preset.addItem("-- Select preset --")
        for key, action, param, desc in PRESETS:
            self.combo_preset.addItem(f"{desc} ({key})")
        self.combo_preset.currentIndexChanged.connect(self._on_preset_selected)
        layout.addRow("Presets:", self.combo_preset)

        # Action
        self.combo_action = QComboBox()
        self.combo_action.setEditable(True)
        self.combo_action.addItems(LABWC_ACTIONS)
        layout.addRow("Action:", self.combo_action)

        # Action parameter
        self.edit_param = QLineEdit()
        self.edit_param.setPlaceholderText("e.g. foot, root-menu, left, right")
        layout.addRow("Parameter:", self.edit_param)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _on_preset_selected(self, index):
        if index <= 0:
            return
        key, action, param, _ = PRESETS[index - 1]
        self.edit_key.setText(key)
        self.combo_action.setCurrentText(action)
        self.edit_param.setText(param)

    def _load_keybind(self, kb):
        self.edit_key.setText(kb['key'])
        if kb['actions']:
            act = kb['actions'][0]
            self.combo_action.setCurrentText(act['name'])
            if act['attrs']:
                self.edit_param.setText(list(act['attrs'].values())[0])
            elif act['text']:
                self.edit_param.setText(act['text'])

    def get_result(self):
        """Return keybind dict from dialog fields."""
        key = self.edit_key.text().strip()
        action_name = self.combo_action.currentText().strip()
        param = self.edit_param.text().strip()

        action = {'name': action_name, 'attrs': {}, 'text': ''}
        if action_name == 'Execute' and param:
            action['text'] = param
        elif action_name in ('ShowMenu',) and param:
            action['attrs']['menu'] = param
        elif action_name in ('GoToDesktop', 'SendToDesktop') and param:
            action['attrs']['to'] = param
        elif action_name in ('MoveToEdge', 'SnapToEdge') and param:
            action['attrs']['direction'] = param
        elif param:
            action['text'] = param

        return {'key': key, 'actions': [action]}


class KeyboardPage(QWidget):
    """Keyboard shortcut configuration page."""

    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self._tree = None
        self._keybinds = []
        self._build_ui()
        self._load_config()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        title = QLabel("Keyboard Shortcuts")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {self.colors['bs']}")
        layout.addWidget(sep)

        # Keybind table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Key", "Action", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._on_edit)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._on_add)
        btn_layout.addWidget(add_btn)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self._on_edit)
        btn_layout.addWidget(edit_btn)
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self._on_delete)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(apply_btn)
        defaults_btn = QPushButton("Defaults")
        defaults_btn.clicked.connect(self._on_defaults)
        btn_layout.addWidget(defaults_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self._on_close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.status = QLabel("")
        self.status.setStyleSheet(
            f"color: {self.colors['sel']}; font: italic 11px"
        )
        layout.addWidget(self.status)

    def _load_config(self):
        self._tree = _load_rc_xml()
        root = self._tree.getroot()
        self._keybinds = _parse_keybinds(root)
        self._refresh_table()

    def _refresh_table(self):
        self.table.setRowCount(len(self._keybinds))
        for row, kb in enumerate(self._keybinds):
            self.table.setItem(row, 0, QTableWidgetItem(_format_key_display(kb['key'])))
            self.table.setItem(row, 1, QTableWidgetItem(_format_action_display(kb['actions'])))
            # Description from preset if matched
            desc = ""
            for key, action, param, d in PRESETS:
                if kb['key'] == key:
                    desc = d
                    break
            self.table.setItem(row, 2, QTableWidgetItem(desc))

    def _on_add(self):
        dlg = KeybindEditDialog(self.colors, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            kb = dlg.get_result()
            if kb['key']:
                self._keybinds.append(kb)
                self._refresh_table()
                self.status.setText(f"Added: {_format_key_display(kb['key'])}")

    def _on_edit(self):
        row = self.table.currentRow()
        if row < 0:
            return
        dlg = KeybindEditDialog(self.colors, self._keybinds[row], parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            kb = dlg.get_result()
            if kb['key']:
                self._keybinds[row] = kb
                self._refresh_table()
                self.status.setText(f"Updated: {_format_key_display(kb['key'])}")

    def _on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            return
        kb = self._keybinds[row]
        reply = QMessageBox.question(
            self, "Delete Keybind",
            f"Delete shortcut {_format_key_display(kb['key'])}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self._keybinds[row]
            self._refresh_table()
            self.status.setText(f"Deleted: {_format_key_display(kb['key'])}")

    def _on_apply(self):
        root = self._tree.getroot()
        # Remove existing keyboard section
        old_kb = root.find('keyboard')
        if old_kb is not None:
            root.remove(old_kb)
        # Create new keyboard section
        kb_el = ET.SubElement(root, 'keyboard')
        for bind in self._keybinds:
            kb = ET.SubElement(kb_el, 'keybind', key=bind['key'])
            for act in bind['actions']:
                attrs = {'name': act['name']}
                attrs.update(act['attrs'])
                action_el = ET.SubElement(kb, 'action', **attrs)
                if act['text']:
                    action_el.text = act['text']
        _save_rc_xml(self._tree)
        reconfigure_labwc()
        self.status.setText("Keyboard shortcuts saved and labwc reconfigured")

    def _on_defaults(self):
        reply = QMessageBox.question(
            self, "Reset Defaults",
            "Reset all keyboard shortcuts to NsCDE defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._keybinds = []
            for key, action, param, _ in PRESETS:
                kb = {'key': key, 'actions': [{'name': action, 'attrs': {}, 'text': ''}]}
                if action == 'Execute':
                    kb['actions'][0]['text'] = param
                elif action == 'ShowMenu':
                    kb['actions'][0]['attrs']['menu'] = param
                elif action == 'GoToDesktop':
                    kb['actions'][0]['attrs']['to'] = param
                self._keybinds.append(kb)
            self._refresh_table()
            self.status.setText("Reset to NsCDE default shortcuts")

    def _on_close(self):
        self.window().close()
