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
    QRect,
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
    QWidget,
    QToolTip,
)

# --- Design System ---

# DESIGN TOKENS - Comprehensive design system based on Carbon Design System principles
# Following WCAG 2.2 AA compliance standards (4.5:1 contrast minimum)

# 1. TYPOGRAPHY SCALE
# Perfect 1.25 ratio scale: 12, 15, 18, 24, 30, 37, 46px
# Consistent font weights: 300/light, 400/regular, 600/semibold, 700/bold
# Optimized line heights: 1.2 for headings, 1.5 for body, 1.4 for UI
# Letter spacing: -0.02em for large text, 0 for body, +0.05em for small caps
TYPOGRAPHY = {
    # Display & Large Headings
    "display-01": "font-weight: 300; font-size: 46px; line-height: 1.2; letter-spacing: -0.02em;",
    "display-02": "font-weight: 300; font-size: 37px; line-height: 1.2; letter-spacing: -0.02em;",
    # Headings - Clear hierarchy
    "heading-01": "font-weight: 600; font-size: 30px; line-height: 1.2; letter-spacing: -0.01em;",
    "heading-02": "font-weight: 600; font-size: 24px; line-height: 1.2; letter-spacing: -0.01em;",
    "heading-03": "font-weight: 600; font-size: 18px; line-height: 1.2;",
    "heading-04": "font-weight: 600; font-size: 15px; line-height: 1.2;",
    # Body Text - Optimized for readability
    "body-01": "font-weight: 400; font-size: 15px; line-height: 1.5;",
    "body-02": "font-weight: 400; font-size: 12px; line-height: 1.5;",
    "body-compact-01": "font-weight: 400; font-size: 15px; line-height: 1.4;",
    "body-compact-02": "font-weight: 400; font-size: 12px; line-height: 1.4;",
    # UI Elements
    "label-01": "font-weight: 400; font-size: 12px; line-height: 1.4; letter-spacing: 0.05em; text-transform: uppercase;",
    "label-02": "font-weight: 400; font-size: 15px; line-height: 1.4;",
    "helper-text": "font-weight: 400; font-size: 12px; line-height: 1.4; font-style: italic;",
    # Code & Monospace
    "code-01": "font-family: 'SF Mono', 'Monaco', 'Consolas', monospace; font-weight: 400; font-size: 12px; line-height: 1.4;",
    "code-02": "font-family: 'SF Mono', 'Monaco', 'Consolas', monospace; font-weight: 400; font-size: 15px; line-height: 1.4;",
    # Legacy compatibility (for smooth migration)
    "h1": "font-weight: 600; font-size: 24px; line-height: 1.2;",
    "h2": "font-weight: 600; font-size: 18px; line-height: 1.2;",
    "body": "font-weight: 400; font-size: 15px; line-height: 1.5;",
    "small": "font-weight: 400; font-size: 12px; line-height: 1.4;",
    "value": "font-weight: 300; font-size: 30px; line-height: 1.2; letter-spacing: -0.02em;",
}


# --- Premium UX Utility Classes ---


class ShadowManager:
    """Qt-native shadow effects manager - replaces CSS box-shadow."""

    @staticmethod
    def create_shadow(
        level: str = "01", color: Optional[QColor] = None
    ) -> QGraphicsDropShadowEffect:
        """Create a drop shadow effect based on design system levels."""
        shadow = QGraphicsDropShadowEffect()

        # Shadow configurations based on design system
        shadow_configs = {
            "none": {"blur": 0, "offset": (0, 0)},
            "01": {"blur": 3, "offset": (0, 1)},
            "02": {"blur": 6, "offset": (0, 4)},
            "03": {"blur": 15, "offset": (0, 10)},
            "04": {"blur": 25, "offset": (0, 20)},
            "05": {"blur": 50, "offset": (0, 25)},
            "hover": {"blur": 12, "offset": (0, 4)},
            "focus": {"blur": 0, "offset": (0, 0)},  # Focus uses border, not shadow
            "active": {"blur": 2, "offset": (0, 1)},
        }

        config = shadow_configs.get(level, shadow_configs["01"])
        shadow.setBlurRadius(config["blur"])
        shadow.setOffset(*config["offset"])

        # Set shadow color
        if color:
            shadow.setColor(color)
        else:
            # Default shadow color from design system
            shadow.setColor(QColor(0, 0, 0, 25))  # rgba(0,0,0,0.1)

        return shadow

    @staticmethod
    def apply_shadow(
        widget: QWidget, level: str = "01", color: Optional[QColor] = None
    ):
        """Apply shadow effect to a widget."""
        if level == "none":
            # Remove existing graphics effect
            current_effect = widget.graphicsEffect()
            if current_effect:
                current_effect.setParent(None)
            widget.setGraphicsEffect(None)  # type: ignore
        else:
            shadow = ShadowManager.create_shadow(level, color)
            widget.setGraphicsEffect(shadow)

    @staticmethod
    def create_hover_shadow() -> QGraphicsDropShadowEffect:
        """Create special hover shadow with blue tint."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(102, 163, 255, 38))  # Blue hover shadow
        return shadow

    @staticmethod
    def create_focus_shadow() -> QGraphicsDropShadowEffect:
        """Create focus shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(4)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(102, 163, 255, 128))  # Blue focus shadow
        return shadow


