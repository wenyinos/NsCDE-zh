# NsCDE-zh 全库代码审计报告

**审计日期**: 2026-04-28
**审计范围**: 全部源码（Shell、Python、C、FvwmScript、打包配置、翻译文件、CI/CD）
**审计工具**: 静态代码分析 + 人工交叉验证

---

## 统计总览

| 严重性 | Shell | Python | C | 打包 | 翻译 | 合计 |
|--------|-------|--------|---|------|------|------|
| 🔴 Critical | 6 | 5 | 3 | 1 | 0 | **15** |
| 🟠 High | 18 | 8 | 4 | 5 | 3 | **30** |
| 🟡 Medium | 14 | 14 | 4 | 10 | 4 | **46** |
| 🔵 Low | 9 | 5 | 3 | 7 | 3 | **27** |
| **合计** | **47** | **32** | **14** | **23** | **10** | **126** |

---

## 处理状态更新（2026-04-28）

### 已处理完成

- ✅ Critical：`C1-C15`（15/15）
- ✅ High：`H1-H22`（22/22）

### 本轮补齐（High 尾项）

- `nscde_tools/bootstrap.in`
- `nscde_tools/style_managers.shlib.in`
- `nscde_tools/fontmgr.in`
- `nscde_tools/colormgr.in`
- `nscde_tools/backdropmgr.in`

### 说明

- 本报告正文保留审计时的问题描述与修复建议，作为审计基线。
- 上述状态反映当前仓库修复进度（截至 2026-04-28）。

---

## 一、🔴 Critical 问题（必须立即修复）

### C1. `nscde_tools/ised.in:76-78` — 竞态条件导致数据丢失

读取和写入同一文件，中断时文件被清零。`ised` 被调用约 50 次，影响面极广。

```ksh
RESULT=$(cat "${IFILE}" | $SED $SEDOPTS "$SEDCODE")
echo "$RESULT" > "$IFILE"  # 如果管道失败，IFILE 被截断为 0 字节
```

**修复**: 先写临时文件再 `mv` 原子替换：

```ksh
tmpfile=$(mktemp "${IFILE}.XXXXXX") || exit 1
cat "${IFILE}" | $SED $SEDOPTS "$SEDCODE" > "$tmpfile" && mv "$tmpfile" "$IFILE"
```

---

### C2. `nscde_tools/confset.in:51` — Python 2 的 `.iteritems()` 在 Python 3 上崩溃

`.iteritems()` 在 Python 3 中已移除。`confset` 是核心配置写入工具，被大量脚本调用。

```python
for k, v in d.iteritems():  # Python 3 已移除此方法
```

**修复**: 改为 `d.items()`。

---

### C3. `lib/python/Opts.py.in:42` — `yaml.load()` 任意代码执行漏洞

未指定 `Loader=` 参数，允许从不受信任的 YAML 文件中执行任意 Python 代码。

```python
tmpdict = yaml.load(stream)  # 无 Loader= 参数
```

**修复**: 改为 `yaml.safe_load(stream)`。

---

### C4. `lib/python/Theme.py.in:30-32` — `sys.exit(2)` 在 try/except 外，成功时也退出

`sys.exit(2)` 缩进在 `except` 块之外，导致即使 `os.makedirs` 成功也会退出程序。

```python
try: os.makedirs(homedotthemes)
except OSError as e: sys.stderr.write("Failed to create ~/.themes stop.\n"), e
sys.exit(2)  # ← 即使成功也执行！
```

**修复**: 将 `sys.exit(2)` 移入 `except` 块内，或删除（`except` 已写 stderr）。

---

### C5. `lib/python/MotifColors.py.in:343-350` — IndexError + 缺少换行符

两个问题：
1. `for i in range(0,20)` — 文件不足 20 行时 `lines[i]` 抛出 `IndexError`
2. `f.write(l)` — 缺少 `\n`，输出文件内容全部连成一行

```python
for i in range(0,20):  # 文件不足 20 行时崩溃
    lines[i]=re.sub('ts_color',ts[colorsetnr],lines[i])
# ...
with open(outfile, 'w') as f:
    for l in lines:
        f.write(l)  # 缺少换行符
```

**修复**:
```python
for i in range(min(20, len(lines))):
# ...
    for l in lines:
        f.write(l + '\n')
```

