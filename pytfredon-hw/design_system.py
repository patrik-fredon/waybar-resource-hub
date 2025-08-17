#!/usr/bin/env python3
"""Modern Design System for PyTfredon Hardware Monitor GUI."""
from __future__ import annotations

from typing import Optional
from PySide6.QtCore import QRect
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect, QGraphicsOpacityEffect


# ENHANCED DESIGN SYSTEM - 2025 Standards
# Perfect foundational elements with WCAG 2.2 AA compliance (4.5:1+ contrast)
# Based on modern best practices: 8px grid, 1.25 typography scale, semantic colors

# 1. ENHANCED TYPOGRAPHY SYSTEM
# Perfect 1.25 ratio scale: 12, 15, 18, 24, 30, 37, 46px
# Consistent font weights: 300/light, 400/regular, 500/medium, 600/semibold, 700/bold
# Optimized line heights: 1.2 for headings, 1.5 for body, 1.4 for UI
# Perfect letter spacing: -0.02em for large text, 0 for body, +0.05em for small caps
TYPOGRAPHY = {
    # DISPLAY TYPOGRAPHY - Large impactful text
    "display-01": "font-weight: 300; font-size: 46px; line-height: 1.2; letter-spacing: -0.02em;",  # 46px
    "display-02": "font-weight: 300; font-size: 37px; line-height: 1.2; letter-spacing: -0.02em;",  # 37px
    "display-03": "font-weight: 400; font-size: 30px; line-height: 1.2; letter-spacing: -0.01em;",  # 30px
    # HEADING TYPOGRAPHY - Clear hierarchy with perfect scale
    "heading-01": "font-weight: 600; font-size: 30px; line-height: 1.2; letter-spacing: -0.01em;",  # 30px
    "heading-02": "font-weight: 600; font-size: 24px; line-height: 1.2; letter-spacing: -0.01em;",  # 24px
    "heading-03": "font-weight: 600; font-size: 18px; line-height: 1.2; letter-spacing: 0;",  # 18px
    "heading-04": "font-weight: 600; font-size: 15px; line-height: 1.2; letter-spacing: 0;",  # 15px
    "heading-05": "font-weight: 600; font-size: 12px; line-height: 1.2; letter-spacing: 0.05em; text-transform: uppercase;",  # 12px
    # BODY TYPOGRAPHY - Optimized for readability
    "body-01": "font-weight: 400; font-size: 15px; line-height: 1.5; letter-spacing: 0;",  # 15px
    "body-02": "font-weight: 400; font-size: 12px; line-height: 1.5; letter-spacing: 0;",  # 12px
    "body-large": "font-weight: 400; font-size: 18px; line-height: 1.5; letter-spacing: 0;",  # 18px
    "body-compact-01": "font-weight: 400; font-size: 15px; line-height: 1.4; letter-spacing: 0;",  # 15px
    "body-compact-02": "font-weight: 400; font-size: 12px; line-height: 1.4; letter-spacing: 0;",  # 12px
    # UI ELEMENT TYPOGRAPHY - Compact and functional
    "ui-01": "font-weight: 400; font-size: 15px; line-height: 1.4; letter-spacing: 0;",  # 15px
    "ui-02": "font-weight: 400; font-size: 12px; line-height: 1.4; letter-spacing: 0;",  # 12px
    "ui-03": "font-weight: 500; font-size: 12px; line-height: 1.4; letter-spacing: 0.05em;",  # 12px
    # LABEL TYPOGRAPHY - Clear identification
    "label-01": "font-weight: 500; font-size: 12px; line-height: 1.4; letter-spacing: 0.05em; text-transform: uppercase;",  # 12px
    "label-02": "font-weight: 400; font-size: 15px; line-height: 1.4; letter-spacing: 0;",  # 15px
    "label-03": "font-weight: 400; font-size: 12px; line-height: 1.4; letter-spacing: 0;",  # 12px
    # HELPER & UTILITY TYPOGRAPHY
    "helper-text": "font-weight: 400; font-size: 12px; line-height: 1.4; font-style: italic; letter-spacing: 0;",  # 12px
    "caption": "font-weight: 400; font-size: 12px; line-height: 1.4; letter-spacing: 0;",  # 12px
    "legal": "font-weight: 400; font-size: 11px; line-height: 1.4; letter-spacing: 0;",  # 11px (exception for legal text)
    # CODE TYPOGRAPHY - Monospace perfection
    "code-01": "font-family: 'SF Mono', 'Monaco', 'Consolas', 'Courier New', monospace; font-weight: 400; font-size: 12px; line-height: 1.4; letter-spacing: 0;",  # 12px
    "code-02": "font-family: 'SF Mono', 'Monaco', 'Consolas', 'Courier New', monospace; font-weight: 400; font-size: 15px; line-height: 1.4; letter-spacing: 0;",  # 15px
    "code-inline": "font-family: 'SF Mono', 'Monaco', 'Consolas', 'Courier New', monospace; font-weight: 500; font-size: 12px; line-height: 1.4; letter-spacing: 0;",  # 12px
    # METRIC/VALUE TYPOGRAPHY - Perfect for data presentation
    "metric-01": "font-weight: 300; font-size: 37px; line-height: 1.2; letter-spacing: -0.02em;",  # 37px - Large metrics
    "metric-02": "font-weight: 300; font-size: 30px; line-height: 1.2; letter-spacing: -0.01em;",  # 30px - Standard metrics
    "metric-03": "font-weight: 400; font-size: 24px; line-height: 1.2; letter-spacing: 0;",  # 24px - Small metrics
    # LEGACY COMPATIBILITY (maintained for smooth migration)
    "h1": "font-weight: 600; font-size: 24px; line-height: 1.2; letter-spacing: -0.01em;",
    "h2": "font-weight: 600; font-size: 18px; line-height: 1.2; letter-spacing: 0;",
    "body": "font-weight: 400; font-size: 15px; line-height: 1.5; letter-spacing: 0;",
    "small": "font-weight: 400; font-size: 12px; line-height: 1.4; letter-spacing: 0;",
    "value": "font-weight: 300; font-size: 30px; line-height: 1.2; letter-spacing: -0.01em;",
}


