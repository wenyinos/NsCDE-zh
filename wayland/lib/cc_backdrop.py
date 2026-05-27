"""
cc_backdrop.py - Backdrop/Wallpaper manager for NsCDE Control Center.

Supports two modes:
  - Backdrop: XPM (.pm) CDE-style tiled backgrounds
  - Photo: PNG/JPG wallpaper images
"""

import os
import subprocess
import tempfile

_script_dir = os.path.dirname(os.path.abspath(__file__))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QListWidget, QListWidgetItem, QPushButton, QCheckBox,
    QComboBox, QFileDialog, QSplitter, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap

# Asset paths
ASSETS_DIR = os.path.join(os.path.dirname(_script_dir), "assets")
BACKDROPS_DIR = os.path.join(ASSETS_DIR, "backdrops")
PHOTOS_DIR = os.path.join(ASSETS_DIR, "photos")


def _get_user_backdrops_dir():
    d = os.path.expanduser("~/.config/nscde-wayland/backdrops")
    os.makedirs(d, exist_ok=True)
    return d


def _get_user_photos_dir():
    d = os.path.expanduser("~/.config/nscde-wayland/photos")
    os.makedirs(d, exist_ok=True)
    return d


def _xpm_to_pixmap(xpm_path, size=200):
    """Convert XPM file to QPixmap. Uses Pillow for conversion."""
    try:
        from PIL import Image
        img = Image.open(xpm_path)
        # Scale to thumbnail
        img.thumbnail((size, size), Image.Resampling.NEAREST)
        # Save to temp PNG
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        img.save(tmp.name, "PNG")
        pm = QPixmap(tmp.name)
        os.unlink(tmp.name)
        return pm
    except Exception:
        return None


def _get_outputs():
    """Detect connected display outputs via wlr-randr."""
    outputs = []
    try:
        r = subprocess.run(["wlr-randr"], capture_output=True, text=True, timeout=3)
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                if line and not line.startswith(" "):
                    name = line.split()[0]
                    if name:
                        outputs.append(name)
    except Exception:
        pass
    return outputs


def _get_outputs_conf_path():
    return os.path.expanduser("~/.config/nscde-wayland/outputs.conf")


def _load_outputs_conf():
    """Load per-output wallpaper config. Returns dict of {output: (image, mode)}."""
    conf = {}
    path = _get_outputs_conf_path()
    if not os.path.isfile(path):
        return conf
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                img = val.split(":")[0]
                mode = val.split(":")[1] if ":" in val else "fill"
                conf[key.strip()] = (img, mode)
    except Exception:
        pass
    return conf


def _save_outputs_conf(conf):
    """Save per-output wallpaper config. conf = {output: (image, mode)}."""
    path = _get_outputs_conf_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("# Per-output wallpaper configuration\n")
        f.write("# format: OUTPUT=image_path:mode\n\n")
        for output, (img, mode) in sorted(conf.items()):
            f.write(f"{output}={img}:{mode}\n")