class AnimationManager:
    """Qt-native property animation manager - replaces CSS transitions."""

    # Animation durations (in milliseconds)
    DURATIONS = {
        "fast": 150,
        "moderate": 300,
        "slow": 500,
        "extra-slow": 700,
    }

    # Easing curves for different animation types
    EASING = {
        "standard": QEasingCurve.Type.OutCubic,
        "decelerate": QEasingCurve.Type.OutQuart,
        "accelerate": QEasingCurve.Type.InQuart,
        "bounce": QEasingCurve.Type.OutBounce,
        "elastic": QEasingCurve.Type.OutElastic,
    }

    @staticmethod
    def create_animation(
        widget: QWidget,
        property_name: str,
        duration: str = "moderate",
        easing: str = "standard",
    ) -> QPropertyAnimation:
        """Create a property animation with design system timing."""
        animation = QPropertyAnimation(widget, property_name.encode())
        animation.setDuration(AnimationManager.DURATIONS[duration])
        animation.setEasingCurve(AnimationManager.EASING[easing])
        return animation

    @staticmethod
    def animate_hover_scale(widget: QWidget, scale_factor: float = 1.02):
        """Animate widget scale on hover."""
        animation = AnimationManager.create_animation(widget, "geometry", "fast")
        current_geometry = widget.geometry()

        # Calculate scaled geometry
        center_x = current_geometry.x() + current_geometry.width() / 2
        center_y = current_geometry.y() + current_geometry.height() / 2
        new_width = int(current_geometry.width() * scale_factor)
        new_height = int(current_geometry.height() * scale_factor)
        new_x = int(center_x - new_width / 2)
        new_y = int(center_y - new_height / 2)

        from PySide6.QtCore import QRect

        scaled_geometry = QRect(new_x, new_y, new_width, new_height)

        animation.setStartValue(current_geometry)
        animation.setEndValue(scaled_geometry)
        animation.start()
        return animation

    @staticmethod
    def animate_opacity(
        widget: QWidget, target_opacity: float, duration: str = "moderate"
    ):
        """Animate widget opacity."""
        # Check if widget already has an opacity effect
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(AnimationManager.DURATIONS[duration])
        animation.setEasingCurve(AnimationManager.EASING["standard"])
        animation.setEndValue(target_opacity)
        animation.start()
        return animation


class InteractionManager:
    """Manages micro-interactions and hover/focus effects."""

    def __init__(self, widget: QWidget):
        self.widget = widget
        self.hover_animation = None
        self.scale_animation = None
        self.original_shadow = None
        self.hover_shadow = None

        # Store original geometry for scale animations
        self.original_geometry = None

    def setup_hover_effects(
        self, enable_scale: bool = True, enable_shadow: bool = True
    ):
        """Setup hover effects for the widget."""
        self.enable_shadow = enable_shadow
        self.enable_scale = enable_scale

        # Apply initial shadow
        if enable_shadow:
            ShadowManager.apply_shadow(self.widget, "01")

        # Install event filter or override events in widget
        self.widget.enterEvent = self._on_enter
        self.widget.leaveEvent = self._on_leave

    def _on_enter(self, event):
        """Handle mouse enter event."""
        # Apply hover shadow - create new effect each time
        if self.enable_shadow:
            hover_shadow = ShadowManager.create_hover_shadow()
            self.widget.setGraphicsEffect(hover_shadow)

        # Animate scale
        if self.enable_scale:
            if self.original_geometry is None:
                self.original_geometry = self.widget.geometry()
            self.scale_animation = AnimationManager.animate_hover_scale(
                self.widget, 1.02
            )

    def _on_leave(self, event):
        """Handle mouse leave event."""
        # Restore original shadow - create new effect each time
        if self.enable_shadow:
            original_shadow = ShadowManager.create_shadow("01")
            self.widget.setGraphicsEffect(original_shadow)

        # Animate back to original scale
        if self.enable_scale and self.original_geometry and self.scale_animation:
            animation = AnimationManager.create_animation(
                self.widget, "geometry", "fast"
            )
            animation.setStartValue(self.widget.geometry())
            animation.setEndValue(self.original_geometry)
            animation.start()
            self.scale_animation = animation


# 2. COLOR SYSTEM
# WCAG AA compliant (4.5:1+ contrast) with cohesive palette
# Semantic colors for clear meaning and purpose
# Dark theme optimized with proper color inversions
COLORS = {
    # --- Background Colors ---
    "background": "#0b1220",  # Primary background - deepest layer
    "background-hover": "#0f1626",  # Hover state for background
    "background-active": "#13192c",  # Active/pressed state
    "background-selected": "#1a2332",  # Selected state
    "background-brand": "#2563eb",  # Brand background
    # --- Layer Colors (Cards, Surfaces) ---
    "layer-01": "#1c2536",  # Primary layer/card background
    "layer-02": "#29344b",  # Secondary layer (elevated)
    "layer-03": "#364461",  # Tertiary layer (highest elevation)
    "layer-accent": "#2d3748",  # Accent layer
    "layer-hover": "#334155",  # Layer hover state
    "layer-active": "#475569",  # Layer active state
    "layer-selected": "#3b4556",  # Layer selected state
    # --- Border Colors ---
    "border-subtle": "#3a4766",  # Subtle borders, dividers
    "border-strong": "#5b6a8e",  # Strong borders, focus rings
    "border-inverse": "#e2e8f0",  # Inverse borders (light on dark)
    "border-interactive": "#66a3ff",  # Interactive element borders
    "border-danger": "#ef4444",  # Error/danger borders
    "border-warning": "#f59e0b",  # Warning borders
    "border-success": "#10b981",  # Success borders
    # --- Text Colors (WCAG AA Compliant) ---
    "text-primary": "#f8fafc",  # Primary text - 16.0:1 contrast
    "text-secondary": "#cbd5e1",  # Secondary text - 8.2:1 contrast
    "text-tertiary": "#94a3b8",  # Tertiary text - 4.7:1 contrast
    "text-placeholder": "#64748b",  # Placeholder text - 3.2:1 contrast
    "text-helper": "#94a3b8",  # Helper text - 4.7:1 contrast
    "text-error": "#fca5a5",  # Error text - 5.1:1 contrast
    "text-warning": "#fbbf24",  # Warning text - 6.8:1 contrast
    "text-success": "#6ee7b7",  # Success text - 5.4:1 contrast
    "text-inverse": "#1e293b",  # Inverse text (dark on light)
    "text-on-color": "#ffffff",  # Text on colored backgrounds
    "text-disabled": "#475569",  # Disabled text - 2.1:1 contrast
    # --- Interactive Colors ---
    "interactive-01": "#3b82f6",  # Primary interactive (buttons, links)
    "interactive-02": "#6366f1",  # Secondary interactive
    "interactive-03": "#8b5cf6",  # Tertiary interactive
    "interactive-04": "#66a3ff",  # Quaternary interactive
    # --- Action Colors ---
    "button-primary": "#3b82f6",  # Primary button background
    "button-primary-hover": "#2563eb",  # Primary button hover
    "button-primary-active": "#1d4ed8",  # Primary button active
    "button-secondary": "transparent",  # Secondary button background
    "button-secondary-hover": "#334155",  # Secondary button hover
    "button-tertiary": "transparent",  # Tertiary button background
    "button-tertiary-hover": "#1e293b",  # Tertiary button hover
    "button-danger": "#ef4444",  # Danger button background
    "button-danger-hover": "#dc2626",  # Danger button hover
    # --- Link Colors ---
    "link-primary": "#60a5fa",  # Primary links - 4.8:1 contrast
    "link-secondary": "#a78bfa",  # Secondary links - 4.6:1 contrast
    "link-visited": "#c084fc",  # Visited links - 4.5:1 contrast
    "link-hover": "#93c5fd",  # Link hover state
    "link-inverse": "#1e40af",  # Inverse links
    # --- Semantic Colors ---
    "support-error": "#ef4444",  # Error states
    "support-warning": "#f59e0b",  # Warning states
    "support-success": "#10b981",  # Success states
    "support-info": "#3b82f6",  # Info states
    "support-caution": "#f97316",  # Caution states
    # --- Focus & Selection ---
    "focus": "#60a5fa",  # Focus ring color
    "focus-inset": "#ffffff",  # Inset focus ring
    "focus-inverse": "#1e40af",  # Inverse focus
    "selection-background": "#1e40af",  # Text selection background
    "selection-text": "#ffffff",  # Text selection color
    # --- Overlays & Shadows ---
    "overlay": "rgba(0, 0, 0, 0.5)",  # Modal/tooltip overlays
    "shadow": "rgba(0, 0, 0, 0.25)",  # Component shadows
    "shadow-strong": "rgba(0, 0, 0, 0.5)",  # Strong shadows
    # --- Legacy Compatibility ---
    "bg_primary": "#0b1220",
    "bg_secondary": "#1c2536",
    "bg_tertiary": "#29344b",
    "border_primary": "#3a4766",
    "border_hover": "#5b6a8e",
    "text_primary": "#f8fafc",
    "text_secondary": "#cbd5e1",
    "text_tertiary": "#94a3b8",
    "action_primary": "#66a3ff",
    "action_danger": "#ef4444",
}

