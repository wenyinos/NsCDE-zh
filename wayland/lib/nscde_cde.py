"""
nscde_cde.py - Shared CDE styling and palette utilities for NsCDE-Wayland.

Extracted from nscde-panel to be reused by nscde-control-center and other tools.
"""

import os
import sys
import subprocess

# NsCDE Colorset 1 - Button colors (gray)
NSDECDE_CS1_BG = '#999999'
NSDECDE_CS1_FG = '#ffffff'
NSDECDE_CS1_HI = '#d2d2d3'
NSDECDE_CS1_SH = '#4f4f50'

# NsCDE Colorset 23 - Front Panel background (warm beige)
NSDECDE_CS23_BG = '#c6b2a8'
NSDECDE_CS23_FG = '#ffffff'
NSDECDE_CS23_HI = '#e7deda'
NSDECDE_CS23_SH = '#6b605b'

NSDECDE_CS14_GAP = '#d2d2d3'
NSDECDE_CS15_GAP = '#4f4f50'

# Font defaults
CJK_FONT = '"Noto Sans CJK SC", "WenQuanYi Micro Hei", sans-serif'
MONO_FONT = '"Noto Sans Mono CJK SC", "WenQuanYi Micro Hei Mono", monospace'


def find_default_palette():
    """Find default palette file, checking user config then system paths."""
    for path in [
        os.path.expanduser("~/.config/nscde-wayland/palette.dp"),
        os.path.expanduser("~/.NsCDE/palettes/GrayScale.dp"),
        "/usr/local/share/nscde-wayland/assets/palettes/GrayScale.dp",
        "/usr/share/nscde-wayland/assets/palettes/GrayScale.dp",
    ]:
        if os.path.exists(path):
            return path
    return None


