# nscde-panel GTK3 → PyQt6 迁移方案

> 创建日期: 2026-05-17
> 状态: 待实施

## 背景

当前 `wayland/bin/nscde-panel` 使用 Python3 + GTK3 + GtkLayerShell 实现（827 行），功能完整但存在以下问题：
- GTK3 在 Wayland 下是二等公民，Qt 是 Wayland 原生支持的一等框架
- 项目已有完善的 Kvantum/Qt 主题生成基础设施
- PyQt6 已验证可用（系统有 Qt 6.11.1 + PyQt6 6.11.0）

目标：用 PyQt6 重写 nscde-panel，保持功能完全等价，不引入 C++ 编译依赖。

## 本地系统验证结论

### ✅ 可行项目

| 检查项 | 结果 | 证据 |
|---|---|---|
| PyQt6 核心模块 | ✅ 可用 | QtWidgets/QtCore/QtGui/QtDBus 全部导入成功 |
| PyQt6 版本 | ✅ 6.11.0 | Qt 6.11.1, PyQt6 6.11.0 |
| QSystemTrayIcon | ✅ 可用 | `isSystemTrayAvailable() = True`，有 activated/showMessage/setContextMenu 等完整 API |
| QSystemTrayIcon 右键菜单 | ✅ 可用 | `setContextMenu(QMenu)` 方法存在 |
| QProcess 调用 colorcalc | ✅ 输出正确 | 8 组颜色变量正常返回 |
| QScreen 获取屏幕信息 | ✅ 可用 | 1536x864, dpr=2.0 |
| 面板窗口原型 | ✅ 3D 边框渲染正确 | FramelessWindowHint + WindowStaysOnTopHint + QSS 样式 |
| Qt 样式表 3D 边框 | ✅ 可用 | QPushButton `border-top: 2px solid #xxx` 精确还原 CDE 效果 |
| layer-shell-qt6 C++ 库 | ✅ 已安装 | 版本 6.6.5，含 libLayerShellQtInterface.so + QML 插件 |
| labwc layer shell 支持 | ✅ 可用 | `zwlr_layer_shell_v1` version 5 已注册 |
| labwc 工作区 action | ✅ 可用 | `GoToDesktop` action + `labwc -a GoToDesktop wsN` 命令行 |
| labwc 窗口切换 action | ✅ 可用 | `NextWindow` / `PreviousWindow` action |

### ⚠️ 需要处理的问题

| 问题 | 影响 | 解决方案 |
|---|---|---|
| PyQt6 无 QtWayland Python 模块 | 无法直接调用 layer-shell-qt C++ API | 使用 Qt 原生窗口 flags 模拟 panel 效果 |
| labwc 0.9.6 运行时未暴露 wlr-foreign-toplevel | 无法通过 Wayland 协议列出窗口 | fallback 用 /proc 枚举 |
| labwc 无 D-Bus 接口 | 无法通过 D-Bus 控制 labwc | 使用 `labwc -a <action>` 命令行替代 |
| QSystemTrayIcon 在 Wayland 下无 XEmbed | 旧应用托盘图标不可用 | 仅支持 SNI 应用（现代应用均支持） |

### ❌ 不可行项目

| 项目 | 原因 |
|---|---|
| PyQt6 直接调用 layer-shell-qt C++ API | PyQt6 没有 QtWayland 模块，layer-shell-qt 只有 C++/QML API |
| wlr-foreign-toplevel 运行时协议 | labwc 0.9.6 编译包含但未在运行时注册该全局对象 |

## Layer Shell 替代方案

不使用 layer-shell-qt C++ 库，改用 Qt 原生窗口 flags + labwc 配置配合：

```python
# 面板窗口 flags
self.setWindowFlags(
    Qt.WindowType.FramelessWindowHint |
    Qt.WindowType.WindowStaysOnTopHint |
    Qt.WindowType.Tool |
    Qt.WindowType.WindowDoesNotAcceptFocus
)
# 设置 WM 窗口类型为 Dock（labwc 识别）
self.setAttribute(Qt.WidgetAttribute.WA_X11NetWmWindowTypeDock, True)
self.setFixedHeight(58)
```

配合 labwc `rc.xml` 中已有的 `<margin top="58">` 配置实现 exclusive-zone 效果。

**注意**：此方案在 Wayland 下 `WA_X11NetWmWindowTypeDock` 不生效，但 `WindowStaysOnTopHint` + 手动定位到屏幕底部 + `setFixedHeight` 可以实现基本面板效果。如果需要严格的 exclusive-zone，需要在 labwc rc.xml 中配置 `<margin>`。

## 架构设计

```
nscde-panel (PyQt6, ~500 行)
├── PaletteLoader      # 调色板加载（QProcess 调用 colorcalc）
├── CDEStyle           # CDE 3D 边框 QSS 生成器
├── SubPanel           # 子面板弹出（QDialog + Popup flag）
├── CDEPanel           # 主面板 QWidget
│   ├── LauncherBar        # 左侧启动器按钮
│   ├── WorkspaceSwitcher  # 工作区切换器（4 按钮）
│   ├── TaskBar            # 任务栏（/proc 枚举窗口，QTimer 刷新）
│   ├── SystemTray         # 系统托盘（QSystemTrayIcon）
│   └── Clock              # 时钟显示（QTimer 每秒更新）
└── main()             # 入口
```

