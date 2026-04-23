# AGENTS.md - NsCDE-zh Development Guide

## 🔴 Critical Constraints

### Shell & Build System
- **Must use AT&T ksh93** - not bash, pdksh, or mksh
- FreeBSD/OpenBSD/NetBSD require GNU tools: `gsed`, `gmake`
- Build system: Autotools (autoconf/automake) with custom macros
- Source generation: `./autogen.sh` → `./configure` → `make`

### Core Dependencies
- **FVWM2 (2.6.7-2.6.9)** or **FVWM3** (required at runtime)
- **Python 3.0+** with modules: `xdg`, `yaml`, `psutil`, `PyQt5`/`PyQt4`
- X11 utils: `xrdb`, `xset`, `xprop`, `xdpyinfo`, `xdotool`

### Configuration Paths
- User config: `~/.NsCDE/` (NOT `~/.fvwm`)
- FVWM data: `$datarootdir/NsCDE/fvwm/`
- Tools: `$libexecdir/NsCDE/`

## 🚀 Quick Commands

**Build & Install:**
```bash
./autogen.sh && ./configure --prefix=/usr && make && sudo make install
```

**Localization:**
```bash
# Validate translations
msgfmt -c po/*.po

# Test build artifacts  
find . -name "*.so" -o -name "nscde" | head -10
```

**Package Builds:**
- Debian/Ubuntu: `dpkg-buildpackage -rfakeroot -b`
- Arch: `makepkg -si` (PKGBUILD in `pkg/pacman/`)
- Fedora/RHEL: `rpmbuild -ba pkg/rpm/NsCDE.spec`

## 📁 Key Directories

```
data/fvwm/           # FVWM configs (Main.fvwmconf, Functions.fvwmconf)
lib/python/          # Theme engine (Theme.py, ThemeGtk.py)
lib/scripts/         # Shell helpers (ColorMgr, FontMgr, BackdropMgr)
nscde_tools/         # Utilities & FvwmScript GUIs
src/                 # C utilities (colorpicker, pclock)
po/                  # Translations (NsCDE.zh.po, NsCDE-*.zh.po)
```

## 🌏 Chinese Localization

### Critical Notes
- **Default fonts**: Noto Sans CJK SC + Noto Sans Mono CJK SC
- **DPI issues**: If Chinese shows as boxes, adjust `Xft.dpi` in `~/.NsCDE/Xdefaults.fontdefs`
- **Translation limits**: FvwmScript dialogs have fixed sizes - keep translations short
- **Qt font rendering**: Must configure `qt5ct` and set `QT_QPA_PLATFORMTHEME=qt5ct`

### Setup
```bash
# Set locale
echo 'LANGUAGE=zh_CN' >> ~/.NsCDE/NsCDE.conf
echo 'LC_MESSAGES=zh_CN' >> ~/.NsCDE/NsCDE.conf

# Install fonts
sudo apt install fonts-noto-cjk fonts-noto-cjk-extra  # Debian/Ubuntu
sudo dnf install google-noto-sans-cjk-fonts          # Fedora/RHEL
```

## ⚠️ Common Pitfalls

### Font Rendering
```bash
# Check DPI
xrdb -query | grep Xft.dpi

# Fix if needed
sed -i 's/Xft.dpi: 96/Xft.dpi: 120/' ~/.NsCDE/Xdefaults.fontdefs
xrdb -merge ~/.NsCDE/Xdefaults.fontdefs
```

### Qt Integration
- Run `qt5ct`, change settings, then save
- Set environment: `export QT_QPA_PLATFORMTHEME=qt5ct`

### Runtime Testing
- Requires X11 session
- Check logs: `~/.NsCDE/session.log`
- No automated test suite - manual verification only

## 🏗️ Build System Notes

### Configuration Variables
- `NSCDE_ROOT`: Installation prefix (default `/usr/local` or `/usr`)
- `FVWM_USERDIR`: User config directory (`~/.NsCDE`, NOT `~/.fvwm`)
- `NSCDE_DATADIR`: `$datarootdir/NsCDE`
- `NSCDE_TOOLSDIR`: `$libexecdir/NsCDE`
- `FVWM_DATADIR`: `$datarootdir/NsCDE/fvwm`

### Key Configuration Files
- Main FVWM config: `data/fvwm/Main.fvwmconf`
- Functions: `data/fvwm/Functions.fvwmconf`
- User overrides: `~/.NsCDE/*.fvwmconf`
- Python theme engine: `lib/python/Theme.py`
- Font definitions: `data/fvwm/Font-*.fvwmconf`

## 🔧 Build Environment Setup

### Essential Packages
```bash
# Debian/Ubuntu
sudo apt install autoconf automake gcc make \
    libx11-dev libxext-dev libxpm-dev \
    ksh gettext

# Arch Linux
sudo pacman -S base-devel libx11 libxext libxpm ksh93 gettext

# Fedora/RHEL
sudo dnf install autoconf automake gcc make \
    libX11-devel libXt-devel libXext-devel \
    ksh gettext-devel
```

### Python Modules
```bash
pip install PyQt5 pyxdg pyyaml psutil
```

## 🏷️ Versioning & Tags

- **Tag format**: `vX.Y.Z_zh` (e.g., `v2.3.3_zh`)
- **CI triggers**: Builds packages from git tags
- **Source archives**: Generated as `NsCDE-zh-vX.Y.Z_zh.tar.gz`
- **Version detection**: Uses `git describe` during configure

## 📋 CI/CD Workflow