def load_palette_colors(palette_file=None):
    """Load colors from CDE palette file via colorcalc.

    Returns a dict with keys: bg, fg, ts, bs, sel,
    btn_bg, btn_ts, btn_bs, btn_fg, gap_hi, gap_lo.
    Falls back to NsCDE default colors if colorcalc fails.
    """
    colors = {
        'bg': NSDECDE_CS23_BG, 'fg': NSDECDE_CS23_FG,
        'ts': NSDECDE_CS23_HI, 'bs': NSDECDE_CS23_SH,
        'sel': '#a0a0a0',
        'btn_bg': NSDECDE_CS1_BG, 'btn_fg': NSDECDE_CS1_FG,
        'btn_ts': NSDECDE_CS1_HI, 'btn_bs': NSDECDE_CS1_SH,
        'gap_hi': NSDECDE_CS14_GAP, 'gap_lo': NSDECDE_CS15_GAP,
    }
    if not palette_file or not os.path.exists(palette_file):
        return colors
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bin_dir = os.path.join(os.path.dirname(script_dir), "bin")
        colorcalc = os.path.join(bin_dir, 'nscde-wayland-colorcalc')
        if not os.path.exists(colorcalc):
            # Try PATH
            colorcalc = 'nscde-wayland-colorcalc'
        result = subprocess.run(
            [colorcalc, palette_file, '8'],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            mapping = {
                'NSCDE_BG_COLOR_5': 'bg', 'NSCDE_FG_COLOR_5': 'fg',
                'NSCDE_TS_COLOR_5': 'ts', 'NSCDE_BS_COLOR_5': 'bs',
                'NSCDE_SEL_COLOR_5': 'sel', 'NSCDE_BG_COLOR_1': 'btn_bg',
                'NSCDE_TS_COLOR_1': 'btn_ts', 'NSCDE_BS_COLOR_1': 'btn_bs',
            }
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, val = line.split('=', 1)
                    if key in mapping:
                        colors[mapping[key]] = val
    except Exception as e:
        print(f"Warning: Failed to load palette: {e}", file=sys.stderr)
    return colors


def load_all_palette_colors(palette_file=None):
    """Load all 8 colorset colors from palette. Returns dict of dicts.

    Keys: 1..8, each with bg, fg, ts, bs, sel, disabled_fg.
    """
    result = {}
    if not palette_file or not os.path.exists(palette_file):
        return result
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bin_dir = os.path.join(os.path.dirname(script_dir), "bin")
        colorcalc = os.path.join(bin_dir, 'nscde-wayland-colorcalc')
        if not os.path.exists(colorcalc):
            colorcalc = 'nscde-wayland-colorcalc'
        proc = subprocess.run(
            [colorcalc, palette_file, '8'],
            capture_output=True, text=True, timeout=3
        )
        if proc.returncode == 0:
            raw = {}
            for line in proc.stdout.strip().split('\n'):
                if '=' in line:
                    k, v = line.split('=', 1)
                    raw[k] = v
            for i in range(1, 9):
                result[i] = {
                    'bg': raw.get(f'NSCDE_BG_COLOR_{i}', '#888888'),
                    'fg': raw.get(f'NSCDE_FG_COLOR_{i}', '#ffffff'),
                    'ts': raw.get(f'NSCDE_TS_COLOR_{i}', '#bbbbbb'),
                    'bs': raw.get(f'NSCDE_BS_COLOR_{i}', '#444444'),
                    'sel': raw.get(f'NSCDE_SEL_COLOR_{i}', '#666666'),
                    'disabled_fg': raw.get(f'NSCDE_DISABLED_FG_COLOR_{i}', '#666666'),
                }
    except Exception:
        pass
    return result


def get_icon_path(icon_name):
    """Resolve icon file path from NsCDE icon assets."""
    for base in [
        "/usr/share/nscde-wayland/assets/icons",
        "/usr/local/share/nscde-wayland/assets/icons",
    ]:
        full = os.path.join(base, "NsCDE", icon_name)
        if os.path.exists(full):
            return full
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_base = os.path.join(os.path.dirname(script_dir), "assets", "icons")
    full = os.path.join(src_base, "NsCDE", icon_name)
    if os.path.exists(full):
        return full
    return None


def get_palette_list():
    """List available .dp palette files. Returns list of (name, path) tuples."""
    palettes = []
    search_dirs = [
        os.path.expanduser("~/.config/nscde-wayland/palettes"),
        os.path.expanduser("~/.NsCDE/palettes"),
        "/usr/local/share/nscde-wayland/assets/palettes",
        "/usr/share/nscde-wayland/assets/palettes",
    ]
    # Also try source tree
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_palettes = os.path.join(os.path.dirname(script_dir), "assets", "palettes")
    if os.path.isdir(src_palettes):
        search_dirs.insert(0, src_palettes)

    seen = set()
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith('.dp') and f not in seen:
                seen.add(f)
                palettes.append((f[:-3], os.path.join(d, f)))
    return palettes


def build_dialog_stylesheet(colors):
    """Build CDE 3D border stylesheet suitable for dialog windows.

    Uses the panel colorset for window background and button colorset
    for controls.
    """
    bg = colors.get('bg', NSDECDE_CS23_BG)
    fg = colors.get('fg', NSDECDE_CS23_FG)
    ts = colors.get('ts', NSDECDE_CS23_HI)
    bs = colors.get('bs', NSDECDE_CS23_SH)
    sel = colors.get('sel', '#a0a0a0')
    btn_bg = colors.get('btn_bg', NSDECDE_CS1_BG)
    btn_fg = colors.get('btn_fg', NSDECDE_CS1_FG)
    btn_ts = colors.get('btn_ts', NSDECDE_CS1_HI)
    btn_bs = colors.get('btn_bs', NSDECDE_CS1_SH)
    return f"""
    QWidget {{
        background-color: {bg};
        color: {fg};
        font: 12px {CJK_FONT};
    }}
    QWidget#dialogWindow {{
        background-color: {bg};
        border-top: 2px solid {ts};
        border-left: 2px solid {ts};
        border-right: 2px solid {bs};
        border-bottom: 2px solid {bs};
    }}
    QPushButton {{
        background-color: {btn_bg};
        color: {btn_fg};
        border-top: 2px solid {btn_ts};
        border-left: 2px solid {btn_ts};
        border-right: 2px solid {btn_bs};
        border-bottom: 2px solid {btn_bs};
        border-radius: 0px;
        padding: 4px 12px;
        min-height: 20px;
        font: 12px {CJK_FONT};
    }}
    QPushButton:hover {{
        background-color: {sel};
    }}
    QPushButton:pressed {{
        border-top: 2px solid {btn_bs};
        border-left: 2px solid {btn_bs};
        border-right: 2px solid {btn_ts};
        border-bottom: 2px solid {btn_ts};
    }}
    QPushButton:disabled {{
        color: {bs};
        background-color: {bg};
    }}
    QLabel {{
        color: {fg};
        background: transparent;
        font: 12px {CJK_FONT};
    }}
    QLabel#title {{
        font: bold 14px {CJK_FONT};
        padding: 4px;
    }}
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {btn_bg};
        color: {btn_fg};
        border-top: 2px solid {btn_bs};
        border-left: 2px solid {btn_bs};
        border-right: 2px solid {btn_ts};
        border-bottom: 2px solid {btn_ts};
        padding: 2px 4px;
        font: 12px {MONO_FONT};
    }}
    QListWidget, QTreeWidget, QTableWidget {{
        background-color: {btn_bg};
        color: {btn_fg};
        border-top: 2px solid {btn_bs};
        border-left: 2px solid {btn_bs};
        border-right: 2px solid {btn_ts};
        border-bottom: 2px solid {btn_ts};
        font: 12px {CJK_FONT};
    }}
    QListWidget::item:selected, QTreeWidget::item:selected {{
        background-color: {sel};
        color: {btn_fg};
    }}
    QComboBox {{
        background-color: {btn_bg};
        color: {btn_fg};
        border-top: 2px solid {btn_ts};
        border-left: 2px solid {btn_ts};
        border-right: 2px solid {btn_bs};
        border-bottom: 2px solid {btn_bs};
        padding: 2px 8px;
        min-height: 20px;
        font: 12px {CJK_FONT};
    }}
    QComboBox:hover {{
        background-color: {sel};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {btn_bg};
        color: {btn_fg};
        selection-background-color: {sel};
        border: 1px solid {btn_bs};
    }}
    QCheckBox {{
        color: {fg};
        spacing: 6px;
        background: transparent;
        font: 12px {CJK_FONT};
    }}
    QRadioButton {{
        color: {fg};
        spacing: 6px;
        background: transparent;
        font: 12px {CJK_FONT};
    }}
    QTabWidget::pane {{
        border-top: 2px solid {btn_ts};
        background-color: {bg};
    }}
    QTabBar::tab {{
        background-color: {btn_bg};
        color: {btn_fg};
        border-top: 2px solid {btn_ts};
        border-left: 2px solid {btn_ts};
        border-right: 2px solid {btn_bs};
        border-bottom: none;
        padding: 4px 12px;
        margin-right: 2px;
        font: 12px {CJK_FONT};
    }}
    QTabBar::tab:selected {{
        background-color: {bg};
        border-bottom: 2px solid {bg};
        font: bold 12px {CJK_FONT};
    }}
    QGroupBox {{
        color: {fg};
        border: 1px solid {bs};
        margin-top: 8px;
        padding-top: 12px;
        font: bold 12px {CJK_FONT};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 8px;
        padding: 0 4px;
    }}
    QSlider::groove:horizontal {{
        background: {btn_bs};
        height: 6px;
    }}
    QSlider::handle:horizontal {{
        background: {btn_bg};
        border: 1px solid {btn_ts};
        width: 14px;
        margin: -5px 0;
    }}
    QSpinBox {{
        background-color: {btn_bg};
        color: {btn_fg};
        border-top: 2px solid {btn_ts};
        border-left: 2px solid {btn_ts};
        border-right: 2px solid {btn_bs};
        border-bottom: 2px solid {btn_bs};
        padding: 2px 4px;
        font: 12px {CJK_FONT};
    }}
    QMenuBar {{
        background-color: {bg};
        color: {fg};
        border-bottom: 1px solid {bs};
    }}
    QMenuBar::item:selected {{
        background-color: {sel};
    }}
    QMenu {{
        background-color: {btn_bg};
        color: {btn_fg};
        border: 1px solid {btn_bs};
    }}
    QMenu::item:selected {{
        background-color: {sel};
    }}
    QStatusBar {{
        background-color: {bg};
        color: {fg};
        border-top: 1px solid {ts};
    }}
    QScrollBar:vertical {{
        background: {bg};
        width: 12px;
    }}
    QScrollBar::handle:vertical {{
        background: {btn_bg};
        border: 1px solid {btn_ts};
        min-height: 20px;
    }}
    QScrollBar:horizontal {{
        background: {bg};
        height: 12px;
    }}
    QScrollBar::handle:horizontal {{
        background: {btn_bg};
        border: 1px solid {btn_ts};
        min-width: 20px;
    }}
    """
