#!/usr/bin/env python3
"""Enhanced Card Component with Fixed Hover Animations."""
from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QGraphicsOpacityEffect,
)

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from design_system import ShadowManager, get_color, get_spacing, get_typography
from animation_manager import AnimationManager, HoverManager


class Card(QFrame):
    """Enhanced metric card with fixed hover animations and professional design."""

    def __init__(self, key: str, title: str):
        super().__init__()
        self.key = key
        self.setObjectName(f"card_{key}")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(f"{title} Metrics Card")
        self.setAccessibleDescription(f"Click to view detailed {title} information")
        self.setToolTip("")

        # Initialize hover manager for professional UX
        self.hover_manager = HoverManager(self)
        self.hover_manager.enable_hover_effects()

        # Apply subtle shadow
        ShadowManager.apply_shadow(self, "02")

        # Enhanced styling with modern design
        self._setup_styles()

        # Setup cursor and size policy
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(140)
        self.setMaximumHeight(160)

        # Create layout with proper spacing
        self._setup_layout(title)

        # Initialize state
        self._is_loading = True
        self._is_selected = False
        self._data_value = None
        self._status = "normal"

        # Setup loading animation
        self._setup_loading_animation()

        # Setup tooltip system
        self._setup_tooltip_system()

        # Start in loading state
        self.set_loading_state(True)

    def _setup_styles(self):
        """Setup modern card styling."""
        self.setStyleSheet(
            f"""
            QFrame[objectName^="card_"] {{
                background-color: {get_color('neutral', '0')};
                border: 1px solid {get_color('neutral', '200')};
                border-radius: 12px;
                padding: {get_spacing('sm')}px;
            }}

            QFrame[objectName^="card_"]:hover {{
                background-color: {get_color('neutral', '50')};
                border-color: {get_color('primary', '300')};
            }}

            QFrame[objectName^="card_"]:focus {{
                outline: 2px solid {get_color('primary', '500')};
                outline-offset: 2px;
                border-color: {get_color('primary', '500')};
            }}

            QFrame[objectName^="card_"][pressed="true"] {{
                background-color: {get_color('neutral', '100')};
            }}

            QFrame[objectName^="card_"][selected="true"] {{
                background-color: {get_color('primary', '50')};
                border-color: {get_color('primary', '500')};
            }}

            QFrame[objectName^="card_"][loading="true"] {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {get_color('neutral', '0')},
                    stop:0.5 {get_color('neutral', '50')},
                    stop:1 {get_color('neutral', '0')});
            }}
        """
        )

    def _setup_layout(self, title: str):
        """Setup card layout with proper spacing."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            get_spacing("md"), get_spacing("md"), get_spacing("md"), get_spacing("md")
        )
        layout.setSpacing(get_spacing("sm"))

        # Title with enhanced typography
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet(
            f"""
            {get_typography('heading-04')}
            color: {get_color('neutral', '700')};
        """
        )
        self.title_lbl.setAccessibleName(f"{title} metric")

        # Value with metric typography for better data presentation
        self.value_lbl = QLabel("Loading...")
        self.value_lbl.setStyleSheet(
            f"""
            {get_typography('metric-02')}
            color: {get_color('neutral', '900')};
        """
        )
        self.value_lbl.setAccessibleName(f"{title} value")

        # Sparkline visualization
        self.spark_lbl = QLabel()
        self.spark_lbl.setMinimumHeight(40)
        self.spark_lbl.setMaximumHeight(40)
        self.spark_lbl.setScaledContents(True)
        self.spark_lbl.setAccessibleName(f"{title} trend visualization")

        # Status indicator
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(8, 8)
        self.status_indicator.setStyleSheet(
            f"""
            background-color: {get_color('success', 'main')};
            border-radius: 4px;
        """
        )
        self.status_indicator.hide()

        # Header layout
        header_layout = QHBoxLayout()
        header_layout.setSpacing(get_spacing("sm"))
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.status_indicator)

        # Main layout assembly
        layout.addLayout(header_layout)
        layout.addWidget(self.value_lbl)
        layout.addStretch()
        layout.addWidget(self.spark_lbl)

    def _setup_loading_animation(self):
        """Setup loading animation without affecting card size."""
        self.loading_effect = QGraphicsOpacityEffect(self.value_lbl)
        self.value_lbl.setGraphicsEffect(self.loading_effect)

        self.loading_anim = QPropertyAnimation(self.loading_effect, b"opacity")
        self.loading_anim.setDuration(AnimationManager.DURATIONS["slow"])
        self.loading_anim.setEasingCurve(AnimationManager.EASING["standard"])
        self.loading_anim.setStartValue(0.3)
        self.loading_anim.setEndValue(1.0)
        self.loading_anim.setLoopCount(-1)

        # Shimmer timer for loading effect
        self.shimmer_timer = QTimer(self)
        self.shimmer_timer.setInterval(100)
        self.shimmer_step = 0
        self.shimmer_timer.timeout.connect(self._update_shimmer)

    def _setup_tooltip_system(self):
        """Setup delayed tooltip system."""
        self._tooltip_timer = QTimer(self)
        self._tooltip_timer.setSingleShot(True)
        self._tooltip_timer.setInterval(500)
        self._tooltip_timer.timeout.connect(self._show_delayed_tooltip)
        self._pending_tooltip = False

    def _update_shimmer(self):
        """Update shimmer effect for loading state."""
        if self._is_loading:
            self.shimmer_step = (self.shimmer_step + 1) % 20
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
            ShadowManager.apply_shadow(self, "01")
        else:
            self.loading_anim.stop()
            self.shimmer_timer.stop()
            self.loading_effect.setOpacity(1.0)
            self.status_indicator.show()
            ShadowManager.apply_shadow(self, "02")

        self.style().unpolish(self)
        self.style().polish(self)

    def set_selected_state(self, selected: bool):
        """Set the selected state with subtle visual feedback."""
        self._is_selected = selected
        self.setProperty("selected", selected)

        if selected:
            ShadowManager.apply_shadow(self, "03")
        else:
            ShadowManager.apply_shadow(self, "02")

        self.style().unpolish(self)
        self.style().polish(self)

    def set_status(self, status: str):
        """Set status with semantic colors."""
        self._status = status

        status_colors = {
            "normal": get_color("success", "main"),
            "warning": get_color("warning", "main"),
            "error": get_color("error", "main"),
            "info": get_color("info", "main"),
            "disabled": get_color("neutral", "500"),
        }

        color = status_colors.get(status, get_color("success", "main"))
        self.status_indicator.setStyleSheet(
            f"""
            background-color: {color};
            border-radius: 4px;
        """
        )

        # Update accessibility
        status_descriptions = {
            "normal": "System operating normally",
            "warning": "Warning - attention may be needed",
            "error": "Error - immediate attention required",
            "info": "Informational status",
            "disabled": "System disabled",
        }

        description = status_descriptions.get(status, "Unknown status")
        self.setAccessibleDescription(
            f"{self.title_lbl.text()}: {self.value_lbl.text()}. {description}. Click for detailed information."
        )

    def update_value(self, value: str, raw_value: Optional[float] = None):
        """Update the card value with accessibility."""
        self._data_value = raw_value
        self.value_lbl.setText(value)

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
        """Enhanced hover entry with subtle effects."""
        self._pending_tooltip = True
        self._tooltip_timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Enhanced hover leave."""
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
        AnimationManager.animate_focus_ring(self, True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Enhanced focus out handling."""
        self.setProperty("focus", False)
        AnimationManager.animate_focus_ring(self, False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        """Enhanced keyboard interaction."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self._trigger_click()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Enhanced mouse press with visual feedback."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setProperty("pressed", True)
            AnimationManager.animate_press_feedback(self)
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
            card_clicked = getattr(window, "card_clicked", None)
            if callable(card_clicked):
                card_clicked(self.key)
                print(f"Card clicked: {self.key}")
        except Exception as e:
            print(f"Error triggering card click: {e}")

    def set_sparkline(self, pixmap):
        """Set sparkline visualization."""
        if pixmap:
            self.spark_lbl.setPixmap(pixmap)
        else:
            self.spark_lbl.clear()
