#!/usr/bin/env python3
#
#  ███████╗██████╗ ███████╗██████╗  ██████╗  ██████╗ ███╗   ██╗██████╗ ██╗   ██╗███████╗
#  ██╔════╝██╔══██╗██╔════╝██╔══██╗██╔═══██╗██╔═══██╗████╗  ██║██╔══██╗██║   ██║██╔════╝
#  █████╗  ██████╔╝█████╗  ██████╔╝██║   ██║██║   ██║██╔██╗ ██║██║  ██║██║   ██║███████╗
#  ██╔══╝  ██╔══██╗██╔══╝  ██╔══██╗██║   ██║██║   ██║██║╚██╗██║██║  ██║██║   ██║╚════██║
#  ███████╗██║  ██║███████╗██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝╚██████╔╝███████║
#  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚══════╝
#
#  @2025 FredonBytes (https://fredonbytes.cloud)
#  "Et in tenebris codicem inveni lucem"
#  Developed by Fredon (https://me.fredonbytes.cloud)
#
#  Where code meets innovation
#

"""
Waybar Hardware Info Module — For Hyprland, Arch, and all Linux tinkerers

This script is your backstage pass to live CPU, RAM, GPU (if you’ve got one), and disk stats, all piped straight to Waybar in JSON. No bloat, no nonsense — just the numbers you care about.

Dependencies:
    - psutil (core stats)
    - pynvml (NVIDIA GPU, optional)
    - pyamdgpuinfo (AMD GPU, optional)
    - smartie (disk model/serial, optional)

Install with:
        pip install psutil
        # For NVIDIA: pip install pynvml
        # For AMD: pip install pyamdgpuinfo
        # For disk info: pip install smartie

Written by Fredon — because your desktop deserves a little more swagger.
"""

import json
import time
import psutil
import logging
import subprocess
import os
import sys

# --- Optional imports: If you don’t have a GPU, don’t sweat it ---
try:
    import pynvml

    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False
    pynvml = None

try:
    import pyamdgpuinfo

    AMDGPU_AVAILABLE = pyamdgpuinfo.is_available()
except ImportError:
    AMDGPU_AVAILABLE = False
    pyamdgpuinfo = None

try:
    import smartie

    SMARTIE_AVAILABLE = True
except ImportError:
    SMARTIE_AVAILABLE = False
    smartie = None


# --- Config ---
UPDATE_INTERVAL = 2  # How often to update (seconds)
USE_FAHRENHEIT = False  # Set True if you like your temps American-style
# ----------------

