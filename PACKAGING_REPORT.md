# NsCDE-zh 打包脚本审计与改进计划 (Packaging Audit & Improvement Plan)

本计划旨在修复和优化 `pkg/` 目录下各发行版的构建脚本，确保跨平台的一致性和构建的健壮性。

## 1. 发现的问题总结

### 1.1 Debian (`pkg/debian/`)
- **依赖精度**：`ksh` 依赖应明确指向 `ksh93`，以避免在某些系统上调用兼容性较差的旧版 ksh。
- **缺失工具**：建议显式列出 `x11-xserver-utils` 之外的子工具（如 `xmodmap`, `xrefresh`）。

### 1.2 Arch Linux (`pkg/pacman/PKGBUILD`)
- **源码解压路径硬编码**：`cd "NsCDE-zh-${pkgver}_zh"` 在上游标签命名微调时会失效。
- **架构支持限制**：目前仅标注 `x86_64`，建议增加 `aarch64`。

### 1.3 RPM (`pkg/rpm/NsCDE.spec`)
- **路径歧义**：未显式定义 `libexecdir`，导致不同发行版间工具路径不统一。
- **文件列表过宽**：`%{_bindir}/*` 存在打包构建环境无关文件的风险。
- **依赖冗余**：Noto 字体依赖项中普通版与可变字体（VF）版重复。

## 2. 拟实施的改进步骤

### 步骤 1: 优化 Debian 配置
- 修改 `pkg/debian/control`，将依赖由 `ksh | ksh93` 改为 `ksh93`。
- 更新 `Standards-Version` 为最新标准。

### 步骤 2: 增强 Arch 构建脚本健壮性
- 将 `PKGBUILD` 中的 `cd` 指令改为动态匹配模式（如 `cd "${srcdir}/NsCDE-zh-"*`）。
- 将 `arch` 扩展为 `('x86_64' 'aarch64')`。

### 步骤 3: 精细化 RPM Spec 文件
- 在 `%configure` 中增加 `--libexecdir=%{_libexecdir}/NsCDE` 参数。
- 精确化 `%files` 列表，显式列出主程序文件。
- 合并并精简 `google-noto-sans-cjk-fonts` 及其相关依赖。

## 3. 验证方案
- 在干净的容器环境（pbuilder/mock/devtools）中分别触发各平台的构建流程。
- 检查生成的包内文件权限（特别是 `XOverrideFontCursor.so` 具备可执行权限）。
- 验证 `/usr/lib/NsCDE` 路径在各平台是否统一。

---
**生成日期**：2026年4月23日
**执行者**：Gemini CLI
