import math
import time
import pytz
import ntplib
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock as KivyClock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.resources import resource_find
from kivy.core.window import Window
from kivy.base import EventLoop
import io

CONFIG_FILE = "timezone.cfg"

ROMAN_NUMERALS = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V",
    6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X",
    11: "XI", 12: "XII"
}


def load_timezone_from_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            tz_name = f.read().strip()
        return tz_name if tz_name in pytz.all_timezones else "Asia/Kuala_Lumpur"
    except:
        return "Asia/Kuala_Lumpur"


class RomanClockWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image = KivyImage(size_hint=(None, None), size=(200, 200),
                               pos_hint={"center_x": 0.5, "center_y": 0.6})
        self.label = Label(text="", font_size='20sp', color=(0, 1, 0, 1),
                           pos_hint={"center_x": 0.5, "y": 0})

        self.add_widget(self.image)
        self.add_widget(self.label)

        self.timezone = pytz.timezone(load_timezone_from_config())
        self.offset = self.get_ntp_offset()
        KivyClock.schedule_interval(self.update_clock, 1)

    def get_ntp_offset(self):
        try:
            client = ntplib.NTPClient()
            response = client.request('pool.ntp.org', version=3)
            return response.tx_time - time.time()
        except:
            return 0

    def update_clock(self, dt):
        now = datetime.utcfromtimestamp(time.time() + self.offset)
        now = pytz.utc.localize(now).astimezone(self.timezone)

        pil_img = self.draw_clock(now.hour, now.minute, now.second)
        self.image.texture = self.pil_image_to_texture(pil_img)
        self.label.text = now.strftime("%H:%M:%S")

    def pil_image_to_texture(self, pil_img):
        pil_img = pil_img.convert("RGBA")
        data = pil_img.tobytes()
        texture = Texture.create(size=pil_img.size, colorfmt='rgba')
        texture.blit_buffer(data, colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        return texture

    def draw_clock(self, hour, minute, second):
        size = 200
        center = size // 2
        radius = size // 2 - 10

        img = Image.new("RGBA", (size, size), (0, 0, 0, 200))
        draw = ImageDraw.Draw(img)

        # Draw outer circle glow
        for i in range(8, 0, -1):
            draw.ellipse(
                [i, i, size - i, size - i],
                outline=(0, 255, 0, 20 + i * 10)
            )

        # Draw Roman numerals
        for h in range(1, 13):
            angle = math.radians((h / 12) * 360 - 90)
            x = center + math.cos(angle) * (radius - 25)
            y = center + math.sin(angle) * (radius - 25)
            numeral = ROMAN_NUMERALS[h]
         # font = ImageFont.truetype("arial.ttf", 16)
            font_path = resource_find("data/fonts/DejaVuSans.ttf")
            font = ImageFont.truetype(font_path, 16)
         # w, h_text = draw.textsize(numeral, font=font)
            bbox = draw.textbbox((0, 0), numeral, font=font)
            w, h_text = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((x - w / 2, y - h_text / 2), numeral, font=font, fill=(0, 255, 0))

        # Draw hands
        def draw_hand(angle_deg, length, width, color):
            angle_rad = math.radians(angle_deg - 90)
            x = center + length * math.cos(angle_rad)
            y = center + length * math.sin(angle_rad)
            draw.line((center, center, x, y), fill=color, width=width)

        second_angle = (second / 60) * 360
        minute_angle = (minute / 60) * 360 + (second / 60) * 6
        hour_angle = ((hour % 12) / 12) * 360 + (minute / 60) * 30

        draw_hand(hour_angle, radius * 0.5, 4, (0, 255, 0))
        draw_hand(minute_angle, radius * 0.75, 3, (0, 255, 0))
        draw_hand(second_angle, radius * 0.9, 1, (0, 255, 0))

        return img


class RomanClockApp(App):
    def build(self):
        Window.size = (200, 240)
        Window.clearcolor = (0, 0, 0, 0.8)  # Dark transparent background
        Window.borderless = True
        Window.top = 100
        Window.left = 100
        return RomanClockWidget()
      
        Window.bind(on_key_down=self.on_key_down)  # 👈 Bind keyboard
        # Your existing setup code...
        return self.root_widget  # or whatever your main widget is

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if key == 27:  # ESC key
            self.stop()
        return True


if __name__ == "__main__":
    RomanClockApp().run()
