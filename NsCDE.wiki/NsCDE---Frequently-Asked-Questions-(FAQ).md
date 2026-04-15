## 主要

**问：什么是 NsCDE？**

**答：** 基于 FVWM 和通用自由软件的 Common Desktop Environment (CDE) 重新实现，开箱即用。复古外观兼具现代计算任务所需功能。某种程度上，是另一种桌面计算未来的严肃体现。

***

**问：为什么选择 NsCDE？**

**答：** 因为扁平设计、缓慢且功能贫乏的界面——模仿大厂“现代”扁平触控风格——在各方面都很糟糕：
* 可用性
* 功能与灵活性
* 性能与速度
* 稳定性
* 视觉外观缺乏与主流差异化的选择

也就是说，NsCDE 在 UNIX 和 Linux X11 显示屏上的表现，就如同建筑中的[粗野主义](https://en.wikipedia.org/wiki/Brutalist_architecture)。粗犷、巨石般、坚固且实用——并非人人喜欢。NsCDE 不试图取悦所有人，也不假装是每个人都想要和喜欢的东西。

## 安装（警告：本节仅适用于 2.0 之前的 NsCDE，对 2.0 版本基本适用，但个别系统可能有差异）

**问：安装和运行 NsCDE 的系统要求是什么？**

**答：** 你需要：

* Linux 或 FreeBSD 系统。NetBSD、OpenBSD 也可能可行。NsCDE 已在 CentOS 7、Fedora 28-31、Debian、Ubuntu、Astra、Arch 等系统上测试过...
* Xorg
* [FVWM](https://github.com/fvwmorg/fvwm)，即将支持 [FVWM3](https://github.com/fvwmorg/fvwm3)
* Korn Shell (ksh)
* Python 3
* Python 模块：yaml, xdg, re, shutil, subprocess, fnmatch, getopt, time, platform, psutil, pwd, socket（大部分已包含在核心 Python 3 中）
* ImageMagick（convert 工具）
* PyQt5 或 PyQt4
* 标准 X11 工具（cpp, xrdb, xset, xrefresh, xprop, xdpyinfo, xterm）
* GNU sed 和 (e)grep
* [xdotool](https://github.com/jordansissel/xdotool)
* 各种第三方开源免费组件 ([xsettingsd](https://github.com/derat/xsettingsd), [stalonetray](http://stalonetray.sourceforge.net/), [xscreensaver](https://www.jwz.org/xscreensaver/download.html), [dunst](https://dunst-project.org/))

另外：

* 至少一个 CPU，不超过 20 年历史
* 256 MB 物理内存
* 90 MB 磁盘空间用于 NsCDE，约 500 MB 用于依赖项

如今大部分依赖项都很容易满足，几乎所有软件都可以从所用操作系统的包仓库中获取。

***

**问：Installer.ksh 有很多选项。我在使用未打补丁的 FVWM 2.6.{7,8,9} 的常规 Linux 系统上，如何安装 NsCDE？**

**答：** 解压发行版或用 git 克隆分支，进入 NsCDE 安装目录并以 root 身份运行：\

`# ./Installer.ksh -w -n -i`

升级过程如下：

`# ./Installer.ksh -w -n -u`

升级时无需卸载旧版本。使用 "-u" 参数调用 Installer.ksh（如上所示）即可完成工作，不会产生垃圾文件。效果如同全新安装。

***

**问：安装程序报告缺少包或 Python 模块的错误**

**答：** 阅读这些消息，然后使用你喜欢的包管理器（yum, apt, dnf, pacman, pkg ...）安装这些依赖项。

***

**问：为什么 NsCDE 为其 X 资源、Stalonetray 和 Xsettingsd、Dunst 等的配置文件使用自己的路径？**

**答：** NsCDE 将这些配置文件作为模板提供。这些文件部分或完全由 NsCDE 样式管理器和应用程序管理。也就是说，所有这些文件都在 `$HOME/.NsCDE` 中，避免覆盖用户原有的配置文件。无论出于何种原因，用户可以选择不使用 NsCDE 提供的一个或多个组件的配置，而是使用自己的配置，这些配置不由 NsCDE 管理。

***

**问：我对运行 Installer.ksh 有点担心。它会对我的系统做什么？**

**答：** 安装程序非常谦逊和谨慎。它会执行以下操作：

* 将 NsCDE 安装到 /opt/NsCDE，或你用可选 "-p" 参数指定的位置，或用 "-D" 进行打包。
* 将名为 "nscde.desktop" 的 txt/ini 文件定义放入 /usr/share/xsessions（在某些系统如 BSD 上，这是 /usr/local/share/xsessions），以便你的显示管理器知晓它。
* 在 /usr/local/share/icons 中创建一个名为 "NsCDE" 的主题图标符号链接。

安装程序的卸载过程将删除主安装目录以及 xsession 文件和符号链接。你也可以手动操作。

***

**问：我尝试在 OpenIndiana Illumos 上安装 NsCDE，但连 Installer.ksh 都无法启动。**

**答：** 你需要编译 FVWM、ksh、xdotool、PyQt5 以及可选的 dunst 和 xsettingsd。使用 IPS 包管理系统 pkg 命令，你需要安装 stalonetray、Python 3（当前为 3.5）模块依赖项、imagemagick 以及其他常规组件。

* 设置 IPS 包管理系统以查找开发包：`pkg set-publisher -p http://pkg.openindiana.org/sfe-encumbered`

* 安装构建环境：`pkg install pkg://openindiana.org/metapackages/build-essential`

* 然后，你需要编译 Korn Shell。OpenIndiana 的 /bin/ksh 目前存在 bug，运行任何稍复杂的脚本都会导致段错误、挂起并占用大量 CPU。先用 pkg(1) 安装 meson 构建工具。在 /usr/bin 中将 "ksh" 重命名为 "ksh.orig"，并将新编译的 ksh 放在其位置。你可以在 https://github.com/att/ast/releases/download/2020.0.0/ksh-2020.0.0.tar.gz 找到 Korn Shell。

* 然后，用 pkg(1) 安装 "scons" 构建系统。你需要这个来编译 xsettingsd。编译 xsettingsd 后，无需安装。你需要将 xsettingsd 和 dump_xsettings 复制到 /opt/local/bin，并将 man 页面复制到 /opt/local/share/man/man1 或你偏好的其他位置。只需确保该 bin 路径已在你的 X 用户 $HOME/.profile 中与其他系统路径一起定义。

* [Dunst](https://github.com/dunst-project/dunst/archive/v1.5.0.tar.gz) 的安装非常简单。只需编辑 config.mk 并运行 make install。

* 对于 PyQt5，使用 pkg(1) 安装 library/qt5。可以通过 `pip3.5 install PyQt5` 获取 PyQt5 —— 这将花费很长时间来编译所有依赖项和 C++ 代码。

* 编译并安装 [xdotool](https://github.com/jordansissel/xdotool/releases)。

* 最后，编译 [FVWM 或 FVWM3](https://github.com/fvwmorg) 并安装。注意：如果你使用的是 FVWM 2.6.X，你应该应用 NsCDE 为 FvwmButtons(1) 和 FvwmScript(1) 提供的补丁（参见 NsCDE 安装解压目录中的 src/FvwmButtons_sunkraise_windowname_unified.patch 和 src/FvwmScript_XC_left_ptr.patch），因为在 SunOS 5.11 基础系统上存在的 32 位和 64 位混合环境中 LD_PRELOAD 将无法工作。即使使用指向不同库的 LD_PRELOAD_32 和 LD_PRELOAD_64，系统也经常会产生关于不安全库路径的警告。如果你使用的是 FVWM3，则无需担心这个问题。

* 确保已安装常规必需品，如 xterm、stalonetray 等。

* 关机/挂起/重启：将以下内容添加到你的 /etc/security/exec_xattr：

`Power Off On Suspend:suser:cmd:::/usr/sbin/shutdown:uid=0`
`Power Off On Suspend:suser:cmd:::/usr/bin/sys-suspend:uid=0`

* 关机/挂起/重启：将以下内容添加到你的 /etc/security/prof_attr：

`Power Off On Suspend:::User power off reboot and suspend:help=NoHelp.help`

* 关机/挂起/重启：将以下内容添加到你的 /etc/user_attr 并将 "youruser" 替换为你的登录名：

`youruser::::type=normal;profiles=Power Off On Suspend;auths=solaris.system.power.*;roles=root`

完成上述步骤后，你应该能够安装 NsCDE。在 OpenIndiana Lightdm 显示管理器登录时，通过选择右上角的 "NsCDE" 作为会话并开始初始设置。在所有这些操作的最后，你终于让 SunOS 再次伟大起来（tm）。:-)

***

**问：在 NetBSD 和 OpenBSD 上，我无法在工作区菜单上生成 XDG 应用程序子菜单。哪里出错了？**

**答：** 桌面菜单生成器 fvwm-menu-desktop(1) 期望 /etc/xdg/menus 是硬编码的。然而，在 NetBSD 上，大部分已安装的软件位于 /etc/pkg 层级结构中。修改 fvwm-menu-desktop(1) 中的路径在这个 python 程序中是可行的，但这可能会被 fvwm 包更新覆盖。最好的方法是简单地创建一个空的 /etc/xdg/menus 目录。这可以防止 fvwm-menu-desktop 出错，而 XDG_DATA_DIRS 中由 NsCDE（重新）定义的其余路径将被处理。

***

**问：在 NetBSD 上有系统默认的 Korn shell。它能与 NsCDE 一起使用吗？**

**答：** 不行。这实际上是 pdksh，而不是 ATT ksh93。即使是 NetBSD 9.0/9.1 包中的 ast-ksh 也存在一些问题（来自 FvwmScript 的管道调用会无声地段错误，字体样式管理器无法工作...）。你需要下载 Korn shell，编译它，并以适当的方式安装，例如 /usr/local/bin。确保它被命名为 "ksh93" 或已链接到该名称，并且 /usr/local/bin 位于 $PATH 中，优先于启动 NsCDE。

***

**问：在 OpenBSD 上有系统默认的 Korn shell。它能与 NsCDE 一起使用吗？**

**答：** 不行。这实际上是 pdksh，而不是 ATT ksh93。执行 `pkg_add ksh93`，那个才是真正的且可用的。

***

**问：在非 Linux 系统上安装有什么特殊要求吗？**

**答：** Installer.ksh 会警告你。基本上，你需要 "gsed" 或 GNU sed 包。它在所有 FreeBSD、OpenBSD、NetBSD、DragonFly BSD 和 OpenIndiana Illumos 系统上都可用。在 NetBSD 上，如果你使用 FVWM3 和 "Watch Errors" 菜单项，则需要 GNU coreutils tail (gtail) 命令。在 FreeBSD 和 DragonFly BSD 上，必须安装 python3-3 元包，而在 NetBSD 上，$PATH 中必须存在名为 "python3" 的 Python3 符号链接。

以下是观察到的一些非 Linux 系统上必须满足的依赖项，以便 NsCDE 安装和运行：

* NetBSD:
   * 必须从源码编译 Korn Shell，pdksh 不是 ksh，而 pkgsrc 端口版本的真实 ksh 存在损坏并会导致核心转储
   * xsettingsd 守护进程不在 ports 中，必须从源码编译
   * 包依赖项：fvwm py37-qt5, py37-yaml, py37-psutil, ImageMagick, xdotool, dunst, stalonetray, goodies: gkrellm, qt5ct, dejavu-ttf, sudo, gsed
   * 根据所使用的显示管理器，必须使用 $HOME/.xsession 或 $HOME/.xinitrc 来执行 NsCDE。如果使用带有 NsCDE xsession 文件安装的 sddm 或类似的现代显示管理器，则不需要这样做。
   * 注意：NetBSD 缺少包含 GTK2 Qt5 引擎的 Qt5 样式插件包。Qt5 应用程序将无法集成到 NsCDE 颜色主题中。
祝你好运编译它 ...

* OpenBSD:
   * 必须从源码编译 fvwm。可以是 fvwm3（连同 libbson）或 fvwm2。OpenBSD 自带的 fvwm2 版本来自罗马时代，而包集合中的版本对 NsCDE 来说也太旧了。fvwm2 的最低支持版本是 2.6.7 或 fvwm3 1.0.2。
   * 包依赖项：fvwm py3-qt5, py3-yaml, py3-psutil, ImageMagick, xdotool, dunst, stalonetray, qt5styleplugins, ksh93, sudo, gsed
   * 如果使用默认的 OpenBSD xenodm 显示管理器，则必须使用 $HOME/.xsession 或 $HOME/.xinitrc 来执行 NsCDE。如果使用带有 NsCDE xsession 文件安装的 sddm 或类似的现代显示管理器，则不需要这样做。

* FreeBSD:
   * 包依赖项：fvwm py37-qt5, py37-yaml, py37-psutil, ImageMagick, xdotool, dunst, stalonetray, qt5-style-plugins, sudo, gsed, ast-ksh
   * 根据所使用的显示管理器，必须使用 $HOME/.xsession 或 $HOME/.xinitrc 来执行 NsCDE。如果使用带有 NsCDE xsession 文件安装的 sddm 或类似的现代显示管理器，则不需要这样做。

* DragonFly BSD:
   * stalonetray xdotool xsettingsd dunst py37-qt5 qt5ct qt5-style-plugins git py37-yaml py37-psutil py37-xdg xterm-359 ImageMagick7 ast-ksh fvwm python3 gsed sudo
   * 根据所使用的显示管理器，必须使用 $HOME/.xsession 或 $HOME/.xinitrc 来执行 NsCDE。如果使用带有 NsCDE xsession 文件安装的 sddm 或类似的现代显示管理器，则不需要这样做。

* OpenIndiana / Ilummos / Solaris / SunOS:
   * 请参阅上方几组问答中关于此 UNIX 系统的特别章节

***

## 配置与自定义

**问：如何更改默认终端模拟器、文件管理器、编辑器等？**

**答：** 在初始设置期间，大多数此类默认应用程序会被询问并为用户设置。然而有些并未设置，需要更改。编辑 $FVWM_USERDIR/NsCDE.conf 并设置适当的 FVWM InfoStore 变量，重新加载（重启 FVWM）即可生效。例如：

`InfoStoreAdd terminal mate-terminal`\
`InfoStoreAdd filemgr pcmanfm-qt`\
`InfoStoreAdd xeditor gvim`\
`InfoStoreAdd browser firefox`\
`InfoStoreAdd volumectrl pavucontrol-qt`\
`InfoStoreAdd xrandr arandr`\
`InfoStoreAdd calculator kcalc`

***

**问：窗口列表字体太大？**

**答：** 在根窗口上点击鼠标中键会弹出窗口列表。此列表上的字体可通过 InfoStore 变量控制。值为 "small"、"medium" 或 "large"。

`InfoStoreAdd windowlist.fontsize large`\
`InfoStoreAdd windowlist.title.fontsize large`

***

**问：如何添加新的子面板和/或前面板的面板列？**

**答：** 可以通过快速双击前面板图标上方的空白处来添加新面板（尝试两次或更多次）。这将弹出子面板设置对话框，可以在其中配置子面板的开关状态、宽度和名称。新的前面板启动器列可以通过前面板窗口选项菜单（左上角小按钮）中的 "Front Panel Controls" 条目，然后选择 "Number of Launchers ..." 子菜单来添加。根据屏幕分辨率，最多可以有 0 到 20 列。默认是 10 —— 工作区管理器两侧各 5 列。

***

**问：我可以更改、移动或添加前面板上的小程序吗？**

**答：** 可以。与静态图标不同，小程序不能从子面板复制到主面板。你必须编辑 $FVWM_USERDIR/FrontPanel.actions。参见 NsCDE 手册第 7.1 节 FrontPanel.actions。

***

**问：子面板宽度太小，项目名称超出空间**

**答：** 打开子面板，选择左侧唯一的标题栏按钮，从窗口操作菜单中选择 "Subpanel Settings"，并更改 "Subpanel Title List Width" 的值。不幸的是，目前没有动态或自动确定此值的方法。也许将来 FvwmButtons(1) 会有根据文本大小动态调整宽度和高度的选项。

***

**问：日历小程序和邮件小程序点击时没有任何功能**

**答：** 有许多邮件和数量较少的日历应用程序。用户可以在 $FVWM_USERDIR/NsCDE-Functions.local 中编写 NsCDE FVWM 函数 f_Calendar 和 f_CheckMail 来调用某些应用程序。在 $FVWM_USERDIR/NsCDE-Functions.local 的初始示例中，甚至有关于如何在 Thunderbird 中选择邮件或日历的有用示例。

***

**问：如何更改工作区和/或页面的数量？**

**答：** 通过使用工作区和页面管理器。可通过以下方式访问：

* 在前面板中间的工作区管理器上点击鼠标中键（关闭 Num Lock 以使点击生效！）
* 前面板的桌面设置子面板（7）
* 工作区菜单 -> 应用程序 -> NsCDE 菜单

***

**问：我能否只设置工作区而不设置页面？**

**答：** 在工作区和页面管理器中，将垂直和水平页面数设置为 1。这将完全禁用 FVWM 页面，NsCDE 将移除相关菜单、占用页面辅助对话框，将其图标的功能调整为显示工作区的全局分页器等。

***

**问：我想要页面，但我讨厌屏幕边缘翻页，如何禁用它？**

**答：** 打开样式管理器（前面板第 7 个按钮），打开窗口样式管理器，选择配置部分 "Page Edges"，然后选择 "Disable Page Change On Screen Edge" 并按 OK 重新加载并应用新配置。

***

**问：如何添加或更改默认快捷键？**

**答：** 通过编辑你的 $FVWM_USERDIR/NsCDE-Keybindings.local。在这里，你可以放置自己的快捷键定义，用 "-" 清除现有定义并覆盖它们。参见 fvwm(1) "Mouse, Key & Stroke Bindings" 部分。

***

**问：我需要更高的 DPI 和字体 DPI，应该在哪里配置什么才能获得最佳效果？**

**答：** 我们必须区分两点：屏幕 DPI（xrandr --dpi X）和字体 DPI。虽然你可以在启动文件中的任何位置放置 "xrandr --dpi XXX"，或方便地放在 ~/.NsCDE/Xset.conf 中以实现某些小部件和程序的更好行为，但字体 DPI 的处理方式不同。\
你必须在 ~/.NsCDE/NsCDE.conf 中使用 XFT_USE_DPI 并将其设置为 96、120、144 或 192 的值。
数值如下：

* DPI 96 是 100% 缩放
* DPI 120 是 125%
* DPI 144 是 150%
* DPI 192 是 200%

这些都是支持的值。默认 DPI 是普遍的 96 DPI。当设置此环境变量时，NsCDE 将计算并为字体大小添加一些填充，因此在大于 96DPI 的屏幕上使用字体样式管理器后立即重新登录并设置字体，应能自动使字体在 GTK（有时在 QT 中无需额外努力，请参见下文）中变大且更易读，并尽可能在基于 FvwmScript 的应用程序中实现，而不会破坏其不灵活的固定性质。在本地化布局下，FvwmScript 中仍可能出现一些损坏，这将在未来版本中进行调整。

***

**问：如何在窗口菜单（标题栏上的第一个按钮）中添加特定于应用程序的项目？**

**答：** 你可能已经注意到，大多数终端应用程序在窗口操作菜单末尾都有一个额外的 "Wide Terminal" 条目。窗口操作菜单可以根据调用此菜单的第一个标题栏按钮的应用程序进行自定义，以添加额外条目。系统范围的配置可以在 $NSCDE_ROOT/config/AppMenus.conf 中观察到。可以创建格式相同的文件作为 ~/.NsCDE/AppMenus.conf。语法如下：

`WindowName,WindowResourceName,Visible Title,Action`

例如：

`Gcolor2,gcolor2,New Window,Exec exec gcolor2`

这将在窗口操作菜单末尾附加 "New Window"，但仅在 gcolor2 工具的窗口上。

***

**问：如何制作自定义颜色主题（调色板）或字体集？**

**答：** 自定义颜色主题是 CDE 调色板文件：一组 8 个基础颜色定义，从中计算顶部、底部和选择偏移量。这些颜色定义（"dp" 文件）可以在 $NSCDE_ROOT/share/palettes 中找到，自定义创建的文件可以放在 ~/.NsCDE/palettes 中。当调色板存在时，它们会出现在颜色样式管理器的调色板列表中。这是手动创建颜色主题或调色板文件的方法。GUI 方法是打开颜色样式管理器并选择一个与期望外观相似的现有颜色主题，逐一选择 8 个基础颜色，然后按下颜色样本右侧的 "Modify" 按钮以微调 RGB 和 HSV 值。结果可以保存为默认的 "Custom" 名称（这将覆盖用户 ~/.NsCDE/palette/Custom.dp 中任何先前同名的调色板）或以新名称命名、保存并应用。\
对于字体集，规则相同：在字体样式管理器中，如果修改了字体列表，结果可以保存为 Custom，或命名为某个字体集。结果将最终存入 ~/.NsCDE/fontsets。请注意，手动编辑字体集只会将更改应用于 FVWM 部分的视觉应用程序，但不会更改 ~/.gtkrc-2.0、~/.config/gtk-3.0/settings.ini、~/.config/qt5ct/qt5ct.conf、~/.NsCDE/Dunst.conf、~/.NsCDE/Xsettingsd.conf、~/.NsCDE/Xdefaults.fontdefs 和其他自定义资源。

***

**问：如何使用壁纸而不是彩色平铺背景？**

**答：** 可以。默认的照片集可以从 NsCDE-Photos 仓库下载，这会放到 $NSCDE_ROOT/share/photos，但自定义照片也可以放在 ~/.NsCDE/photos 中，PNG 文件可以手动放置或通过背景样式管理器中的 "Add" 按钮添加，当选择 "Use photo or picture" 复选框时，上面的列表将从平铺颜色生成的背景更改为照片。选择照片是按工作区进行的，功能与背景相同，但这些壁纸不会像背景那样经过主题颜色预处理。

***

**问：工作区菜单中的 "Quick Menu" 子菜单是什么？**

**答：** 这是一个简单的条目和占位符，供用户在 ~/.NsCDE/NsCDE-Menus.local 中自定义，制作最喜欢的、重要的或经常使用的应用程序列表。在 ~/.NsCDE/NsCDE-Menus.local 中提供了几乎现成的 m_QuickMenu 菜单示例。只需取消注释并进行编辑即可。

***

**问：我想完全禁用页面或工作区切换时的图形本地分页器。**

**答：** 在 ~/.NsCDE/NsCDE.conf 中添加 InfoStoreAdd pageshowrootpager 0

***

**问：我想要 Solaris 风格的前面板时钟，带有地球仪和红色的时/分针，白色秒针。**

**答：** 参见 NsCDE 手册第 7.1 节的第三个示例。

***

## 可能的问题与故障排除

**问：似乎无法关机、重启、挂起或休眠系统，哪里出错了？**

**答：** 每个操作系统都有各种方式来执行这些任务。其中一些需要提升的系统权限，而另一些则不需要本地物理屏幕登录的用户权限。对于前者，必须安装并正确配置 sudo，以允许 nscde ACPI 包装器无密码操作。详情参见 NsCDE 手册第 4.15 节，以及 /opt/NsCDE/share/doc/examples/sudo/。

*** 
 
**问：似乎 Qt 应用程序没有应用字体集更改。如何解决？**

**答：** 是的。即使颜色样式管理器在 ~/.config/Trolltech.conf 中为 Qt4 和在 ~/.config/qt5ct/qt5ct.conf 中为 Qt5 放置了 GTK2 引擎，应用了主题的颜色部分，但对于字体生效，你通常必须（经常）启动 qtconfig 和/或 qt5ct 并按下字体标签中已存在条目的应用按钮。这将暂停 3-4 秒，然后所有已启动和新启动的 Qt 应用程序将动态应用新字体。

*** 
 
**问：某些应用程序缺少标题栏和边框。我想修复这个问题。**

**答：** 使用标准 FVWM 样式覆盖，99% 的情况下可以覆盖并强制应用程序按用户意愿运行。然而，有一些 GNOME 人员提出了所谓的 "客户端侧装饰"，这些应用程序向 FVWM 发出提示，表明它们不需要标题栏、句柄和边框，通常表现为未管理状态。它们的内部控件较差，整体视觉外观和功能通常严重受限。\
幸运的是，[这位仁兄，PCMan](https://github.com/PCMan/gtk3-nocsd) 编写了一个小的覆盖库，强制 GTK 库放弃 CSD 并请求正常行为。gtk3-nocsd 包甚至在 Debian 和一些其他发行版上可用以解决此问题。阅读包说明并根据需要应用。
 
*** 
 
**问：我在与 NsCDE 结合使用 compton/compton-ng 时，有时 FvwmScript 应用程序的弹出菜单无法正确刷新。** 

**答：** 编辑你的 ~/.NsCDE/NsCDE.conf 并添加或取消注释

SetEnv NSCDE_REDRAW_WORKAROUND 1

注销并重新登录。
 
*** 
 
**问：ImageMagick 和 SVG（在 Debian 上发现）：应卸载包 libmagickcore-6.q16-6-extra** 

**答：** 在生成 SVG 菜单时，fvwm-menu-desktop 将从 /usr/share/applications/*.desktop 文件中选取图标。对于许多 SVG 文件，它将调用 ImageMagick convert 工具。这可能会阻塞并在 CPU 上永远挂起，或直到被终止。

***

**问：当我从菜单中调用需要 root 权限的程序时，它们根本不启动。**

**答：** 似乎 f_PolkitAgent 函数找不到任何已知的 PolicyKit 认证代理。你应该在 ~/.NsCDE/NsCDE.conf 中设置 `$[infostore.polkit.agent]`。不存在但可能的奇怪 PATH 示例：
```
InfoStoreAdd polkit.agent /usr/local/libexec/mate/polkit-mate-authentication-agent-1
```

***

**问：在某些 CDE 颜色调色板下，VirtualBox 管理 GUI 界面在白色背景上显示白色文本。**

**答：** 这是一个已知问题。不仅限于 NsCDE GTK/QT 主题组件。参见[原始报告](https://www.virtualbox.org/ticket/18258)和问题[#57](https://github.com/NsCDE/NsCDE/issues/57)了解如何解决。

***

## 技巧与窍门

**问：NsCDE 中的窗口几何管理是什么？**

**答：** 这是 NsCDE 独有的功能（据我所知），手动保存某些窗口的大小和位置，以便在页面或工作区上初始呈现，但前提是同一 X 类和资源的窗口尚未存在于该页面上。通过窗口操作菜单，此对话框可通过 "Save Geometry ..." 调用，或在指针和焦点位于某个窗口上时按 Meta+F6 调用。此对话框将允许用户在保存这些属性之前微调类和资源名称、X 和 Y 位置、宽度和高度（这些是从当前默认值中选取的）。如果窗口已有先前保存的属性，它们将呈现给用户。使用 Clear 按钮清除并保存空字段将擦除该特定应用程序或窗口的静态几何参数。几何参数依赖于屏幕分辨率。这意味着如果屏幕分辨率改变，必须为这种新的视觉条件从头开始设置所有窗口参数。回到旧分辨率（例如本地笔记本屏幕与更高分辨率的外部显示器）将再次识别该分辨率的窗口属性。这些属性保存在用户的 ~/.NsCDE/GeoDB.ini 中，可以谨慎地手动编辑。

***

## 杂项

**问：NsCDE 是否有其他语言版本？**

**答：** NsCDE 在某个较晚的发布候选版本期间实现了 FvwmScript 应用程序、菜单和其他组件的本地化。克罗地亚语本地化是第一个。可以轻松制作其他翻译。参见下一个问题。

***

**问：我想贡献本地化。从哪里开始？**

**答：** 可以通过进入 $NSCDE_ROOT/share/locale/ 并将 "hr" 复制到 <其他语言> 来实现。之后，所有 msgstr 行应替换为 msgid 行的英文翻译，并检查在界面上的效果。有关详细信息，请参阅随 NsCDE 提供的 README.localization 文件。

***

**问：什么是沙盒模式？**

**答：** 沙盒模式是 ~/.NsCDE/NsCDE.conf 中的 FVWM InfoStore 变量 "InfoStoreAdd sandboxmode 1"。此变量会改变很多。不提供工作区或页面，几乎没有（或根本没有）FvwmScript 应用程序和功能，没有前面板，减少的工作区菜单和几乎没有 FVWM 模块。\
这种工作模式旨在用于嵌套的 X 服务器，如 Xephyr、VNC 或 Spice 连接到单应用程序的隔离和虚拟化环境，其中通过虚拟化和隔离实现安全性。此模式下的应用程序通常是无边框且只有标题栏。另一方面，主机上的 X 服务器或其他呈现客户端可以只有边框和句柄，而没有标题栏。这样，我们就能在嵌套服务器和虚拟机内部获得无缝完整的 NsCDE 和 FVWM 窗口，其部分装饰位于内部，部分外部装饰位于主机上。

***

**问：我想为我的 Linux 发行版或类 unix 系统制作一个包。如何制作例如 /home/build/tmp 的暂存安装？**

**答：** 通过使用 Installer.ksh 的 "-D" 标志。此标志仅在非交互式安装模式下工作，这对于自动构建系统是合理的。示例：

`./Installer.ksh -D /home/build/root/nscde_package_root -w -n -i`