# NsCDE Wayland 依赖清单

> 本文档是阶段 0 交付物之一。标注每个依赖的 systemd 兼容性。

---

## 核心依赖（必需）

| 组件 | 作用 | systemd 依赖 | 非 systemd 替代 |
|---|---|---|---|
| `labwc` | Wayland 合成器 | 无 | — |
| `foot` | 默认终端 | 无 | — |
| `fuzzel` | 应用启动器 | 无 | — |
| `fnott` | 通知守护进程 | 无（避免 `mako` 默认拉入 systemd-libs） | — |
| `nscde-panel` | 原生 CDE 前面板 | 无（GTK3 + GtkLayerShell） | 替代 sfwbar |
| `sfwbar` | 面板（fallback） | 无 | nscde-panel 不可用时的备选方案 |
| `swaybg` 或 `wbg` | 壁纸设置 | 无 | 两者二选一 |
| `wl-clipboard` | 剪贴板（wl-copy / wl-paste） | 无 | — |
| `grim` | 截图 | 无 | — |
| `slurp` | 区域选择 | 无 | — |
| `wlr-randr` | 显示器配置 | 无 | — |
| `python3` | 主题引擎运行时 | 无 | — |
| `python3-yaml` | 主题配置解析 | 无 | — |
| `python3-pyxdg` | XDG 桌面文件解析 | 无 | — |

## Seat 管理（三选一）

NsCDE Wayland 会话不绑定特定 seat 管理器。以下三种均受支持：

| 组件 | 说明 |
|---|---|
| `seatd` | 轻量级 seat 管理器，无 systemd 依赖 |
| `elogind` | systemd-logind 的独立提取版，适用于非 systemd 系统 |
| `systemd-logind` | systemd 系统的原生 seat 管理器 |

打包时使用 `seatd | elogind | systemd-logind` 表达此依赖。

## 可选依赖

| 组件 | 作用 | systemd 依赖 | 说明 |
|---|---|---|---|
| `lavalauncher` | 应用启动按钮 | 无 | 配合面板使用 |
| `gtk3` | nscde-panel 运行时 | 无 | GTK3 基础库 |
| `gtk-layer-shell` | nscde-panel Wayland 集成 | 无 | GTK3 Layer Shell 绑定 |
| `python3` | 颜色计算器/主题引擎运行时 | 无 | nscde-wayland-colorcalc 依赖 |
| `kanshi` | 自动显示器配置 | 无 | 多显示器场景 |
| `nwg-look` | GTK 主题设置 GUI | 视发行版 | — |
| `PCManFM-Qt` | 文件管理器 | 视发行版 | 用 Qt Wayland 后端启动 |
| `qt5ct` / `qt6ct` | Qt 主题配置 | 视发行版 | 部分发行版的 Qt 包依赖 systemd-libs |
| `Kvantum` | Qt 主题引擎 | 视发行版 | 同上 |
| `kvantummanager` | Kvantum 配置工具 | 视发行版 | 同上 |
| `xcur2png` | 光标主题转换 | 无 | 仅开发/打包时需要 |
| `swaylock` | 屏幕锁定 | 无 | — |
| `wtype` | Wayland 键盘模拟 | 无 | 能力比 xdotool 受限 |

## 构建依赖

| 组件 | 作用 |
|---|---|
| `make` | 构建系统 |
| `sh` | 脚本语法检查 |
| `python3` | Python 脚本编译检查（`make check` 使用） |
| `xmllint` | XML 配置验证（可选，`make check` 使用） |
| `fuzzel` | 配置自检（可选，`make check` 使用） |
| `foot` | 配置自检（可选，`make check` 使用） |

## 与 X11 版依赖对比

以下 X11 版依赖在 Wayland 版中被移除或替换：

| X11 版依赖 | Wayland 版替代 | 说明 |
|---|---|---|
| `fvwm` / `fvwm3` | `labwc` | 窗口管理器替换 |
| `xterm` | `foot` | 终端替换 |
| `rofi` | `fuzzel` | 启动器替换 |
| `dunst` | `fnott` | 通知替换 |
| `stalonetray` | `nscde-panel`（内置 SNI tray） | 托盘替换 |
| `xclip` | `wl-clipboard` | 剪贴板替换 |
| `xdotool` | `wtype`（受限） | 键盘模拟替换 |
| `xrandr` | `wlr-randr` / `kanshi` | 显示器配置替换 |
| `xrdb` / `Xdefaults` | 环境变量 + 配置文件 | X resources 不再使用 |
| `xset` | 无直接替代 | 部分功能由 labwc 接管 |
| `xprop` | 无直接替代 | Wayland 安全模型不允许 |
| `xscreensaver` | `swaylock`（可选） | 屏幕锁定替换 |
| `imagemagick` (convert/import) | `grim` + `slurp` | 截图替换 |
| `fvwm-root` | `swaybg` / `wbg` | 壁纸设置替换 |

## 安装命令参考

### Fedora
```bash
sudo dnf install labwc foot fuzzel fnott sfwbar swaybg \
  wl-clipboard grim slurp wlr-randr kanshi \
  python3 python3-pyyaml python3-pyxdg \
  lavalauncher nwg-look pcmanfm-qt qt5ct kvantum
```

### Debian/Ubuntu
```bash
sudo apt install labwc foot fuzzel fnott sfwbar swaybg \
  wl-clipboard grim slurp wlr-randr-tools kanshi \
  python3 python3-yaml python3-xdg \
  lavalauncher nwg-look pcmanfm-qt qt5ct
```

### Arch Linux
```bash
sudo pacman -S labwc foot fuzzel fnott sfwbar swaybg \
  wl-clipboard grim slurp wlroots kanshi \
  python python-pyyaml python-pyxdg \
  lavalauncher nwg-look pcmanfm-qt qt5ct kvantum
```
