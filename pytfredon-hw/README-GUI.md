pytfredon-hw GUI wrapper

This repository ships a small PySide6-based GUI that can be launched from Waybar.

Usage

1. Install optional GUI dependency:

   python -m pip install -r requirements.txt

2. Example Waybar module `on-click` configuration (in your Crispy-Goggles Waybar module):

   {
   "on-click": "python3 /home/fredon/github/waybar-resource-hub/pytfredon-hw/gui.py &"
   }

Notes

- The GUI will center on the primary screen and close when the X button is pressed or when you click outside the popup area.
- PySide6 is optional; if not installed, run the existing web server frontend as before.