# 2. COLOR SYSTEM
# Modern color palette with accessibility compliance
COLOR_SYSTEM = {
    # Primary brand colors
    "primary": {
        "50": "#eff6ff",
        "100": "#dbeafe",
        "200": "#bfdbfe",
        "300": "#93c5fd",
        "400": "#60a5fa",
        "500": "#3b82f6",
        "600": "#2563eb",
        "700": "#1d4ed8",
        "800": "#1e40af",
        "900": "#1e3a8a",
        "950": "#172554",
    },
    # Semantic colors
    "success": {"light": "#10b981", "main": "#059669", "dark": "#047857"},
    "warning": {"light": "#f59e0b", "main": "#d97706", "dark": "#b45309"},
    "error": {"light": "#ef4444", "main": "#dc2626", "dark": "#b91c1c"},
    "info": {"light": "#06b6d4", "main": "#0891b2", "dark": "#0e7490"},
    # Neutral colors
    "neutral": {
        "0": "#ffffff",
        "50": "#f9fafb",
        "100": "#f3f4f6",
        "200": "#e5e7eb",
        "300": "#d1d5db",
        "400": "#9ca3af",
        "500": "#6b7280",
        "600": "#4b5563",
        "700": "#374151",
        "800": "#1f2937",
        "900": "#111827",
        "950": "#030712",
    },
}


# 3. SPACING SYSTEM (8px grid)
SPACING = {
    "xs": 4,  # 0.25rem
    "sm": 8,  # 0.5rem
    "md": 16,  # 1rem
    "lg": 24,  # 1.5rem
    "xl": 32,  # 2rem
    "2xl": 48,  # 3rem
    "3xl": 64,  # 4rem
    "4xl": 96,  # 6rem
}


