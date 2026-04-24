# TODO 功能实现难度与方案分析

## 总体结论

仓库 TODO 分两类：

1. 根目录 `TODO`：NsCDE 桌面集成级功能，涉及 FVWM、FvwmScript、配置文件、工具脚本、安装依赖，风险中等到高。
2. `src/pclock/TODO`：独立 X11 C 小程序增强，范围集中在 `src/pclock/src/Main.c`、`Graphics.c`、`PClock.h`，多数可逐项小步实现，风险从低到高不等。

推荐优先级：

1. 优先做根目录第 3 项：默认终端、编辑器、文件管理器的 FvwmScript 设置界面。
2. 其次修根目录第 1 项：把 `pcmanfm-qt` 作为 Application Manager 的体验做完整。
3. `pclock` 可优先做点击执行命令、`-geometry` 位置支持、小背景支持。
4. PyQt 替代方案和 pclock 高级绘制优化属于较大设计任务，不建议作为第一批实现。

## 根目录 TODO

### 1. 默认文件管理器作为 Application Manager

位置：`TODO:5-6`

当前状态：

- `data/fallback/app-catalog/filemgr` 已将 `pcmanfm-qt` 放在第一优先级。
- `nscde_tools/bootstrap.in:645-684` 已在首次配置时检测并写入 `InfoStoreAdd filemgr ...`。
- `nscde_tools/fpseticon.in` 已有针对 `pcmanfm` / `pcmanfm-qt` 的硬编码特殊处理。
- `data/fvwm/Menus.fvwmconf:22` 已通过 `$[infostore.filemgr]` 启动文件管理器。
- `data/fvwm/Main.fvwmconf.in` 中已有 `f_AppMgrOrXEditor` 相关逻辑。

难度：中等

主要难点：

- “Application Manager” 在 NsCDE 里不只是打开文件管理器，可能还涉及前面板按钮、子面板菜单、桌面应用列表生成。
- 需要确认现有 `appmgr` 与 `filemgr` 的职责是否应合并，还是只在无原生 App Manager 时 fallback 到 `pcmanfm-qt`。
- `pcmanfm-qt` 的桌面文件 ID 在不同发行版可能不同，bootstrap 里当前通过 `${ans}.desktop`、`org.kde.${ans}.desktop`、`org.gnome.${ans}.desktop` 猜测，有兼容性风险。

推荐方案：

1. 梳理 `infostore.appmgr`、`infostore.filemgr`、前面板按钮配置和 `f_AppMgrOrXEditor` 的实际调用路径。
2. 明确行为：如果有应用管理器则启动 app manager，否则用 `pcmanfm-qt` 打开应用目录或 `applications:///`。
3. 在 fallback catalog 中保留 `pcmanfm-qt` 第一优先级，不新增强依赖。
4. 如果需要更像 Application Manager，可为 `pcmanfm-qt` 增加专用启动参数或目录路径，但需要验证其行为。
5. 修改范围预计为 `data/fvwm/Main.fvwmconf.in`、`data/fvwm/Functions.fvwmconf.in`、可能还有 `nscde_tools/fpseticon.in` 和文档。

风险：

- 可能改变用户当前前面板按钮行为。
- 不同桌面环境下 `pcmanfm-qt` 可用性和 `.desktop` 名称不一致。
- 需要手动验证 FVWM2/FVWM3。

### 2. 替换 PyQt4/PyQt5 API，降低 GTK/Qt 主题集成依赖

位置：`TODO:8-9`

当前状态：

- README 仍列出 `PyQt5`、`qt5ct`、`qt5-qtstyleplugins`。
- 主题和字体集成主要在 `lib/scripts/FontMgr.in`、`lib/scripts/ColorMgr.in`、`nscde_tools/chtheme.in` 等处处理。
- 现有逻辑很多已经通过 `confset` 写 `qt5ct.conf`、`qt6ct.conf`、GTK config、xsettingsd，而不是直接依赖 PyQt GUI API。
- 需要进一步定位真正使用 PyQt 的 Python 文件，当前只读搜索看到 “PyQt” 匹配很多，但多数是说明或配置相关。

难度：高

主要难点：