---

### C6. `src/colorpicker/colorpicker.c:61-62,100` — 空指针解引用 + 错误销毁 Root Window

三个问题：
1. `XOpenDisplay(NULL)` 返回值未检查 NULL
2. 随后对 `display` 直接解引用导致崩溃
3. `XDestroyWindow(display, root)` 销毁 Root Window 会破坏会话

```c
Display *display = XOpenDisplay(NULL);  // 未检查 NULL
Window root = DefaultRootWindow(display);  // 直接解引用
// ...
XDestroyWindow(display, root);  // Root Window 不应被销毁！
```

**修复**:
```c
Display *display = XOpenDisplay(NULL);
if (!display) { fprintf(stderr, "Cannot open display\n"); return 1; }
// ...
// 删除 XDestroyWindow(display, root);
```

---

### C7. `nscde_tools/chtheme.in:158-159,203-204` — 死代码，Qt5/Qt6 Kvantum 样式表配置永远不会写入

内层 `if` 条件与外层矛盾，形成不可达分支。`qt5kvantumsetup` 和 `qt6setup` 均有此 bug。

```ksh
if (($STYLE5Check1 != 0)); then      # 外层：Check1 不为 0
   if (($STYLE5Check1 == 0)); then    # 内层：永远为假！（死代码）
```

**修复**: 重写逻辑分支，将内层条件改为 `else` 分支处理 `@Invalid()` 存在的情况。

---

### C8. `lib/python/MiscFun.py.in:39` — `OSError` 没有 `.output` 属性

访问不存在的属性会抛出 `AttributeError`，掩盖真正的错误。

```python
except OSError as e:
    print (e.output)  # AttributeError！应该是 CalledProcessError
```

**修复**: 改为 `print(e)` 或 `print(e.strerror)`。

---

### C9. `lib/python/Theme.py.in:31` — 错误信息被丢弃

逗号表达式创建元组，错误详情被静默丢弃。

```python
sys.stderr.write("Failed to create ~/.themes stop.\n"), e  # e 被丢弃
```

**修复**: `sys.stderr.write(f"Failed to create ~/.themes: {e}\n")`

---

### C10. `lib/python/ThemeGtk.py.in:16-18` — 仍尝试导入 PyQt4

PyQt4 已于 2015 年 EOL，在现代 Python 3 上必定失败，增加启动延迟。

```python
try:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
except ImportError:
    from PyQt5.QtGui import *
```

**修复**: 移除 PyQt4 分支，改为 PyQt5 → PyQt6 fallback。

---

### C11. `nscde_tools/confset.in:101` — 裸 `except:` 吞掉所有异常

捕获 `SystemExit`、`KeyboardInterrupt`、`MemoryError` 等不应被捕获的异常。

```python
except:
    print ("Cannot open file", conffile, "trying to create it.")
```

**修复**: 改为 `except (FileNotFoundError, PermissionError, IOError):`。

---

### C12. `nscde_tools/confset.in:108-110` — `cmdoptions()` 被调用两次

第一次调用结果被丢弃，且如果缺少必需参数会在第一次调用时崩溃。

```python
if __name__ == '__main__':
    cmdoptions()     # 第一次调用，结果丢弃
    main()           # main() 内部再次调用 cmdoptions()
```

**修复**: 删除第 109 行的 `cmdoptions()`。

---

### C13. `nscde_tools/confget.in:75-76` — 同上，`cmdoptions()` 被调用两次

与 C12 相同的问题模式。

---

### C14. `src/colorpicker/colorpicker.c:70,77` — XGetImage 快照坐标越界

启动时截屏获取快照，后续鼠标点击坐标可能超出截图范围（窗口移动/多屏变化）。

```c
XImage *image = XGetImage(display, root, 0, 0, gwa.width, gwa.height, AllPlanes, ZPixmap);
// ...
unsigned long pixel = XGetPixel(image, e.xbutton.x_root, e.xbutton.y_root);  // 可能越界
```

**修复**: 改为每次点击时执行一次 `XGetImage`，或校验坐标范围。

---

### C15. `nscde_tools/bootstrap.in:44-48` — 错误信息变量名写错

检查 `NSCDE_TOOLSDIR` 但错误信息显示 `NSCDE_ROOT`，复制粘贴 bug。