# Logging: If something goes sideways, you’ll know
logging.basicConfig(
    level=logging.WARNING,
    stream=sys.stderr,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_cpu_info():
    """Get CPU usage and temp. Because you want to know if it’s melting."""
    cpu_percent = psutil.cpu_percent(interval=0.5)  # Short interval for responsiveness
    cpu_info = {"usage": cpu_percent, "temp": None}

    # Get CPU temperature
    try:
        temps = psutil.sensors_temperatures()
        # Common labels for CPU temperature
        for name, entries in temps.items():
            if name.lower() in ("coretemp", "k10temp", "acpi", "cpu_thermal"):
                # Usually, the first entry is the package temp or a core temp
                if entries:
                    cpu_info["temp"] = round(entries[0].current, 1)
                    if USE_FAHRENHEIT:
                        cpu_info["temp"] = round((cpu_info["temp"] * 9 / 5) + 32, 1)
                    break
    except (AttributeError, KeyError) as e:
        logger.debug(f"Could not get CPU temperature: {e}")

    return cpu_info


def get_ram_info():
    """Get RAM stats. How much is left for Chrome?"""
    ram = psutil.virtual_memory()
    ram_info = {
        "total_gb": round(ram.total / (1024**3), 2),
        "used_gb": round(ram.used / (1024**3), 2),
        "percent": ram.percent,
    }
    return ram_info


def get_gpu_info():
    """Get GPU stats (NVIDIA/AMD). If you have one, flex it."""
    gpus = []
    # Try NVIDIA first
    if NVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8")
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                util_info = pynvml.nvmlDeviceGetUtilizationRates(handle)
                temp_info = pynvml.nvmlDeviceGetTemperature(
                    handle, pynvml.NVML_TEMPERATURE_GPU
                )

                gpu = {
                    "name": name,
                    "mem_total_gb": round(mem_info.total / (1024**3), 2),
                    "mem_used_gb": round(mem_info.used / (1024**3), 2),
                    "mem_percent": (
                        round((mem_info.used / mem_info.total) * 100, 1)
                        if mem_info.total > 0
                        else 0
                    ),
                    "util_percent": util_info.gpu,
                    "temp": (
                        temp_info
                        if not USE_FAHRENHEIT
                        else round((temp_info * 9 / 5) + 32, 1)
                    ),
                }
                gpus.append(gpu)
            pynvml.nvmlShutdown()
        except Exception as e:
            logger.debug(f"Error getting NVIDIA GPU info: {e}")

    # Try AMD if NVIDIA not found or failed

    if not gpus and AMDGPU_AVAILABLE and pyamdgpuinfo is not None:
        try:
            # pyamdgpuinfo.get_gpu_count() returns the number of AMD GPUs
            device_count = (
                pyamdgpuinfo.detect_gpus()
                if hasattr(pyamdgpuinfo, "detect_gpus")
                else pyamdgpuinfo.get_gpu_count()
            )
            for i in range(device_count):
                try:
                    name = pyamdgpuinfo.get_gpu_name(i)
                except Exception:
                    name = "AMD GPU"
                try:
                    vram_total = pyamdgpuinfo.get_vram_size(i)
                    vram_used = pyamdgpuinfo.get_vram_usage(i)
                    mem_percent = (
                        round((vram_used / vram_total) * 100, 1)
                        if vram_total > 0
                        else 0
                    )
                except Exception:
                    vram_total, vram_used, mem_percent = 0, 0, 0
                try:
                    util_percent = pyamdgpuinfo.get_gpu_load(i)
                except Exception:
                    util_percent = 0
                try:
                    temp = pyamdgpuinfo.get_temp(i)
                    if USE_FAHRENHEIT:
                        temp = round((temp * 9 / 5) + 32, 1)
                except Exception:
                    temp = None

                gpu_info = {
                    "name": name,
                    "mem_total_gb": (
                        round(vram_total / (1024**3), 2) if vram_total else 0
                    ),
                    "mem_used_gb": round(vram_used / (1024**3), 2) if vram_used else 0,
                    "mem_percent": mem_percent,
                    "util_percent": (
                        round(util_percent * 100, 1)
                        if isinstance(util_percent, float)
                        else util_percent
                    ),
                    "temp": temp,
                }
                gpus.append(gpu_info)
        except Exception as e:
            logger.debug(f"Error getting AMD GPU info: {e}")

    return gpus


def get_disk_model_serial_smartie(disk_name):
    """Try to get disk model/serial with smartie. May need root. YMMV."""
    model, serial = "Unknown", "Unknown"
    if not SMARTIE_AVAILABLE:
        return model, serial
    try:
        # smartie expects the full path like /dev/sda
        device_path = f"/dev/{disk_name}"
        if os.path.exists(device_path) and smartie is not None:
            d = smartie.SCSI(device_path)
            # Attempt to open, might require permissions
            try:
                d.open()
                model = (
                    d.inquiry().product_identification.decode("utf-8").strip()
                    or "Unknown"
                )
                # Serial can be tricky, try different pages or methods
                # This is a basic attempt, might need refinement
                serial = "Check SMART"  # smartie.get_smart_info might be needed, but it's complex
                d.close()
            except Exception as e:
                logger.debug(f"smartie failed to open {device_path}: {e}")
                # Fallback to sysfs if smartie fails to open
                return get_disk_model_serial_sysfs(disk_name)
        else:
            logger.debug(
                f"Device path {device_path} does not exist for smartie or smartie not available."
            )
    except Exception as e:
        logger.debug(f"Error using smartie for {disk_name}: {e}")
    return model, serial


def get_disk_model_serial_sysfs(disk_name):
    """Get disk model/serial from /sys/block/. Works on most Linux setups."""
    model_path = f"/sys/block/{disk_name}/device/model"
    serial_path = f"/sys/block/{disk_name}/device/serial"
    model, serial = "Unknown", "Unknown"

    try:
        if os.path.exists(model_path):
            with open(model_path, "r") as f:
                model = f.read().strip() or "Unknown"
    except Exception as e:
        logger.debug(f"Error reading model for {disk_name}: {e}")

    try:
        if os.path.exists(serial_path):
            with open(serial_path, "r") as f:
                serial = f.read().strip() or "Unknown"
    except Exception as e:
        logger.debug(f"Error reading serial for {disk_name}: {e}")

    return model, serial


def get_disk_info():
    """Get info for all mounted disks. Because full disks = sad days."""
    disks = []
    partitions = psutil.disk_partitions(all=False)  # Only get mounted partitions

    for partition in partitions:
        if partition.fstype in (
            "ext4",
            "ext3",
            "ext2",
            "xfs",
            "btrfs",
            "ntfs",
            "vfat",
            "zfs",
        ):
            usage = psutil.disk_usage(partition.mountpoint)
            # Get the underlying disk name (e.g., sda, nvme0n1)
            # This is a bit heuristic, might need refinement for complex setups
            disk_name = ""
            if "nvme" in partition.device:
                # /dev/nvme0n1p1 -> nvme0n1
                disk_name = partition.device.split("/")[-1].split("p", 1)[0]
            elif "sd" in partition.device:
                # /dev/sda1 -> sda
                disk_name = partition.device.split("/")[-1][
                    :-1
                ]  # Remove last char (partition number)
            else:
                # Generic fallback, might not work perfectly
                disk_name = partition.device.split("/")[-1]
                if disk_name and disk_name[-1].isdigit():
                    # Try to remove trailing digits for potential disk name
                    disk_name = "".join([c for c in disk_name if not c.isdigit()])

            # Get model and serial
            model, serial = get_disk_model_serial_sysfs(disk_name)  # Prefer sysfs
            if model == "Unknown" and SMARTIE_AVAILABLE:
                model, serial = get_disk_model_serial_smartie(
                    disk_name
                )  # Fallback to smartie

            disk = {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent": (
                    round((usage.used / usage.total) * 100, 1) if usage.total > 0 else 0
                ),
                "disk_name": disk_name,
                "model": model,
                "serial": serial,
            }
            disks.append(disk)
    return disks


