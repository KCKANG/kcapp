import tkinter as tk
import time
import math
from PIL import Image, ImageDraw, ImageTk, ImageFont

class AnalogClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini RTC Roman Clock")

        self.canvas_size = 200  # ~20cm on-screen
        self.center = self.canvas_size // 2
        self.radius = self.center - 10

        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg='black', highlightthickness=0)
        self.canvas.pack()

        self.font = ImageFont.truetype("arial.ttf", 10)  # You can replace with a different font if needed

        self.update_clock()

    def draw_clock(self, hour, minute, second):
        image = Image.new("RGB", (self.canvas_size, self.canvas_size), "black")
        draw = ImageDraw.Draw(image)

        # Roman numeral labels
        roman_numerals = {
            1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
            7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"
        }

        for i in range(1, 13):
            angle = math.radians(i * 30)
            x = self.center + (self.radius - 20) * math.sin(angle)
            y = self.center - (self.radius - 20) * math.cos(angle)
            bbox = self.font.getbbox(roman_numerals[i])
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text((x - w / 2, y - h / 2), roman_numerals[i], fill="white", font=self.font)

        # Calculate angles
        hour_angle = (hour % 12 + minute / 60) * 30
        minute_angle = (minute + second / 60) * 6
        second_angle = second * 6

        # Draw clock hands with fluorescent colors
        self.draw_hand(draw, hour_angle, self.radius * 0.5, 4, "#00FF88")    # Greenish
        self.draw_hand(draw, minute_angle, self.radius * 0.75, 3, "#33FFAA")  # Light green
        self.draw_hand(draw, second_angle, self.radius * 0.85, 1, "#FFFF00")  # Yellow

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
        self.root.after(1000, self.update_clock)

# Start the clock
root = tk.Tk()
root.configure(bg="black")
clock = AnalogClock(root)
root.mainloop()