- **Workflow file**: `.github/workflows/build-packages.yml`
- **Multi-platform**: Debian, Ubuntu, Arch, Fedora RPM
- **Environment vars**: `DEBIAN_FRONTEND=noninteractive TZ=Asia/Shanghai`
- **RPM naming**: Uses `NsCDE` internally (not `NsCDE-zh`)

## 🌏 Localization Quick Reference

### Translation Files Structure
- Main translations: `po/NsCDE.zh.po`
- Component translations: `po/NsCDE-*.zh.po`
- Bootstrap: `po/nscde-bootstrap.zh.po`
- Migration: `po/nscde-migrate-1x_to_2x.zh.po`

### Translation Workflow
1. Edit `.po` files in `po/`
2. Compile: `msgfmt -c po/*.po` (validate)
3. Install to `LC_MESSAGES` directory
4. Restart NsCDE for changes to take effect

### Important Constraints
- FvwmScript dialogs have fixed dimensions - keep translations concise
- Maximum translation length varies by component (check original English text)
- Test with actual Chinese fonts: Noto Sans CJK SC + Noto Sans Mono CJK SC

## 🏗️ Architecture Overview

### Core Components
**FVWM Configuration Engine:**
- Main config: `data/fvwm/Main.fvwmconf`
- Key modules: `FrontPanel.fvwmconf`, `Menus.fvwmconf`, `Keybindings.fvwmconf`
- Theme engine: `lib/python/Theme.py`

**GUI Management:**
- FvwmScript applications: `nscde_tools/FvwmScripts/` (GWM, Notifier, Splash)
- Python utilities: `lib/scripts/` (ColorMgr, FontMgr, BackdropMgr)
- System tools: `nscde_tools/` (fontmgr, colormgr, backdropmgr)

**Integration Layer:**
- GTK/Qt themes: Configured via `Xsettingsd.conf`
- X11 resource management: `~/.NsCDE/Xdefaults.fontdefs`
- Session handling: `xdg/xsessions/nscde.desktop`

### Build Process Flow
1. **Configure**: Sets paths (`NSCDE_DATADIR`, `FVWM_USERDIR`) and detects dependencies
2. **Generate**: Creates config files from templates (`*.in` → `*`)
3. **Compile**: Builds C utilities in `src/` and generates scripts
4. **Install**: Places configs in system locations, compiles translations

### Runtime Architecture
```
User Space (~/.NsCDE/)
├── FVWM User Configs (*.fvwmconf)
├── X Resources (Xdefaults.fontdefs)
└── Session Logs (session.log)

System Space (/usr/share/NsCDE/)
├── FVWM Core Config (Main.fvwmconf)
├── Python Theme Engine
└── Generated Scripts & Utilities

Integration Points
├── XDG Menu System
├── Qt/Gtk Theming (Xsettingsd)
└── Desktop Environment Integration
```

## 🔧 Runtime Dependencies

### Essential Tools
- `ksh` - AT&T Korn Shell (core script interpreter)
- `fvwm` or `fvwm3` - Window manager (required)
- `xrdb`, `xset`, `xprop`, `xdpyinfo` - X11 utilities
- `xdotool` - For FVWM3 integration (optional but recommended)
- `xterm` - Terminal emulator (for initial setup)

### Optional but Recommended
- `xsettingsd` - GTK/Qt theme daemon
- `stalonetray` - System tray
- `dunst` - Notification daemon
- `qt5ct` - Qt configuration tool
- `xclip` - Clipboard utility
- `convert`/`import` - ImageMagick (screenshots)

### Python Modules (Runtime)
- `xdg` - Desktop integration
- `yaml` - Configuration parsing
- `psutil` - System monitoring
- `PyQt5` or `PyQt4` - GUI toolkit

## 🛠️ Common Development Tasks

### Building from Source
```bash
# Fresh build
./autogen.sh && ./configure --prefix=/usr && make clean && make

# Incremental build (after config changes)
make -j$(nproc)

# Install to custom prefix
./configure --prefix=$HOME/nscde-test && make && make install
```

### Translation Management
```bash
# Update translations from source strings
msginit -i po/NsCDE.zh.po -l zh_CN

# Validate all translations
msgfmt -c po/*.po

# Compile specific translation
msgfmt -o locale/zh/LC_MESSAGES/NsCDE.mo po/NsCDE.zh.po
```

### Configuration Testing
```bash
# Test FVWM config syntax
fvwm -test Main.fvwmconf

# Check Python theme engine
python3 -c "from lib.python.Theme import *; print('Theme engine OK')"

# Verify build artifacts
find . -name "*.so" -o -name "nscde" | head -5
```

## 🐛 Troubleshooting

### Build Issues
- **Autotools errors**: Run `./autogen.sh` first, then `./configure`
- **Missing dependencies**: Check `config.log` for specific missing packages
- **Python module errors**: Verify `PYTHON_SHEBANG` in configure output matches your system

### Runtime Issues
- **Chinese as boxes**: Check DPI settings in `~/.NsCDE/Xdefaults.fontdefs`
- **Qt fonts not applying**: Run `qt5ct`, change settings, save, restart session
- **FVWM crashes**: Check `~/.NsCDE/session.log` for error messages
- **Missing tray/icons**: Ensure `stalonetray` is installed and running

### Debug Tips
- **Test FVWM config**: `fvwm -test data/fvwm/Main.fvwmconf`
- **Check Python imports**: `python3 -c "import xdg, yaml, psutil"`
- **Verify X resources**: `xrdb -query | grep -i font`
- **Test notifications**: `notify-send "Test message"` (requires dunst)
