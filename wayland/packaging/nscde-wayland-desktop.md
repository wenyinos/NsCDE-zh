# NsCDE-Wayland 元包安装指南

本文档说明如何将 NsCDE-Wayland 作为完整桌面环境安装到各 Linux 发行版。

---

## 概念说明

`nscde-wayland` 是一个**元包**（meta-package），它本身不包含代码，而是定义了完整的桌面环境依赖关系。安装元包会自动拉入所有必要的组件。

---

## 依赖关系

### 核心依赖（必须）

| 组件 | 作用 | Fedora | Arch | Debian/Ubuntu |
|------|------|--------|------|---------------|
| labwc | Wayland 合成器 | labwc | labwc | labwc |
| python3 | 运行时 | python3 | python | python3 |
| python3-pyqt6 | 控制中心 | python3-pyqt6 | python-pyqt6 | python3-pyqt6 |
| swaybg | 桌面背景 | swaybg | swaybg | swaybg |
| fuzzel | 应用启动器 | fuzzel | fuzzel | fuzzel |
| foot | 默认终端 | foot | foot | foot-terminal |
| fnott | 通知守护进程 | fnott | fnott | fnott |
| sfwbar | 备用面板 | sfwbar | sfwbar | sfwbar |
| lavalauncher | 启动栏 | lavalauncher | lavalauncher | lavalauncher |
| wl-clipboard | 剪贴板工具 | wl-clipboard | wl-clipboard | wl-clipboard |
| grim | 截图 | grim | grim | grim |
| slurp | 区域选择 | slurp | slurp | slurp |
| pcmanfm-qt | 文件管理器 | pcmanfm-qt | pcmanfm-qt | pcmanfm-qt |
| python3-pillow | 图像处理 | python3-pillow | python-pillow | python3-pil |

### 推荐依赖（可选）

| 组件 | 作用 |
|------|------|
| wlr-randr | 显示缩放 |
| kanshi | 动态输出配置 |
| swaylock | 屏幕锁定 |
| kvantum | Qt 主题引擎 |
| qt5ct / qt6ct | Qt 配置工具 |
| nwg-look | GTK 主题配置 |
| wlrctl | 窗口管理 CLI |

---

## 安装方式

### 方式一：从源码构建安装（推荐开发测试）

```bash
cd wayland
make check
sudo make install PREFIX=/usr
```

验证安装：

```bash
nscde-wayland-doctor
```

### 方式二：Fedora（COPR）

```bash
# 启用 COPR 仓库（如已发布）
sudo dnf copr enable wenyinos/nscde-wayland

# 安装元包
sudo dnf install nscde-wayland
```

### 方式三：Arch Linux（AUR）

```bash
# 使用 AUR 助手（如 yay）
yay -S nscde-wayland

# 或手动构建
cd wayland/packaging/arch
makepkg -si
```

### 方式四：Debian/Ubuntu

```bash
# 构建 deb 包
cd wayland/packaging/debian
dpkg-buildpackage -us -uc

# 安装
sudo dpkg -i ../nscde-wayland_*.deb
sudo apt-get install -f  # 修复依赖
```

---

## 首次运行配置

### 1. 选择显示管理器

安装后，`nscde-labwc` 会话会出现在显示管理器的会话列表中。选择 "NsCDE-labwc" 登录。

支持的显示管理器：
- GDM
- SDDM
- LightDM
- Ly
- TUI（无显示管理器）

### 2. 无显示管理器启动

```bash
# 使用 dbus-run-session 启动
dbus-run-session nscde-labwc

# 或直接从 TTY 启动
nscde-labwc
```

### 3. 首次运行自动配置

首次启动时，`nscde-labwc` 会自动：

1. 创建 `~/.config/nscde-wayland/` 配置目录
2. 复制默认 labwc 配置（rc.xml、menu.xml、autostart）
3. 生成默认 CDE 风格主题
4. 设置默认应用（foot 终端、PCManFM-Qt 文件管理器）

### 4. 自定义配置

登录后，使用控制中心进行配置：

```bash
nscde-control-center
```

可配置项：
- **系统信息**：查看系统状态
- **默认应用**：设置浏览器、邮件、终端等
- **桌面背景**：选择照片或纯色背景
- **颜色主题**：选择 CDE 调色板，自动生成 labwc/GTK/Kvantum/Firefox 主题
- **字体管理**：配置系统字体和等宽字体
- **窗口管理**：labwc 行为、主题、放置、快捷键
- **快捷键**：自定义键盘快捷键
- **鼠标绑定**：自定义鼠标动作

---

## 卸载

### 从源码安装的卸载

```bash
cd wayland
sudo make uninstall PREFIX=/usr
```

### 包管理器安装的卸载

```bash
# Fedora
sudo dnf remove nscde-wayland

# Arch
sudo pacman -R nscde-wayland

# Debian
sudo dpkg -r nscde-wayland
```

### 清理用户配置

```bash
rm -rf ~/.config/nscde-wayland
rm -rf ~/.config/labwc/themerc
rm -rf ~/.config/labwc/menu.xml
```

---

## 故障排查

### 检查会话状态

```bash
nscde-wayland-doctor
```

输出示例：

```
NsCDE Wayland Doctor v0.1.0
============================

Session Components:
  [OK] nscde-labwc          /usr/bin/nscde-labwc
  [OK] nscde-panel          /usr/bin/nscde-panel
  [OK] nscde-control-center /usr/bin/nscde-control-center

Required Tools:
  [OK] labwc                /usr/bin/labwc
  [OK] foot                 /usr/bin/foot
  [OK] fuzzel               /usr/bin/fuzzel
  [OK] swaybg               /usr/bin/swaybg

Optional Tools:
  [OK] wlr-randr            /usr/bin/wlr-randr
  [WARN] kanshi             not found
```

### 常见问题

**Q: 面板不显示**
```bash
# 检查 GtkLayerShell 是否可用
pkg-config --modversion gtk-layer-shell

# 手动启动面板
nscde-panel --palette ~/.config/nscde-wayland/palette.dp
```

**Q: 主题未生效**
```bash
# 重新生成主题
nscde-wayland-theme ~/.config/nscde-wayland/palette.dp > ~/.config/labwc/themerc

# 重启 labwc
labwc -r
```

**Q: 中文显示异常**
```bash
# 检查字体配置
fc-list :lang=zh

# 安装中文字体
sudo dnf install google-noto-sans-cjk-fonts  # Fedora
sudo pacman -S noto-fonts-cjk                 # Arch
sudo apt install fonts-noto-cjk               # Debian
```

---

## 发行版特定说明

### Fedora

- COPR 仓库提供预编译包
- fnott 需要单独构建（见 `packaging/fedora/fnott/`）
- 推荐使用 elogind 替代 systemd-logind

### Arch Linux

- AUR 包含完整依赖
- 支持 systemd 和 elogind
- 推荐使用 `ly` 作为显示管理器

### Debian/Ubuntu

- 需要 Debian 12+ 或 Ubuntu 22.04+
- 部分依赖可能需要从源码构建
- 推荐使用 LightDM

---

## 相关链接

- [项目主页](https://github.com/wenyinos/NsCDE-zh)
- [功能差异清单](../FEATURE_DIFF.md)
- [依赖列表](../DEPENDENCIES.md)
- [移植计划](../WAYLAND_LABWC_PORT_PLAN.md)
