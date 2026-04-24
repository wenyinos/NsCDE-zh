# NsCDE-zh 开发速查指南

## 🔧 核心约束
- **必须使用 AT&T ksh93**（非 bash/pdksh/mksh）
- FreeBSD/OpenBSD/NetBSD 需 GNU 工具：`gsed`, `gmake`
- 构建系统：Autotools (autoconf/automake) → `./autogen.sh && ./configure && make`
- 运行时依赖：FVWM2 2.6.7+ 或 FVWM3 + Python3 + X11 工具链

## 🚀 关键命令
```bash
# 完整构建安装
./autogen.sh && ./configure --prefix=/usr && make && sudo make install

# 验证翻译文件
msgfmt -c po/*.po

# 手动设置 DPI（中文显示异常时）
sed -i 's/Xft.dpi: 96/Xft.dpi: 120/' ~/.NsCDE/Xdefaults.fontdefs
xrdb -merge ~/.NsCDE/Xdefaults.fontdefs
```

## 📁 目录结构
- `data/fvwm/` - FVWM 核心配置
- `lib/python/` - 主题引擎 (Theme.py)
- `lib/scripts/` - Shell 工具脚本
- `po/` - 中文翻译文件 (.zh.po)
- `nscde_tools/` - GUI 工具集合

## ⚠️ 常见陷阱
1. **字体渲染**：中文显示为方框 → 检查并调整 `Xft.dpi`
2. **Qt 集成**：必须运行 `qt5ct` 并设置 `QT_QPA_PLATFORMTHEME=qt5ct`
3. **无自动化测试**：所有功能需手动验证
4. **翻译长度限制**：FvwmScript 对话框有固定尺寸，保持翻译简短

## 🌏 中文支持
- 默认字体：Noto Sans CJK SC + Mono CJK SC
- 设置语言：在 `~/.NsCDE/NsCDE.conf` 中添加 `LANGUAGE=zh_CN`
- 配置 Qt 字体：通过 `qt5ct` 工具单独设置