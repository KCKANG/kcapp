import tkinter as tk
import time
import configparser

class RomanClock:
    def __init__(self, root, config):
        self.root = root
        self.config = config

        # Set up window
        self.root.geometry(f"{config['window_width']}x{config['window_height']}")
        self.root.configure(bg=config["background_color"])
        self.root.overrideredirect(True)  # Remove title bar

        # Optional digital clock label
        if config["digital_clock"]:
            self.label = tk.Label(root, text="", fg=config["foreground_color"],
                                  bg=config["background_color"],
                                  font=("Consolas", config["font_size"]))
            self.label.pack()
        else:
            self.label = None

        # Mouse-follow toggle
        self.follow_mouse = config["follow_mouse"]
        self.root.bind("<Button-1>", self.toggle_follow_mouse)

        # Exit button if enabled
        if config["show_exit_button"]:
            self.exit_button = tk.Button(root, text="X", command=self.root.destroy)
            self.exit_button.place(x=5, y=5)
        else:
            self.exit_button = None

        self.update_clock()

    def update_clock(self):
        if self.label:
            current_time = time.strftime("%H:%M:%S")
            self.label.config(text=current_time)

        if self.follow_mouse:
            x, y = self.root.winfo_pointerxy()
            self.root.geometry(f"+{x}+{y}")

        self.root.after(1000, self.update_clock)

    def toggle_follow_mouse(self, event):
        self.follow_mouse = not self.follow_mouse


# -------- Main App Entry Point --------
if __name__ == "__main__":
    # Load configuration from config.ini
    config_ini = configparser.ConfigParser()
    config_ini.read("config.ini")

    config = {
        "window_width": config_ini.getint("Window", "width", fallback=300),
        "window_height": config_ini.getint("Window", "height", fallback=300),
        "digital_clock": config_ini.getboolean("Clock", "digital_clock", fallback=True),
        "foreground_color": config_ini.get("Clock", "foreground_color", fallback="white"),
        "background_color": config_ini.get("Clock", "background_color", fallback="black"),
        "font_size": config_ini.getint("Clock", "font_size", fallback=20),
        "follow_mouse": config_ini.getboolean("Clock", "follow_mouse", fallback=False),
        "show_exit_button": config_ini.getboolean("Clock", "show_exit_button", fallback=True)
    }

    root = tk.Tk()
    clock = RomanClock(root, config)
    root.mainloop()