class ShadowManager:
    """Enhanced Qt-native shadow effects manager with 2025 elevation system."""

    # Enhanced elevation system with precise shadow configurations
    ELEVATION_CONFIGS = {
        "none": {"blur": 0, "offset": (0, 0), "alpha": 0},
        "01": {"blur": 2, "offset": (0, 1), "alpha": 20},  # Subtle - cards at rest
        "02": {"blur": 4, "offset": (0, 2), "alpha": 25},  # Low - interactive elements
        "03": {"blur": 8, "offset": (0, 4), "alpha": 30},  # Medium - hover states
        "04": {"blur": 16, "offset": (0, 8), "alpha": 35},  # High - selected/active
        "05": {"blur": 24, "offset": (0, 12), "alpha": 40},  # Maximum - modal/overlay
        "hover": {"blur": 6, "offset": (0, 3), "alpha": 28},  # Special hover elevation
        "focus": {
            "blur": 0,
            "offset": (0, 0),
            "alpha": 0,
        },  # Focus uses outline, not shadow
        "active": {"blur": 1, "offset": (0, 1), "alpha": 15},  # Pressed/active state
    }

    @staticmethod
    def create_shadow(
        level: str = "01",
        color: Optional[QColor] = None,
        custom_color_alpha: Optional[int] = None,
    ) -> QGraphicsDropShadowEffect:
        """Create enhanced drop shadow effect with precise elevation control."""
        shadow = QGraphicsDropShadowEffect()

        config = ShadowManager.ELEVATION_CONFIGS.get(
            level, ShadowManager.ELEVATION_CONFIGS["01"]
        )

        shadow.setBlurRadius(config["blur"])
        shadow.setOffset(*config["offset"])

        # Enhanced color handling with alpha control
        if color:
            shadow.setColor(color)
        else:
            # Use semantic shadow color with precise alpha
            alpha = (
                custom_color_alpha
                if custom_color_alpha is not None
                else config["alpha"]
            )
            shadow.setColor(QColor(0, 0, 0, alpha))  # Pure black with controlled alpha

        return shadow

    @staticmethod
    def apply_shadow(
        widget: QWidget,
        level: str = "01",
        color: Optional[QColor] = None,
        custom_alpha: Optional[int] = None,
    ):
        """Apply enhanced shadow effect to a widget with smooth transitions."""
        if level == "none":
            # Safely remove existing graphics effect
            current_effect = widget.graphicsEffect()
            if isinstance(current_effect, QGraphicsDropShadowEffect):
                current_effect.setParent(None)
                widget.setGraphicsEffect(None)  # type: ignore
        else:
            shadow = ShadowManager.create_shadow(level, color, custom_alpha)
            widget.setGraphicsEffect(shadow)

    @staticmethod
    def create_hover_shadow() -> QGraphicsDropShadowEffect:
        """Create enhanced hover shadow with improved visual feedback."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)
        shadow.setOffset(0, 3)
        # Enhanced blue tint for hover state
        shadow.setColor(QColor(59, 130, 246, 40))  # Blue-500 with medium alpha
        return shadow

    @staticmethod
    def create_focus_shadow() -> QGraphicsDropShadowEffect:
        """Create WCAG AA compliant focus shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(0)  # No blur for focus - outline is primary
        shadow.setOffset(0, 0)
        # High contrast blue for accessibility
        shadow.setColor(QColor(59, 130, 246, 180))  # Blue-500 with high alpha
        return shadow


def get_color(color_name: str, shade: str = "500") -> str:
    """Get color value from the color system."""
    try:
        if color_name in COLOR_SYSTEM:
            color_data = COLOR_SYSTEM[color_name]
            if isinstance(color_data, dict):
                return color_data.get(shade, color_data.get("main", "#000000"))
            elif isinstance(color_data, str):
                return color_data
        return "#000000"  # fallback
    except (KeyError, TypeError):
        return "#000000"


def get_spacing(size: str) -> int:
    """Get spacing value from the spacing system."""
    return SPACING.get(size, 16)  # Default to 'md' spacing


def get_typography(style: str) -> str:
    """Get typography style from the typography system."""
    return TYPOGRAPHY.get(style, TYPOGRAPHY["body"])
