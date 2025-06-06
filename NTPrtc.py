import ctypes
import win32con
import win32gui
from tkinter import *

def make_window_click_through(hwnd):
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

root = Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.wm_attributes("-transparentcolor", "black")

# Get the window handle and apply click-through
hwnd = ctypes.windll.user32.GetForegroundWindow()
make_window_click_through(hwnd)
