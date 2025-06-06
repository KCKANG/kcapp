from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Line
from datetime import datetime
import pytz
import math

class RomanClockWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timezone = pytz.timezone("Asia/Singapore")
        Clock.schedule_interval(self.update, 1)

    def update(self, dt):
        self.canvas.clear()
        now = datetime.now(pytz.utc).astimezone(self.timezone)
        hour, minute, second = now.hour, now.minute, now.second

        with self.canvas:
            self.draw_clock(hour, minute, second)

    def draw_clock(self, hour, minute, second):
        center_x, center_y = self.center
        radius = min(self.width, self.height) / 2 - 10

        # Draw hour, minute, second hands
        def draw_hand(angle_deg, length_ratio, width, r, g, b):
            angle_rad = math.radians(angle_deg - 90)
            end_x = center_x + length_ratio * radius * math.cos(angle_rad)
            end_y = center_y + length_ratio * radius * math.sin(angle_rad)
            Color(r, g, b)
            Line(points=[center_x, center_y, end_x, end_y], width=width)

        draw_hand((hour % 12 + minute / 60) * 30, 0.5, 4, 0, 1, 0)   # Hour
        draw_hand(minute * 6, 0.7, 2, 0, 1, 1)                       # Minute
        draw_hand(second * 6, 0.9, 1, 1, 0, 0)                       # Second

class RomanClockApp(App):
    def build(self):
        return RomanClockWidget()

if __name__ == "__main__":
    RomanClockApp().run()
