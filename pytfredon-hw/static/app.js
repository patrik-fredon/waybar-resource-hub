// Modern, animated, and interactive hardware monitor frontend
// Fetches hardware info from backend and updates UI dynamically

let layout = localStorage.getItem("layout") || "grid";
// minimal history for sparklines (per component)
const history = { cpu: [], ram: [], gpu: [], disk: [] };
const HISTORY_MAX = 30; // small to keep memory low

function setLayout(newLayout) {
  layout = newLayout;
  localStorage.setItem("layout", layout);
  const stats = document.querySelector(".stats");
  if (layout === "list") {
    stats.classList.add("list");
  } else {
    stats.classList.remove("list");
  }
}

function showModal(component) {
  const modal = document.getElementById("modal");
  const content = document.getElementById("modal-content");
  let details = component.details || {};
  // Build a deduplicated table: skip main_metric, main_metric_label, label_value, label_name, and sensors (handled separately)
  let html = `<h2 style="margin-bottom:12px;">${component.icon} ${component.title} Details</h2>`;
  html += '<div class="modal-details">';
  html +=
    '<table class="ix-table ix-table-striped" style="width:100%;border-radius:8px;overflow:hidden;">';
  html += "<thead><tr><th>Sensor</th><th>Value</th></tr></thead><tbody>";
  // Add main metric and label as first rows (if present)
  if (
    details.main_metric_label !== undefined &&
    details.main_metric !== undefined
  ) {
    html += `<tr><td>${details.main_metric_label}</td><td>${details.main_metric}</td></tr>`;
  }
  if (
    details.label_name &&
    details.label_value !== undefined &&
    details.label_value !== null
  ) {
    html += `<tr><td>${details.label_name}</td><td>${details.label_value}</td></tr>`;
  }
  // Add other details, skipping already shown keys
  for (const [k, v] of Object.entries(details)) {
    if (
      [
        "main_metric",
        "main_metric_label",
        "label_value",
        "label_name",
        "sensors",
      ].includes(k)
    )
      continue;
    if (typeof v === "object" && v !== null) continue; // skip objects (sensors handled below)
    html += `<tr><td>${k.replace(/_/g, " ")}</td><td>${v}</td></tr>`;
  }
  // Add sensors table if present
  if (details.sensors && Object.keys(details.sensors).length > 0) {
    html += '<tr><td colspan="2"><b>Sensors</b></td></tr>';
    for (const [sensorType, sensorArr] of Object.entries(details.sensors)) {
      if (Array.isArray(sensorArr)) {
        sensorArr.forEach((sensor) => {
          let label = sensor.label || sensorType;
          let val =
            sensor.current !== undefined
              ? sensor.current
              : JSON.stringify(sensor);
          html += `<tr><td>${label}</td><td>${val}</td></tr>`;
        });
      } else if (typeof sensorArr === "object") {
        for (const [label, val] of Object.entries(sensorArr)) {
          html += `<tr><td>${label}</td><td>${val}</td></tr>`;
        }
      }
    }
  }
  html += "</tbody></table>";
  html += "</div>";
  // Add sparkline canvas and buttons
  html += '<div style="position:relative;margin-top:10px;">';
  html +=
    '<canvas id="sparkline" width="320" height="60" style="width:100%;height:60px;border-radius:8px;display:block;background:transparent"></canvas>';
  html +=
    '<button class="close-modal" onclick="closeModal()" title="Close">&times;</button>';
  html +=
    '<button class="exit-modal" onclick="exitApp()" title="Exit" style="position:absolute;top:18px;left:22px;font-size:1.1rem;color:#ff6b6b;background:none;border:none;cursor:pointer;">&#x2716;</button>';
  html += "</div>";
  content.innerHTML = html;
  modal.style.display = "flex";
  // draw sparkline using available history
  try {
    const key = component.key;
    const data = history[key] || [];
    const canvas = document.getElementById("sparkline");
    if (canvas && data.length > 0) {
      const ctx = canvas.getContext("2d");
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      ctx.lineWidth = 2;
      ctx.strokeStyle = "#4facfe";
      ctx.beginPath();
      const max = Math.max(...data);
      const min = Math.min(...data);
      const range = max - min || 1;
      data.forEach((v, i) => {
        const x = (i / (data.length - 1 || 1)) * w;
        const y = h - ((v - min) / range) * h;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    }
  } catch (e) {
    /* silent */
  }
}

// Exit app: send request to backend to kill server, then close window
function exitApp() {
  fetch("/api/exit", { method: "POST" }).then(() => {
    window.close();
    setTimeout(() => {
      window.location.href = "about:blank";
    }, 500);
  });
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("layout-toggle").addEventListener("click", () => {
    setLayout(layout === "grid" ? "list" : "grid");
  });
  setLayout(layout);
  fetchAndUpdate();
});

function fetchAndUpdate() {
  // implement simple backoff
  let backoff = 10000; // start 10s
  function attempt() {
    fetch("/api/hwinfo")
      .then((r) => {
        if (!r.ok) throw new Error("bad");
        return r.json();
      })
      .then((data) => {
        updateStats(data);
        backoff = 10000; // reset
        setTimeout(attempt, backoff);
      })
      .catch(() => {
        // exponential backoff capped at 2 minutes
        backoff = Math.min(backoff * 1.8, 120000);
        setTimeout(attempt, backoff);
      });
  }
  attempt();
}

function updateStats(data) {
  const stats = document.querySelector(".stats");
  stats.innerHTML = "";
  const components = [
    {
      key: "cpu",
      icon: "🖥️",
      title: "CPU",
      value:
        data.cpu.main_metric !== undefined
          ? `${data.cpu.main_metric} ${data.cpu.main_metric_label}`
          : `Usage: ${data.cpu.raw_usage}%`,
      label:
        data.cpu.label_value !== null && data.cpu.label_value !== undefined
          ? `${data.cpu.label_name}: ${data.cpu.label_value}`
          : "",
      detail: data.cpu.model,
      progress: typeof data.cpu.raw_usage === "number" ? data.cpu.raw_usage : 0,
      details: data.cpu,
    },
    {
      key: "ram",
      icon: "💾",
      title: "RAM",
      value: data.ram.main_metric
        ? `${data.ram.main_metric}`
        : `${data.ram.raw_percent}%`,
      label: data.ram.label_value
        ? `${data.ram.label_name}: ${data.ram.label_value}`
        : "",
      detail: data.ram.details,
      progress:
        typeof data.ram.raw_percent === "number" ? data.ram.raw_percent : 0,
      details: data.ram,
    },
    {
      key: "gpu",
      icon: "🎮",
      title: "GPU",
      value: data.gpu
        ? `${data.gpu.main_metric} ${data.gpu.main_metric_label}`
        : "N/A",
      label:
        data.gpu &&
        data.gpu.label_value !== null &&
        data.gpu.label_value !== undefined
          ? `${data.gpu.label_name}: ${data.gpu.label_value}`
          : "",
      detail: data.gpu ? data.gpu.name : "No GPU Detected",
      progress:
        data.gpu && typeof data.gpu.raw_usage === "number"
          ? data.gpu.raw_usage
          : 0,
      details: data.gpu || {},
    },
    {
      key: "disk",
      icon: "💿",
      title: "Storage",
      value:
        data.disk && data.disk.main_metric !== undefined
          ? `${data.disk.main_metric} ${data.disk.main_metric_label}`
          : "N/A",
      label: data.disk.label_value
        ? `${data.disk.label_name}: ${data.disk.label_value}`
        : "",
      detail: data.disk.model || "",
      progress:
        typeof data.disk.main_metric === "number" ? data.disk.main_metric : 0,
      details: data.disk,
    },
  ];
  components.forEach((component) => {
    const card = document.createElement("div");
    card.className = `stat-card ${component.key}`;
    card.innerHTML = `
      <div class="icon">${component.icon}</div>
      <h2 class="stat-title">${component.title}</h2>
      <div class="stat-value">${component.value}</div>
      <div class="stat-detail">${component.detail}</div>
      <div class="temp-indicator temp-normal">${component.label}</div>
      <div class="progress-container">
        <div class="progress-bar" style="width: ${component.progress.toFixed(
          1
        )}%"></div>
      </div>
    `;
    card.onclick = () => showModal(component);
    stats.appendChild(card);
    // push numeric value into history if possible
    try {
      const key = component.key;
      const numeric =
        typeof component.progress === "number"
          ? component.progress
          : parseFloat(component.progress) || 0;
      history[key] = history[key] || [];
      history[key].push(numeric);
      if (history[key].length > HISTORY_MAX) history[key].shift();
    } catch (e) {
      /* noop */
    }
  });
}

function getTempClass(temp, component) {
  if (temp === null || temp === undefined) return "temp-normal";
  if (component === "cpu") {
    if (temp < 60) return "temp-normal";
    if (temp < 80) return "temp-warning";
    return "temp-critical";
  }
  if (component === "gpu") {
    if (temp < 70) return "temp-normal";
    if (temp < 85) return "temp-warning";
    return "temp-critical";
  }
  return "temp-normal";
}
