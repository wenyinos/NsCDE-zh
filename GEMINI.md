# NsCDE-zh 项目上下文 (Project Context)

## 项目概述 (Project Overview)
**NsCDE-zh** 是 **NsCDE (Not so Common Desktop Environment)** 的简体中文本地化版本。它通过 FVWM 窗口管理器和一系列辅助脚本，在现代操作系统上重现了 90 年代商业 UNIX 系统（如 Solaris, HP-UX, AIX）中常见的 **CDE (Common Desktop Environment)** 视觉体验。

### 核心架构
- **窗口管理器 (WM):** 基于 **FVWM** (2.6.x 或 3.x)，NsCDE 本质上是一套极其复杂的 FVWM 配置和模块集合。
- **后台驱动:** 使用 **Korn Shell (ksh93)** 编写高性能的后台处理脚本。
- **主题引擎:** 基于 **Python 3** 的生成器，能够实时同步生成 GTK2, GTK3, Qt4, Qt5 和 Motif 的主题，实现全局视觉统一。
- **本地化:** 采用 **gettext** 系统。由于 `FvwmScript` 编写的 GUI 界面尺寸是静态硬编码的，中文翻译必须在保持语义的同时尽量精简，以防 UI 溢出。

## 构建与运行 (Building and Running)
项目使用标准的 GNU Autotools 构建系统。

### 构建指令
```bash
./autogen.sh
./configure --prefix=/usr
make
sudo make install
```

### 核心依赖
- **必需:** `fvwm`, `ksh93`, `gettext`, `python3` (需 `psutil`, `pyxdg`, `yaml`, `PyQt5`)。
- **视觉/功能:** `ImageMagick` (用于截屏和图标转换), `xsettingsd` (用于动态 GTK 主题应用), `stalonetray` (系统托盘)。
- **中文支持:** 强烈建议安装 `fonts-noto-cjk`。

## 目录结构 (Key Directories)
- `bin/`: 启动脚本 (`nscde`)。
- `data/`: 包含 FVWM 基础配置、复古图标集、调色板 (`palettes/`) 和背景图片 (`backdrops/`)。
- `lib/python/`: Python 主题引擎的核心逻辑，处理不同 Toolkit 的样式转换。
- `nscde_tools/`: 桌面管理工具集，如字体管理器 (`fontmgr`)、背景管理器 (`backdropmgr`) 和初始化脚本 (`bootstrap`)。
- `po/`: 翻译源文件。`NsCDE.zh.po` 是主程序的中文翻译。
- `src/`: 嵌入式 C 工具，如 `pclock` (复古时钟) 和 `colorpicker`。
- `xdg/`: 符合 XDG 标准的菜单、图标和桌面入口定义。

## 开发与贡献规范 (Development Conventions)
- **本地化工作流:** 修改 `po/` 下的 `.po` 文件后，需运行 `make` 重新编译为 `.mo`。
- **UI 限制:** 在翻译 `FvwmScript` 相关文本时，务必进行运行时测试，确保中文文本不会导致按钮或标签被截断。
- **脚本标准:** 
    - 后台逻辑和驱动优先使用 `ksh93`。
    - 涉及 GUI 交互或复杂逻辑（如主题生成）优先使用 `Python 3`。
- **路径规范:** 所有的安装路径应遵循 `$NSCDE_ROOT`。用户配置文件存储在 `~/.NsCDE/`。

## 验证与测试
- **语法检查:** 使用 `msgfmt -c po/*.po` 检查翻译文件。
- **运行日志:** 检查 `~/.NsCDE/` 下的日志文件以调试 FVWM 或脚本错误。
- **环境变量:** 本地化生效依赖于 `LC_MESSAGES` 或 `LANG` 正确设置为 `zh_CN.UTF-8`。
