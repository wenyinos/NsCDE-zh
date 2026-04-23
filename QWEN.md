# NsCDE-zh 项目上下文

## 项目概述

**NsCDE-zh** 是 **NsCDE** (Not so Common Desktop Environment) 的中文本地化版本。NsCDE 是一个复古风格的 UNIX 桌面环境，模仿 90 年代商业 UNIX 系统上常见的 **CDE** (Common Desktop Environment) 外观，但基于更现代灵活的框架。

### 核心特性

- 🌏 完整的简体中文本地化支持（25+ 个语言文件）
- 🎨 默认使用 Noto Sans CJK SC 字体显示中文
- 🎯 复古 CDE 外观，融合现代功能
- 💻 基于 FVWM 的轻量级桌面环境
- ⚙️ 支持 GTK2/GTK3/Qt4/Qt5/Qt6 主题集成
- 🎭 提供 GUI 配置的颜色和字体样式管理器

### 技术栈

- **窗口管理器**: FVWM (FVWM2 或 FVWM3)
- **脚本语言**: Korn Shell (ksh), Python 3
- **GUI 框架**: FvwmScript, PyQt5/PyQt4
- **构建系统**: GNU Autotools (autoconf/automake)
- **主题引擎**: GTK2/GTK3 pixmap engine, Qt 样式
- **本地化**: gettext (.po/.mo 文件)

## 项目结构

```
NsCDE-zh/
├── bin/                    # 启动脚本 (nscde, nscde_fvwmclnt)
├── data/                   # FVWM 配置文件和模板
│   ├── fvwm/               # FVWM 主配置 (Main.fvwmconf, Functions.fvwmconf)
│   └── config_templates/   # 配置模板
├── doc/                    # 文档
├── lib/                    # Python 模块和 shell 脚本库
│   ├── fvwm-modules/       # FvwmScript 模块
│   ├── python/             # Python 库 (Globals.py, Theme.py 等)
│   └── scripts/            # Shell 脚本 (ColorMgr, FontMgr 等)
├── nscde_tools/            # 主要工具和管理器
│   ├── FvwmScripts/        # FvwmScript 程序
│   └── (各种管理器工具)
├── po/                     # 本地化文件 (.po 翻译文件)
│   ├── NsCDE.zh.po         # 中文主翻译文件
│   ├── NsCDE-*.zh.po       # 各模块中文翻译
│   └── nscde-bootstrap.zh.po  # 初始设置翻译
├── pkg/                    # 打包脚本
│   ├── debian/             # DEB 包构建
│   ├── pacman/             # Arch Linux PKGBUILD
│   └── rpm/                # RPM 包构建
├── src/                    # C 源代码
│   ├── colorpicker/        # 颜色选择器
│   ├── XOverrideFontCursor/# 字体/光标覆盖工具
│   └── pclock/             # 面板时钟
├── xdg/                    # XDG 集成 (xsessions/nscde.desktop)
├── configure.ac            # Autoconf 配置
├── Makefile.am             # Automake 配置
└── autogen.sh              # 构建系统初始化脚本
```

## 构建与安装

### 从源码构建

```bash
# 1. 生成 configure 脚本
./autogen.sh

# 2. 配置（推荐 prefix=/usr）
./configure --prefix=/usr

# 3. 编译
make

# 4. 安装
sudo make install
```

### 包管理器安装

**Debian/Ubuntu:**
```bash
sudo apt install ./nscde-zh_*.deb
# 或从源码构建
dpkg-buildpackage -rfakeroot -b
```

**Fedora/RHEL:**
```bash
sudo dnf install <rpm-package>.rpm
```

**Arch Linux (AUR):**
```bash
paru -S nscde-zh
```

### 主要依赖

**运行时依赖:**
- `fvwm` (FVWM2 或 FVWM3)
- `ksh` (AT&T Korn Shell 93)
- `python3` + `python3-pyxdg`, `python3-psutil`, `python3-yaml`, `PyQt5`
- `xsettingsd`, `stalonetray`, `dunst`
- `xterm`, `xdotool`, `xclip`
- `imagemagick` (convert, import)
- `gettext`, `xrdb`, `xset`, `xprop`, `xdpyinfo`, `xrandr`
- `qt5ct`, `dex-autostart`
- `google-noto-sans-cjk-fonts` (中文字体)

**构建时依赖:**
- `autoconf`, `automake`
- C 编译器 (gcc/clang)
- `libx11-dev`, `libxext-dev`, `libxpm-dev`
- `make`

