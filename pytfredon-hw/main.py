#!/usr/bin/env python3


import psutil
import threading
import time
import os
from flask import Flask, jsonify, send_from_directory, render_template_string

import sys

# Flask app must be defined before route decorators
app = Flask(__name__, static_folder="static")
# hwinfo cache
hwinfo = {"cpu": {}, "ram": {}, "gpu": {}, "disk": {}, "gpus": [], "disks": []}


# Optional GPU libraries
try:
    import pynvml

    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

try:
    import pyamdgpuinfo

    AMDGPU_AVAILABLE = True
except ImportError:
    AMDGPU_AVAILABLE = False


@app.route("/api/exit", methods=["POST"])
def api_exit():
    os._exit(0)
    return "", 200


def get_cpu_info():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_temp = None
    sensors = {}
    try:
        temps = psutil.sensors_temperatures()
        for k, v in temps.items():
            sensors[k] = [
                {
                    "label": t.label,
                    "current": t.current,
                    "high": getattr(t, "high", None),
                }
                for t in v
            ]
        if "coretemp" in temps:
            cpu_temp = temps["coretemp"][0].current
        elif "k10temp" in temps:
            cpu_temp = temps["k10temp"][0].current
        elif "cpu_thermal" in temps:
            cpu_temp = temps["cpu_thermal"][0].current
    except Exception:
        pass
    cpu_model = "Unknown CPU"
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("model name"):
                    cpu_model = line.split(":")[1].strip()
                    break
    except Exception:
        pass
    # Provide a best-display metric and compact fields for frontend
    best_metric = None
    best_label = None
    # Prefer temperature if available, otherwise percent usage
    if cpu_temp is not None:
        best_metric = cpu_temp
        best_label = "Temp (°C)"
    else:
        best_metric = cpu_percent
        best_label = "Usage (%)"

    return {
        "main_metric": best_metric,
        "main_metric_label": best_label,
        "raw_usage": cpu_percent,
        "label_value": cpu_temp,
        "label_name": "Temp (°C)",
        "model": cpu_model,
        "sensors": sensors,
    }


def get_ram_info():
    ram = psutil.virtual_memory()
    ram_total_gb = round(ram.total / (1024**3), 2)
    ram_used_gb = round(ram.used / (1024**3), 2)
    ram_details = f"{int(ram_total_gb)}GB RAM"
    # RAM: prefer available/used as main readable metric if usage percent isn't meaningful
    main_metric = f"{ram_used_gb}GB / {ram_total_gb}GB"
    main_label = "Used / Total (GB)"
    return {
        "main_metric": main_metric,
        "main_metric_label": main_label,
        "raw_percent": ram.percent,
        "label_value": ram.percent,
        "label_name": "Usage (%)",
        "details": ram_details,
        "sensors": {},
    }


def get_gpu_info():
    gpus = []
    if NVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8")
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_util = util.gpu
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                mem_percent = (
                    (mem_info.used / mem_info.total) * 100 if mem_info.total > 0 else 0
                )
                temp = pynvml.nvmlDeviceGetTemperature(
                    handle, pynvml.NVML_TEMPERATURE_GPU
                )
                sensors = {}
                try:
                    sensors["fan_speed"] = pynvml.nvmlDeviceGetFanSpeed(handle)
                except Exception:
                    pass
                # Provide best metric (temp preferred) and compact fields
                best_metric = temp if temp is not None else gpu_util
                best_label = "Temp (°C)" if temp is not None else "Usage (%)"
                gpus.append(
                    {
                        "name": name,
                        "main_metric": best_metric,
                        "main_metric_label": best_label,
                        "raw_usage": gpu_util,
                        "label_value": temp,
                        "label_name": "Temp (°C)",
                        "sensors": sensors,
                    }
                )
            pynvml.nvmlShutdown()
        except Exception:
            pass
    elif AMDGPU_AVAILABLE:
        try:
            device_count = pyamdgpuinfo.detect_gpus()
            for i in range(device_count):
                gpu = pyamdgpuinfo.get_gpu(i)
                if gpu:
                    try:
                        name = gpu.query_name()
                    except Exception:
                        name = "AMD GPU"
                    try:
                        util = gpu.query_load() * 100
                    except Exception:
                        util = 0
                    try:
                        temp = gpu.query_temperature()
                    except Exception:
                        temp = None
                    sensors = {}
                    best_metric = temp if temp is not None else util
                    best_label = "Temp (°C)" if temp is not None else "Usage (%)"
                    gpus.append(
                        {
                            "name": name,
                            "main_metric": best_metric,
                            "main_metric_label": best_label,
                            "raw_usage": util,
                            "label_value": temp,
                            "label_name": "Temp (°C)",
                            "sensors": sensors,
                        }
                    )
        except Exception:
            pass
    return gpus


def get_disk_info():
    disks = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if partition.fstype and partition.mountpoint in ["/", "/home"]:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                percent = (usage.used / usage.total) * 100
                disk_model = "NVMe SSD" if "nvme" in partition.device else "SSD/HDD"
                sensors = {}
                # Provide free space as main, available/used as label
                disks.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "main_metric": round(usage.free / (1024**3), 2),
                        "main_metric_label": "Free (GB)",
                        "label_value": f"{round(usage.used / (1024**3), 2)}GB / {round(usage.total / (1024**3), 2)}GB",
                        "label_name": "Used / Total (GB)",
                        "model": disk_model,
                        "sensors": sensors,
                    }
                )
            except Exception:
                pass
    return disks


# --- Background Thread ---


def update_hwinfo():
    global hwinfo
    while True:
        cpu = get_cpu_info()
        ram = get_ram_info()
        gpus = get_gpu_info()
        disks = get_disk_info()
        # Use first GPU and root disk for summary
        gpu = gpus[0] if gpus else None
        disk = next(
            (d for d in disks if d["mountpoint"] == "/"), disks[0] if disks else None
        )
        hwinfo = {
            "cpu": cpu,
            "ram": ram,
            "gpu": gpu,
            "disk": disk,
            "gpus": gpus,
            "disks": disks,
        }
        time.sleep(10)


@app.route("/api/hwinfo")
def api_hwinfo():
    return jsonify(hwinfo)


@app.route("/")
def index():
    # Serve the main HTML page
    return render_template_string(
        """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hardware Monitor</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <button id="layout-toggle">Toggle Layout</button>
    <div class="container">
        <div class="header">
            <h1>System Hardware Monitor</h1>
            <p>Real-time performance metrics, modern UI, pop-up details, grid/list toggle</p>
        </div>
        <div class="stats"></div>
        <div class="footer">
            <p>Hardware Monitor • Updated every 10 seconds • Low Resource Usage</p>
        </div>
    </div>
    <div class="modal" id="modal" onclick="if(event.target===this)closeModal()">
        <div class="modal-content" id="modal-content">
            <button class="close-modal" onclick="closeModal()">&times;</button>
        </div>
    </div>
    <script src="/static/app.js"></script>
</body>
</html>
"""
    )


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == "__main__":
    t = threading.Thread(target=update_hwinfo, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=8000, debug=True)
