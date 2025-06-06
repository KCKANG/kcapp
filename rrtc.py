import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
import time
import math
import threading
import ntplib
import ctypes
import win32con
import win32gui

class RomanClock:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.wm_attributes("-topmost", 1)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.configure(bg="black")

        self.clock_size = 300
        self.center = self.clock_size // 2
        self.canvas = tk.Canvas(root, width=self.clock_size, height=self.clock_size, bg="black", highlightthickness=0)
        self.canvas.pack()

        self.label = tk.Label(root, text="", fg="lime", bg="black", font=("Consolas", 16))
        self.label.pack()

        self.slider = tk.Scale(root, from_=30, to=255, orient=tk.HORIZONTAL, label="Transparency", 
                               fg="lime", bg="black", troughcolor="gray", highlightthickness=0,
                               command=self.adjust_alpha)
        self.slider.set(200)
        self.slider.pack()

        self.font = ImageFont.truetype("arial.ttf", 18)
        self.offset = self.get_ntp_offset()
        self.alpha = 200

        hwnd = ctypes.windll.user32.GetForegroundWindow()
        self.hwnd = hwnd
        self.make_window_layered(hwnd, self.alpha)

        self.update_clock()
        self.follow_mouse()

    def get_ntp_offset(self):
        try:
            client = ntplib.NTPClient()
            response = client.request('pool.ntp.org')
            return response.tx_time - time.time()
        except:
            return 0

    def make_window_layered(self, hwnd, alpha):
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               styles | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, alpha, win32con.LWA_ALPHA)

    def adjust_alpha(self, val):
        self.alpha = int(val)
        self.make_window_layered(self.hwnd, self.alpha)

    def draw_clock(self, hour, minute, second):
        image = Image.new("RGBA", (self.clock_size, self.clock_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        radius = self.center - 10
        roman = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]

        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x = self.center + radius * 0.8 * math.cos(angle)
            y = self.center + radius * 0.8 * math.sin(angle)
            text = roman[i]
            bbox = draw.textbbox((0, 0), text, font=self.font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

            # Draw glow effect
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        draw.text((x - w/2 + dx, y - h/2 + dy), text, font=self.font, fill="cyan")
            draw.text((x - w/2, y - h/2), text, font=self.font, fill="white")

        def draw_hand(length, angle_deg, width, color):
            angle = math.radians(angle_deg - 90)
            x = self.center + length * math.cos(angle)
            y = self.center + length * math.sin(angle)
            draw.line((self.center, self.center, x, y), fill=color, width=width)

        draw_hand(60, (hour % 12 + minute / 60) * 30, 6, "lime")   # Hour
        draw_hand(90, minute * 6, 4, "cyan")                       # Minute
        draw_hand(110, second * 6, 2, "red")                       # Second

        return ImageTk.PhotoImage(image)

    def update_clock(self):
        now = time.localtime(time.time() + self.offset)
        hour, minute, second = now.tm_hour, now.tm_min, now.tm_sec
        photo = self.draw_clock(hour, minute, second)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo

        self.label.config(text=time.strftime("%H:%M:%S", now))
        self.root.after(1000, self.update_clock)

    def follow_mouse(self):
        x, y = self.root.winfo_pointerxy()
        self.root.geometry(f"+{x}+{y}")
        self.root.after(200, self.follow_mouse)

if __name__ == "__main__":
    root = tk.Tk()
    app = RomanClock(root)
    root.mainloop()
