import tkinter as tk
import time
import math
from PIL import Image, ImageDraw, ImageTk

class AnalogClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Desktop RTC Analog Clock")
        self.canvas_size = 400
        self.center = self.canvas_size // 2
        self.radius = self.center - 20

        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg='white')
        self.canvas.pack()

        self.update_clock()

    def draw_clock(self, hour, minute, second):
        image = Image.new("RGB", (self.canvas_size, self.canvas_size), "white")
        draw = ImageDraw.Draw(image)

        # Draw clock face
        draw.ellipse((20, 20, self.canvas_size - 20, self.canvas_size - 20), outline="black", width=4)

        # Draw hour markers
        for i in range(12):
            angle = math.radians(i * 30)
            x1 = self.center + (self.radius - 20) * math.sin(angle)
            y1 = self.center - (self.radius - 20) * math.cos(angle)
            x2 = self.center + self.radius * math.sin(angle)
            y2 = self.center - self.radius * math.cos(angle)
            draw.line((x1, y1, x2, y2), fill="black", width=3)

        # Calculate angles
        hour_angle = (hour % 12 + minute / 60) * 30
        minute_angle = (minute + second / 60) * 6
        second_angle = second * 6

        # Draw hands
        self.draw_hand(draw, hour_angle, self.radius * 0.5, 6, "black")
        self.draw_hand(draw, minute_angle, self.radius * 0.7, 4, "blue")
        self.draw_hand(draw, second_angle, self.radius * 0.9, 2, "red")

        # Convert to Tkinter image
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

# Run the clock
root = tk.Tk()
clock = AnalogClock(root)
root.mainloop()