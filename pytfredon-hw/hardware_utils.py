#!/usr/bin/env python3
"""Hardware monitoring utilities for PyTfredon Hardware Monitor."""
from __future__ import annotations

from typing import Optional
import psutil

# Configuration
UPDATE_INTERVAL_MS = 2000
HISTORY_MAX = 30
HISTORY: dict[str, list[float]] = {"cpu": [], "ram": [], "gpu": [], "disk": []}


def get_cpu_info() -> dict[str, Optional[float]]:
    """Get CPU usage and temperature information."""
    usage = psutil.cpu_percent(interval=0.05)
    temp: Optional[float] = None
    cores = psutil.cpu_count(logical=False)

    try:
        temps = psutil.sensors_temperatures()
        for sensor_name, sensors in temps.items():
            if (
                sensor_name.lower() in ("coretemp", "k10temp", "cpu_thermal", "acpi")
                and sensors
            ):
                temp = round(sensors[0].current, 1)
                break
    except Exception:
        pass

    return {"usage": usage, "temp": temp, "cores": cores}


def get_ram_info() -> dict[str, float]:
    """Get memory usage information."""
    vm = psutil.virtual_memory()
    return {
        "used_gb": round(vm.used / (1024**3), 2),
        "total_gb": round(vm.total / (1024**3), 2),
        "available_gb": round(vm.available / (1024**3), 2),
        "percent": float(vm.percent),
    }


def get_gpu_info() -> list[dict[str, float | str | None]]:
    """Get GPU information from available sources."""
    gpus: list[dict[str, float | str | None]] = []

    # Try NVIDIA first
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

    # Try AMD
    try:
        import pyamdgpuinfo as amdgpu  # type: ignore

        cnt = getattr(amdgpu, "detect_gpus", lambda: 0)()
        for i in range(int(cnt)):
            name = getattr(amdgpu, "get_gpu_name", lambda _i: "AMD GPU")(i)
            util = float(getattr(amdgpu, "get_gpu_load", lambda _i: 0)(i))
            temp = getattr(amdgpu, "get_temp", lambda _i: None)(i)
            temp = float(temp) if temp is not None else None

            gpus.append(
                {
                    "name": str(name),
                    "util": util,
                    "temp": temp,
                    "mem_used_gb": None,
                    "mem_total_gb": None,
                }
            )
    except Exception:
        pass

    return gpus


def get_disk_info() -> list[dict[str, float | str]]:
    """Get disk usage information."""
    disks: list[dict[str, float | str]] = []

    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append(
                {
                    "device": partition.device,
                    "mount": partition.mountpoint,
                    "percent": round((usage.used / usage.total) * 100, 1),
                    "used_gb": round(usage.used / (1024**3), 1),
                    "total_gb": round(usage.total / (1024**3), 1),
                    "fstype": partition.fstype,
                }
            )
        except Exception:
            continue

    return disks


def update_history(key: str, value: float) -> None:
    """Update historical data for sparklines."""
    if key in HISTORY:
        HISTORY[key].append(value)
        HISTORY[key] = HISTORY[key][-HISTORY_MAX:]


def get_history(key: str) -> list[float]:
    """Get historical data for a metric."""
    return HISTORY.get(key, [])


def clear_history() -> None:
    """Clear all historical data."""
    for key in HISTORY:
        HISTORY[key].clear()
