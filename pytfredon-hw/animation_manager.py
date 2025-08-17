#!/usr/bin/env python3
"""Modern Animation Manager for PyTfredon Hardware Monitor GUI."""
from __future__ import annotations

from typing import Optional
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PySide6.QtGui import QColor

from design_system import ShadowManager


class AnimationManager:
    """Enhanced Qt-native property animation manager with 2025 motion design principles."""

    # Enhanced animation durations following modern timing standards
    DURATIONS = {
        "instant": 0,  # Immediate - no animation
        "fast": 120,  # Quick interactions - micro animations
        "moderate": 200,  # Standard transitions - UI state changes
        "slow": 350,  # Deliberate - major layout changes
        "extra-slow": 500,  # Dramatic - modal/overlay entrance
        "loading": 1200,  # Loading states - breathing animation
    }

    # Enhanced easing curves for natural motion feel
    EASING = {
        "standard": QEasingCurve.Type.OutCubic,  # Default - most UI transitions
        "emphasized": QEasingCurve.Type.OutQuart,  # Strong emphasis - important changes
        "decelerate": QEasingCurve.Type.OutQuint,  # Entrance animations
        "accelerate": QEasingCurve.Type.InQuart,  # Exit animations
        "bounce": QEasingCurve.Type.OutBounce,  # Playful interactions
        "elastic": QEasingCurve.Type.OutElastic,  # Spring-like feedback
        "linear": QEasingCurve.Type.Linear,  # Continuous processes
        "overshoot": QEasingCurve.Type.OutBack,  # Attention-grabbing
    }

    @staticmethod
    def create_animation(
        widget: QWidget,
        property_name: str,
        duration: str = "moderate",
        easing: str = "standard",
    ) -> QPropertyAnimation:
        """Create enhanced property animation with modern timing principles."""
        animation = QPropertyAnimation(widget, property_name.encode())
        animation.setDuration(AnimationManager.DURATIONS[duration])
        animation.setEasingCurve(AnimationManager.EASING[easing])
        return animation

    @staticmethod
    def animate_subtle_hover(widget: QWidget, is_entering: bool = True):
        """Modern subtle hover animation - no geometry scaling, only visual enhancement."""
        # Apply subtle shadow elevation change
        if is_entering:
            ShadowManager.apply_shadow(widget, "hover")
            # Subtle opacity enhancement
            AnimationManager.animate_opacity(widget, 1.0, "fast")
        else:
            ShadowManager.apply_shadow(widget, "02")  # Back to default elevation
            AnimationManager.animate_opacity(widget, 0.95, "fast")

    @staticmethod
    def animate_opacity(
        widget: QWidget, target_opacity: float, duration: str = "moderate"
    ):
        """Enhanced opacity animation with smooth transitions."""
        # Check if widget already has an opacity effect
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            # Only add opacity effect if no shadow effect exists
            if effect is None:
                effect = QGraphicsOpacityEffect()
                widget.setGraphicsEffect(effect)
            else:
                # Don't override existing effects like shadows
                return None

        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(AnimationManager.DURATIONS[duration])
        animation.setEasingCurve(AnimationManager.EASING["standard"])
        animation.setEndValue(target_opacity)
        animation.start()
        return animation

    @staticmethod
    def animate_fade_in(widget: QWidget, duration: str = "moderate"):
        """Smooth fade-in animation for element entrance."""
        return AnimationManager.animate_opacity(widget, 1.0, duration)

    @staticmethod
    def animate_fade_out(widget: QWidget, duration: str = "moderate"):
        """Smooth fade-out animation for element exit."""
        return AnimationManager.animate_opacity(widget, 0.0, duration)

    @staticmethod
    def animate_press_feedback(widget: QWidget):
        """Subtle press feedback animation without scaling."""
        # Temporary shadow reduction for press feedback
        ShadowManager.apply_shadow(widget, "active")

        # Create a quick opacity flash
        animation = AnimationManager.animate_opacity(widget, 0.8, "fast")
        if animation:
            # Restore opacity after a brief moment
            def restore_opacity():
                AnimationManager.animate_opacity(widget, 1.0, "fast")
                ShadowManager.apply_shadow(widget, "02")

            animation.finished.connect(restore_opacity)

    @staticmethod
    def animate_focus_ring(widget: QWidget, focused: bool = True):
        """Animate focus ring appearance for accessibility."""
        if focused:
            # Create focus shadow effect
            ShadowManager.apply_shadow(widget, "focus")
        else:
            # Return to normal shadow
            ShadowManager.apply_shadow(widget, "02")


class HoverManager:
    """Enhanced hover management for modern UI interactions."""

    def __init__(self, widget: QWidget):
        self.widget = widget
        self._original_cursor = None
        self._is_hovering = False

    def enable_hover_effects(self):
        """Enable modern hover effects for the widget."""
        # Store original cursor
        self._original_cursor = self.widget.cursor()

        # Override enter and leave events
        original_enter = getattr(self.widget, "enterEvent", None)
        original_leave = getattr(self.widget, "leaveEvent", None)

        def enhanced_enter(event):
            self._is_hovering = True
            self.widget.setCursor(Qt.CursorShape.PointingHandCursor)
            AnimationManager.animate_subtle_hover(self.widget, True)
            if original_enter:
                original_enter(event)

        def enhanced_leave(event):
            self._is_hovering = False
            self.widget.setCursor(self._original_cursor or Qt.CursorShape.ArrowCursor)
            AnimationManager.animate_subtle_hover(self.widget, False)
            if original_leave:
                original_leave(event)

        # Assign enhanced event handlers
        self.widget.enterEvent = enhanced_enter
        self.widget.leaveEvent = enhanced_leave

    def is_hovering(self) -> bool:
        """Check if widget is currently being hovered."""
        return self._is_hovering
