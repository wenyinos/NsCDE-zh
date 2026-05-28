"""
cc_mouse.py - Mouse configuration for NsCDE Control Center.

Edits labwc rc.xml <mouse> section for mouse button bindings.
"""

import os
import sys
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QDialog, QFormLayout, QComboBox,
    QDialogButtonBox, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from nscde_cde import reconfigure_labwc
from cc_window import _load_rc_xml, _save_rc_xml

# labwc mouse context names
MOUSE_CONTEXTS = [
    "Root", "TitleBar", "Close", "Maximize", "Iconify",
    "Client", "Frame", "Border", "Desktop",
]

# Mouse buttons
MOUSE_BUTTONS = ["Left", "Middle", "Right", "ScrollUp", "ScrollDown"]

# Mouse actions (binding types)
MOUSE_BIND_ACTIONS = ["Press", "Click", "Drag", "DoubleClick"]

# Window actions available for mousebinds
WINDOW_ACTIONS = [
    "Focus", "Raise", "Move", "Resize", "Close",
    "ToggleMaximize", "Iconify", "ShowMenu",
    "ToggleFullscreen", "Shade", "MoveToEdge",
    "NextWindow", "PreviousWindow",
]

# Default mouse config per context
DEFAULT_MOUSE = {
    "Root": [
        {"button": "Right", "bind_action": "Press",
         "actions": [{"name": "ShowMenu", "attrs": {"menu": "root-menu"}}]},
    ],
    "TitleBar": [
        {"button": "Left", "bind_action": "Press",
         "actions": [{"name": "Focus"}, {"name": "Raise"}]},
        {"button": "Left", "bind_action": "Drag",
         "actions": [{"name": "Move"}]},
        {"button": "Left", "bind_action": "DoubleClick",
         "actions": [{"name": "ToggleMaximize"}]},
        {"button": "Right", "bind_action": "Press",
         "actions": [{"name": "Focus"}, {"name": "Raise"}]},
    ],
    "Close": [
        {"button": "Left", "bind_action": "Click",
         "actions": [{"name": "Close"}]},
    ],
    "Maximize": [
        {"button": "Left", "bind_action": "Click",
         "actions": [{"name": "ToggleMaximize"}]},
    ],
    "Iconify": [
        {"button": "Left", "bind_action": "Click",
         "actions": [{"name": "Iconify"}]},
    ],
    "Client": [
        {"button": "Left", "bind_action": "Press",
         "actions": [{"name": "Focus"}, {"name": "Raise"}]},
    ],
}


def _parse_mousebinds(root):
    """Extract mouse bindings from rc.xml root. Returns dict of context -> list."""
    result = {}
    mouse_section = root.find('mouse')
    if mouse_section is None:
        return result
    for ctx in mouse_section.findall('context'):
        ctx_name = ctx.get('name', '')
        binds = []
        for mb in ctx.findall('mousebind'):
            button = mb.get('button', 'Left')
            bind_action = mb.get('action', 'Press')
            actions = []
            for act in mb.findall('action'):
                name = act.get('name', '')
                attrs = {k: v for k, v in act.attrib.items() if k != 'name'}
                actions.append({'name': name, 'attrs': attrs})
            binds.append({
                'button': button,
                'bind_action': bind_action,
                'actions': actions,
            })
        result[ctx_name] = binds
    return result


def _format_actions_display(actions):
    """Format action list for display."""
    parts = []
    for act in actions:
        name = act['name']
        if act['attrs']:
            val = list(act['attrs'].values())[0]
            parts.append(f"{name}({val})")
        else:
            parts.append(name)
    return ', '.join(parts)


class MousebindEditDialog(QDialog):
    """Dialog for adding/editing a mouse binding."""

    def __init__(self, colors, mousebind=None, parent=None):
        super().__init__(parent)
        self.colors = colors
        self.mousebind = mousebind
        self.setWindowTitle("Edit Mouse Binding" if mousebind else "Add Mouse Binding")
        self.setMinimumWidth(380)
        self._build_ui()
        if mousebind:
            self._load_bind(mousebind)

    def _build_ui(self):
        layout = QFormLayout(self)

        self.combo_button = QComboBox()
        self.combo_button.addItems(MOUSE_BUTTONS)
        layout.addRow("Button:", self.combo_button)

        self.combo_bind_action = QComboBox()
        self.combo_bind_action.addItems(MOUSE_BIND_ACTIONS)
        layout.addRow("Trigger:", self.combo_bind_action)

        self.combo_action = QComboBox()
        self.combo_action.setEditable(True)
        self.combo_action.addItems(WINDOW_ACTIONS)
        layout.addRow("Action:", self.combo_action)

        self.combo_param = QComboBox()
        self.combo_param.setEditable(True)
        self.combo_param.addItem("")
        self.combo_param.addItems(["root-menu", "client-menu"])
        layout.addRow("Menu:", self.combo_param)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _load_bind(self, mb):
        idx = self.combo_button.findText(mb['button'])
        if idx >= 0:
            self.combo_button.setCurrentIndex(idx)
        idx = self.combo_bind_action.findText(mb['bind_action'])
        if idx >= 0:
            self.combo_bind_action.setCurrentIndex(idx)
        if mb['actions']:
            act = mb['actions'][0]
            self.combo_action.setCurrentText(act['name'])
            if act['attrs']:
                self.combo_param.setCurrentText(list(act['attrs'].values())[0])

    def get_result(self):
        """Return mousebind dict."""
        action_name = self.combo_action.currentText().strip()
        param = self.combo_param.currentText().strip()
        attrs = {}
        if action_name == 'ShowMenu' and param:
            attrs['menu'] = param
        elif action_name in ('MoveToEdge', 'SnapToEdge') and param:
            attrs['direction'] = param

        return {
            'button': self.combo_button.currentText(),
            'bind_action': self.combo_bind_action.currentText(),
            'actions': [{'name': action_name, 'attrs': attrs}],
        }


