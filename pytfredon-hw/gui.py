#!/usr/bin/env python3
"""Wayland-friendly PySide6 GUI for pytfredon-hw."""
from __future__ import annotations

import sys
from typing import Optional

import psutil

from PySide6.QtCore import (
    QCoreApplication,
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QSize,
    QTimer,
    Qt,
)
from PySide6.QtGui import QGuiApplication, QCursor, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QSizePolicy,
    QVBoxLayout,
)

# --- Design System ---

# 1. Color Palette (Dark Theme) - WCAG AA compliant
#    - Backgrounds: Subtle variations for depth.
#    - Text: Clear hierarchy from primary to disabled.
#    - Action: Primary color for interactive elements.
#    - Semantic: Colors for states like danger.
COLORS = {
    "bg_primary": "#0b1220",  # Main window background
    "bg_secondary": "#1c2536",  # Card background
    "bg_tertiary": "#29344b",  # Details panel background
    "border_primary": "#3a4766",  # Card borders
    "border_hover": "#5b6a8e",  # Card border on hover
    "text_primary": "#e6eef8",  # Main text, titles
    "text_secondary": "#a9b8d4",  # Lighter text, values
    "text_tertiary": "#7f8da9",  # Footer, disabled text
    "action_primary": "#66a3ff",  # Sparklines, interactive elements
    "action_danger": "#ff6b6b",  # Close button
    "shadow": "#000000",
}

# 2. Typography (1.25 ratio, 15px base)
#    - Consistent weights and line heights for readability.
#    - Letter spacing adjusted for visual balance.
TYPOGRAPHY = {
    "h1": "font-weight: 600; font-size: 18px;",
    "h2": "font-weight: 600; font-size: 15px;",
    "body": "font-weight: 400; font-size: 15px; line-height: 1.5;",
    "small": "font-weight: 400; font-size: 12px;",
    "value": "font-weight: 300; font-size: 24px; letter-spacing: -0.02em;",
}

# 3. Spacing & Layout (4px grid)
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
}

# 4. Border Radius
RADIUS = {"sm": 4, "md": 8, "lg": 12}

# --- Config ---
UPDATE_INTERVAL_MS = 2000
HISTORY_MAX = 30
HISTORY: dict[str, list[float]] = {"cpu": [], "ram": [], "gpu": [], "disk": []}


# --------- Metrics helpers ---------
def get_cpu_info() -> dict[str, Optional[float]]:
    usage = psutil.cpu_percent(interval=0.05)
    temp: Optional[float] = None
    try:
        temps = psutil.sensors_temperatures()
        for k, v in temps.items():
            if k.lower() in ("coretemp", "k10temp", "cpu_thermal", "acpi") and v:
                temp = round(v[0].current, 1)
                break
    except Exception:
        pass
    return {"usage": usage, "temp": temp}


def get_ram_info() -> dict[str, float]:
    vm = psutil.virtual_memory()
    return {
        "used_gb": round(vm.used / (1024**3), 2),
        "total_gb": round(vm.total / (1024**3), 2),
        "percent": float(vm.percent),
    }


def get_gpu_info() -> list[dict[str, float | str | None]]:
    gpus: list[dict[str, float | str | None]] = []
    try:
        import pynvml as nvml  # type: ignore

        nvml.nvmlInit()
        count = nvml.nvmlDeviceGetCount()
        for i in range(count):
            h = nvml.nvmlDeviceGetHandleByIndex(i)
            name = nvml.nvmlDeviceGetName(h)
            if isinstance(name, bytes):
                name = name.decode()
            util = float(nvml.nvmlDeviceGetUtilizationRates(h).gpu)
            mem = nvml.nvmlDeviceGetMemoryInfo(h)
            temp: Optional[float] = None
            try:
                temp = float(
                    nvml.nvmlDeviceGetTemperature(h, nvml.NVML_TEMPERATURE_GPU)
                )
            except Exception:
                pass
            gpus.append(
                {
                    "name": str(name),
                    "util": util,
                    "mem_used_gb": round(int(mem.used) / float(1024**3), 2),
                    "mem_total_gb": round(int(mem.total) / float(1024**3), 2),
                    "temp": temp,
                }
            )
        nvml.nvmlShutdown()
        return gpus
    except Exception:
        pass
    try:
        import pyamdgpuinfo as amdgpu  # type: ignore

        cnt = getattr(amdgpu, "detect_gpus", lambda: 0)()
        for i in range(int(cnt)):
            name = getattr(amdgpu, "get_gpu_name", lambda _i: "AMD GPU")(i)
            util = float(getattr(amdgpu, "get_gpu_load", lambda _i: 0)(i))
            temp = getattr(amdgpu, "get_temp", lambda _i: None)(i)
            temp = float(temp) if temp is not None else None
            gpus.append({"name": str(name), "util": util, "temp": temp})
    except Exception:
        pass
    return gpus