```ksh
if [ -z $NSCDE_TOOLSDIR ]; then
   gettext -s "Error: NSCDE_ROOT is not set cannot continue."  # 应为 NSCDE_TOOLSDIR
```

---

## 二、🟠 High 问题（严重影响可靠性）

### H1. Shell 脚本大量变量未加引号（18 处）

`bootstrap.in`、`style_managers.shlib.in`、`fontmgr.in`、`colormgr.in`、`backdropmgr.in` 等文件中：

```ksh
if [ -z $HOME ]; then        # 空值时语法错误
if [ -z $NSCDE_ROOT ]; then  # 同上
cp ${NSCDE_DATADIR}/...       # 路径有空格时断裂
mkdir -p ${FVWM_USERDIR}/{palettes,templates,...}  # 花括号展开不安全
```

**修复**: 统一加引号 `[ -z "$HOME" ]`、`"${NSCDE_DATADIR}/..."`。

---

### H2. `nscde_tools/confset.in:85` — properties 模式解析空行崩溃

```python
props = dict(line.split('=', 1) for line in cff)  # 空行没有 '='，ValueError
```

**修复**: 添加过滤 `if '=' in line`。

---

### H3. `nscde_tools/bootstrap.in:361` — gsettings 输出重定向到 /dev/null

stdout 被丢弃，`gcolorscheme` 变量永远为空，后续条件判断失效。

```ksh
gcolorscheme=$(gsettings get org.gnome.desktop.interface color-scheme >/dev/null 2>&1)
```

**修复**: 移除 `>/dev/null`，保留 `2>/dev/null`。

---

### H4. `nscde_tools/chtheme.in:92-98` — gsettings 条件反转

gsettings 不存在时尝试使用它。

```ksh
whence -q gsettings
if (($? != 0)); then        # gsettings 不存在
   COLOR_SCHEME=$(gsettings get ...)  # 却尝试使用！
```

**修复**: 改为 `if (($? == 0)); then`。

---

### H5. `nscde_tools/bootstrap.in:763-764` — ised 替换模式错误

搜索条件应为 `xeditor` 而非 `filemgr`。

```ksh
$NSCDE_TOOLSDIR/ised -c "s/InfoStoreAdd filemgr true/InfoStoreAdd xeditor ${xedit_suggest}/g"
#                       ^^^^^^^^^^^^^^^^^^^^^^^^ 应为 InfoStoreAdd xeditor gvim
```

**修复**: 改为 `s/InfoStoreAdd xeditor gvim/InfoStoreAdd xeditor ${xedit_suggest}/g`。

---

### H6. `lib/python/Opts.py.in:52-53,60-61` — shell=True 命令注入

```python
cmd='cp'+' '+filename+' '+backup
output = subprocess.check_output(cmd, shell=True)  # 命令注入
# ...
cmd='ls'+' '+palettedir+'/*.dp'
output = subprocess.check_output(cmd, shell=True)  # 命令注入
```

**修复**: 用 `shutil.copy2()` 和 `glob.glob()` 替代。

---

### H7. `lib/python/Opts.py.in:62` — Python 3 bytes vs str

`subprocess.check_output()` 返回 `bytes`，`splitlines()` 返回 `[bytes, ...]`，后续 `os.path.basename` 接收 `bytes` 类型。

```python
output = subprocess.check_output(cmd, shell=True)
lines = output.splitlines()  # [bytes, ...]
return [os.path.basename(l) for l in lines]  # bytes 路径
```

**修复**: `output.decode('utf-8').splitlines()`。

---

### H8. `src/pclock/src/Graphics.c:165-169` — XTextProperty 内存泄漏

`XStringListToTextProperty` 分配的 `window_name.value` 未释放。

**修复**: `XSetWMName` 后调用 `XFree(window_name.value);`。

---

### H9. `src/pclock/src/Graphics.c:226,294` — `old_second` 类型/比较语义错误

`old_second` 为 `double`，`s` 为 `int`，比较 `s == old_second` 语义不稳定，导致每次循环都认为时间变化而持续重绘。

**修复**: 将 `old_second` 改为 `int`。

---

### H10. `src/pclock/src/Main.c:208-233` — `atoi` 缺少范围校验

