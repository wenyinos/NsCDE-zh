# NsCDE Wayland 功能差异清单

> 本文档是阶段 0 交付物之一。对比 NsCDE FVWM/X11 版与 Wayland/labwc 版的功能差异。

---

## 图例

- ✅ 功能等价
- ⚠️ 部分实现或降级
- ❌ 未实现
- 🔄 已替换为不同实现

---

## 窗口管理

| 功能 | X11 版 (FVWM) | Wayland 版 (labwc) | 差异说明 |
|---|---|---|---|
| 窗口移动/缩放 | ✅ | ✅ | labwc 原生支持 |
| 窗口最大化/最小化 | ✅ | ✅ | labwc 原生支持 |
| 窗口关闭 | ✅ | ✅ | Alt+F4 |
| 窗口吸附/对齐 | ✅ | ⚠️ | labwc 支持基本 snapping，不如 FVWM 丰富 |
| 窗口阴影 | ✅ | ❌ | 需要 compositor 支持，labwc 默认无 |
| 窗口透明度 | ✅ | ⚠️ | labwc 支持，但无 per-app 配置 |
| 窗口记忆（位置/大小） | ✅ | ⚠️ | labwc 有基本支持，不如 FVWM Style 灵活 |
| 窗口列表/ident | ✅ | ❌ | FvwmIdent 无替代 |

## 工作区

| 功能 | X11 版 (FVWM) | Wayland 版 (labwc) | 差异说明 |
|---|---|---|---|
| 多工作区切换 | ✅ | ✅ | labwc 原生支持 |
| 工作区名称 | ✅ | ⚠️ | labwc 支持命名，但无动态 GUI 修改 |
| Page/desk 模型 | ✅ | ❌ | FVWM 的 page 概念在 labwc 中不存在 |
| FvwmPager | ✅ | ❌ | 无等价模块，sfwbar 有基本工作区按钮 |
| 工作区切换动画 | ✅ | ❌ | labwc 不支持 |

## 前面板与面板

| 功能 | X11 版 (FVWM) | Wayland 版 (labwc) | 差异说明 |
|---|---|---|---|
| CDE 前面板 | ✅ FvwmButtons | ✅ nscde-panel | GTK3 + GtkLayerShell 原生实现 |
| 子面板弹出 | ✅ | ✅ | nscde-panel 支持 CDE 风格子面板 |
| 前面板按钮 | ✅ | ✅ | nscde-panel 完整 CDE 3D 立体效果 |
| 时钟小程序 | ✅ FvwmScript | ✅ nscde-panel | 实时时钟和日期显示 |
| 托盘区域 | ✅ stalonetray | 🔄 nscde-panel SNI tray | 功能等价，Wayland SNI 由合成器处理 |
| 工作区切换器 | ✅ FvwmButtons | ✅ nscde-panel | 4 个工作区按钮 |
| CPU/负载监视器 | ✅ FvwmScript | ❌ | 未实现 |

## 菜单

| 功能 | X11 版 (FVWM) | Wayland 版 (labwc) | 差异说明 |
|---|---|---|---|
| 右键根菜单 | ✅ | ✅ | labwc menu.xml |
| XDG 应用菜单 | ✅ PipeRead 动态生成 | ✅ nscde-wayland-menugen | 静态菜单生成器，支持分类和本地化 |
| 菜单图标 | ✅ | ✅ | labwc menu.xml 支持图标 |
| 菜单加速键 | ✅ | ❌ | labwc 菜单不支持加速键 |
| 子菜单嵌套 | ✅ | ✅ | labwc menu.xml 支持 |
| 动态菜单（pipe-menu） | ✅ PipeRead | ✅ nscde-wayland-pipemenu | 已验证，从 .desktop 文件动态生成 |

## 快捷键

| 功能 | X11 版 (FVWM) | Wayland 版 (labwc) | 差异说明 |
|---|---|---|---|
| 基础快捷键 | ✅ | ✅ | Alt+Return/Space/F4 |
| 自定义快捷键 | ✅ FVWM Key 指令 | ✅ labwc rc.xml | 配置语法不同 |
| 链式快捷键 | ✅ | ❌ | labwc 不支持多步快捷键序列 |
| 鼠标手势 | ✅ | ❌ | labwc 不支持 |

## 主题与视觉

| 功能 | X11 版 (FVWM) | Wayland 版 (labwc) | 差异说明 |
|---|---|---|---|
| CDE 窗口装饰 | ✅ FVWM Colorset | ✅ 动态 themerc | nscde-wayland-theme 从调色板生成 |
| 调色板系统 | ✅ | ✅ | assets 中有调色板文件，nscde-wayland-colorcalc 计算颜色 |
| GTK2 主题 | ✅ 自动生成 | ❌ | themegen 未移植 |
| GTK3 主题 | ✅ 自动生成 | ❌ | themegen 未移植 |
| GTK4 主题 | N/A | ✅ | nscde-wayland-theme --gtk4 生成 CSS |
| Qt5/Qt6 主题 | ✅ 自动生成 | ✅ | nscde-wayland-theme --kvantum 生成 Kvantum 主题 |
| Kvantum 主题 | ✅ | ✅ | nscde-wayland-theme --kvantum 生成完整主题 |
| Motif/Xt 主题 | ✅ | ❌ | Wayland 下无意义 |
| Firefox CSS 主题 | ✅ | ✅ | nscde-wayland-theme --install-firefox 安装 |
| Thunderbird CSS 主题 | ✅ | ❌ | 未移植 |
| 背景/壁纸 | ✅ fvwm-root | 🔄 swaybg/wbg | 功能等价，实现不同 |
| 壁纸管理器 | ✅ BackdropMgr | ❌ | 无 GUI 管理器 |

