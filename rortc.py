import tkinter as tk
import time
import math
import threading
import winsound
from PIL import Image, ImageDraw, ImageTk, ImageFont

class AnalogClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Roman RTC Clock")
        self.root.configure(bg="black")
        self.root.attributes('-topmost', True)  # Always on top

        self.canvas_size = 200
        self.center = self.canvas_size // 2
        self.radius = self.center - 10

        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg='black', highlightthickness=0)
        self.canvas.pack()

        self.digital_time = tk.Label(root, text="", fg="lime", bg="black", font=("Courier", 12))
        self.digital_time.pack()

        try:
            self.font = ImageFont.truetype("arial.ttf", 14)
        except:
            from PIL import ImageFont
            self.font = ImageFont.load_default()

        self.update_clock()
        self.start_ticking()

    def draw_clock(self, hour, minute, second):
        image = Image.new("RGB", (self.canvas_size, self.canvas_size), "black")
        draw = ImageDraw.Draw(image)

        # Glowing ring effect
        draw.ellipse((10, 10, self.canvas_size - 10, self.canvas_size - 10), outline="#00ff88", width=3)

        roman_numerals = {
            1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
            7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"
        }

        for i in range(1, 13):
            angle = math.radians(i * 30)
            x = self.center + (self.radius - 20) * math.sin(angle)
            y = self.center - (self.radius - 20) * math.cos(angle)
            mask = self.font.getmask(roman_numerals[i])
            w, h = mask.size         
            draw.text((x - w / 2, y - h / 2), roman_numerals[i], fill="white", font=self.font)

        # Angles
        hour_angle = (hour % 12 + minute / 60) * 30
        minute_angle = (minute + second / 60) * 6
        second_angle = second * 6

        self.draw_hand(draw, hour_angle, self.radius * 0.5, 4, "#00FF88")
        self.draw_hand(draw, minute_angle, self.radius * 0.75, 3, "#33FFAA")
        self.draw_hand(draw, second_angle, self.radius * 0.85, 1, "#FFFF00")

        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def draw_hand(self, draw, angle_deg, length, width, color):
        angle = math.radians(angle_deg)
        x = self.center + length * math.sin(angle)
        y = self.center - length * math.cos(angle)
        draw.line((self.center, self.center, x, y), fill=color, width=width)

    def update_clock(self):
        now = time.localtime()
        self.draw_clock(now.tm_hour, now.tm_min, now.tm_sec)
        self.digital_time.config(text=time.strftime("%I:%M:%S %p"))
        self.root.after(1000, self.update_clock)

    def start_ticking(self):
        def tick():
            while True:
                winsound.Beep(900, 30)
                time.sleep(1)
        threading.Thread(target=tick, daemon=True).start()

# Run the app
root = tk.Tk()
clock = AnalogClock(root)
root.mainloop()