# 3. SPACING SYSTEM
# Refined 4px/8px base unit system with consistent application
# Following 8-point grid system for precise alignment
SPACING = {
    "0": 0,  # No spacing
    "xs": 4,  # Extra small - 4px
    "sm": 8,  # Small - 8px
    "md": 12,  # Medium - 12px (3 units)
    "lg": 16,  # Large - 16px (4 units)
    "xl": 24,  # Extra large - 24px (6 units)
    "2xl": 32,  # 2X large - 32px (8 units)
    "3xl": 48,  # 3X large - 48px (12 units)
    "4xl": 64,  # 4X large - 64px (16 units)
    "5xl": 96,  # 5X large - 96px (24 units)
    "6xl": 128,  # 6X large - 128px (32 units)
    # Component-specific spacing
    "button-padding-sm": "8px 16px",  # Small button padding
    "button-padding-md": "12px 24px",  # Medium button padding
    "button-padding-lg": "16px 32px",  # Large button padding
    "input-padding": "12px 16px",  # Input field padding
    "card-padding": "16px 24px",  # Card content padding
    "modal-padding": "24px 32px",  # Modal content padding
}

# 4. BORDER RADIUS SYSTEM
# Consistent rounded corner system
RADIUS = {
    "none": 0,  # No radius
    "xs": 2,  # Extra small
    "sm": 4,  # Small
    "md": 8,  # Medium
    "lg": 12,  # Large
    "xl": 16,  # Extra large
    "2xl": 24,  # 2X large
    "full": 9999,  # Fully rounded (pills)
    # Component-specific radius
    "button": 8,  # Button corners
    "card": 12,  # Card corners
    "input": 6,  # Input field corners
    "modal": 16,  # Modal corners
    "tooltip": 4,  # Tooltip corners
}

# 5. ELEVATION SYSTEM
# Now handled by ShadowManager class - removing CSS box-shadow for Qt compatibility
# CSS box-shadow is not supported by Qt stylesheets, use ShadowManager instead
ELEVATION = {
    # Elevation levels for reference (use ShadowManager.apply_shadow() instead)
    "none": "",  # ShadowManager.apply_shadow(widget, "none")
    "01": "",  # ShadowManager.apply_shadow(widget, "01")
    "02": "",  # ShadowManager.apply_shadow(widget, "02")
    "03": "",  # ShadowManager.apply_shadow(widget, "03")
    "04": "",  # ShadowManager.apply_shadow(widget, "04")
    "05": "",  # ShadowManager.apply_shadow(widget, "05")
    # Interactive shadows
    "hover": "",  # ShadowManager.create_hover_shadow()
    "focus": "",  # ShadowManager.create_focus_shadow()
    "active": "",  # ShadowManager.apply_shadow(widget, "active")
}

