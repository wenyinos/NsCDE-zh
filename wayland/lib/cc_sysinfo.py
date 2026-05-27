"""
cc_sysinfo.py - System Information page for NsCDE Control Center.

Read-only display of system information in CDE style.
"""

import os
import platform
import subprocess

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt


def _run_cmd(cmd, fallback=""):
    """Run a command and return first line of stdout."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return r.stdout.strip().split('\n')[0]
    except Exception:
        pass
    return fallback


def _read_file(path, fallback=""):
    """Read first line of a file."""
    try:
        with open(path) as f:
            return f.readline().strip()
    except Exception:
        return fallback


class SysinfoPage(QWidget):
    """System information display page."""

    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        # Title
        title = QLabel("System Information")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {self.colors['bs']}")
        layout.addWidget(sep)

        # Info grid
        grid = QGridLayout()
        grid.setSpacing(6)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        info = self._gather_info()
        for row, (label, value) in enumerate(info):
            lbl = QLabel(label)
            lbl.setStyleSheet(f"font: bold 12px; color: {self.colors['fg']}")
            val = QLabel(value)
            val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            val.setWordWrap(True)
            grid.addWidget(lbl, row, 0, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(val, row, 1)

        layout.addLayout(grid)
        layout.addStretch()

    def _gather_info(self):
        """Collect system information fields."""
        uname = platform.uname()
        info = []

        # User
        info.append(("User Name:", _run_cmd(["id", "-un"], os.environ.get("USER", ""))))

        # Hostname
        info.append(("Workstation Name:", uname.node))

        # Architecture
        info.append(("Type:", f"{uname.machine} {uname.processor}"))

        # IP address
        ip = _run_cmd(["hostname", "-I"])
        if not ip:
            ip = _run_cmd(["ip", "-4", "addr", "show"], "")
            # Try to extract from ip addr output
            import re
            m = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', ip)
            if m:
                ip = m.group(1)
        info.append(("Internet (IP) Address:", ip or "N/A"))

        # Host ID
        hostid = _run_cmd(["hostid"])
        if not hostid:
            hostid = _run_cmd(["/sbin/sysctl", "-n", "kern.hostid"])
        info.append(("Host ID:", hostid or "N/A"))

        # Domain
        domain = _run_cmd(["domainname"])
        info.append(("Network Domain:", domain if domain and domain != "(none)" else "N/A"))

        # Memory
        mem_total = _read_file("/proc/meminfo")
        if mem_total.startswith("MemTotal:"):
            parts = mem_total.split()
            if len(parts) >= 2:
                kb = int(parts[1])
                gb = kb / 1048576
                mem_str = f"{gb:.1f} GB ({kb:,} kB)"
            else:
                mem_str = mem_total
        else:
            mem_str = _run_cmd(["free", "-h"], "N/A")
        info.append(("Physical Memory RAM:", mem_str))

        # Swap
        swap_line = ""
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("SwapTotal:"):
                        parts = line.split()
                        if len(parts) >= 2:
                            kb = int(parts[1])
                            gb = kb / 1048576
                            swap_line = f"{gb:.1f} GB ({kb:,} kB)"
                        break
        except Exception:
            pass
        info.append(("Virtual Memory Swap:", swap_line or "N/A"))

        # OS
        info.append(("Operating System:",
                      f"{uname.system} {uname.release}"))
        info.append(("OS Version:", uname.version))

        # Window Manager
        info.append(("Window Manager:", "labwc"))

        # NsCDE Version
        version = "NsCDE-Wayland"
        for vpath in [
            "/usr/share/nscde-wayland/VERSION",
            os.path.expanduser("~/.config/nscde-wayland/VERSION"),
        ]:
            v = _read_file(vpath)
            if v:
                version = v
                break
        info.append(("NsCDE-Wayland Version:", version))

        # Last boot
        boot_time = "N/A"
        uptime = _read_file("/proc/uptime")
        if uptime:
            try:
                secs = float(uptime.split()[0])
                import datetime
                boot = datetime.datetime.now() - datetime.timedelta(seconds=secs)
                boot_time = boot.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
        info.append(("System Last Booted:", boot_time))

        # Uptime
        uptime_str = _run_cmd(["uptime", "-p"])
        if not uptime_str:
            uptime_str = _run_cmd(["uptime"])
        info.append(("Uptime:", uptime_str or "N/A"))

        # CPU
        cpu_model = "N/A"
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("model name"):
                        cpu_model = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass
        info.append(("CPU:", cpu_model))

        # Kernel
        info.append(("Kernel:", f"{uname.system} {uname.release}"))

        return info
