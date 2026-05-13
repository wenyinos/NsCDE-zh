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
| CDE 前面板 | ✅ FvwmButtons | ⚠️ sfwbar 临时方案 | 外观近似但非 CDE 等价 |
| 子面板弹出 | ✅ | ❌ | sfwbar 不支持子面板概念 |
| 前面板按钮 | ✅ | ⚠️ | sfwbar 有启动按钮，但无 CDE 3D 立体效果 |
| 时钟小程序 | ✅ FvwmScript | ⚠️ sfwbar 内置 | 功能简单，无 CDE 风格外观 |
| 托盘区域 | ✅ stalonetray | 🔄 sfwbar SNI tray | 功能等价，实现不同 |
| 工作区切换器 | ✅ FvwmButtons | ⚠️ sfwbar 基本按钮 | 无 page 概念 |
| CPU/负载监视器 | ✅ FvwmScript | ❌ | 未实现 |

## 菜单

| 功能 | X11 版 (FVWM) | Wayland 版 (labwc) | 差异说明 |
|---|---|---|---|
| 右键根菜单 | ✅ | ✅ | labwc menu.xml |
| XDG 应用菜单 | ✅ PipeRead 动态生成 | ⚠️ pipe-menu 静态脚本 | 刚实现基础版本 |
| 菜单图标 | ✅ | ⚠️ | labwc 支持但配置方式不同 |
| 菜单加速键 | ✅ | ❌ | labwc 菜单不支持加速键 |
| 子菜单嵌套 | ✅ | ✅ | labwc menu.xml 支持 |
| 动态菜单（pipe-menu） | ✅ PipeRead | ⚠️ 刚验证 | 需要脚本输出 XML |

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
| CDE 窗口装饰 | ✅ FVWM Colorset | ⚠️ 静态 themerc | 手写固定配色，无动态生成 |
| 调色板系统 | ✅ | ⚠️ | assets 中有调色板文件，但无生成器 |
| GTK2 主题 | ✅ 自动生成 | ❌ | themegen 未移植 |
| GTK3 主题 | ✅ 自动生成 | ❌ | themegen 未移植 |
| GTK4 主题 | N/A | ❌ | 新增需求 |
| Qt5/Qt6 主题 | ✅ 自动生成 | ⚠️ | nscde-wayland-run 有基本配置，但无生成器 |
| Kvantum 主题 | ✅ | ⚠️ | nscde-wayland-run 写入基本配置 |
| Motif/Xt 主题 | ✅ | ❌ | Wayland 下无意义 |
| Firefox CSS 主题 | ✅ | ❌ | 未移植 |
| Thunderbird CSS 主题 | ✅ | ❌ | 未移植 |
| 背景/壁纸 | ✅ fvwm-root | 🔄 swaybg/wbg | 功能等价，实现不同 |
| 壁纸管理器 | ✅ BackdropMgr | ❌ | 无 GUI 管理器 |

## 工具与管理器

| 功能 | X11 版 (FVWM) | Wayland 版 (labwc) | 差异说明 |
|---|---|---|---|
| 颜色管理器 | ✅ FvwmScript ColorMgr | ❌ | 需重写为 GTK/Qt |
| 字体管理器 | ✅ FvwmScript FontMgr | ❌ | 需重写为 GTK/Qt |
| 样式管理器 | ✅ FvwmScript StyleMgr | ❌ | 需重写为 GTK/Qt |
| 背景管理器 | ✅ FvwmScript BackdropMgr | ❌ | 需重写为 GTK/Qt |
| 窗口管理器设置 | ✅ FvwmScript WindowMgr | ❌ | 需重写为 GTK/Qt |
| 键盘管理器 | ✅ FvwmScript KeyboardMgr | ❌ | 需重写为 GTK/Qt |
| 指针管理器 | ✅ FvwmScript PointerMgr | ❌ | 需重写为 GTK/Qt |
| 系统信息 | ✅ FvwmScript Sysinfo | ❌ | 需重写为 GTK/Qt |
| 默认应用管理器 | ✅ FvwmScript DefaultAppsMgr | ❌ | 需重写为 GTK/Qt |
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

## 统计

| 类别 | 等价 | 部分/降级 | 未实现 | 替换 |
|---|---|---|---|---|
| 窗口管理 | 4 | 3 | 2 | 0 |
| 工作区 | 2 | 2 | 2 | 0 |
| 前面板 | 1 | 4 | 2 | 1 |
| 菜单 | 3 | 2 | 1 | 0 |
| 快捷键 | 2 | 0 | 2 | 0 |
| 主题视觉 | 0 | 5 | 6 | 1 |
| 工具管理器 | 0 | 0 | 12 | 0 |
| 会话启动 | 4 | 1 | 0 | 0 |
| 辅助工具 | 0 | 1 | 1 | 4 |
| **合计** | **16** | **18** | **28** | **6** |

等价率：16/68 = **24%**。加上部分实现：34/68 = **50%**。