- 这不是单点替换，涉及主题集成架构。
- 如果完全去掉 PyQt，需要确认哪些工具还需要 GUI、颜色选择、Qt palette 生成、预览能力。
- GTK/Qt 集成跨 GTK2/GTK3/GTK4、Qt4/Qt5/Qt6、Kvantum、qt5ct/qt6ct，兼容面很大。
- 项目支持多 BSD 与 Linux，不能依赖过新的桌面 API。

推荐方案：

1. 先做依赖审计：找出所有 PyQt import、configure 检测、包说明、运行时调用。
2. 将功能分层：配置写入、颜色/字体转换、GUI 展示、外部工具调用。
3. 优先把非 GUI 部分收敛到已有 shell/Python 工具，例如 `confset`、`palette_colorgen`、`chtheme`。
4. 对 Qt 集成优先走配置文件协议：`qt5ct.conf`、`qt6ct.conf`、Kvantum 模板，而不是 Qt API。
5. 如果仍需 GUI，优先复用 FvwmScript，而不是引入新 GUI toolkit。
6. 最后才移除 configure/README 里的 PyQt 依赖。

风险：

- 高概率影响 Style Manager、Font Manager、Color Manager。
- 需要大量人工视觉验证。
- 一次性做容易回归，建议拆成“审计、配置写入替代、GUI 替代、依赖移除”四个阶段。

### 3. FvwmScript 设置默认终端、编辑器、文件管理器

位置：`TODO:11-12`

当前状态：

- `nscde_tools/bootstrap.in:645-811` 已在初始配置时用命令行交互设置 `filemgr`、`xeditor`，并提示用户可手动设置 `terminal`。
- `data/fvwm/Functions.fvwmconf.in:1053-1069` 已有 `f_FindApp` 自动查找逻辑。
- `data/fallback/app-catalog/terminal`、`filemgr`、`text-editor` 已有候选列表。
- `data/fvwm/Menus.fvwmconf:21-23` 已从 `infostore.terminal`、`infostore.filemgr`、`infostore.xeditor` 启动默认应用。

难度：中等偏低

这是根目录 TODO 中最适合优先实现的一项。

推荐方案：

1. 新增一个 FvwmScript，例如 `DefaultAppsMgr.in` 或 `AppDefaultsMgr.in`。
2. UI 提供三组输入框或列表：Terminal、File Manager、Editor。
3. 默认值读取 `$[infostore.terminal]`、`$[infostore.filemgr]`、`$[infostore.xeditor]`。
4. 候选值来自 `data/fallback/app-catalog/terminal`、`filemgr`、`text-editor`，通过 helper 脚本过滤当前 PATH 中存在的程序。
5. 保存时使用现有 `nscde_tools/ised` 更新 `$FVWM_USERDIR/NsCDE.conf`。
6. 可选：同步调用 `xdg-mime default`，但建议第一版只写 NsCDE 配置，避免副作用。
7. 在 Style Manager 或控制菜单中增加入口。

建议第一版范围：

- 新增 FvwmScript UI。
- 新增或复用 shell helper 读取候选。
- 只改 `~/.NsCDE/NsCDE.conf` 的三项 `InfoStoreAdd`。
- 不碰系统 MIME 默认应用。

风险：

- FvwmScript 语法较特殊，调试成本比普通 shell 高。
- 中文翻译长度受固定窗口尺寸影响，需要短文案。
- 保存后是否立即生效需要明确：可以提示重启 NsCDE，或执行 `Read $FVWM_USERDIR/NsCDE.conf`。

额外发现：

- `nscde_tools/bootstrap.in:764` 看起来有疑似 bug：在设置推荐编辑器时使用了 `s/InfoStoreAdd filemgr true/InfoStoreAdd xeditor ${xedit_suggest}/g`，这里搜索条件可能应为 `InfoStoreAdd xeditor gvim`。这不属于 TODO 本身，但和默认编辑器设置功能相关，建议实现该 TODO 前先确认并修复。

## pclock TODO

### 1. 点击时执行命令

位置：`src/pclock/TODO:1`

当前状态：

- `Graphics.c:163` 只监听 `ExposureMask | StructureNotifyMask`。
- `HandleEvents()` 当前只处理 `Expose`、`DestroyNotify`、`ClientMessage`。
- `options` 结构无 command 字段。
- `Main.c` 使用 `getopt_long`，新增参数成本低。

难度：低

推荐方案：