## 使用方法

1. **启动**: 从显示管理器 (lightdm/gdm/sddm) 选择 NsCDE 会话
2. **字体配置**: 使用 **Font Style Manager** 配置字体
3. **颜色配置**: 使用 **Color Style Manager** 配置颜色和主题
4. **配置文件**: 用户配置位于 `~/.NsCDE/`

### 中文显示配置

默认使用 **Noto Sans CJK SC** 和 **Noto Sans Mono CJK SC** 字体。

安装字体:
```bash
# Debian/Ubuntu
sudo apt install fonts-noto-cjk fonts-noto-cjk-extra

# Fedora/RHEL
sudo dnf install google-noto-sans-cjk-fonts google-noto-sans-mono-cjk-vf-fonts
```

如果中文显示为方框，可能需要调整 DPI:
```bash
# 查看当前 DPI
xrdb -query | grep Xft.dpi

# 编辑配置文件（根据实际 DPI 修改）
sed -i 's/Xft.dpi: 96/Xft.dpi: 120/' ~/.NsCDE/Xdefaults.fontdefs
xrdb -merge ~/.NsCDE/Xdefaults.fontdefs
```

## 本地化开发

### 翻译文件

本项目提供完整的简体中文翻译，位于 `po/` 目录:

- `NsCDE.zh.po` - 主翻译文件（包含 Notifier 对话框翻译）
- `NsCDE-*.zh.po` - 各模块翻译（如 FontMgr, ColorMgr 等）
- `nscde-bootstrap.zh.po` - 初始设置脚本翻译
- `nscde-migrate-1x_to_2x.zh.po` - 迁移脚本翻译

### 翻译注意事项

详见 [README.localization](README.localization) 文件:

1. **FvwmScript 对话框空间有限**，翻译需考虑文本长度
2. **Notifier 对话框**翻译在 `NsCDE.po` 中，更新后需重启 NsCDE
3. **菜单加速键**用 `&` 前缀标记，翻译时需选择合适的加速键
4. 编译 `.po` 为 `.mo`:
   ```bash
   msgfmt -o NsCDE.mo NsCDE.zh.po
   ```

### 配置语言环境

在 `~/.bash_profile` 或 `~/.NsCDE/NsCDE.conf` 中设置:
```bash
export LANGUAGE=zh_CN
export LC_MESSAGES=zh_CN
```

## 关键配置文件

| 文件路径 | 说明 |
|----------|------|
| `~/.NsCDE/NsCDE.conf` | 主配置文件 |
| `~/.NsCDE/Xdefaults.fontdefs` | Xft 字体定义 |
| `~/.NsCDE/Font-*.fvwmconf` | FVWM 窗口管理器字体 |
| `~/.NsCDE/Xsettingsd.conf` | GTK/Qt 应用程序字体 |
| `~/.NsCDE/GeoDB.ini` | 窗口几何数据 |

## 架构要点

### 核心组件

1. **FVWM 配置**: 大量的 FVWM 配置和定制（`data/fvwm/`）
2. **FvwmScript 程序**: GUI 对话框和工具
3. **主题引擎**: GTK2/GTK3/Qt4/Qt5 统一外观
4. **Python 脚本**: 后台驱动和工具（`lib/python/`）
5. **Shell 脚本**: Korn Shell 辅助脚本（`lib/scripts/`）
6. **集成组件**: Firefox/Thunderbird CSS、XDG 菜单等
7. **第三方工具**: stalonetray、dunst、xsettingsd 等

### 目录约定

- `FVWM_USERDIR` = `~/.NsCDE`（用户配置目录）
- `NSCDE_ROOT` = 安装路径（默认 `/usr/local` 或 `/usr`）
- `NSCDE_DATADIR` = `$datarootdir/NsCDE`
- `NSCDE_TOOLSDIR` = `$libexecdir/NsCDE`

## 开发约定

- **Shell 脚本**: 使用 Korn Shell (ksh)，不是 bash/pdksh/mksh
- **Python**: Python 3，使用 PyQt5 或 PyQt4
- **许可协议**: GPLv3
- **版本管理**: Git，版本号通过 `git describe` 生成

## 相关链接

- **GitHub**: https://github.com/wenyinos/NsCDE-zh
- **原始项目**: https://github.com/NsCDE/NsCDE
- **FAQ**: https://github.com/NsCDE/NsCDE/wiki