def format_tooltip(cpu, ram, gpus, disks):
    """Builds a pretty tooltip for Waybar. Show off your stats in style."""
    tooltip_parts = ["<b>System Info</b>"]

    # CPU
    cpu_str = f"CPU: {cpu['usage']:.1f}%"
    if cpu["temp"] is not None:
        unit = "°F" if USE_FAHRENHEIT else "°C"
        cpu_str += f" ({cpu['temp']}{unit})"
    tooltip_parts.append(cpu_str)

    # RAM
    tooltip_parts.append(
        f"RAM: {ram['used_gb']:.2f}G / {ram['total_gb']:.2f}G ({ram['percent']:.1f}%)"
    )

    # GPU
    if gpus:
        tooltip_parts.append("<b>GPUs:</b>")
        for i, gpu in enumerate(gpus):
            gpu_str = f"  {gpu['name']}: Util {gpu['util_percent']:.1f}%, Mem {gpu['mem_used_gb']:.2f}G/{gpu['mem_total_gb']:.2f}G ({gpu['mem_percent']:.1f}%)"
            if gpu["temp"] is not None:
                unit = "°F" if USE_FAHRENHEIT else "°C"
                gpu_str += f" ({gpu['temp']}{unit})"
            tooltip_parts.append(gpu_str)
    else:
        tooltip_parts.append("GPU: Not Detected")

    # Disks
    if disks:
        tooltip_parts.append("<b>Disks:</b>")
        for disk in disks:
            tooltip_parts.append(
                f"  {disk['device']} ({disk['model']}) [{disk['serial']}]: {disk['used_gb']:.2f}G/{disk['total_gb']:.2f}G ({disk['percent']:.1f}%) free: {disk['free_gb']:.2f}G"
            )
    else:
        tooltip_parts.append("Disks: No data")

    return "\n".join(tooltip_parts)


def format_bar_text(cpu, ram, gpus, disks):
    """Short, sweet, and to the point — for the Waybar text field."""
    # Example: CPU:45% RAM:60% GPU:70% [Disk1:20%]
    parts = []
    parts.append(f"CPU:{cpu['usage']:.0f}%")
    parts.append(f"RAM:{ram['percent']:.0f}%")
    if gpus:
        # Show first GPU's utilization or memory usage
        primary_gpu = gpus[0]
        gpu_usage = primary_gpu.get("util_percent", primary_gpu.get("mem_percent", 0))
        parts.append(f"GPU:{gpu_usage:.0f}%")

    # Show disk usage summary (e.g., lowest free space or average usage)
    if disks:
        # Simple approach: show usage of first disk or worst case
        primary_disk = disks[0]
        parts.append(f"D:{primary_disk['percent']:.0f}%")

    return " | ".join(parts)


def main():
    """Main loop: fetch, print, repeat. Waybar reads, you enjoy."""
    while True:
        try:
            cpu_data = get_cpu_info()
            ram_data = get_ram_info()
            gpu_data = get_gpu_info()
            disk_data = get_disk_info()

            bar_text = format_bar_text(cpu_data, ram_data, gpu_data, disk_data)
            tooltip_text = format_tooltip(cpu_data, ram_data, gpu_data, disk_data)

            output = {
                "text": bar_text,
                "tooltip": tooltip_text,
                # "class": "hw-info-module", # Optional CSS class
                # "percentage": cpu_data['usage'] # Optional for progress bars
            }

            print(json.dumps(output, ensure_ascii=False))
            sys.stdout.flush()  # Ensure immediate output

        except Exception as e:
            logger.error(f"An error occurred in the main loop: {e}")
            # Output a simple error message to Waybar
            print(json.dumps({"text": "HW Err", "tooltip": f"Error: {e}"}))
            sys.stdout.flush()

        time.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
