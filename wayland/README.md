# NsCDE Wayland Labwc Prototype

This directory is a standalone Wayland session project for an NsCDE-like
desktop based on labwc.

The prototype keeps two rules:

- NsCDE-provided session components run as native Wayland clients.
- Runtime configuration uses copied assets from this project, not direct
  references to the parent NsCDE tree.

## Initial Components

- `labwc` for the Wayland compositor.
- `nscde-panel` for the native CDE-style front panel (GTK3 + GtkLayerShell).
- `sfwbar` and `lavalauncher` as fallback panel alternatives.
- `fuzzel` for launching applications.
- `foot` for the default terminal.
- `fnott` for notifications.
- `swaybg` or `wbg` for wallpaper.
- `wl-clipboard`, `grim`, `slurp`, `wlr-randr`, and `kanshi` for Wayland tools.

## Build And Install

This subproject is intentionally independent from the parent Autotools build.

```sh
cd wayland
make check
sudo make install PREFIX=/usr/local
```

For packaging, use `DESTDIR`:

```sh
make install PREFIX=/usr/local DESTDIR="$pkgdir"
```

Installed files are placed under:

```text
/usr/local/bin/nscde-labwc
/usr/local/bin/nscde-panel
/usr/local/bin/nscde-control-center
/usr/local/bin/nscde-wayland-lock
/usr/local/bin/nscde-wayland-logout
/usr/local/bin/nscde-wayland-run
/usr/local/bin/nscde-wayland-theme
/usr/local/bin/nscde-wayland-menugen
/usr/local/bin/nscde-wayland-colorcalc
/usr/local/bin/nscde-wayland-doctor
/usr/local/bin/nscde-wayland-pipemenu
/usr/local/bin/nscde-output-scale
/usr/local/bin/nscde-wayland-screenshot
/usr/local/share/nscde-wayland/lib/nscde_cde.py
/usr/local/share/nscde-wayland/lib/cc_*.py
/usr/local/share/wayland-sessions/nscde-labwc.desktop
/usr/local/share/nscde-wayland/
/usr/local/share/themes/NsCDE-Wayland/
/usr/local/share/icons/NsCDE/
```

## Running From The Source Tree

```sh
wayland/bin/nscde-labwc
```

To apply one compositor-wide output scale during startup:

```sh
NSCDE_WAYLAND_SCALE=1.5 wayland/bin/nscde-labwc
```

For display-manager sessions, write the scale factor to:

```text
~/.config/nscde-wayland/scale
```

To inspect the current test session:

```sh
nscde-wayland-doctor
```

To capture a Wayland screenshot:

```sh
nscde-wayland-screenshot area
nscde-wayland-screenshot copy-area
```

Static assets stay in the source or installation directory:

```text
wayland/assets/
/usr/local/share/nscde-wayland/assets/
```

Component configuration for `fuzzel`, `foot`, `fnott`, and `nscde-panel` also stays
under the same Wayland project directory. `nscde-wayland-run` passes those paths
to individual NsCDE components without changing global XDG search paths for the
whole session.

The bundled assets are copied into this subproject from the parent tree so the
Wayland session can be built and packaged on its own. They include CDE
backdrops, palettes, photos, fontsets, icon sets, XDG menu metadata, integration
templates, and translation sources.

On first run, only editable labwc configuration is copied into:

```text
~/.config/nscde-wayland/labwc/
```

The labwc session then reads configuration from:

```text
~/.config/nscde-wayland/labwc/
```

Systemd is supported through the host distribution, but this session does not
require `systemctl --user`; labwc `autostart` is the default startup path.

## Runtime Isolation

`nscde-labwc` does not globally override `XDG_CONFIG_DIRS` or `XDG_DATA_DIRS`.
NsCDE-specific component paths are applied by `nscde-wayland-run` only for the
component being launched. Use `nscde-wayland-run app COMMAND` when panel actions
start normal desktop applications so they keep the original XDG environment.

