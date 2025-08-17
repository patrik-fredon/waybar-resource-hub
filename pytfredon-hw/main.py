#!/usr/bin/env python3
"""Modern Hardware Monitor Application."""
from __future__ import annotations

import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QGuiApplication, QCursor
from PySide6.QtWidgets import QApplication

from app_window import HwPopup
from hardware_utils import (
    get_cpu_info,
    get_ram_info,
    get_gpu_info,
    get_disk_info,
    UPDATE_INTERVAL_MS,
    update_history,
    get_history,
)
from animation_manager import AnimationManager


class HardwareMonitorApp:
    """Main application class for the hardware monitor."""

    def __init__(self):
        """Initialize the application."""
        self._setup_qt_application()
        self._create_window()
        self._setup_update_timer()

    def _setup_qt_application(self):
        """Setup Qt application with proper attributes."""
        try:
            QGuiApplication.setAttribute(
                Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True
            )
        except Exception:
            pass

        self.app = QApplication(sys.argv)
        self.app.setApplicationName("PyTfredon Hardware Monitor")
        self.app.setApplicationDisplayName("Hardware Monitor")

        # Try to set Fusion style for better appearance
        try:
            self.app.setStyle("Fusion")
        except Exception:
            pass

    def _create_window(self):
        """Create and configure the main window."""
        self.window = HwPopup(app_instance=self)

        # Show window with entrance animation
        screen = QGuiApplication.screenAt(QCursor.pos()) or self.app.primaryScreen()
        self.window.show_with_entrance_animation(screen)

    def cleanup(self):
        """Cleanup resources before application exit."""
        if hasattr(self, 'update_timer') and self.update_timer:
            self.update_timer.stop()
            self.update_timer = None

    def _setup_update_timer(self):
        """Setup the periodic update timer."""
        self.update_timer = QTimer()
        self.update_timer.setInterval(UPDATE_INTERVAL_MS)
        self.update_timer.timeout.connect(self._update_hardware_stats)
        self.update_timer.start()

        # Initial update
        self._update_hardware_stats()

    def _update_hardware_stats(self):
        """Update all hardware statistics and UI."""
        try:
            # Gather system metrics
            cpu_data = get_cpu_info()
            ram_data = get_ram_info()
            gpu_data = get_gpu_info()
            disk_data = get_disk_info()

            # Update CPU card
            cpu_usage = float(cpu_data.get("usage", 0) or 0)
            self.window.card_cpu.update_value(f"{cpu_usage:.0f}%", cpu_usage)

            # Add temperature info if available
            cpu_temp = cpu_data.get("temp")
            if cpu_temp is not None:
                self.window.card_cpu.set_additional_info(f"Temperature: {cpu_temp}°C")
                # Set status based on temperature
                if cpu_temp < 80:
                    self.window.card_cpu.set_status("normal")
                elif cpu_temp < 90:
                    self.window.card_cpu.set_status("warning")
                else:
                    self.window.card_cpu.set_status("error")
            else:
                self.window.card_cpu.set_status("normal")

            # Update RAM card
            ram_percent = float(ram_data.get("percent", 0) or 0)
            self.window.card_ram.update_value(f"{ram_percent:.0f}%", ram_percent)

            ram_info = (
                f"Used: {ram_data['used_gb']:.1f} GiB / {ram_data['total_gb']:.1f} GiB"
            )
            self.window.card_ram.set_additional_info(ram_info)

            # Set status based on usage
            if ram_percent < 80:
                self.window.card_ram.set_status("normal")
            elif ram_percent < 90:
                self.window.card_ram.set_status("warning")
            else:
                self.window.card_ram.set_status("error")

            # Update GPU card
            gpu_util = 0.0
            gpu_info = "No GPU detected"

            if gpu_data:
                try:
                    gpu = gpu_data[0]  # Use first GPU
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

                    # Set status based on utilization
                    if gpu_util < 80:
                        self.window.card_gpu.set_status("normal")
                    elif gpu_util < 95:
                        self.window.card_gpu.set_status("warning")
                    else:
                        self.window.card_gpu.set_status("error")
                except (ValueError, TypeError):
                    gpu_util = 0.0
                    self.window.card_gpu.set_status("error")
            else:
                self.window.card_gpu.set_status("info")

            self.window.card_gpu.update_value(f"{gpu_util:.0f}%", gpu_util)
            self.window.card_gpu.set_additional_info(gpu_info)

            # Update Disk card
            disk_percent = 0.0
            disk_info = "No disks detected"

            if disk_data:
                disk = disk_data[0]  # Primary disk
                disk_percent = float(disk.get("percent", 0) or 0)
                disk_info = f"Device: {disk['device']}\nMount: {disk['mount']}"
                if len(disk_data) > 1:
                    disk_info += f"\n{len(disk_data)} storage devices total"

                # Set status based on usage
                if disk_percent < 80:
                    self.window.card_disk.set_status("normal")
                elif disk_percent < 90:
                    self.window.card_disk.set_status("warning")
                else:
                    self.window.card_disk.set_status("error")
            else:
                self.window.card_disk.set_status("info")

            self.window.card_disk.update_value(f"{disk_percent:.0f}%", disk_percent)
            self.window.card_disk.set_additional_info(disk_info)

            # Update history for sparklines
            update_history("cpu", cpu_usage)
            update_history("ram", ram_percent)
            update_history("gpu", gpu_util)
            update_history("disk", disk_percent)

            # Update sparklines
            self._update_sparklines()

        except Exception as e:
            print(f"Error updating hardware stats: {e}")
            self._handle_update_error()

    def _update_sparklines(self):
        """Update sparkline visualizations for all cards."""
        cards = {
            "cpu": self.window.card_cpu,
            "ram": self.window.card_ram,
            "gpu": self.window.card_gpu,
            "disk": self.window.card_disk,
        }

        for key, card in cards.items():
            history = get_history(key)
            if len(history) > 1:
                pixmap = self.window.draw_sparkline(history)
                if pixmap:
                    card.set_sparkline(pixmap)

    def _handle_update_error(self):
        """Handle errors during statistics update."""
        # Set error state for all cards
        cards = [
            self.window.card_cpu,
            self.window.card_ram,
            self.window.card_gpu,
            self.window.card_disk,
        ]

        for card in cards:
            card.set_status("error")
            card.update_value("Error", 0)
            card.set_additional_info("Failed to load hardware data")

    def run(self) -> int:
        """Run the application main loop."""
        try:
            return self.app.exec()
        except KeyboardInterrupt:
            return 0


def main() -> int:
    """Main entry point for the application."""
    app = HardwareMonitorApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