数值参数仅 `atoi(optarg)`，非法输入导致绘制异常或数值溢出。

**修复**: 使用 `strtol` 并做上下界校验。

---

### H11. `src/*/Makefile.am` — `_SOURCE` 应为 `_SOURCES`

Automake 标准变量名错误。

| 文件 | 错误变量 | 应改为 |
|------|----------|--------|
| `src/pclock/src/Makefile.am:10` | `fpclock_SOURCE` | `fpclock_SOURCES` |
| `src/colorpicker/Makefile.am:9` | `colorpicker_SOURCE` | `colorpicker_SOURCES` |

---

### H12. `lib/python/ThemeGtk.py.in:23`、`Theme.py.in:15` — 通配符导入

```python
from MiscFun import *  # 污染命名空间
```

**修复**: 改为显式导入 `from MiscFun import checkFile, checkDir, execWithShell`。

---

### H13. `lib/python/MotifColors.py.in:308,342` — `open()` 未指定编码

非 UTF-8 locale 下，调色板文件中的特殊字符会乱码或失败。

```python
with open(filename) as f:  # 无 encoding=
```

**修复**: `open(filename, encoding='utf-8')`。

---

### H14. `po/NsCDE-FontMgr.zh.po:76` — 按钮文本缺少前导空格

FvwmScript 对话框按钮使用前导/尾随空格填充，缺失会导致视觉裁剪。

```
msgid: " Save "
msgstr: "保存"  # 应为 " 保存 "
```

---

### H15. `po/nscde-migrate-1x_to_2x.zh.po` — 3 条未翻译字符串

| 行号 | msgid | 建议 msgstr |
|------|-------|-------------|
| 87 | `"removing "` | `"删除 "` |
| 109 | `"and pathnames consolidated in them."` | `"且其中的路径名已合并之后。"` |
| 178 | `"Backup copy of "` | `"备份副本 "` |

---

### H16. `po/NsCDE-WindowMgr.zh.po:28` 等 — 尾随空格缺失影响布局

管道 `|` 分隔的菜单字符串，尾随空格定义列宽，中文翻译中缺失。

| 文件 | 行号 | 问题 |
|------|------|------|
| `NsCDE-WindowMgr.zh.po` | 28 | `"配置部分："` → `"配置部分： "` |
| `NsCDE-BackdropMgr.zh.po` | 37 | `"背景变体："` → `"背景变体： "` |
| `NsCDE-BackdropMgr.zh.po` | 40 | `"图片变体："` → `"图片变体： "` |
| `NsCDE-Subpanel.zh.po` | 82 | `"子面板标题列表宽度："` → `"子面板标题列表宽度： "` |
| `NsCDE-Subpanel.zh.po` | 85 | `"此子面板已启用："` → `"此子面板已启用： "` |

---

### H17. `pkg/debian/control:19` — 用户偏好软件列为硬依赖

`qterminal, pcmanfm-qt, gvim, pavucontrol-qt, arandr, kcalc` 应为 Recommends 而非 Depends。

---

### H18. `pkg/rpm/NsCDE.spec:24` — 同上，RPM 也有相同问题

---

### H19. `pkg/rpm/NsCDE.spec:15` — 幽灵 BuildRequires

`libXt-devel` — configure.ac 不检查 Xt，这是多余依赖。

---

### H20. `pkg/pacman/PKGBUILD:27` — `sha256sums=('SKIP')` 无完整性校验

任何被篡改的源码包都会被接受。

---

### H21. `pkg/freebsd/Makefile:20-32` — 缺少运行时依赖

`imagemagick`、`xdotool`、`groff`、`xterm` 均缺失。

---

### H22. `pkg/rpm/NsCDE.spec:82` — RPM changelog 缺少 2.3.4 版本条目

最新条目为 `2.3.2-1`，但 spec Version 为 `2.3.4`。

---

## 三、🟡 Medium 问题

### Shell 脚本

