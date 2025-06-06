import sys
import os
import shutil

import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
from datetime import datetime
import pytz
import time
import math
import threading
import ntplib
import ctypes
import win32con
import win32gui
from PIL import Image, ImageTk
import time
import requests


def load_config():
    # 1. Default settings as strings
    defaults = {
        "timezone": "Asia/Singapore",
        "window_width": "100",
        "window_height": "120",
        "background_color": "black",
        "foreground_color": "lime",
        # "transparent_color": "black",
        "opacity": "0.85",
        "follow_mouse": "True",
        "show_exit_button": "True",
        "digital_clock": "True",
        "font_name": "arial.ttf",
        "font_size": "10",
        "ntp_sync": "True",
        "ntp_server": "pool.ntp.org",
        "update_check_url": "https://yourdomain.com/romanclock/version.txt"
    }

    # 2. Where is config.txt?
    config_path = os.path.join(
        os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__),
        "config.txt"
    )

    # 3. Create config.txt with defaults if it doesn't exist
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            for k, v in defaults.items():
                f.write(f"{k}={v}\n")

    # 4. Load config values from file, overwrite defaults if present
    config = defaults.copy()
    with open(config_path, "r") as f:
        for line in f:
            line = line.strip()
            if '=' in line:
                key, val = line.split('=', 1)
                config[key.strip()] = val.strip()

    # 5. Convert string values to proper Python types
    config["follow_mouse"] = config["follow_mouse"].lower() == "true"
    config["show_exit_button"] = config["show_exit_button"].lower() == "true"
    config["digital_clock"] = config["digital_clock"].lower() == "true"
    config["ntp_sync"] = config["ntp_sync"].lower() == "true"
    config["opacity"] = float(config["opacity"])
    config["window_width"] = int(config["window_width"])
    config["window_height"] = int(config["window_height"])
    config["font_size"] = int(config["font_size"])

    # 6. Return the config dictionary ready to use
    return config

def check_for_updates():
    version_url = "https://yourdomain.com/romanclock/version.txt"
    latest_version = requests.get(version_url).text.strip()

    current_version = "1.0"  # Set your app version here

    if latest_version != current_version:
        print("Update available!")
        # Download new EXE from URL and replace or prompt user
        
startup_path = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
shortcut_path = os.path.join(startup_path, "RomanClock.lnk")
target = os.path.join(os.getcwd(), "rrtctw.exe")

import win32com.client
shell = win32com.client.Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(shortcut_path)
shortcut.Targetpath = target
shortcut.WorkingDirectory = os.getcwd()
shortcut.IconLocation = target
shortcut.save()

def show_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.geometry("400x300+500+300")  # Adjust as needed
    img = Image.open("splash.png")
    photo = ImageTk.PhotoImage(img)
    label = tk.Label(splash, image=photo)
    label.pack()
    splash.update()
    time.sleep(3)  # show for 3 seconds
    splash.destroy()

     # Call splash before your main clock code
    show_splash()

     # Then launch the actual app window


def load_timezone_from_config():
    default_timezone = "Asia/Singapore"
    config_path = os.path.join(
        os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__),
        "config.txt"
    )

    # Auto-create config.txt with default timezone if missing
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write(f"timezone={default_timezone}\n")

    # Read timezone from file
    with open(config_path, "r") as f:
        for line in f:
            if line.startswith("timezone="):
                return line.strip().split("=")[1]

    return default_timezone  # fallback if not found in file
   
   
