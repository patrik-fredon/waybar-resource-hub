<!--
	███████╗██████╗ ███████╗██████╗  ██████╗  ██████╗ ███╗   ██╗██████╗ ██╗   ██╗███████╗
	██╔════╝██╔══██╗██╔════╝██╔══██╗██╔═══██╗██╔═══██╗████╗  ██║██╔══██╗██║   ██║██╔════╝
	█████╗  ██████╔╝█████╗  ██████╔╝██║   ██║██║   ██║██╔██╗ ██║██║  ██║██║   ██║███████╗
	██╔══╝  ██╔══██╗██╔══╝  ██╔══██╗██║   ██║██║   ██║██║╚██╗██║██║  ██║██║   ██║╚════██║
	███████╗██║  ██║███████╗██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝╚██████╔╝███████║
	╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚══════╝

	@2025 [FredonBytes](https://fredonbytes.cloud) - "Et in tenebris codicem inveni lucem"
	Developed by [Fredon](https://me.fredonbytes.cloud)
	Where code meets innovation

	Waybar on-click integration
	---------------------------

	To launch the native `pytfredon-hw` GUI popup when the Crispy-Goggles module is clicked, set the module's `on-click` to run the provided launcher script:

	```jsonc
	"on-click": "/home/fredon/github/waybar-resource-hub/crispy-goggles/launch_pytfredon_gui.sh"
	```

	Make sure the launcher is executable (chmod +x launch_pytfredon_gui.sh) and that `PySide6` is installed for the GUI.
-->

# 🚀 Waybar Hardware Info Module (crispy-goggles)

![License](https://img.shields.io/github/license/patrik-fredon/crispy-goggles)
![Stars](https://img.shields.io/github/stars/patrik-fredon/crispy-goggles?style=social)
![Last Commit](https://img.shields.io/github/last-commit/patrik-fredon/crispy-goggles)

---

> **crispy-goggles**: Because your Linux desktop deserves more than just numbers.

Welcome to the _Waybar Hardware Info Module_ — a project crafted by a real developer (yes, a human, not a bot) who loves clean code, sharp UIs, and a dash of wit. If you want your Waybar to show off your CPU, RAM, GPU, and disk stats in real time (and look good doing it), you’re in the right place.

---

## ⭐ Why crispy-goggles?

- **Instant Hardware Monitoring:** Get live CPU, RAM, temperature, and device stats right in your Waybar. No more guessing what’s cooking under the hood.
- **Ridiculously Easy Install:** One command. One script. Done. (Because your time is valuable.)
- **Customizable & Stylish:** Includes CSS and JSONC snippets so you can make it yours. Minimalist? Maximalist? You do you.
- **Open Source, MIT, and Proud:** Fork it, star it, break it, fix it. It’s your playground.
- **Built for Linux, Tuned for Waybar:** No hacks, no workarounds. Just smooth integration.

---

## 🚦 Quick Start

1. **Clone the repo:**

   ```sh
   git clone https://github.com/patrik-fredon/crispy-goggles.git
   cd crispy-goggles
   ```

2. **Run the installer:**

   ```sh
   fish install_waybar_hwinfo_module.fish
   ```

3. **Plug into Waybar:**

   Copy the config from `waybar_config_snippet.jsonc` into your Waybar config.

4. **Style it up:**

   Drop in `waybar_hwinfo_style.css` for a modern, clean look.

---

## 📦 Features

- Real-time CPU, RAM, GPU, and disk stats
- Plug-and-play with Waybar
- Customizable output and styling
- Minimal resource usage
- Easy updates and maintenance
- Written by a real developer (Fredon) who actually uses it

---

## 🏷️ SEO & Discoverability

**Keywords:** waybar, hardware info, linux status bar, system monitor, cpu temperature, memory usage, open source, python, desktop customization, linux tools, real-time monitoring, waybar module, system stats, lightweight, plug-and-play

---

## 📚 Documentation

- [Installation Guide](#-quick-start)
- [Configuration Example](waybar_config_snippet.jsonc)
- [Styling Example](waybar_hwinfo_style.css)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## � License

MIT License. See [LICENSE](LICENSE) for details.

---

## ⭐ Star This Project

If you find this module useful, please star the repo to help others discover it!