| 文件 | 行号 | 问题 | 修复 |
|------|------|------|------|
| `backdropmgr.in` | 163,184 | ksh 语法错误：`if (($? == 0)) then` 缺分号 | 加 `;` |
| `fontmgr.in` | 26 | 全局 `IFS=" "` 影响后续所有字段分割 | 仅在需要时局部设置 |
| `fontmgr.in` | 239 | `tr '[a-z]' '[A-Z]'` 语法错误 | 改为 `tr 'a-z' 'A-Z'` |
| `fontmgr.in` | 266 | `if [ -n $NewFont ]` 永远为真 | 加引号 `"$NewFont"` |
| `colormgr.in` | 227 | `mv` 目标路径未加引号 | 加引号 |
| `style_managers.shlib.in` | 24,48,72 | `ls -1` 输出解析不可靠 | 用 glob 替代 |
| `sysinfo.in` | 43 | swap 百分比计算错误 | 移除 `/ 1024 / 1024` |
| `sysinfo.in` | 26,34 | 裸 `except:` | 指定异常类型 |
| 多文件 | — | `egrep` 已废弃 | 改为 `grep -E` |
| `chtheme.in` | 284 | `/usr/bin/cpp` 硬编码 | 用 `@CPP@` 或 `type -p cpp` |
| `backdropmgr.in` | 34,47 | `[ -x $(type -p file) ]` 空值时为真 | 加引号 |

### Python 代码

| 文件 | 行号 | 问题 | 修复 |
|------|------|------|------|
| `MotifColors.py.in` | 19-23 | 模块级可变全局状态 | 封装为类 |
| `MotifColors.py.in` | 56-63 | `int2hex()` 浮点精度问题 | 用 `format(n, '04x')` |
| `MotifColors.py.in` | 349-350 | 文件句柄泄漏（无 `with`） | 使用 `with` |
| `ThemeGtk.py.in` | 117-119 | 逐字符写文件 | 直接 `f.write(lines)` |
| `ThemeGtk.py.in` | 156-234 | 三段近乎相同的代码块 | 提取辅助函数 |
| `ThemeGtk.py.in` | 171,195,220 | QPixmap 无存在性检查 | 检查 `isNull()` |
| `Theme.py.in` | 46 | `shutil.rmtree` 无安全检查 | 断言路径在用户目录内 |
| `Opts.py.in` | 67-68 | `@classmethod` 用 `self` 而非 `cls` | 改为 `cls` |
| `MiscFun.py.in` | 18 | 调试 `print(cmd)` 残留 | 删除 |
| `MiscFun.py.in` | 47,53 | `sys.exit()` 无退出码 | 改为 `sys.exit(1)` |
| `palette_colorgen.in` | 628-637 | 文件句柄泄漏 | 使用 `with` |
| `palette_colorgen.in` | 760-772 | 用 `NameError` 做控制流 | 初始化默认值 |

### C 源码

| 文件 | 行号 | 问题 | 修复 |
|------|------|------|------|
| `colorpicker.c` | 33,43-46 | `output_format` 位操作语义不清 | 改用枚举 |
| `Graphics.c` | 339-354 | `GetColor` 失败静默返回黑色 | 明确返回默认值并记录 |
| `XOverrideFontCursor.c` | 47 | `strncmp` 前缀匹配可能误触发 | 改用精确匹配 |

### 打包配置

| 文件 | 行号 | 问题 | 修复 |
|------|------|------|------|
| `NsCDE.spec` | 26-27 | Noto 字体 VF 与非 VF 包重复 | 精简为 2 个 |
| `PKGBUILD` | 33 | 缺少 `--sysconfdir=/etc` | 添加参数 |
| `freebsd/Makefile` | 41 | 同上 | 添加参数 |
| `freebsd/Makefile` | 43-44 | `pre-configure` 与 `USES= autoreconf` 冲突 | 删除 `pre-configure` |
| `debian/control` | 15 | 允许 fvwm2，与其他平台不一致 | 统一为 `fvwm3` |
| `debian/control` | 18 | `groff-base, groff` 冗余 | 仅保留 `groff` |
| `debian/copyright` | 2 | 版权年份过期（2021） | 更新为 `2019-2026` |
| `debian/control` | 8 | `Standards-Version: 4.5.0` 过期 | 更新为 `4.7.0` |
| `debian/watch` | 1 | 无实际 watch URL | 添加 GitHub tags 监控 |
| `NsCDE.spec` | 22 | `dunst`、`xclip` 作为硬依赖 | 移至 Recommends |

### 翻译文件