Theme, icon, MIME/default-application, GTK, Qt, KDE, and portal preferences must
use NsCDE-specific extra config files. Do not write directly to shared desktop
files such as `~/.config/gtk-3.0/settings.ini`, `~/.config/kdeglobals`,
`~/.config/mimeapps.list`, `qt5ct.conf`, or `qt6ct.conf`. Keep generated
runtime preferences under `~/.config/nscde-wayland/` or pass explicit config
paths to the component that needs them.

## Tools Reference

### nscde-panel

Native CDE-style front panel built with GTK3 + GtkLayerShell.

```sh
nscde-panel [--palette PALETTE.dp] [--position top|bottom]
```

Features:
- CDE 3D bevel borders with palette-driven colors
- Subpanel popups on launcher buttons
- Workspace switcher (4 desktops)
- Real-time clock and date display
- System tray area (SNI placeholder)
- Taskbar for window switching

### nscde-wayland-theme

Generate themes from CDE palette files.

```sh
nscde-wayland-theme [PALETTE.dp]              # labwc themerc (stdout)
nscde-wayland-theme --firefox [PALETTE.dp]    # Firefox CSS (stdout)
nscde-wayland-theme --gtk4 [PALETTE.dp]       # GTK4 CSS (stdout)
nscde-wayland-theme --kvantum [PALETTE.dp]    # Kvantum theme (tar, stdout)
nscde-wayland-theme --kvantum-dir DIR [PALETTE.dp]  # Kvantum theme (write to DIR)
nscde-wayland-theme --install-firefox [PALETTE.dp]  # Install Firefox CSS
nscde-wayland-theme --all [PALETTE.dp]        # All themes (stdout)
```

### nscde-wayland-menugen

Generate labwc menu.xml from XDG .desktop files.

```sh
nscde-wayland-menugen > ~/.config/labwc/menu.xml
nscde-wayland-menugen --lang zh_CN > menu.xml
```

### nscde-wayland-colorcalc

Calculate Motif/CDE colors from palette file (Python3, no PyQt dependency).

```sh
nscde-wayland-colorcalc PALETTE.dp [ncolors]
```

Outputs `NSCDE_*_COLOR_N=VALUE` pairs for shell evaluation.

### nscde-control-center

PyQt6-based settings manager with CDE-style UI.

```sh
nscde-control-center [--palette PALETTE.dp] [--page sysinfo|defaultapps|backdrop|color|font|window]
```

Pages:
- **Sysinfo** - Read-only system information display
- **DefaultApps** - Default application associations (8 categories)
- **Backdrop** - Wallpaper/photo manager (swaybg integration)
- **Color** - Palette selection with labwc/GTK4/Kvantum/Firefox integration
- **Font** - Font set management with GTK/Qt configuration
- **Window** - labwc rc.xml editor (behavior/theme/placement/keyboard)

### nscde-wayland-logout

Session exit dialog with CDE-style UI.

```sh
nscde-wayland-logout [--palette PALETTE.dp]
```

Options: Logout, Lock Screen, Reboot, Shutdown. Uses `loginctl` for system operations (works with systemd and elogind).

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Alt+Tab | Window switcher |
| Alt+F4 | Close window |
| Alt+Return | Toggle maximize |
| Alt+Space | Root menu |
| Ctrl+Alt+Left/Right/Up/Down | Switch workspace |
| Super+Return | Terminal (foot) |
| Super+f | File manager |
| Alt+F2 | Run dialog (fuzzel) |
| Super+l | Lock screen |
| Ctrl+Alt+Delete | Session dialog |

## Configuration Files

```text
~/.config/nscde-wayland/         # NsCDE-Wayland user config
~/.config/nscde-wayland/settings.ini  # DefaultApps, Font, ColorIntegration
~/.config/nscde-wayland/palette.dp    # Current palette
~/.config/nscde-wayland/fontsets/     # User font sets
~/.config/nscde-wayland/backdrops/    # User backdrops
~/.config/nscde-wayland/photos/       # User photos
~/.config/labwc/rc.xml               # labwc configuration
~/.config/labwc/themerc              # labwc theme (generated)
~/.config/labwc/menu.xml             # Application menu (generated)
```