## GTK → Qt API 映射表

| GTK3 功能 (nscde-panel 行号) | PyQt6 等价 |
|---|---|
| `Gtk.Window` + `set_decorated(False)` (L475-482) | `QWidget` + `FramelessWindowHint` |
| `GtkLayerShell.set_layer(BOTTOM)` (L549) | `WindowStaysOnTopHint` + 手动定位 |
| `GtkLayerShell.set_exclusive_zone(58)` (L550) | `setFixedHeight(58)` + labwc margin 配置 |
| `Gtk.Box(HORIZONTAL)` (L607) | `QHBoxLayout` |
| `Gtk.Button` + CSS (L667) | `QPushButton` + `setStyleSheet()` |
| `Gtk.Label` (L652) | `QLabel` |
| `Gtk.CssProvider` (L561-606) | `QWidget.setStyleSheet()` 直接设置 QSS |
| `GLib.timeout_add(1000, cb)` (L716) | `QTimer.timeout.connect(cb)` + `timer.start(1000)` |
| `subprocess.Popen(cmd)` (L38) | `QProcess.startDetached(cmd)` |
| `subprocess.run([colorcalc, ...])` (L526-529) | `QProcess.start()` + `waitForFinished(3000)` |
| `signal.signal(SIGINT, handler)` (L493) | 保持不变，Python signal 模块 |
| `Gdk.Screen.get_primary_monitor()` (L449) | `QApplication.primaryScreen()` |
| `dbus-python` SNI 实现 (L219-327) | `QSystemTrayIcon`（内置 SNI 支持） |
| 工作区切换 `labwc -a GoToDesktop wsN` (L796) | `QProcess.startDetached("labwc", ["-a", "GoToDesktop", f"ws{N}"])` |
| `Gtk.Window` + `LayerShell OVERLAY` 子面板 (L329-461) | `QDialog` + `Qt.WindowType.Popup` + `FramelessWindowHint` |

## 关键设计决策

### Layer Shell
纯 Qt 窗口 flags，不引入 C++ 编译依赖。labwc 的 `<margin top="58">` 配置保证面板不与其他窗口重叠。

### 系统托盘
使用 `QSystemTrayIcon`（已验证在 labwc 下 `isSystemTrayAvailable() = True`），替代手动 D-Bus SNI 实现。右键菜单用 `setContextMenu(QMenu)`。

### 窗口跟踪
labwc 0.9.6 运行时未暴露 `wlr_foreign_toplevel_management_v1`（虽然二进制包含该代码），fallback 用 `/proc` 枚举：

```python
GUI_APPS = {'foot', 'firefox', 'pcmanfm-qt', 'thunderbird', 'fuzzel', ...}
for pid in os.listdir('/proc'):
    if pid.isdigit():
        comm = open(f'/proc/{pid}/comm').read().strip()
        if comm in GUI_APPS:
            yield pid, comm
```

使用 `QTimer` 每 2 秒刷新一次任务栏。

### 子面板
用 `QDialog` + `Popup` flag 替代 `Gtk.Window` + `LayerShell OVERLAY`：

```python
dialog = QDialog(parent)
dialog.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
dialog.exec()  # 模态弹出
```

### 调色板加载
保持调用 `nscde-wayland-colorcalc` 的方式，用 `QProcess` 替代 `subprocess.run`。

## 文件变更

| 文件 | 操作 | 说明 |
|---|---|---|
| `wayland/bin/nscde-panel` | **重写** | 827 行 PyGTK → ~500 行 PyQt6 |
| `wayland/labwc/autostart` | **不修改** | 启动逻辑不变 |
| 其他文件 | **不修改** | nscde-wayland-run/colorcalc/theme 等保持不变 |

## 实施步骤

1. 创建新文件 `wayland/bin/nscde-panel`（PyQt6 版本）
2. 保留旧文件（已有 `wayland/bin/nscde-panel.bak`）
3. 验证：导入检查 → 启动面板 → 目视检查 → 功能测试

## 验证方式

1. `python3 -c "from PyQt6.QtWidgets import QApplication, QSystemTrayIcon; print('OK')"`
2. `wayland/bin/nscde-panel` — 启动面板，目视检查 CDE 3D 边框效果
3. 点击启动器按钮验证子面板弹出
4. 点击工作区按钮验证切换
5. 检查时钟每秒更新
6. 运行 `nscde-wayland-doctor` 确认面板进程正常

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| Qt 面板无法获得 exclusive-zone | labwc rc.xml 中配置 `<margin top="58">` |
| QSystemTrayIcon 在 labwc 下功能受限 | 已验证可用；如右键菜单有问题，fallback 到手动 Qt D-Bus SNI |
| 窗口跟踪不精确 | 与 GTK 版相同限制，后续等 labwc 启用 foreign-toplevel 再改进 |
| PyQt6 在目标系统上不可用 | 作为依赖声明，与 nscde-wayland-session 包一起安装 |
| 面板窗口在 Wayland 下无法精确定位到底部 | `QScreen.availableGeometry()` 获取工作区，手动 `move(x, y+height-58)` |