| 文件 | 行号 | 问题 | 修复 |
|------|------|------|------|
| `NsCDE-FontMgr.zh.po` | 头部 | 元数据仍为原始作者 | 更新为 `Wenyin Root` |
| `NsCDE-GWM.zh.po` | 头部 | 同上 | 同上 |
| `NsCDE.zh.po` | 1365 | 上游 typo "Fifeteen" | 报告上游 |
| `NsCDE.zh.po` | 959,962 | 上游语法错误 "it's" → "its" | 报告上游 |

---

## 四、🔵 Low 问题

| 文件 | 问题 |
|------|------|
| 多文件 | `==` 在 `[ ]` 中非 POSIX（ksh 支持但不推荐） |
| 多文件 | 引号风格不一致（部分路径加引号，部分不加） |
| `colormgr.in:139` | `""${HOME}""` 多余的空引号 |
| `palette_colorgen.in:333` | `with` 块内多余 `.close()` |
| `confset.in:82-105` | properties 模式解析脆弱（空行、无 `=` 行） |
| `XOverrideFontCursor.c:25-26` | `_Xconst` 宏已无必要 |
| `pclock/getopt.c` | 内置旧版 GNU getopt，可能与系统 libc 冲突 |
| `NsCDE.spec:22` | `sed` 作为运行时依赖（每个系统都有） |
| `PKGBUILD:25` | `provides=('nscde-zh')` 冗余 |
| `debian/rules:13` | `-XREADME` 不匹配 `README.md` |
| `debian/control:20-21` | 两个 Qt 平台主题包名重复 |
| `freebsd/pkg-descr:11` | "Qt4/Qt5" 应为 "Qt5/Qt6" |
| `SpritesGtk2.py` | 无类型提示和文档字符串 |
| `MotifColors.py.in:86,103` | 无效颜色静默回退 |
| `MiscFun.py.in:31` | 返回类型不一致 |

---

## 五、现有 TODO 清单

### 根目录 `TODO`（3 项）

1. **文件管理器作为 Application Manager** — 中等难度，`pcmanfm-qt` 已有部分支持
2. **替换 PyQt4/PyQt5 API** — 高难度，涉及主题集成架构
3. **FvwmScript 设置默认终端/编辑器/文件管理器** — 中低难度，**推荐优先实现**

### `src/pclock/TODO`（9 项）

| 项目 | 难度 | 推荐 |
|------|------|------|
| 点击执行命令 | 低 | ✅ 优先做 |
| `-geometry` 位置支持 | 低-中 | ✅ 优先做 |
| 每次只画指针不重绘 | 中 | ❌ 收益低 |
| 指针加入 shape mask | 中-高 | 可选 |
| 允许小于 64x64 背景 | 中 | 可选 |
| Alarm/chime 功能 | 中-高 | 可选 |
| 动画指针 | 中 | 可选 |
| 指针阴影和抗锯齿 | 高 | ❌ 不建议 |
| 任意 pixmap 指针 | 高 | ❌ 不建议 |

### `bootstrap.in:763` 疑似 bug（非 TODO 但相关）

xeditor 替换使用了错误的搜索模式（`filemgr` 应为 `xeditor`），实现默认应用设置 TODO 前应先修复。

---

## 六、翻译完整性

| 语言 | 文件数 | 已翻译 | 未翻译 | 完成率 |
|------|--------|--------|--------|--------|
| 中文 (zh) | 25 | ~1162 | 3 | 99.7% |
| 克罗地亚文 (hr) | 25 | ~1165 | 0 | 100% |

**中文缺失条目**: `nscde-migrate-1x_to_2x.zh.po` 中 3 条（见 H15）。

---

## 七、跨平台依赖一致性矩阵

| 依赖 | Debian | RPM | Arch | FreeBSD | configure.ac | 状态 |
|------|--------|-----|------|---------|-------------|------|
| `fvwm` | `fvwm\|fvwm3` | `fvwm3` | `fvwm3` | `fvwm3` | fvwm/fvwm2/fvwm3 | ⚠️ Debian 不一致 |
| `imagemagick` | 隐式 | 二进制检查 | ✅ | **缺失** | convert/import | 🔴 FreeBSD 缺失 |
| `xdotool` | ✅ | ✅ | ✅ | **缺失** | xdotool | 🔴 FreeBSD 缺失 |
| `dunst` | Recommends | **硬依赖** | optdepends | **缺失** | warn | ⚠️ 不一致 |
| `xclip` | Recommends | **硬依赖** | optdepends | **缺失** | warn | ⚠️ 不一致 |
| `groff` | 冗余双列 | `groff-base` | `groff` | **缺失** | warn | ⚠️ FreeBSD 缺失 |
| `python3-yaml` | ✅ | ✅ | ✅ | ✅ | yaml | ✅ 一致 |
| `python3-pyqt5` | ✅ | ✅ | ✅ | ✅ | PyQt5 | ✅ 一致 |