## 工具与管理器

| 功能 | X11 版 (FVWM) | Wayland 版 (labwc) | 差异说明 |
|---|---|---|---|
| 颜色管理器 | ✅ FvwmScript ColorMgr | ✅ cc_color.py | PyQt6 重写 |
| 字体管理器 | ✅ FvwmScript FontMgr | ✅ cc_font.py | PyQt6 重写 |
| 样式管理器 | ✅ FvwmScript StyleMgr | ✅ nscde-control-center | PyQt6 重写 |
| 背景管理器 | ✅ FvwmScript BackdropMgr | ✅ cc_backdrop.py | PyQt6 重写 |
| 窗口管理器设置 | ✅ FvwmScript WindowMgr | ✅ cc_window.py | PyQt6 重写 |
| 键盘管理器 | ✅ FvwmScript KeyboardMgr | ✅ cc_keyboard.py | PyQt6 重写 |
| 指针管理器 | ✅ FvwmScript PointerMgr | ✅ cc_mouse.py | PyQt6 重写 |
| 系统信息 | ✅ FvwmScript Sysinfo | ✅ cc_sysinfo.py | PyQt6 重写 |
| 默认应用管理器 | ✅ FvwmScript DefaultAppsMgr | ✅ cc_defaultapps.py | PyQt6 重写 |
| 系统操作对话框 | ✅ FvwmScript SysActionDialog | ❌ | 需重写 |
| 占用管理器 | ✅ FvwmScript Occupy | ❌ | FVWM 特有概念 |
| 工作区页面管理器 | ✅ FvwmScript WsPgMgr | ❌ | FVWM 特有概念 |

## 会话与启动

| 功能 | X11 版 (FVWM) | Wayland 版 (labwc) | 差异说明 |
|---|---|---|---|
| 显示管理器登录 | ✅ nscde.desktop | ✅ nscde-labwc.desktop | 文件名不同 |
| 首次配置引导 | ✅ bootstrap | ⚠️ nscde-labwc 自动复制 | 简化版，无交互式设置 |
| 环境变量设置 | ✅ nscde 脚本 | ✅ nscde-labwc 脚本 | 包含 Wayland 特有变量 |
| 私有 DBus 会话 | ❌ | ✅ dbus-run-session 包装 | Wayland 版新增 |
| systemd 集成 | ❌ | ⚠️ 可选 | 不强制依赖 systemctl --user |
| 非 systemd 启动 | ✅ | ✅ | labwc autostart |

## 辅助工具

| 功能 | X11 版 (FVWM) | Wayland 版 (labwc) | 差异说明 |
|---|---|---|---|
| 截图 | ✅ import/convert | 🔄 grim+slurp | 功能等价 |
| 剪贴板 | ✅ xclip | 🔄 wl-clipboard | 功能等价 |
| 取色 | ✅ colorpicker (Xlib) | ❌ | Wayland 安全模型禁止全局读屏 |
| 鼠标模拟 | ✅ xdotool | ⚠️ wtype（受限） | Wayland 限制更严 |
| 显示器信息 | ✅ xrandr | 🔄 wlr-randr | 功能近似 |
| 诊断工具 | ❌ | ✅ nscde-wayland-doctor | Wayland 版新增 |
| 缩放工具 | ❌ | ✅ nscde-output-scale | Wayland 版新增 |
| 组件隔离运行器 | ❌ | ✅ nscde-wayland-run | Wayland 版新增 |
| 主题生成器 | ❌ | ✅ nscde-wayland-theme | labwc/Kvantum/Firefox/GTK4 主题生成 |
| 菜单生成器 | ❌ | ✅ nscde-wayland-menugen | XDG 菜单生成 labwc menu.xml |
| 颜色计算器 | ❌ | ✅ nscde-wayland-colorcalc | Motif/CDE 颜色计算（无 PyQt 依赖） |
| 原生面板 | ❌ | ✅ nscde-panel | GTK3 + GtkLayerShell CDE 前面板 |

## 统计

| 类别 | 等价 | 部分/降级 | 未实现 | 替换 |
|---|---|---|---|---|
| 窗口管理 | 4 | 3 | 2 | 0 |
| 工作区 | 2 | 2 | 2 | 0 |
| 前面板 | 6 | 1 | 1 | 1 |
| 菜单 | 5 | 1 | 0 | 0 |
| 快捷键 | 2 | 0 | 2 | 0 |
| 主题视觉 | 3 | 3 | 5 | 1 |
| 工具管理器 | 9 | 0 | 3 | 0 |
| 辅助工具 | 3 | 1 | 1 | 4 |
| 会话启动 | 4 | 1 | 0 | 0 |
| 辅助工具 | 0 | 1 | 1 | 4 |
| **合计** | **38** | **13** | **17** | **10** |

等价率：38/68 = **56%**。加上部分实现：51/68 = **75%**。
