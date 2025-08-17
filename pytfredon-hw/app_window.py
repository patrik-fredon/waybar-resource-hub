#!/usr/bin/env python3
"""Modern Hardware Monitor Application Window."""
from __future__ import annotations

import sys
from typing import Optional

from PySide6.QtCore import (
    QCoreApplication,
    QTimer,
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    QEvent,
)
from PySide6.QtGui import QGuiApplication, QCursor, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QFrame,
    QGraphicsOpacityEffect,
)

from design_system import ShadowManager, get_color, get_spacing, get_typography
from animation_manager import AnimationManager
from components.card import Card
from hardware_utils import (
    get_cpu_info,
    get_ram_info,
    get_gpu_info,
    get_disk_info,
    UPDATE_INTERVAL_MS,
    HISTORY,
    HISTORY_MAX,
)


class HwPopup(QWidget):
    """Modern hardware monitoring popup with responsive design and professional layout."""

    def __init__(self, app_instance=None):
        super().__init__()
        self.app_instance = app_instance
        self.is_loading = True
        self._setup_window()
        self._setup_styling()
        self._setup_layout()
        self._setup_animations()
        self._setup_loading_timer()

    def _setup_window(self):
        """Setup modern window properties with transparency and centering."""
        self.setWindowTitle("Hardware Monitor")
        self.setFixedSize(800, 600)  # Professional fixed size

        # Modern window flags for overlay behavior
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        # Set semi-transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Center on current screen
        self._center_on_screen()

        # Focus handling for click-outside-to-close
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Install event filter for global mouse events
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)

    def _center_on_screen(self):
        """Center window on the current screen."""
        screen = (
            QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        )
        screen_geometry = screen.availableGeometry()

        x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - self.height()) // 2

        self.move(x, y)

    def _setup_styling(self):
        """Setup modern styling with transparent background."""
        self.setStyleSheet(
            f"""
            QWidget {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
                             'Helvetica Neue', Arial, sans-serif;
            }}

            #main-container {{
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid {get_color('neutral', '200')};
                border-radius: 16px;
                backdrop-filter: blur(20px);
            }}

            #header {{
                background-color: rgba(248, 250, 252, 0.8);
                border-bottom: 1px solid {get_color('neutral', '200')};
                border-radius: 16px 16px 0 0;
                padding: {get_spacing('md')}px;
            }}

            #close-button {{
                background-color: {get_color('error', 'light')};
                border: none;
                border-radius: 16px;
                color: white;
                font-weight: 600;
                font-size: 14px;
            }}

            #close-button:hover {{
                background-color: {get_color('error', 'main')};
            }}

            #close-button:pressed {{
                background-color: {get_color('error', 'dark')};
            }}

            #details {{
                background-color: rgba(248, 250, 252, 0.6);
                border: 1px solid {get_color('neutral', '200')};
                border-radius: 12px;
                margin: {get_spacing('sm')}px;
            }}

            #footer {{
                color: {get_color('neutral', '500')};
                {get_typography('body-02')}
            }}
        """
        )

    def _setup_layout(self):
        """Setup responsive layout with proper margins and padding."""
        # Main container for transparency effect
        self.main_container = QFrame()
        self.main_container.setObjectName("main-container")

        # Apply subtle shadow to main container
        ShadowManager.apply_shadow(self.main_container, "04")

        # Root layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(
            get_spacing("md"), get_spacing("md"), get_spacing("md"), get_spacing("md")
        )
        root_layout.addWidget(self.main_container)

        # Container layout
        self.root_layout = QVBoxLayout(self.main_container)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(get_spacing("md"))

        self._create_header()
        self._create_cards_grid()
        self._create_details_panel()
        self._create_footer()

    def _create_header(self):
        """Create modern header with close button."""
        header = QFrame()
        header.setObjectName("header")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(
            get_spacing("lg"), get_spacing("md"), get_spacing("lg"), get_spacing("md")
        )

        # Title
        title = QLabel("Hardware Monitor")
        title.setStyleSheet(
            f"""
            {get_typography('heading-02')}
            color: {get_color('neutral', '800')};
            font-weight: 700;
        """
        )

        header_layout.addWidget(title)
        header_layout.addStretch()

        # Close button in top right
        close_btn = QPushButton("✕")
        close_btn.setObjectName("close-button")
        close_btn.setFixedSize(32, 32)
        close_btn.setAccessibleName("Close application")
        close_btn.setToolTip("Close (Esc or click outside)")
        close_btn.clicked.connect(self.close_application)

        header_layout.addWidget(close_btn)
        self.root_layout.addWidget(header)

    def _create_cards_grid(self):
        """Create responsive cards grid."""
        cards_container = QWidget()
        self.grid = QGridLayout(cards_container)
        self.grid.setSpacing(get_spacing("lg"))

        # Create cards with improved design
        self.card_cpu = Card("cpu", "CPU")
        self.card_ram = Card("ram", "Memory")
        self.card_gpu = Card("gpu", "Graphics")
        self.card_disk = Card("disk", "Storage")

        # Arrange in 2x2 grid
        self.grid.addWidget(self.card_cpu, 0, 0)
        self.grid.addWidget(self.card_ram, 0, 1)
        self.grid.addWidget(self.card_gpu, 1, 0)
        self.grid.addWidget(self.card_disk, 1, 1)

        # Add some padding around the grid
        cards_wrapper = QVBoxLayout()
        cards_wrapper.setContentsMargins(
            get_spacing("lg"), get_spacing("md"), get_spacing("lg"), get_spacing("md")
        )
        cards_wrapper.addWidget(cards_container)

        self.root_layout.addLayout(cards_wrapper)

    def _create_details_panel(self):
        """Create collapsible details panel."""
        self.details = QFrame()
        self.details.setObjectName("details")

        self.details_layout = QVBoxLayout(self.details)
        self.details_layout.setContentsMargins(
            get_spacing("lg"), get_spacing("lg"), get_spacing("lg"), get_spacing("lg")
        )

        # Details title and content
        self.details_title = QLabel("Select a metric card for details")
        self.details_title.setStyleSheet(
            f"""
            {get_typography('heading-04')}
            color: {get_color('neutral', '700')};
        """
        )

        self.details_body = QLabel(
            "Click on any metric card above to view detailed information, trends, and insights."
        )
        self.details_body.setWordWrap(True)
        self.details_body.setStyleSheet(
            f"""
            {get_typography('body-01')}
            color: {get_color('neutral', '600')};
            line-height: 1.5;
        """
        )

        self.details_layout.addWidget(self.details_title)
        self.details_layout.addWidget(self.details_body)

        # Start hidden
        self.details.setMaximumHeight(0)
        self.details.hide()

        self.root_layout.addWidget(self.details)

    def _create_footer(self):
        """Create subtle footer with status info."""
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(
            get_spacing("lg"), get_spacing("sm"), get_spacing("lg"), get_spacing("md")
        )

        status_text = QLabel("Real-time monitoring • Wayland compatible")
        status_text.setObjectName("footer")

        footer_layout.addWidget(status_text)
        footer_layout.addStretch()

        interval_text = QLabel(f"Updates every {UPDATE_INTERVAL_MS//1000}s")
        interval_text.setObjectName("footer")

        footer_layout.addWidget(interval_text)
        self.root_layout.addLayout(footer_layout)

    def _setup_animations(self):
        """Setup entrance and interaction animations."""
        # Entrance animation
        self.entrance_anim = QPropertyAnimation(self, b"geometry")
        self.entrance_anim.setDuration(AnimationManager.DURATIONS["moderate"])
        self.entrance_anim.setEasingCurve(AnimationManager.EASING["decelerate"])

        # Opacity animation
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(AnimationManager.DURATIONS["fast"])
        self.opacity_anim.setEasingCurve(AnimationManager.EASING["standard"])

        # Details panel animation
        self.details_anim = QPropertyAnimation(self.details, b"maximumHeight")
        self.details_anim.setDuration(AnimationManager.DURATIONS["moderate"])
        self.details_anim.setEasingCurve(AnimationManager.EASING["standard"])

    def _setup_loading_timer(self):
        """Setup initial loading completion timer."""
        self.loading_timer = QTimer()
        self.loading_timer.setSingleShot(True)
        self.loading_timer.timeout.connect(self._finish_initial_load)

    def _finish_initial_load(self):
        """Complete initial loading with staggered card animations."""
        self.is_loading = False

        # Stagger card loading completion
        cards = [self.card_cpu, self.card_ram, self.card_gpu, self.card_disk]
        for i, card in enumerate(cards):
            QTimer.singleShot(i * 100, lambda c=card: c.set_loading_state(False))

    def show_with_entrance_animation(self, screen):
        """Show window with professional entrance animation."""
        # Start slightly smaller and fade in
        self.setWindowOpacity(0.0)

        original_geometry = self.geometry()
        small_scale = 0.95
        small_width = int(original_geometry.width() * small_scale)
        small_height = int(original_geometry.height() * small_scale)

        # Center the smaller window
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
        self.entrance_anim.setStartValue(small_geometry)
        self.entrance_anim.setEndValue(original_geometry)
        self.entrance_anim.start()

        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()

        # Start loading timer
        self.loading_timer.start(1000)

    def card_clicked(self, key: str):
        """Handle card click events."""
        try:
            # Get detailed info for the clicked card
            details = self._get_detailed_info(key)

            # Update details panel
            card_titles = {
                "cpu": "CPU",
                "ram": "Memory",
                "gpu": "Graphics",
                "disk": "Storage",
            }
            self.details_title.setText(f"{card_titles.get(key, key.upper())} Details")
            self.details_body.setText(details)

            # Show details panel with animation
            if self.details.maximumHeight() == 0:
                self.details.show()
                self.details_anim.setStartValue(0)
                self.details_anim.setEndValue(120)
                self.details_anim.start()

        except Exception as e:
            print(f"Error handling card click: {e}")

    def _get_detailed_info(self, key: str) -> str:
        """Get detailed information for a specific metric."""
        try:
            if key == "cpu":
                cpu = get_cpu_info()
                lines = [f"Usage: {cpu.get('usage', 0):.1f}%"]
                if cpu.get("temp"):
                    lines.append(f"Temperature: {cpu['temp']}°C")
                lines.append(f"Cores: {cpu.get('cores', 'Unknown')}")
                return "\n".join(lines)

            elif key == "ram":
                ram = get_ram_info()
                return f"Used: {ram['used_gb']:.1f} GiB / {ram['total_gb']:.1f} GiB\nAvailable: {ram['available_gb']:.1f} GiB"

            elif key == "gpu":
                gpus = get_gpu_info()
                if not gpus:
                    return "No GPU information available"
                gpu = gpus[0]
                lines = [f"Device: {gpu.get('name', 'Unknown')}"]
                if gpu.get("util"):
                    lines.append(f"Utilization: {gpu['util']}%")
                if gpu.get("temp"):
                    lines.append(f"Temperature: {gpu['temp']}°C")
                if gpu.get("mem_used_gb") and gpu.get("mem_total_gb"):
                    lines.append(
                        f"Memory: {gpu['mem_used_gb']:.1f} / {gpu['mem_total_gb']:.1f} GiB"
                    )
                return "\n".join(lines)

            elif key == "disk":
                disks = get_disk_info()
                if not disks:
                    return "No disk information available"
                lines = []
                for disk in disks[:3]:  # Show top 3 disks
                    lines.append(
                        f"{disk['device']} ({disk['mount']}): {disk['percent']}%"
                    )
                return "\n".join(lines)

        except Exception as e:
            return f"Error loading details: {e}"

        return "No information available"

    def draw_sparkline(self, values, width=120, height=40):
        """Draw a simple sparkline visualization."""
        if len(values) < 2:
            return None

        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set pen for line
        pen = QPen(QColor(get_color("primary", "500")))
        pen.setWidth(2)
        painter.setPen(pen)

        # Calculate points
        max_val = max(values)
        min_val = min(values)
        val_range = max_val - min_val if max_val > min_val else 1

        points = []
        for i, val in enumerate(values):
            x = (i / (len(values) - 1)) * (width - 4) + 2
            y = height - 2 - ((val - min_val) / val_range) * (height - 4)
            points.append((x, y))

        # Draw lines
        for i in range(len(points) - 1):
            painter.drawLine(
                points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]
            )

        painter.end()
        return pixmap

    def close_application(self):
        """Close application with fade out animation."""
        # Prevent multiple close attempts
        if hasattr(self, "_closing") and self._closing:
            return
        self._closing = True

        # Start fade out animation
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)

        # Disconnect any previous connections to avoid multiple calls
        # Just connect without trying to disconnect to avoid warnings
        if not hasattr(self, '_opacity_connected'):
            self.opacity_anim.finished.connect(self._quit_application)
            self._opacity_connected = True
        self.opacity_anim.start()

        # Fallback timer in case animation fails
        QTimer.singleShot(300, self._quit_application)

    def _quit_application(self):
        """Actually quit the application."""
        # Stop any running timers first
        if self.app_instance and hasattr(self.app_instance, 'cleanup'):
            self.app_instance.cleanup()

        app = QCoreApplication.instance()
        if app:
            app.quit()
        else:
            import sys
            sys.exit(0)