1. 增加 `--command=CMD` 或 `-e CMD` 参数。
2. 在 `options` 增加 `click_command`。
3. `XSelectInput` 增加 `ButtonPressMask`。
4. 在 `HandleEvents()` 里处理 `ButtonPress`。
5. 使用 `fork` + `execl("/bin/sh", "sh", "-c", command, NULL)`，避免阻塞时钟主循环。
6. 文档和 `--help` 增加说明。

风险：

- 命令执行涉及 shell 注入，但这是用户本地显式传入命令，行为类似 `sh -c`，可接受。
- 需要避免僵尸进程，可使用 `signal(SIGCHLD, SIG_IGN)` 或双 fork。

### 2. 每次只画指针，不重绘整体

位置：`src/pclock/TODO:2`

当前状态：

- `Graphics.c:229` 每次 `XCopyArea(back_pm -> all_pm)`，随后绘制所有指针。
- 当前固定 64x64，性能压力很小。

难度：中等

价值：低

推荐方案：

- 不建议优先做。
- 如果做，需要保存上次指针覆盖区域，只重绘 dirty rectangle。
- 透明 mask 和异形窗口会让局部刷新复杂化。
- 由于只有 64x64，完整重绘更简单、更可靠。

风险：

- 容易引入残影、透明背景边缘错误。
- 性能收益几乎不可见。

### 3. 将指针加入 shape mask，支持透明时钟

位置：`src/pclock/TODO:3`

当前状态：

- `CreateWindow()` 中 `XShapeCombineMask(... mask_pm ...)` 只使用背景 XPM mask。
- README 已说明限制：`clock hands are drawn within the mask of the background XPM file`。
- 如果指针超出背景 mask，会被裁剪。

难度：中等偏高

推荐方案：

1. 创建动态 shape pixmap。
2. 每次更新时间后，将背景 mask 复制到动态 mask。
3. 按当前指针几何在 mask 上绘制白色区域。
4. `XShapeCombineMask` 更新窗口 bounding shape。
5. 注意 hour/minute 是 polygon，second hand 是 line，需要对应绘制到 1-bit mask。

风险：

- 每秒更新 shape 可能有窗口管理器兼容问题。
- X Shape 1-bit mask 绘制与普通 depth pixmap 不同，需要谨慎处理 GC。
- 对固定 64x64 可接受，但测试必须覆盖透明 XPM。

### 4. 允许小于 64x64 的背景

位置：`src/pclock/TODO:4`

当前状态：

- `PClock.h:41` 固定 `SIZE 64`。
- `Graphics.c:111-112` 强制外部 XPM 必须 `64x64`。
- 窗口 size hints 也固定为 `SIZE`。
- 指针长度默认假定 64 中心和半径。

难度：中等

推荐方案：

1. 保持窗口仍为 64x64。
2. 允许小图作为背景，居中或平铺到 64x64 pixmap。
3. 第一版建议“居中绘制小背景”，不要同时支持任意缩放。
4. `XpmReadFileToPixmap` 后如果小于 64，创建 64x64 `back_pm`，将小 pixmap copy 到中间。
5. mask 同理合成到 64x64 mask。

风险：

- mask 合成较容易出错。
- 任意大于 64 的背景是否拒绝要明确。建议仍拒绝大于 64，降低范围。

### 5. 支持 `-geometry`，至少位置

位置：`src/pclock/TODO:5`

当前状态：

- `Graphics.c:132` 调用了 `XWMGeometry(display, screen, "", NULL, 0, &size_hints, ...)`，但没有把用户 geometry 字符串传进去。
- `Main.c` 未提供 `-geometry` 参数。
- `size_hints.flags` 已包含 `PPosition`，但当前实际位置默认 0,0。

难度：低到中等

推荐方案：

1. 增加 `--geometry=GEOMETRY` 参数。
2. `options` 增加 `geometry` 字段。
3. 将 `XWMGeometry` 的 user geometry 参数从 `NULL` 改为 `option.geometry`。
4. 第一版只支持位置，不支持改变大小。
5. 如传入尺寸，忽略尺寸或报错，避免和固定 `SIZE` 冲突。

风险：

- X geometry 语义包含负坐标、屏幕边缘锚定，需要验证 `-0-0` 等形式。
- withdrawn/icon window 模式下位置可能受 Window Maker/FVWM swallow 影响。

### 6. Alarm/chime 功能