---

## 八、代码重复问题

| 位置 | 描述 | 建议 |
|------|------|------|
| `bootstrap.in:171-241` | 6 个 GTK/Qt 集成问答块 ~90% 相同 | 提取 `ask_yn_integration` 函数 |
| `chtheme.in:134-177` vs `179-222` | `qt5kvantumsetup` 和 `qt6setup` 95% 相同 | 参数化 `qtctsetup(version)` |
| `style_managers.shlib.in` | `FindPalettes`/`FindBackdrops`/`FindPhotos` 结构相同 | 提取 `FindResources(pattern)` |
| `style_managers.shlib.in` | `GetPaletteByNumber`/`GetBackdropByNumber`/`GetPhotoByNumber` 相同 | 提取 `GetByNumber(list, num)` |
| `ThemeGtk.py.in:156-234` | 三段 colorset 处理代码近乎相同 | 提取 `_apply_colorset()` |

---

## 九、建议修复优先级

### P0 紧急（数据丢失/崩溃/安全漏洞）

| 编号 | 问题 | 文件 | 风险 |
|------|------|------|------|
| C1 | ised 竞态条件 | `ised.in:76-78` | 低 |
| C2 | iteritems 崩溃 | `confset.in:51` | 低 |
| C3 | yaml.load RCE | `Opts.py.in:42` | 低 |
| C4 | sys.exit 逻辑错误 | `Theme.py.in:30-32` | 低 |
| C6 | colorpicker 空指针 | `colorpicker.c:61` | 低 |

### P1 重要（功能异常）

| 编号 | 问题 | 文件 | 风险 |
|------|------|------|------|
| C5 | MotifColors 换行 | `MotifColors.py.in:349` | 低 |
| C7 | chtheme 死代码 | `chtheme.in:158` | 低 |
| C8 | OSError.output | `MiscFun.py.in:39` | 低 |
| H3 | gsettings 输出丢弃 | `bootstrap.in:361` | 低 |
| H4 | gsettings 条件反转 | `chtheme.in:92` | 低 |
| H5 | ised 模式错误 | `bootstrap.in:763` | 低 |
| H6 | shell 注入 | `Opts.py.in:52,60` | 低 |
| H15 | 翻译缺失 | `nscde-migrate-1x_to_2x.zh.po` | 低 |

### P2 改善（代码质量）

| 范围 | 工作量 |
|------|--------|
| Shell 变量引号统一 | 中（18 处） |
| `egrep` → `grep -E` | 低（全局替换） |
| Makefile.am `_SOURCES` 修正 | 低（2 处） |
| 翻译空格修复 | 低（6 处） |
| 元数据更新 | 低（2 个 .po 文件） |

### P3 优化（架构改进）

| 范围 | 工作量 |
|------|------|
| 代码去重（5 处） | 中 |
| PyQt4 导入移除 | 低 |
| 打包依赖精简 | 中 |
| pclock TODO 实现 | 中 |
| 默认应用 FvwmScript | 高 |

---

## 十、附录：版本一致性检查

| 组件 | 版本 | 来源 | 状态 |
|------|------|------|------|
| `configure.ac:9` | `2.3.4` | 规范 | ✅ |
| Debian changelog | `2.3.4+zh-1` | 派生 | ✅ |
| RPM spec Version | `2.3.4` | 派生 | ✅ |
| RPM changelog 最新 | **`2.3.2-1`** | 手动 | 🔴 **缺失 2.3.4** |
| Arch PKGBUILD | `2.3.4` | 派生 | ✅ |
| FreeBSD Makefile | `2.3.4` | 派生 | ✅ |
| CI workflow | 自动提取 | `configure.ac` | ✅ |

---

*报告生成完毕。*