def _set_wallpaper(image_path, mode="fill"):
    """Set wallpaper using swaybg (kill old instance first)."""
    # Kill existing swaybg/wbg
    for cmd in ["swaybg", "wbg"]:
        subprocess.run(["pkill", "-x", cmd], capture_output=True)
    # Start new swaybg
    try:
        subprocess.Popen(
            ["swaybg", "-i", image_path, "-m", mode],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        # Fallback to wbg
        try:
            subprocess.Popen(
                ["wbg", image_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            pass


class BackdropPage(QWidget):
    """Backdrop/wallpaper management page."""

    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self._photo_mode = False
        self._preview_path = None
        self._build_ui()
        self._load_list()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        # Title
        title = QLabel("Backdrop Manager")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {self.colors['bs']}")
        layout.addWidget(sep)

        # Mode toggle
        mode_layout = QHBoxLayout()
        self.photo_check = QCheckBox("Use a photo or picture")
        self.photo_check.toggled.connect(self._on_mode_toggle)
        mode_layout.addWidget(self.photo_check)
        mode_layout.addStretch()

        # Variant/stretch mode
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["fill", "stretch", "tile", "center"])
        self.mode_combo.setCurrentText("fill")
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # Main content: list + preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: list
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(64, 64))
        self.list_widget.currentItemChanged.connect(self._on_selection_changed)
        splitter.addWidget(self.list_widget)

        # Right: preview
        preview_frame = QFrame()
        preview_frame.setMinimumWidth(220)
        preview_layout = QVBoxLayout(preview_frame)
        self.preview_label = QLabel("No preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(200, 200)
        self.preview_label.setStyleSheet(
            f"border: 1px solid {self.colors['bs']}; "
            f"background-color: {self.colors['btn_bg']}"
        )
        preview_layout.addWidget(self.preview_label)

        self.name_label = QLabel("")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        preview_layout.addWidget(self.name_label)

        splitter.addWidget(preview_frame)
        splitter.setSizes([300, 220])
        layout.addWidget(splitter)

        # Per-output wallpaper section
        self._output_combos = {}
        outputs = _get_outputs()
        if len(outputs) > 1:
            out_group = QGroupBox("Per-Output Wallpapers")
            out_layout = QGridLayout(out_group)
            saved_conf = _load_outputs_conf()
            for row, output in enumerate(outputs):
                out_layout.addWidget(QLabel(f"{output}:"), row, 0)
                combo = QComboBox()
                combo.setMinimumWidth(250)
                combo.setEditable(True)
                combo.addItem("(default)")
                self._populate_output_combo(combo)
                # Restore saved value
                if output in saved_conf:
                    img, _ = saved_conf[output]
                    idx = combo.findText(os.path.basename(img))
                    if idx >= 0:
                        combo.setCurrentIndex(idx)
                    else:
                        combo.setCurrentText(img)
                out_layout.addWidget(combo, row, 1)
                self._output_combos[output] = combo
            apply_out_btn = QPushButton("Apply Per-Output")
            apply_out_btn.clicked.connect(self._on_apply_per_output)
            out_layout.addWidget(apply_out_btn, len(outputs), 1)
            layout.addWidget(out_group)

        # Buttons
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(self.apply_btn)

        self.add_btn = QPushButton("Add...")
        self.add_btn.clicked.connect(self._on_add)
        btn_layout.addWidget(self.add_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self._on_close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        # Status
        self.status = QLabel("")
        self.status.setStyleSheet(f"color: {self.colors['sel']}; font: italic 11px")
        layout.addWidget(self.status)

    def _on_mode_toggle(self, checked):
        self._photo_mode = checked
        self._load_list()

    def _load_list(self):
        """Populate the list with backdrops or photos."""
        self.list_widget.clear()
        if self._photo_mode:
            dirs = [PHOTOS_DIR, _get_user_photos_dir()]
            exts = {".png", ".jpg", ".jpeg", ".webp"}
        else:
            dirs = [BACKDROPS_DIR, _get_user_backdrops_dir()]
            exts = {".pm", ".xpm"}

        seen = set()
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                ext = os.path.splitext(f)[1].lower()
                if ext in exts and f not in seen:
                    seen.add(f)
                    item = QListWidgetItem(f)
                    item.setData(Qt.ItemDataRole.UserRole, os.path.join(d, f))

                    # Generate thumbnail
                    full_path = os.path.join(d, f)
                    if self._photo_mode:
                        pm = QPixmap(full_path)
                        if not pm.isNull():
                            item.setIcon(
                                pm.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
                            )
                    else:
                        pm = _xpm_to_pixmap(full_path, 64)
                        if pm and not pm.isNull():
                            item.setIcon(pm)

                    self.list_widget.addItem(item)

    def _on_selection_changed(self, current, previous):
        if not current:
            self.preview_label.setText("No preview")
            self.name_label.setText("")
            self._preview_path = None
            return

        path = current.data(Qt.ItemDataRole.UserRole)
        self._preview_path = path
        name = os.path.basename(path)
        self.name_label.setText(name)

        if self._photo_mode:
            pm = QPixmap(path)
            if not pm.isNull():
                scaled = pm.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
                self.preview_label.setPixmap(scaled)
            else:
                self.preview_label.setText("Cannot preview")
        else:
            pm = _xpm_to_pixmap(path, 200)
            if pm and not pm.isNull():
                self.preview_label.setPixmap(pm)
            else:
                self.preview_label.setText("Cannot preview")

    def _on_apply(self):
        if not self._preview_path:
            self.status.setText("Select a backdrop first")
            return
        mode = self.mode_combo.currentText()
        _set_wallpaper(self._preview_path, mode)
        self.status.setText(f"Wallpaper set: {os.path.basename(self._preview_path)}")

    def _on_add(self):
        if self._photo_mode:
            filt = "Images (*.png *.jpg *.jpeg *.webp);;All (*)"
            dest_dir = _get_user_photos_dir()
        else:
            filt = "X Pixmap (*.pm *.xpm);;All (*)"
            dest_dir = _get_user_backdrops_dir()

        path, _ = QFileDialog.getOpenFileName(self, "Add backdrop", "", filt)
        if path:
            import shutil
            dest = os.path.join(dest_dir, os.path.basename(path))
            shutil.copy2(path, dest)
            self._load_list()
            self.status.setText(f"Added: {os.path.basename(path)}")

    def _populate_output_combo(self, combo):
        """Fill a combo box with available wallpaper files."""
        for d in [PHOTOS_DIR, _get_user_photos_dir(),
                  BACKDROPS_DIR, _get_user_backdrops_dir()]:
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                ext = os.path.splitext(f)[1].lower()
                if ext in {".png", ".jpg", ".jpeg", ".webp", ".pm", ".xpm"}:
                    full = os.path.join(d, f)
                    combo.addItem(f, full)

    def _on_apply_per_output(self):
        """Save per-output config and restart swaybg."""
        mode = self.mode_combo.currentText()
        conf = {}
        for output, combo in self._output_combos.items():
            text = combo.currentText()
            if text == "(default)":
                continue
            # Try to resolve full path from combo data
            idx = combo.currentIndex()
            full_path = combo.itemData(idx) if idx >= 0 else None
            if not full_path or not os.path.isfile(full_path):
                # Maybe user typed a path directly
                full_path = text if os.path.isfile(text) else None
            if full_path:
                conf[output] = (full_path, mode)
        if not conf:
            self.status.setText("No per-output wallpapers configured")
            return
        _save_outputs_conf(conf)
        # Restart swaybg with per-output args
        for cmd in ["swaybg", "wbg"]:
            subprocess.run(["pkill", "-x", cmd], capture_output=True)
        args = []
        for output, (img, m) in conf.items():
            args.extend(["-o", output, "-i", img, "-m", m])
        try:
            subprocess.Popen(["swaybg"] + args,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            pass
        self.status.setText(f"Per-output wallpapers applied ({len(conf)} outputs)")

    def _on_close(self):
        self.window().close()