class MousePage(QWidget):
    """Mouse configuration page."""

    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self._tree = None
        self._mousebinds = {}  # context -> list of mousebinds
        self._build_ui()
        self._load_config()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        title = QLabel("Mouse Configuration")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {self.colors['bs']}")
        layout.addWidget(sep)

        # Context selector
        ctx_layout = QHBoxLayout()
        ctx_layout.addWidget(QLabel("Context:"))
        self.combo_context = QComboBox()
        self.combo_context.addItems(MOUSE_CONTEXTS)
        self.combo_context.currentTextChanged.connect(self._on_context_changed)
        ctx_layout.addWidget(self.combo_context)
        ctx_layout.addStretch()
        layout.addLayout(ctx_layout)

        # Bindings table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Button", "Trigger", "Action"])
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
        self._mousebinds = _parse_mousebinds(root)
        self._refresh_table()

    def _current_context(self):
        return self.combo_context.currentText()

    def _refresh_table(self):
        ctx = self._current_context()
        binds = self._mousebinds.get(ctx, [])
        self.table.setRowCount(len(binds))
        for row, mb in enumerate(binds):
            self.table.setItem(row, 0, QTableWidgetItem(mb['button']))
            self.table.setItem(row, 1, QTableWidgetItem(mb['bind_action']))
            self.table.setItem(row, 2, QTableWidgetItem(
                _format_actions_display(mb['actions'])
            ))

    def _on_context_changed(self, _ctx):
        self._refresh_table()

    def _on_add(self):
        dlg = MousebindEditDialog(self.colors, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            mb = dlg.get_result()
            ctx = self._current_context()
            if ctx not in self._mousebinds:
                self._mousebinds[ctx] = []
            self._mousebinds[ctx].append(mb)
            self._refresh_table()
            self.status.setText(f"Added binding to {ctx}")

    def _on_edit(self):
        row = self.table.currentRow()
        if row < 0:
            return
        ctx = self._current_context()
        binds = self._mousebinds.get(ctx, [])
        if row >= len(binds):
            return
        dlg = MousebindEditDialog(self.colors, binds[row], parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            binds[row] = dlg.get_result()
            self._refresh_table()
            self.status.setText(f"Updated binding in {ctx}")

    def _on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            return
        ctx = self._current_context()
        binds = self._mousebinds.get(ctx, [])
        if row >= len(binds):
            return
        mb = binds[row]
        reply = QMessageBox.question(
            self, "Delete Binding",
            f"Delete {mb['button']} {mb['bind_action']} in {ctx}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del binds[row]
            self._refresh_table()
            self.status.setText(f"Deleted binding from {ctx}")

    def _on_apply(self):
        root = self._tree.getroot()
        old_mouse = root.find('mouse')
        if old_mouse is not None:
            root.remove(old_mouse)
        mouse_el = ET.SubElement(root, 'mouse')
        # Add default element
        ET.SubElement(mouse_el, 'default')
        for ctx_name in MOUSE_CONTEXTS:
            binds = self._mousebinds.get(ctx_name, [])
            if not binds:
                continue
            ctx_el = ET.SubElement(mouse_el, 'context', name=ctx_name)
            for mb in binds:
                mb_el = ET.SubElement(
                    ctx_el, 'mousebind',
                    button=mb['button'], action=mb['bind_action']
                )
                for act in mb['actions']:
                    attrs = {'name': act['name']}
                    attrs.update(act['attrs'])
                    ET.SubElement(mb_el, 'action', **attrs)
        _save_rc_xml(self._tree)
        reconfigure_labwc()
        self.status.setText("Mouse configuration saved and labwc reconfigured")

    def _on_defaults(self):
        reply = QMessageBox.question(
            self, "Reset Defaults",
            "Reset mouse bindings to NsCDE defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._mousebinds = {k: list(v) for k, v in DEFAULT_MOUSE.items()}
            self._refresh_table()
            self.status.setText("Reset to NsCDE default mouse bindings")

    def _on_close(self):
        self.window().close()