class RomanClock:

    def __init__(self, root):
        self.timezone = pytz.timezone(load_timezone_from_config())
        # self.timezone = pytz.timezone("Asia/singapore")
        self.root = root
        self.root.title("Roman Clock")
        self.root.geometry("100x120")  # 100x100 clock + 20 for digital time
        self.root.configure(bg="black")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)  # no window border
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.wm_attributes("-alpha", 0.85)  # slight transparency
        self.root.resizable(False, False)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.canvas = tk.Canvas(root, width=100, height=100, bg="black", highlightthickness=0)
        self.canvas.pack()

        self.label = tk.Label(root, text="", fg="lime", bg="black", font=("Consolas", 14))
        self.label.pack()
        
   
        # Load font for Roman numerals - use a common font, adjust size for 100x100 clock
        try:
            self.font = ImageFont.truetype("arial.ttf", 10)
        except:
            self.font = ImageFont.load_default()

        # Hidden exit button (slightly visible)
        self.exit_btn = tk.Button(root, text="X", font=("Arial", 7), fg="red", bg="black",
                                  activebackground="darkred", relief="flat", command=self.root.destroy)
        self.exit_btn.place(x=2, y=2, width=10, height=10)

        # Follow mode: True = clock follows mouse; False = stops moving
        self.follow_mouse = True

        # Bind clicks globally
        root.bind("<Button-1>", self.on_click)
        # Bind Ctrl+Q to quit
        root.bind_all("<Control-q>", lambda e: self.root.destroy())

        # Start position tracking
        self.root.after(50, self.move_clock)

        # Get NTP offset once at start
        self.offset = self.get_ntp_offset()

        # Draw clock initially
        self.update_clock()

    def on_click(self, event):
        # Determine if click was inside canvas (clock face)
        widget = event.widget
        x, y = event.x, event.y

        if widget == self.canvas:
            # Clicked on clock canvas: stop following
            self.follow_mouse = False
        else:
            # Clicked anywhere else (window background, exit button, etc): resume following
            self.follow_mouse = True

    def move_clock(self):
        if self.follow_mouse:
            # Get current mouse position
            x, y = self.root.winfo_pointerxy()
            # Move window so clock center aligns with mouse
            new_x = x - 50
            new_y = y - 50
            self.root.geometry(f"+{new_x}+{new_y}")
        self.root.after(50, self.move_clock)

    def get_ntp_offset(self):
        try:
            client = ntplib.NTPClient()
            response = client.request('pool.ntp.org', version=3)
            return response.tx_time - time.time()
        except:
            return 0

    def draw_clock(self, hour, minute, second):
        image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))  # transparent background
        draw = ImageDraw.Draw(image)

        center = 50
        radius = 45
        roman = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]

        # Draw glowing Roman numerals
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x = center + radius * 0.8 * math.cos(angle)
            y = center + radius * 0.8 * math.sin(angle)

            # Glow effect: draw text multiple times offset with translucent green
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    draw.text((x - 8 + dx, y - 8 + dy), roman[i], font=self.font, fill=(0, 255, 0, 90))
            # Main text
            draw.text((x - 8, y - 8), roman[i], font=self.font, fill=(0, 255, 0, 255))

        def draw_hand(length, angle_deg, width, color):
            angle = math.radians(angle_deg - 90)
            x = center + length * math.cos(angle)
            y = center + length * math.sin(angle)
            draw.line((center, center, x, y), fill=color, width=width)

        # Hour hand glow
        for offset in [-1, 0, 1]:
            draw_hand(25, (hour % 12 + minute / 60) * 30 + offset, 4, (0, 255, 0, 120))
        draw_hand(25, (hour % 12 + minute / 60) * 30, 4, (0, 255, 0, 255))

        # Minute hand glow
        for offset in [-1, 0, 1]:
            draw_hand(35, minute * 6 + offset, 2, (0, 255, 255, 120))
        draw_hand(35, minute * 6, 2, (0, 255, 255, 255))

        # Second hand glow
        for offset in [-1, 0, 1]:
            draw_hand(40, second * 6 + offset, 1, (255, 0, 0, 120))
        draw_hand(40, second * 6, 1, (255, 0, 0, 255))

        return ImageTk.PhotoImage(image)

    def update_clock(self):
        now = datetime.now(pytz.utc).astimezone(self.timezone)
        hour, minute, second = now.hour, now.minute, now.second     
        # now = time.localtime(time.time() + self.offset)
        # hour, minute, second = now.tm_hour, now.tm_min, now.tm_sec

        photo = self.draw_clock(hour, minute, second)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo  # prevent garbage collection
         
        self.label.config(text=now.strftime("%H:%M:%S")) 
        # self.label.config(text=time.strftime("%H:%M:%S", now))
        
        self.root.after(1000, self.update_clock)

if __name__ == "__main__":
    root = tk.Tk()
    clock = RomanClock(root)
    config = load_config()
    print(config["timezone"])         # Asia/Singapore
    print(config["opacity"])          # 0.85 (float)
    print(config["follow_mouse"])     # True (bool)
    root.mainloop()