def get_disk_info() -> list[dict[str, float | str]]:
    out: list[dict[str, float | str]] = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            out.append(
                {
                    "device": part.device,
                    "mount": part.mountpoint,
                    "percent": round((usage.used / usage.total) * 100, 1),
                }
            )
        except Exception:
            continue
    return out


# --------- UI Widgets ---------
class Card(QFrame):
    """Clickable metric card with perfected styling."""

    def __init__(self, key: str, title: str):
        super().__init__()
        self.key = key
        self.setObjectName(f"card_{key}")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(f"{title} Metrics Card")
        self.setToolTip("")
        self.setStyleSheet(
            f"""
            QFrame[objectName^="card_"] {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_primary']};
                border-radius: {RADIUS['lg']}px;
                transition: border-color 0.2s cubic-bezier(.4,0,.2,1), box-shadow 0.2s cubic-bezier(.4,0,.2,1), background-color 0.2s cubic-bezier(.4,0,.2,1);
            }}
            QFrame[objectName^="card_"]:hover, QFrame[objectName^="card_"]:focus {{
                border-color: {COLORS['border_hover']};
                box-shadow: 0 2px 12px 0 rgba(102,163,255,0.10);
                outline: 2px solid {COLORS['action_primary']};
                outline-offset: 0px;
            }}
            QFrame[objectName^="card_"][pressed="true"] {{
                background-color: {COLORS['bg_tertiary']};
            }}
            """
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"]
        )
        lay.setSpacing(SPACING["sm"])

        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet(
            f"{TYPOGRAPHY['h2']} color: {COLORS['text_primary']};"
        )
        self.value_lbl = QLabel("…")
        self.value_lbl.setStyleSheet(
            f"{TYPOGRAPHY['value']} color: {COLORS['text_secondary']};"
        )
        self.spark_lbl = QLabel()
        self.spark_lbl.setMinimumHeight(32)
        self.spark_lbl.setScaledContents(True)

        lay.addWidget(self.title_lbl)
        lay.addWidget(self.value_lbl)
        lay.addStretch()
        lay.addWidget(self.spark_lbl)

        # Skeleton loading animation
        self.skel_anim = QPropertyAnimation(self.value_lbl, b"windowOpacity")
        self.skel_anim.setDuration(900)
        self.skel_anim.setStartValue(0.4)
        self.skel_anim.setEndValue(1.0)
        self.skel_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.skel_anim.setLoopCount(-1)
        self.skel_anim.start()

        # Tooltip timer
        self._tooltip_timer = QTimer(self)
        self._tooltip_timer.setSingleShot(True)
        self._tooltip_timer.setInterval(300)
        self._tooltip_timer.timeout.connect(self._show_tooltip)
        self._pending_tooltip = False

    def enterEvent(self, event):
        self._pending_tooltip = True
        self._tooltip_timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._pending_tooltip = False
        self._tooltip_timer.stop()
        self.setToolTip("")
        super().leaveEvent(event)

    def _show_tooltip(self):
        if self._pending_tooltip and self.toolTip():
            QFrame.setToolTip(self, self.toolTip())

    def focusInEvent(self, event):
        self.setProperty("focus", True)
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setProperty("focus", False)
        self.update()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            try:
                w = self.window()
                if w and hasattr(w, "card_clicked"):
                    getattr(w, "card_clicked")(self.key)
            except Exception:
                pass
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        self.setProperty("pressed", True)
        self.update()
        try:
            w = self.window()
            if w and hasattr(w, "card_clicked"):
                getattr(w, "card_clicked")(self.key)
        except Exception:
            pass
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setProperty("pressed", False)
        self.update()
        super().mouseReleaseEvent(event)