位置：`src/pclock/TODO:6`

难度：中等偏高

推荐方案：

1. 第一版支持 `--chime-command=CMD` 每小时执行。
2. 第二版支持 `--alarm=HH:MM --alarm-command=CMD`。
3. 使用主循环中当前时间变化判断，不引入线程。
4. 防止同一分钟重复执行，可记录上次触发日期/分钟。

风险：

- 时区、系统时间跳变、休眠恢复后重复触发。
- 命令执行同样需要非阻塞处理。
- UI 不存在，只能命令行配置。

### 7. 动画指针

位置：`src/pclock/TODO:7`

难度：中等

当前主循环 `PERIOD 200000L`，理论上每 0.2 秒更新一次，但秒针角度仍按整数秒计算。

推荐方案：

1. 使用 `gettimeofday` 得到小数秒。
2. 秒针角度按 `sec + usec / 1000000.0`。
3. 分针可选择平滑或保持分钟跳变。
4. 增加 `--smooth` 或 `--animated-hands` 参数，默认保持旧行为。

风险：

- 增加 CPU 唤醒频率意义不大，因为主循环已经 0.2 秒。
- 老式 X11 环境下可能有闪烁，但 64x64 问题不大。

### 8. 指针阴影和抗锯齿

位置：`src/pclock/TODO:8`

难度：高

原因：

- 当前直接用 Xlib primitive 绘制 polygon/line，没有 XRender/Cairo。
- 抗锯齿需要额外依赖或自行 supersampling。
- 项目整体偏轻量，新增 Cairo/XRender 依赖要谨慎。

推荐方案：

1. 阴影可低成本实现：先用偏移 1px 的暗色绘制一遍，再绘制正常指针。
2. 抗锯齿不建议直接做，除非接受引入 XRender 或 Cairo。
3. 如果做 AA，建议可选编译开关，不影响基础构建。

风险：

- 新依赖会影响 Autotools、包构建和 BSD 兼容。
- 视觉收益有限，但回归面较大。

### 9. 任意 pixmap 作为指针

位置：`src/pclock/TODO:9`

难度：高

推荐方案：

1. 增加 `--hour-hand-pixmap`、`--minute-hand-pixmap`、`--second-hand-pixmap`。
2. 载入 XPM 后需要按角度旋转。
3. Xlib 没有简单高质量旋转，需要自己做像素变换，或引入图像库。
4. 更现实的替代方案：支持静态线形配置、长度、宽度、颜色、阴影，而不是 pixmap 指针。

风险：

- 实现复杂度和收益不成比例。
- 旋转透明 pixmap、mask、抗锯齿都很麻烦。
- 不建议近期实现。

## 推荐实施路线

### 第一阶段：低风险可见改进

1. 实现 pclock 点击执行命令。
2. 实现 pclock `--geometry` 位置支持。
3. 修正/确认 bootstrap 默认编辑器写入逻辑。
4. 设计默认应用 FvwmScript 的最小版本，只写 `terminal/filemgr/xeditor`。

### 第二阶段：桌面集成完善

1. 完成默认应用 FvwmScript 菜单入口。
2. 增加候选程序检测 helper。
3. 增加中文 gettext 文案。
4. 手动验证 FVWM2/FVWM3、首次启动和 reconfigure。

### 第三阶段：Application Manager 行为

1. 明确 `appmgr` 与 `filemgr` 的关系。
2. 将 `pcmanfm-qt` fallback 行为固化到前面板/菜单。
3. 处理 `.desktop` 和 MIME 的兼容性，但避免强行修改系统默认应用。

### 第四阶段：高成本视觉与主题任务

1. PyQt 依赖替换先做审计报告，再拆实现。
2. pclock 透明 mask、动画、阴影可逐项做。
3. 抗锯齿和 pixmap 指针不建议优先做。

## 建议优先落地的最小方案

如果下一步进入实现，建议先做这个组合：

1. `pclock --command`：单文件小改，功能明确，验证简单。
2. `pclock --geometry`：顺手补齐已有 `XWMGeometry` 未使用的能力。
3. 修 `bootstrap.in` 默认编辑器替换疑似 typo。
4. 之后再做默认应用 FvwmScript，因为它涉及更多文件和手动验证。

这个顺序风险最低，也能快速清掉一部分 TODO。
