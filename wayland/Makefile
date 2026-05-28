PREFIX ?= /usr/local
DESTDIR ?=

BINDIR ?= $(PREFIX)/bin
DATADIR ?= $(PREFIX)/share
SESSIONDIR ?= $(DATADIR)/wayland-sessions
PROJECT := nscde-wayland
PROJECTDATADIR := $(DATADIR)/$(PROJECT)
INSTALL ?= install

.PHONY: all install uninstall check

all:

check:
	sh -n bin/nscde-labwc
	sh -n bin/nscde-wayland-run
	sh -n bin/nscde-output-scale
	sh -n bin/nscde-wayland-lock
	sh -n bin/nscde-wayland-screenshot
	sh -n bin/nscde-wayland-doctor
	sh -n bin/nscde-wayland-pipemenu
	sh -n bin/nscde-wayland-theme
	sh -n bin/nscde-wayland-menugen
	python3 -m py_compile bin/nscde-wayland-colorcalc
	python3 -m py_compile bin/nscde-panel
	python3 -m py_compile bin/nscde-wayland-logout
	python3 -m py_compile bin/nscde-control-center
	python3 -m py_compile lib/nscde_cde.py
	python3 -m py_compile lib/cc_sysinfo.py
	python3 -m py_compile lib/cc_defaultapps.py
	python3 -m py_compile lib/cc_backdrop.py
	python3 -m py_compile lib/cc_color.py
	python3 -m py_compile lib/cc_font.py
	python3 -m py_compile lib/cc_window.py
	python3 -m py_compile lib/cc_keyboard.py
	python3 -m py_compile lib/cc_mouse.py
	sh -n labwc/autostart
	command -v fuzzel >/dev/null && fuzzel --check-config --config=fuzzel/fuzzel.ini || true
	command -v foot >/dev/null && foot --check-config --config=foot/foot.ini || true
	test -s sfwbar/sfwbar.config
	xmllint --noout labwc/rc.xml labwc/menu.xml
	sh bin/nscde-wayland-pipemenu | xmllint --noout -

install:
	$(INSTALL) -d "$(DESTDIR)$(BINDIR)"
	$(INSTALL) -m 0755 bin/nscde-labwc "$(DESTDIR)$(BINDIR)/nscde-labwc"
	$(INSTALL) -m 0755 bin/nscde-wayland-run "$(DESTDIR)$(BINDIR)/nscde-wayland-run"
	$(INSTALL) -m 0755 bin/nscde-output-scale "$(DESTDIR)$(BINDIR)/nscde-output-scale"
	$(INSTALL) -m 0755 bin/nscde-wayland-lock "$(DESTDIR)$(BINDIR)/nscde-wayland-lock"
	$(INSTALL) -m 0755 bin/nscde-wayland-screenshot "$(DESTDIR)$(BINDIR)/nscde-wayland-screenshot"
	$(INSTALL) -m 0755 bin/nscde-wayland-doctor "$(DESTDIR)$(BINDIR)/nscde-wayland-doctor"
	$(INSTALL) -m 0755 bin/nscde-wayland-pipemenu "$(DESTDIR)$(BINDIR)/nscde-wayland-pipemenu"
	$(INSTALL) -m 0755 bin/nscde-wayland-theme "$(DESTDIR)$(BINDIR)/nscde-wayland-theme"
	$(INSTALL) -m 0755 bin/nscde-wayland-menugen "$(DESTDIR)$(BINDIR)/nscde-wayland-menugen"
	$(INSTALL) -m 0755 bin/nscde-wayland-colorcalc "$(DESTDIR)$(BINDIR)/nscde-wayland-colorcalc"
	$(INSTALL) -m 0755 bin/nscde-panel "$(DESTDIR)$(BINDIR)/nscde-panel"
	$(INSTALL) -m 0755 bin/nscde-control-center "$(DESTDIR)$(BINDIR)/nscde-control-center"
	$(INSTALL) -m 0755 bin/nscde-wayland-logout "$(DESTDIR)$(BINDIR)/nscde-wayland-logout"
	$(INSTALL) -d "$(DESTDIR)$(PROJECTDATADIR)/lib"
	$(INSTALL) -m 0644 lib/nscde_cde.py "$(DESTDIR)$(PROJECTDATADIR)/lib/nscde_cde.py"
	$(INSTALL) -m 0644 lib/cc_sysinfo.py "$(DESTDIR)$(PROJECTDATADIR)/lib/cc_sysinfo.py"
	$(INSTALL) -m 0644 lib/cc_defaultapps.py "$(DESTDIR)$(PROJECTDATADIR)/lib/cc_defaultapps.py"
	$(INSTALL) -m 0644 lib/cc_backdrop.py "$(DESTDIR)$(PROJECTDATADIR)/lib/cc_backdrop.py"
	$(INSTALL) -m 0644 lib/cc_color.py "$(DESTDIR)$(PROJECTDATADIR)/lib/cc_color.py"
	$(INSTALL) -m 0644 lib/cc_font.py "$(DESTDIR)$(PROJECTDATADIR)/lib/cc_font.py"
	$(INSTALL) -m 0644 lib/cc_window.py "$(DESTDIR)$(PROJECTDATADIR)/lib/cc_window.py"
	$(INSTALL) -m 0644 lib/cc_keyboard.py "$(DESTDIR)$(PROJECTDATADIR)/lib/cc_keyboard.py"
	$(INSTALL) -m 0644 lib/cc_mouse.py "$(DESTDIR)$(PROJECTDATADIR)/lib/cc_mouse.py"
	$(INSTALL) -d "$(DESTDIR)$(SESSIONDIR)"
	$(INSTALL) -m 0644 session/nscde-labwc.desktop "$(DESTDIR)$(SESSIONDIR)/nscde-labwc.desktop"
	$(INSTALL) -d "$(DESTDIR)$(PROJECTDATADIR)"
	cp -R labwc themes assets sfwbar fuzzel foot fnott lavalauncher "$(DESTDIR)$(PROJECTDATADIR)/"
	$(INSTALL) -d "$(DESTDIR)$(DATADIR)/themes" "$(DESTDIR)$(DATADIR)/icons"
	cp -R themes/NsCDE-Wayland "$(DESTDIR)$(DATADIR)/themes/"
	cp -R assets/xdg/icons/NsCDE "$(DESTDIR)$(DATADIR)/icons/"

uninstall:
	rm -f "$(DESTDIR)$(BINDIR)/nscde-labwc"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-wayland-run"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-output-scale"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-wayland-lock"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-wayland-screenshot"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-wayland-doctor"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-wayland-pipemenu"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-wayland-theme"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-wayland-menugen"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-wayland-colorcalc"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-panel"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-control-center"
	rm -f "$(DESTDIR)$(BINDIR)/nscde-wayland-logout"
	rm -rf "$(DESTDIR)$(PROJECTDATADIR)/lib"
	rm -f "$(DESTDIR)$(SESSIONDIR)/nscde-labwc.desktop"
	rm -rf "$(DESTDIR)$(PROJECTDATADIR)"
	rm -rf "$(DESTDIR)$(DATADIR)/themes/NsCDE-Wayland"
	rm -rf "$(DESTDIR)$(DATADIR)/icons/NsCDE"