class HwPopup(QFrame):
    """Main application window with perfected design."""

    def __init__(self):
        super().__init__()
        self.setObjectName("hwpopup")
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"""
            #hwpopup {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_primary']};
                border-radius: {RADIUS['lg']}px;
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                {TYPOGRAPHY['body']}
            }}
            """
        )
        self.setMinimumSize(QSize(560, 380))

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(SPACING["xl"])
        shadow.setOffset(0, SPACING["sm"])
        shadow.setColor(QColor(COLORS["shadow"]).__class__(0, 0, 0, 180))
        self.setGraphicsEffect(shadow)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(
            SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"]
        )
        self.root_layout.setSpacing(SPACING["md"])

        # --- Header ---
        header = QHBoxLayout()
        title = QLabel("System Hardware Monitor")
        title.setStyleSheet(f"{TYPOGRAPHY['h1']} color: {COLORS['text_primary']};")
        header.addWidget(title)
        header.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['action_danger']};
                font-size: 16px;
                border-radius: {RADIUS['md']}px;
            }}
            QPushButton:hover {{ background-color: {COLORS['bg_secondary']}; }}
            QPushButton:pressed {{ background-color: {COLORS['border_primary']}; }}
            """
        )
        close_btn.clicked.connect(QCoreApplication.quit)
        header.addWidget(close_btn)
        self.root_layout.addLayout(header)

        # --- Cards Grid ---
        self.grid = QGridLayout()
        self.grid.setSpacing(SPACING["md"])
        self.card_cpu = Card("cpu", "CPU")
        self.card_ram = Card("ram", "RAM")
        self.card_gpu = Card("gpu", "GPU")
        self.card_disk = Card("disk", "Disk")
        self.grid.addWidget(self.card_cpu, 0, 0)
        self.grid.addWidget(self.card_ram, 0, 1)
        self.grid.addWidget(self.card_gpu, 1, 0)
        self.grid.addWidget(self.card_disk, 1, 1)
        self.root_layout.addLayout(self.grid)

        # --- Details Panel ---
        self.details = QFrame()
        self.details.setObjectName("details")
        self.details.setStyleSheet(
            f"""
            #details {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border_primary']};
                border-radius: {RADIUS['md']}px;
            }}
            """
        )
        self.details_lay = QVBoxLayout(self.details)
        self.details_lay.setContentsMargins(
            SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"]
        )
        self.details_lay.setSpacing(SPACING["sm"])
        self.details_title = QLabel("Details")
        self.details_title.setStyleSheet(
            f"{TYPOGRAPHY['h2']} color: {COLORS['text_primary']};"
        )
        self.details_body = QLabel("")
        self.details_body.setWordWrap(True)
        self.details_body.setStyleSheet(
            f"{TYPOGRAPHY['body']} color: {COLORS['text_secondary']}; line-height: 1.4;"
        )
        self.details_lay.addWidget(self.details_title)
        self.details_lay.addWidget(self.details_body)
        self.details_effect = QGraphicsOpacityEffect(self.details)
        self.details.setGraphicsEffect(self.details_effect)
        self.details.setMaximumHeight(0)
        self.root_layout.addWidget(self.details)

        # --- Footer ---
        footer = QLabel("Wayland-friendly, floating popup")
        footer.setStyleSheet(
            f"{TYPOGRAPHY['small']} color: {COLORS['text_tertiary']}; margin-top: {SPACING['xs']}px;"
        )
        self.root_layout.addWidget(footer, 0, Qt.AlignmentFlag.AlignRight)

        # --- Animations ---
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(240)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.details_anim_h = QPropertyAnimation(self.details, b"maximumHeight")
        self.details_anim_h.setDuration(220)
        self.details_anim_h.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.details_anim_o = QPropertyAnimation(self.details_effect, b"opacity")
        self.details_anim_o.setDuration(200)
        self.details_anim_o.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def card_clicked(self, key: str):
        text = self._build_details_text(key)
        self.details_title.setText(key.upper() + " Details")
        self.details_body.setText(text)
        target_h = (
            self.details_body.sizeHint().height()
            + self.details_title.sizeHint().height()
            + SPACING["md"] * 2
        )
        if not text:
            target_h = 0
        self._animate_details_to(target_h)

    def _animate_details_to(self, h: int):
        self.details_anim_h.stop()
        self.details_anim_o.stop()
        self.details_anim_h.setStartValue(self.details.maximumHeight())
        self.details_anim_h.setEndValue(h)
        self.details_anim_o.setStartValue(0.0 if h > 0 else 1.0)
        self.details_anim_o.setEndValue(1.0 if h > 0 else 0.0)
        self.details_anim_h.start()
        self.details_anim_o.start()

    def show_with_fade(self, screen):
        pg = screen.availableGeometry()
        x = pg.x() + (pg.width() - self.width()) // 2
        y = pg.y() + (pg.height() - self.height()) // 2
        self.move(x, y)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

    def draw_sparkline(self, values: list[float], width: int = 120, height: int = 32):
        pix = QPixmap(width * 2, height * 2)  # HiDPI
        pix.setDevicePixelRatio(2)
        pix.fill(Qt.GlobalColor.transparent)
        if not values:
            return pix
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(COLORS["action_primary"]))
        pen.setWidth(2)
        p.setPen(pen)
        mx, mn = max(values), min(values)
        rng = mx - mn or 1
        step = (width * 2) / max(len(values) - 1, 1)
        last_xy: Optional[tuple[int, int]] = None
        for i, v in enumerate(values):
            x = int(i * step)
            y = int((height * 2) - ((v - mn) / rng) * (height * 2 - 4) - 2)
            if last_xy is not None:
                p.drawLine(last_xy[0], last_xy[1], x, y)
            last_xy = (x, y)
        p.end()
        return pix

    def _build_details_text(self, key: str) -> str:
        try:
            if key == "cpu":
                cpu = get_cpu_info()
                return (
                    f"Usage: {cpu['usage']:.1f}%\nTemp: {cpu['temp']}°C"
                    if cpu["temp"] is not None
                    else f"Usage: {cpu['usage']:.1f}%"
                )
            if key == "ram":
                ram = get_ram_info()
                return f"Used: {ram['used_gb']} GiB\nTotal: {ram['total_gb']} GiB\nPercent: {ram['percent']:.1f}%"
            if key == "gpu":
                gpus = get_gpu_info()
                if not gpus:
                    return "No GPU info available"
                lines = []
                for g in gpus:
                    nm = g.get("name", "GPU")
                    util = g.get("util") or g.get("mem_percent") or 0
                    temp = g.get("temp")
                    mem_used = g.get("mem_used_gb")
                    mem_total = g.get("mem_total_gb")
                    extra = (
                        f" | Mem: {mem_used}/{mem_total} GiB"
                        if mem_used is not None and mem_total is not None
                        else ""
                    )
                    lines.append(
                        f"{nm}: {float(util):.0f}%"
                        + (f" ({temp}°C)" if temp is not None else "")
                        + extra
                    )
                return "\n".join(lines)
            if key == "disk":
                parts = get_disk_info()
                if not parts:
                    return "No disk info"
                return "\n".join(
                    f"{p['device']} on {p['mount']}: {p['percent']}%" for p in parts
                )
        except Exception:
            return ""
        return ""

    def focusOutEvent(self, _):
        QCoreApplication.quit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QCoreApplication.quit()


# --------- App wrapper ---------
class HwApp:
    def __init__(self):
        try:
            QGuiApplication.setAttribute(
                Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True
            )
        except Exception:
            pass
        self.app = QApplication([])
        self.app.setApplicationName("pytfredon-hw-gui")
        try:
            self.app.setStyle("Fusion")
        except Exception:
            pass
        self.popup = HwPopup()
        scr = QGuiApplication.screenAt(QCursor.pos()) or self.app.primaryScreen()
        self.popup.show_with_fade(scr)
        self.timer = QTimer()
        self.timer.setInterval(UPDATE_INTERVAL_MS)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start()
        self.update_stats()  # Initial call

    def update_stats(self):
        try:
            cpu = get_cpu_info()
            ram = get_ram_info()
            gpus = get_gpu_info()
            disks = get_disk_info()

            self.popup.card_cpu.value_lbl.setText(f"{cpu['usage']:.0f}%")
            self.popup.card_ram.value_lbl.setText(f"{ram['percent']:.0f}%")
            gpu_util = 0.0
            if gpus:
                try:
                    gpu_util = float(gpus[0].get("util") or 0)
                except (ValueError, TypeError):
                    pass  # Keep gpu_util as 0.0
            self.popup.card_gpu.value_lbl.setText(f"{gpu_util:.0f}%")
            disk_pct = float(disks[0]["percent"]) if disks else 0.0
            self.popup.card_disk.value_lbl.setText(f"{disk_pct:.0f}%")

            HISTORY["cpu"].append(float(cpu.get("usage") or 0.0))
            HISTORY["ram"].append(float(ram.get("percent", 0)))
            HISTORY["gpu"].append(gpu_util)
            HISTORY["disk"].append(disk_pct)

            for key in HISTORY:
                HISTORY[key] = HISTORY[key][-HISTORY_MAX:]
                card = getattr(self.popup, f"card_{key}")
                pix = self.popup.draw_sparkline(HISTORY[key])
                if pix:
                    card.spark_lbl.setPixmap(pix)
        except Exception:
            pass

    def run(self):
        try:
            sys.exit(self.app.exec())
        except KeyboardInterrupt:
            sys.exit(0)


def main():
    HwApp().run()


if __name__ == "__main__":
    main()
