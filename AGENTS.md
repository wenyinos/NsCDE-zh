# AGENTS.md - NsCDE-zh Development Guide

## Quick Start

**Build & Install:**
```bash
./autogen.sh && ./configure --prefix=/usr && make && sudo make install
```

**Package Builds:**
- Debian/Ubuntu: `dpkg-buildpackage -rfakeroot -b`
- Arch Linux: `makepkg -si` (use `pkg/pacman/PKGBUILD`)
- Fedora/RHEL: `rpmbuild -ba pkg/rpm/NsCDE.spec`

## Critical Constraints

### Shell Scripting
- **Must use AT&T Korn Shell (ksh93)** - not bash, pdksh, or mksh
- All shell routines in config, helpers, and FvwmScript use ksh syntax
- FreeBSD/OpenBSD/NetBSD require GNU sed (gsed) and GNU make (gmake)

### Python Requirements
- Python 3 required (minimum 3.0)
- Required modules: `xdg`, `yaml`, `os`, `re`, `shutil`, `subprocess`, `sys`, `fnmatch`, `getopt`, `time`, `platform`, `psutil`, `pwd`, `socket`
- GUI components use PyQt5 or PyQt4 (one required)
- Custom Python shebang supported via `--with-python-shebang=STRING`

### FVWM Dependencies
- **FVWM2 (2.6.7-2.6.9 recommended)** or **FVWM3 (latest)**
- FVWM is the core driver - this is essentially a heavyweight FVWM theme
- WindowName patch required for FvwmButtons if not using FVWM3

## Architecture Highlights

### Directory Structure
- `~/.NsCDE` = `FVWM_USERDIR` (user configuration, NOT `~/.fvwm`)
- `NSCDE_ROOT` = installation prefix (default `/usr/local` or `/usr`)
- `NSCDE_DATADIR` = `$datarootdir/NsCDE`
- `NSCDE_TOOLSDIR` = `$libexecdir/NsCDE`
- `FVWM_DATADIR` = `$datarootdir/NsCDE/fvwm`

### Key Components
1. **FVWM configuration** (`data/fvwm/`) - Main.fvwmconf, Functions.fvwmconf
2. **Python theme engine** (`lib/python/`) - Theme.py, ThemeGtk.py
3. **Shell helpers** (`lib/scripts/`) - ColorMgr, FontMgr, BackdropMgr
4. **FvwmScript GUIs** (`nscde_tools/FvwmScripts/`) - Notifier, GWM, Splash
5. **C utilities** (`src/`) - colorpicker, pclock, XOverrideFontCursor

### Chinese Localization
- **Default fonts**: Noto Sans CJK SC and Noto Sans Mono CJK SC
- Translation files in `po/`: NsCDE.zh.po, NsCDE-*.zh.po, nscde-bootstrap.zh.po
- Set `LANGUAGE=zh_CN` and `LC_MESSAGES=zh_CN` in `~/.NsCDE/NsCDE.conf`
- FvwmScript dialog widgets have fixed dimensions - translations must be concise

## Common Gotchas

### Font Display Issues
If Chinese appears as boxes:
```bash
xrdb -query | grep Xft.dpi  # Check current DPI
sed -i 's/Xft.dpi: 96/Xft.dpi: 120/' ~/.NsCDE/Xdefaults.fontdefs
xrdb -merge ~/.NsCDE/Xdefaults.fontdefs
```

### Qt Integration Quirks
- `qtconfig-qt4` or `qt5ct` must be run, settings changed, and saved for fonts to apply
- `QT_QPA_PLATFORMTHEME` must be set to `qt5ct` for qt5ct configurator

### Build Dependencies
Required for `make install`:
- autoconf, automake
- libx11-dev, libxext-dev, libxpm-dev
- C compiler (gcc/clang)
- make

### Testing
- No automated test suite exists
- Validate translations: `msgfmt -c po/*.po`
- Runtime testing requires X11 environment
- Check `~/.NsCDE/` for session logs

## Localization Workflow

1. Edit `.po` files in `po/`
2. Compile: `msgfmt -o NsCDE.mo NsCDE.zh.po`
3. Install to `LC_MESSAGES` directory
4. Restart NsCDE for Notifier dialog changes to take effect
5. FvwmScript translations must be concise to avoid UI clipping

## Versioning & Tags
- Tags follow format: `vX.Y.Z_zh` (e.g., `v2.3.3_zh`)
- CI builds packages for Debian, Ubuntu, Arch, Fedora RPM from tags
- Version info embedded via `git describe` during configure

## CI/CD Workflow
- Workflow: `.github/workflows/build-packages.yml`
- prepare job extracts version from tag or `configure.ac`
- `DEBIAN_FRONTEND=noninteractive TZ=Asia/Shanghai` required for apt operations
- RPM spec file (`pkg/rpm/NsCDE.spec`) uses `NsCDE` not `NsCDE-zh` for internal paths
- PKGBUILD source URL format: `v${pkgver}.tar.gz` (not `v${pkgver}_zh.tar.gz`)
