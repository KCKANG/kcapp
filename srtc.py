import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
import time
import math
import winsound
import threading
import ntplib
import ctypes
import win32con
import win32gui

class RomanClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Roman Clock")
        self.root.geometry("150x180")
        self.root.configure(bg="black")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=90, height=90, bg="black", highlightthickness=0)
        self.canvas.pack()

        self.label = tk.Label(root, text="", fg="lime", bg="black", font=("Consolas", 12))
        self.label.pack()

        self.sound_on = True
        self.toggle_btn = tk.Button(root, text="Sound ON", command=self.toggle_sound, bg="gray20", fg="lime")
        self.toggle_btn.pack(pady=2)

        self.alpha_slider = tk.Scale(root, from_=30, to=255, orient=tk.HORIZONTAL, label="Transparency",
                                      fg="lime", bg="black", troughcolor="gray", highlightthickness=0,
                                     command=self.adjust_alpha)
        self.alpha_slider.set(255)  # Default fully opaque
        self.alpha_slider.pack(pady=2)
        



        # Load font for Roman numerals
        self.font = ImageFont.truetype("arial.ttf", 10)

        # Make window click-through
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        self.make_click_through(hwnd)

        # Sync time
        self.offset = self.get_ntp_offset()

        self.update_clock()

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        self.toggle_btn.config(text="Sound ON" if self.sound_on else "Sound OFF")
        
    def adjust_alpha(self, val):
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        alpha = int(val)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, alpha, win32con.LWA_ALPHA)
         
  
  
  
    def get_ntp_offset(self):
        try:
            client = ntplib.NTPClient()
            response = client.request('pool.ntp.org')
            return response.tx_time - time.time()
        except:
            return 0

    def make_click_through(self, hwnd):
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

    def draw_clock(self, hour, minute, second):
        image = Image.new("RGB", (100, 100), "black")
        draw = ImageDraw.Draw(image)

        center = 50
        radius = 45
        roman = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]

        # Draw numerals
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x = center + radius * 0.8 * math.cos(angle)
            y = center + radius * 0.8 * math.sin(angle)
            bbox = draw.textbbox((0, 0), roman[i], font=self.font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((x - w/2, y - h/2), roman[i], font=self.font, fill="white")

        def draw_hand(length, angle_deg, width, color):
            angle = math.radians(angle_deg - 90)
            x = center + length * math.cos(angle)
            y = center + length * math.sin(angle)
            draw.line((center, center, x, y), fill=color, width=width)

        draw_hand(40, (hour % 12 + minute / 60) * 30, 4, "lime")     # Hour hand
        draw_hand(60, minute * 6, 2, "cyan")                          # Minute hand
        draw_hand(70, second * 6, 1, "red")                           # Second hand

        return ImageTk.PhotoImage(image)

    def update_clock(self):
        now = time.localtime(time.time() + self.offset)
        hour, minute, second = now.tm_hour, now.tm_min, now.tm_sec

        photo = self.draw_clock(hour, minute, second)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo  # Prevent garbage collection

        self.label.config(text=time.strftime("%H:%M:%S", now))

        if self.sound_on:
            threading.Thread(target=lambda: winsound.Beep(1000, 50)).start()



        self.root.after(1000, self.update_clock)
        
   

if __name__ == "__main__":
    root = tk.Tk()
    clock = RomanClock(root)
    root.mainloop()