# 6. ANIMATION SYSTEM
# Now handled by AnimationManager class - removing CSS transitions for Qt compatibility
# CSS transitions are not supported by Qt stylesheets, use AnimationManager instead
ANIMATION = {
    # Duration references (use AnimationManager.DURATIONS instead)
    "duration-fast": "150ms",  # AnimationManager.DURATIONS["fast"]
    "duration-moderate": "300ms",  # AnimationManager.DURATIONS["moderate"]
    "duration-slow": "500ms",  # AnimationManager.DURATIONS["slow"]
    "duration-extra-slow": "700ms",  # AnimationManager.DURATIONS["extra-slow"]
    # Easing references (use AnimationManager.EASING instead)
    "easing-standard": "cubic-bezier(0.4, 0.0, 0.2, 1)",  # AnimationManager.EASING["standard"]
    "easing-emphasized": "cubic-bezier(0.0, 0.0, 0.2, 1)",  # AnimationManager.EASING["decelerate"]
    "easing-decelerated": "cubic-bezier(0.0, 0.0, 0.2, 1)",  # AnimationManager.EASING["decelerate"]
    "easing-accelerated": "cubic-bezier(0.4, 0.0, 1, 1)",  # AnimationManager.EASING["accelerate"]
}

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
    """Enhanced metric card with perfected styling and accessibility."""

    def __init__(self, key: str, title: str):
        super().__init__()
        self.key = key
        self.setObjectName(f"card_{key}")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(f"{title} Metrics Card")
        self.setAccessibleDescription(f"Click to view detailed {title} information")
        self.setToolTip("")

        # Initialize interaction manager for premium UX
        self.interaction_manager = InteractionManager(self)

        # Apply native Qt shadow instead of CSS box-shadow
        ShadowManager.apply_shadow(self, "02")

        # Enhanced styling with new design tokens (removed incompatible CSS)
        self.setStyleSheet(
            f"""
            QFrame[objectName^="card_"] {{
                background-color: {COLORS['layer-01']};
                border: 1px solid {COLORS['border-subtle']};
                border-radius: {RADIUS['card']}px;
                padding: {SPACING['card-padding']};
                /* Shadows now handled by ShadowManager */
                /* Transitions now handled by AnimationManager and InteractionManager */
            }}

            QFrame[objectName^="card_"]:hover {{
                background-color: {COLORS['layer-hover']};
                border-color: {COLORS['border-interactive']};
                /* Hover animations now handled by InteractionManager */
            }}

            QFrame[objectName^="card_"]:focus {{
                outline: 2px solid {COLORS['focus']};
                outline-offset: 2px;
                border-color: {COLORS['border-interactive']};
            }}

            QFrame[objectName^="card_"][pressed="true"] {{
                background-color: {COLORS['layer-active']};
            }}

            QFrame[objectName^="card_"][selected="true"] {{
                background-color: {COLORS['layer-selected']};
                border-color: {COLORS['interactive-01']};
            }}

            /* Loading state styling */
            QFrame[objectName^="card_"][loading="true"] {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['layer-01']},
                    stop:0.5 {COLORS['layer-hover']},
                    stop:1 {COLORS['layer-01']});
            }}
            """
        )

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(120)  # Consistent card height

        # Setup premium hover effects
        self.interaction_manager.setup_hover_effects(
            enable_scale=True, enable_shadow=True
        )

        # Enhanced layout with better spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"]
        )
        layout.setSpacing(SPACING["md"])

        # Title with enhanced typography
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet(
            f"{TYPOGRAPHY['heading-04']} color: {COLORS['text-primary']};"
        )
        self.title_lbl.setAccessibleName(f"{title} metric")

        # Value with enhanced typography and loading state
        self.value_lbl = QLabel("Loading...")
        self.value_lbl.setStyleSheet(
            f"{TYPOGRAPHY['value']} color: {COLORS['text-secondary']};"
        )
        self.value_lbl.setAccessibleName(f"{title} value")

        # Sparkline with improved styling
        self.spark_lbl = QLabel()
        self.spark_lbl.setMinimumHeight(40)  # Increased height for better visibility
        self.spark_lbl.setMaximumHeight(40)
        self.spark_lbl.setScaledContents(True)
        self.spark_lbl.setAccessibleName(f"{title} trend visualization")

        # Status indicator (new feature)
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(8, 8)
        self.status_indicator.setStyleSheet(
            f"""
            background-color: {COLORS['support-success']};
            border-radius: 4px;
            """
        )
        self.status_indicator.hide()  # Hidden by default

        # Header layout with title and status
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.status_indicator)

        # Main layout assembly
        layout.addLayout(header_layout)
        layout.addWidget(self.value_lbl)
        layout.addStretch()
        layout.addWidget(self.spark_lbl)

        # Enhanced loading animation using QPropertyAnimation directly for opacity effect
        self.loading_effect = QGraphicsOpacityEffect(self.value_lbl)
        self.value_lbl.setGraphicsEffect(self.loading_effect)

        # Create opacity animation for loading effect
        self.loading_anim = QPropertyAnimation(self.loading_effect, b"opacity")
        self.loading_anim.setDuration(AnimationManager.DURATIONS["slow"])
        self.loading_anim.setEasingCurve(AnimationManager.EASING["standard"])
        self.loading_anim.setStartValue(0.3)
        self.loading_anim.setEndValue(1.0)
        self.loading_anim.setLoopCount(-1)

        # Premium loading shimmer effect
        self.shimmer_timer = QTimer(self)
        self.shimmer_timer.setInterval(100)  # Update every 100ms
        self.shimmer_step = 0
        self.shimmer_timer.timeout.connect(self._update_shimmer)

        # Tooltip timer for delayed tooltip display
        self._tooltip_timer = QTimer(self)
        self._tooltip_timer.setSingleShot(True)
        self._tooltip_timer.setInterval(500)  # 500ms delay
        self._tooltip_timer.timeout.connect(self._show_delayed_tooltip)
        self._pending_tooltip = False

        # State management
        self._is_loading = True
        self._is_selected = False
        self._data_value = None

        # Start loading animation
        self.set_loading_state(True)

    def _update_shimmer(self):
        """Update shimmer effect for loading state."""
        if self._is_loading:
            self.shimmer_step = (self.shimmer_step + 1) % 20
            # Create shimmer effect by cycling through opacity values
            alpha = 0.3 + 0.4 * (0.5 + 0.5 * (self.shimmer_step / 10))
            self.loading_effect.setOpacity(alpha)

    def set_loading_state(self, loading: bool):
        """Set the loading state of the card."""
        self._is_loading = loading
        self.setProperty("loading", loading)

        if loading:
            self.value_lbl.setText("Loading...")
            self.loading_anim.start()
            self.shimmer_timer.start()
            self.status_indicator.hide()
            # Apply special loading shadow
            ShadowManager.apply_shadow(self, "01")
        else:
            self.loading_anim.stop()
            self.shimmer_timer.stop()
            self.loading_effect.setOpacity(1.0)
            self.status_indicator.show()
            # Restore normal shadow
            ShadowManager.apply_shadow(self, "02")

        self.style().unpolish(self)
        self.style().polish(self)

    def set_selected_state(self, selected: bool):
        """Set the selected state of the card with enhanced visual feedback."""
        self._is_selected = selected
        self.setProperty("selected", selected)

        # Apply appropriate shadow based on selection state
        if selected:
            ShadowManager.apply_shadow(self, "03")
            # Add subtle scale animation for selection
            AnimationManager.animate_hover_scale(self, 1.01)
        else:
            ShadowManager.apply_shadow(self, "02")

        self.style().unpolish(self)
        self.style().polish(self)

    def set_status(self, status: str):
        """Set the status indicator color based on system state."""
        colors = {
            "normal": COLORS["support-success"],
            "warning": COLORS["support-warning"],
            "error": COLORS["support-error"],
            "info": COLORS["support-info"],
        }

        color = colors.get(status, COLORS["support-success"])
        self.status_indicator.setStyleSheet(
            f"""
            background-color: {color};
            border-radius: 4px;
            """
        )

    def update_value(self, value: str, raw_value: Optional[float] = None):
        """Update the card value with enhanced accessibility."""
        self._data_value = raw_value
        self.value_lbl.setText(value)

        # Update accessible description with current value
        if raw_value is not None:
            self.setAccessibleDescription(
                f"{self.title_lbl.text()}: {value}. Click for detailed information."
            )

        if self._is_loading:
            self.set_loading_state(False)

    def set_additional_info(self, info: str):
        """Set additional information for tooltip."""
        self._additional_info = info

    def enterEvent(self, event):
        """Enhanced hover event with delayed tooltip."""
        self._pending_tooltip = True
        self._tooltip_timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Enhanced leave event."""
        self._pending_tooltip = False
        self._tooltip_timer.stop()
        self.setToolTip("")
        super().leaveEvent(event)

    def _show_delayed_tooltip(self):
        """Show tooltip after delay if still hovering."""
        if self._pending_tooltip and self._data_value is not None:
            tooltip_text = f"{self.title_lbl.text()}: {self.value_lbl.text()}"
            if hasattr(self, "_additional_info"):
                tooltip_text += f"\n{self._additional_info}"
            self.setToolTip(tooltip_text)

    def focusInEvent(self, event):
        """Enhanced focus handling."""
        self.setProperty("focus", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Enhanced focus out handling."""
        self.setProperty("focus", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        """Enhanced keyboard interaction."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self._trigger_click()
        elif event.key() == Qt.Key.Key_Tab:
            # Ensure proper tab navigation
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Enhanced mouse press with visual feedback."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setProperty("pressed", True)
            self.style().unpolish(self)
            self.style().polish(self)
            self._trigger_click()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Enhanced mouse release."""
        self.setProperty("pressed", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().mouseReleaseEvent(event)

    def _trigger_click(self):
        """Trigger click action with accessibility support."""
        try:
            window = self.window()
            if window and hasattr(window, "card_clicked"):
                # Simple audio feedback alternative
                print(f"Card clicked: {self.key}")  # Audio feedback for accessibility
                getattr(window, "card_clicked")(self.key)
        except Exception as e:
            print(f"Card click error: {e}")  # Debug logging


class HwPopup(QFrame):
    """Enhanced main application window with premium UX design system."""

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

        # Initialize interaction managers for premium UX
        self.animation_manager = AnimationManager()
        self.cards_interaction_managers = {}

        # Apply premium window shadow
        ShadowManager.apply_shadow(self, "05")

        # Enhanced styling with Qt-native shadows and animations
        self.setStyleSheet(
            f"""
            #hwpopup {{
                background-color: {COLORS['background']};
                color: {COLORS['text-primary']};
                border-radius: {RADIUS['modal']}px;
                border: 1px solid {COLORS['border-subtle']};
                /* Shadows now handled by ShadowManager */
            }}

            QLabel {{
                color: {COLORS['text-primary']};
                {TYPOGRAPHY['body-01']}
            }}

            QPushButton {{
                background-color: {COLORS['button-secondary']};
                color: {COLORS['text-primary']};
                border: 1px solid {COLORS['border-subtle']};
                border-radius: {RADIUS['button']}px;
                padding: {SPACING['button-padding-sm']};
                {TYPOGRAPHY['body-compact-01']}
                /* Transitions now handled by AnimationManager */
            }}

            QPushButton:hover {{
                background-color: {COLORS['button-secondary-hover']};
                border-color: {COLORS['border-strong']};
            }}

            QPushButton:focus {{
                outline: 2px solid {COLORS['focus']};
                outline-offset: 2px;
            }}

            QPushButton:pressed {{
                background-color: {COLORS['layer-active']};
            }}

            /* Close button specific styling */
            QPushButton#close-button {{
                background-color: transparent;
                color: {COLORS['text-tertiary']};
                border: none;
                border-radius: {RADIUS['md']}px;
                font-size: 16px;
                font-weight: 600;
                width: 32px;
                height: 32px;
            }}

            QPushButton#close-button:hover {{
                background-color: {COLORS['support-error']};
                color: {COLORS['text-on-color']};
            }}

            QPushButton#close-button:focus {{
                background-color: {COLORS['support-error']};
                color: {COLORS['text-on-color']};
                outline: 2px solid {COLORS['focus']};
            }}

            /* Loading state overlay */
            QFrame#loading-overlay {{
                background-color: rgba(0, 0, 0, 50);
                border-radius: {RADIUS['modal']}px;
            }}
            """
        )

        # Enhanced minimum size with better proportions
        self.setMinimumSize(QSize(600, 420))
        self.setMaximumSize(QSize(800, 600))

        # Initialize loading state management
        self.is_loading = True
        self.loading_timer = QTimer(self)
        self.loading_timer.setSingleShot(True)
        self.loading_timer.timeout.connect(self._finish_initial_load)

        # Premium entrance animation
        self.entrance_animation = None
        self._setup_entrance_animation()

        # Main layout with enhanced spacing
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(
            SPACING["2xl"], SPACING["2xl"], SPACING["2xl"], SPACING["2xl"]
        )
        self.root_layout.setSpacing(SPACING["xl"])

        # --- Enhanced Header ---
        self._create_header()

        # --- Enhanced Cards Grid ---
        self._create_cards_grid()

        # --- Enhanced Details Panel ---
        self._create_details_panel()

        # --- Enhanced Footer ---
        self._create_footer()

        # Enhanced animations with new timing
        self._setup_animations()

        # Accessibility improvements
        self.setAccessibleName("System Hardware Monitor")
        self.setAccessibleDescription(
            "Monitor CPU, RAM, GPU, and disk usage with detailed metrics"
        )

    def _create_header(self):
        """Create enhanced header with proper typography and spacing."""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(SPACING["lg"])

        # Main title with enhanced typography
        title = QLabel("System Hardware Monitor")
        title.setStyleSheet(
            f"{TYPOGRAPHY['heading-02']} color: {COLORS['text-primary']};"
        )
        title.setAccessibleName("Application title")

        # Subtitle for context
        subtitle = QLabel("Real-time system metrics")
        subtitle.setStyleSheet(
            f"{TYPOGRAPHY['body-compact-01']} color: {COLORS['text-secondary']};"
        )
        subtitle.setAccessibleName("Application description")

        # Title container
        title_container = QVBoxLayout()
        title_container.setSpacing(SPACING["xs"])
        title_container.addWidget(title)
        title_container.addWidget(subtitle)

        header_layout.addLayout(title_container)
        header_layout.addStretch()

        # Enhanced close button
        close_btn = QPushButton("✕")
        close_btn.setObjectName("close-button")
        close_btn.setFixedSize(32, 32)
        close_btn.setAccessibleName("Close application")
        close_btn.setAccessibleDescription("Press to close the hardware monitor")
        close_btn.clicked.connect(QCoreApplication.quit)
        close_btn.setToolTip("Close (Esc)")

        header_layout.addWidget(close_btn)
        self.root_layout.addLayout(header_layout)

    def _create_cards_grid(self):
        """Create enhanced cards grid with consistent spacing."""
        self.grid = QGridLayout()
        self.grid.setSpacing(SPACING["lg"])
        self.grid.setRowStretch(0, 1)
        self.grid.setRowStretch(1, 1)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)

        # Enhanced cards with new styling
        self.card_cpu = Card("cpu", "CPU")
        self.card_ram = Card("ram", "Memory")
        self.card_gpu = Card("gpu", "Graphics")
        self.card_disk = Card("disk", "Storage")

        self.grid.addWidget(self.card_cpu, 0, 0)
        self.grid.addWidget(self.card_ram, 0, 1)
        self.grid.addWidget(self.card_gpu, 1, 0)
        self.grid.addWidget(self.card_disk, 1, 1)

        self.root_layout.addLayout(self.grid)

    def _create_details_panel(self):
        """Create enhanced details panel with improved styling."""
        self.details = QFrame()
        self.details.setObjectName("details")
        self.details.setStyleSheet(
            f"""
            #details {{
                background-color: {COLORS['layer-02']};
                border: 1px solid {COLORS['border-subtle']};
                border-radius: {RADIUS['lg']}px;
                {ELEVATION['02']}
            }}
            """
        )

        self.details_layout = QVBoxLayout(self.details)
        self.details_layout.setContentsMargins(
            SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"]
        )
        self.details_layout.setSpacing(SPACING["md"])

        # Enhanced details title
        self.details_title = QLabel("Select a metric card for details")
        self.details_title.setStyleSheet(
            f"{TYPOGRAPHY['heading-03']} color: {COLORS['text-primary']};"
        )
        self.details_title.setAccessibleName("Details panel title")

        # Enhanced details body
        self.details_body = QLabel(
            "Click on any metric card above to view detailed information, trends, and system insights."
        )
        self.details_body.setWordWrap(True)
        self.details_body.setStyleSheet(
            f"{TYPOGRAPHY['body-01']} color: {COLORS['text-secondary']}; line-height: 1.5;"
        )
        self.details_body.setAccessibleName("Details panel content")

        self.details_layout.addWidget(self.details_title)
        self.details_layout.addWidget(self.details_body)

        # Enhanced opacity effect
        self.details_effect = QGraphicsOpacityEffect(self.details)
        self.details.setGraphicsEffect(self.details_effect)
        self.details.setMaximumHeight(0)

        self.root_layout.addWidget(self.details)

    def _create_footer(self):
        """Create enhanced footer with additional information."""
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(SPACING["lg"])

        # Status info
        status_text = QLabel("Wayland-friendly • Real-time monitoring")
        status_text.setStyleSheet(
            f"{TYPOGRAPHY['body-02']} color: {COLORS['text-tertiary']};"
        )
        status_text.setAccessibleName("Application status")

        footer_layout.addWidget(status_text)
        footer_layout.addStretch()

        # Update interval info
        interval_text = QLabel(f"Updates every {UPDATE_INTERVAL_MS//1000}s")
        interval_text.setStyleSheet(
            f"{TYPOGRAPHY['body-02']} color: {COLORS['text-tertiary']};"
        )
        interval_text.setAccessibleName("Update interval information")

        footer_layout.addWidget(interval_text)
        self.root_layout.addLayout(footer_layout)

    def _setup_entrance_animation(self):
        """Setup premium entrance animation."""
        # Scale animation for entrance
        self.entrance_scale_anim = QPropertyAnimation(self, b"geometry")
        self.entrance_scale_anim.setDuration(AnimationManager.DURATIONS["moderate"])
        self.entrance_scale_anim.setEasingCurve(AnimationManager.EASING["bounce"])

        # Opacity animation for entrance
        self.entrance_opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.entrance_opacity_anim.setDuration(AnimationManager.DURATIONS["fast"])
        self.entrance_opacity_anim.setEasingCurve(AnimationManager.EASING["standard"])

    def _finish_initial_load(self):
        """Finish initial loading state with smooth transition."""
        self.is_loading = False
        # Animate cards into view with staggered timing
        for i, card in enumerate(
            [self.card_cpu, self.card_ram, self.card_gpu, self.card_disk]
        ):
            # Stagger the animations by 100ms each
            QTimer.singleShot(i * 100, lambda c=card: c.set_loading_state(False))

    def _create_loading_overlay(self):
        """Create premium loading overlay."""
        self.loading_overlay = QFrame(self)
        self.loading_overlay.setObjectName("loading-overlay")
        self.loading_overlay.setGeometry(self.rect())

        # Loading spinner
        self.loading_spinner = QLabel("Loading...", self.loading_overlay)
        self.loading_spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_spinner.setStyleSheet(
            f"""
            color: {COLORS['text-primary']};
            {TYPOGRAPHY['heading-02']}
        """
        )

        # Position spinner in center
        overlay_layout = QVBoxLayout(self.loading_overlay)
        overlay_layout.addStretch()
        overlay_layout.addWidget(self.loading_spinner)
        overlay_layout.addStretch()

    def show_with_entrance_animation(self, screen):
        """Enhanced show with premium entrance animation."""
        # Start with small scale and fade (skip opacity on Wayland)
        try:
            self.setWindowOpacity(0.0)
            use_opacity = True
        except:
            use_opacity = False

        original_geometry = self.geometry()

        # Scale down initially
        small_width = int(original_geometry.width() * 0.8)
        small_height = int(original_geometry.height() * 0.8)
        small_x = original_geometry.x() + (original_geometry.width() - small_width) // 2
        small_y = (
            original_geometry.y() + (original_geometry.height() - small_height) // 2
        )
        small_geometry = QRect(small_x, small_y, small_width, small_height)

        self.setGeometry(small_geometry)
        self.show()
        self.raise_()
        self.activateWindow()

        # Animate to full size and opacity
        self.entrance_scale_anim.setStartValue(small_geometry)
        self.entrance_scale_anim.setEndValue(original_geometry)
        self.entrance_opacity_anim.setStartValue(0.0)
        self.entrance_opacity_anim.setEndValue(1.0)

        # Start both animations
        self.entrance_scale_anim.start()
        self.entrance_opacity_anim.start()

        # Start initial loading process
        self.loading_timer.start(1000)  # Show loading for 1 second

    def _setup_animations(self):
        """Setup enhanced animations with new timing system."""
        # Window fade animation
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(
            int(ANIMATION["duration-moderate"].replace("ms", ""))
        )
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Details panel height animation
        self.details_anim_h = QPropertyAnimation(self.details, b"maximumHeight")
        self.details_anim_h.setDuration(
            int(ANIMATION["duration-moderate"].replace("ms", ""))
        )
        self.details_anim_h.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Details panel opacity animation
        self.details_anim_o = QPropertyAnimation(self.details_effect, b"opacity")
        self.details_anim_o.setDuration(
            int(ANIMATION["duration-fast"].replace("ms", ""))
        )
        self.details_anim_o.setEasingCurve(QEasingCurve.Type.OutCubic)

    def card_clicked(self, key: str):
        """Enhanced card click handler with improved details."""
        # Clear any existing selection
        for card in [self.card_cpu, self.card_ram, self.card_gpu, self.card_disk]:
            card.set_selected_state(False)

        # Set selected card
        selected_card = getattr(self, f"card_{key}", None)
        if selected_card:
            selected_card.set_selected_state(True)

        # Build enhanced details
        text = self._build_details_text(key)
        self.details_title.setText(f"{key.upper()} Metrics")
        self.details_body.setText(text)

        # Calculate target height
        if text:
            # Account for margins, title, and content
            title_height = self.details_title.sizeHint().height()
            body_height = self.details_body.sizeHint().height()
            margins = SPACING["xl"] * 2  # Top and bottom margins
            spacing = SPACING["md"]  # Spacing between title and body
            target_height = title_height + body_height + margins + spacing
            target_height = min(target_height, 200)  # Max height limit
        else:
            target_height = 0

        self._animate_details_to(target_height)

    def _animate_details_to(self, height: int):
        """Enhanced details animation with smooth transitions."""
        self.details_anim_h.stop()
        self.details_anim_o.stop()

        current_height = self.details.maximumHeight()
        self.details_anim_h.setStartValue(current_height)
        self.details_anim_h.setEndValue(height)

        if height > 0:
            # Expanding: fade in after height animation starts
            self.details_anim_o.setStartValue(0.0)
            self.details_anim_o.setEndValue(1.0)
        else:
            # Collapsing: fade out immediately
            self.details_anim_o.setStartValue(1.0)
            self.details_anim_o.setEndValue(0.0)

        self.details_anim_h.start()
        self.details_anim_o.start()

    def show_with_fade(self, screen):
        """Enhanced show with fade animation."""
        # Center window on screen
        available_geometry = screen.availableGeometry()
        x = available_geometry.x() + (available_geometry.width() - self.width()) // 2
        y = available_geometry.y() + (available_geometry.height() - self.height()) // 2
        self.move(x, y)

        # Fade in animation (skip opacity on Wayland)
        try:
            self.setWindowOpacity(0.0)
            use_opacity = True
        except:
            use_opacity = False

        self.show()
        self.raise_()
        self.activateWindow()

        if use_opacity:
            self.fade_anim.setStartValue(0.0)
            self.fade_anim.setEndValue(1.0)
            self.fade_anim.start()

    def draw_sparkline(self, values: list[float], width: int = 140, height: int = 40):
        """Enhanced sparkline with better styling and HiDPI support."""
        device_pixel_ratio = 2  # HiDPI support
        pix = QPixmap(width * device_pixel_ratio, height * device_pixel_ratio)
        pix.setDevicePixelRatio(device_pixel_ratio)
        pix.fill(Qt.GlobalColor.transparent)

        if not values or len(values) < 2:
            return pix

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Enhanced pen with proper color from design tokens
        pen = QPen(QColor(COLORS["interactive-01"]))
        pen.setWidth(3)  # Slightly thicker line for better visibility
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        # Calculate value range with padding
        max_val = max(values)
        min_val = min(values)
        range_val = max_val - min_val if max_val != min_val else 1

        # Add small padding to prevent line from touching edges
        padding = height * 0.1
        usable_height = height - (2 * padding)

        # Calculate step between points
        step = width / max(len(values) - 1, 1)

        # Draw gradient fill under the line
        gradient_brush = QColor(COLORS["interactive-01"])
        gradient_brush.setAlpha(30)  # 30% opacity
        painter.setBrush(gradient_brush)

        # Create path for line and fill
        from PySide6.QtGui import QPainterPath

        path = QPainterPath()
        fill_path = QPainterPath()

        # Calculate first point
        first_y = (
            padding
            + usable_height
            - ((values[0] - min_val) / range_val) * usable_height
        )
        path.moveTo(0, first_y)
        fill_path.moveTo(0, height)
        fill_path.lineTo(0, first_y)

        # Draw line through all points
        for i, value in enumerate(values):
            x = i * step
            y = (
                padding
                + usable_height
                - ((value - min_val) / range_val) * usable_height
            )

            if i == 0:
                continue

            path.lineTo(x, y)
            fill_path.lineTo(x, y)

        # Complete fill path
        fill_path.lineTo(width, height)
        fill_path.closeSubpath()

        # Draw fill first, then line
        painter.fillPath(fill_path, gradient_brush)
        painter.strokePath(path, pen)

        # Add subtle glow effect
        glow_pen = QPen(QColor(COLORS["interactive-01"]))
        glow_pen.setWidth(5)
        glow_pen.setColor(QColor(COLORS["interactive-01"]))
        glow_color = QColor(COLORS["interactive-01"])
        glow_color.setAlpha(20)
        glow_pen.setColor(glow_color)
        painter.setPen(glow_pen)
        painter.strokePath(path, glow_pen)

        painter.end()
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
        self.popup.show_with_entrance_animation(scr)
        self.timer = QTimer()
        self.timer.setInterval(UPDATE_INTERVAL_MS)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start()
        self.update_stats()  # Initial call

    def update_stats(self):
        """Enhanced statistics update with better error handling and accessibility."""
        try:
            # Gather system metrics
            cpu = get_cpu_info()
            ram = get_ram_info()
            gpus = get_gpu_info()
            disks = get_disk_info()

            # Update CPU card
            cpu_usage = float(cpu.get("usage", 0) or 0)
            self.popup.card_cpu.update_value(f"{cpu_usage:.0f}%", cpu_usage)
            cpu_temp = cpu.get("temp")
            if cpu_temp is not None:
                self.popup.card_cpu.set_additional_info(f"Temperature: {cpu_temp}°C")
                self.popup.card_cpu.set_status(
                    "normal"
                    if cpu_temp < 80
                    else "warning" if cpu_temp < 90 else "error"
                )
            else:
                self.popup.card_cpu.set_status("normal")

            # Update RAM card
            ram_percent = float(ram.get("percent", 0) or 0)
            self.popup.card_ram.update_value(f"{ram_percent:.0f}%", ram_percent)
            ram_info = f"Used: {ram['used_gb']:.1f} GiB / {ram['total_gb']:.1f} GiB"
            self.popup.card_ram.set_additional_info(ram_info)
            self.popup.card_ram.set_status(
                "normal"
                if ram_percent < 80
                else "warning" if ram_percent < 90 else "error"
            )

            # Update GPU card
            gpu_util = 0.0
            gpu_info = "No GPU detected"
            if gpus:
                try:
                    gpu = gpus[0]
                    gpu_util = float(gpu.get("util", 0) or 0)
                    gpu_name = gpu.get("name", "GPU")
                    gpu_temp = gpu.get("temp")
                    gpu_mem_used = gpu.get("mem_used_gb")
                    gpu_mem_total = gpu.get("mem_total_gb")

                    gpu_info = f"Device: {gpu_name}"
                    if gpu_temp is not None:
                        gpu_info += f"\nTemperature: {gpu_temp}°C"
                    if gpu_mem_used is not None and gpu_mem_total is not None:
                        gpu_info += (
                            f"\nMemory: {gpu_mem_used:.1f} / {gpu_mem_total:.1f} GiB"
                        )

                    self.popup.card_gpu.set_status(
                        "normal"
                        if gpu_util < 80
                        else "warning" if gpu_util < 95 else "error"
                    )
                except (ValueError, TypeError):
                    gpu_util = 0.0
                    self.popup.card_gpu.set_status("error")
            else:
                self.popup.card_gpu.set_status("info")

            self.popup.card_gpu.update_value(f"{gpu_util:.0f}%", gpu_util)
            self.popup.card_gpu.set_additional_info(gpu_info)

            # Update Disk card
            disk_percent = 0.0
            disk_info = "No disks detected"
            if disks:
                disk = disks[0]  # Primary disk
                disk_percent = float(disk.get("percent", 0) or 0)
                disk_info = f"Device: {disk['device']}\nMount: {disk['mount']}"
                if len(disks) > 1:
                    disk_info += f"\n{len(disks)} storage devices total"

                self.popup.card_disk.set_status(
                    "normal"
                    if disk_percent < 80
                    else "warning" if disk_percent < 90 else "error"
                )
            else:
                self.popup.card_disk.set_status("info")

            self.popup.card_disk.update_value(f"{disk_percent:.0f}%", disk_percent)
            self.popup.card_disk.set_additional_info(disk_info)

            # Update history for sparklines
            HISTORY["cpu"].append(cpu_usage)
            HISTORY["ram"].append(ram_percent)
            HISTORY["gpu"].append(gpu_util)
            HISTORY["disk"].append(disk_percent)

            # Maintain history size
            for key in HISTORY:
                HISTORY[key] = HISTORY[key][-HISTORY_MAX:]

                # Update sparklines with enhanced styling
                card = getattr(self.popup, f"card_{key}")
                if len(HISTORY[key]) > 1:
                    pixmap = self.popup.draw_sparkline(HISTORY[key])
                    if pixmap:
                        card.spark_lbl.setPixmap(pixmap)

        except Exception as e:
            print(f"Error updating stats: {e}")  # Debug logging
            # Set error state for all cards with enhanced visual feedback
            for card in [
                self.popup.card_cpu,
                self.popup.card_ram,
                self.popup.card_gpu,
                self.popup.card_disk,
            ]:
                card.set_status("error")
                card.value_lbl.setText("Error")
                card.set_additional_info(f"Failed to load data: {str(e)[:50]}...")

                # Add error animation
                error_animation = AnimationManager.animate_opacity(card, 0.7, "fast")
                # After error animation, restore opacity
                QTimer.singleShot(
                    300, lambda c=card: AnimationManager.animate_opacity(c, 1.0, "fast")
                )

    def run(self):
        try:
            sys.exit(self.app.exec())
        except KeyboardInterrupt:
            sys.exit(0)


def main():
    HwApp().run()


if __name__ == "__main__":
    main()
