import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from tkinter import ttk
import math
import re
import os

class GCodeViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NC/G-code Viewer")
        self.geometry("1200x700")
        self.configure(bg='gray')

        self.gcode_lines = []
        self.current_file = None

        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0

        self.code_bg = "white"
        self.draw_bg = "white"

        self.follow_cursor = False
        self.follow_key_held = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.crosshair = None

        self.create_widgets()

    def create_widgets(self):
        self.create_menu()

        self.main_frame = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left: NC Code Viewer
        self.code_frame = tk.Frame(self.main_frame)
        self.code_text = tk.Text(self.code_frame, wrap=tk.NONE, bg=self.code_bg)
        self.code_text.pack(fill=tk.BOTH, expand=True)
        self.code_text.config(state=tk.DISABLED)
        self.main_frame.add(self.code_frame, minsize=300)

        # Right: Drawing Canvas
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.draw_bg)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<KeyPress-Shift_L>", self.on_shift_press)
        self.canvas.bind("<KeyRelease-Shift_L>", self.on_shift_release)
        self.canvas.focus_set()
        self.main_frame.add(self.canvas_frame)

    def create_menu(self):
        menubar = tk.Menu(self)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.load_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save As", command=self.save_as_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Zoom In", command=lambda: self.adjust_zoom(1.2))
        viewmenu.add_command(label="Zoom Out", command=lambda: self.adjust_zoom(0.8))
        viewmenu.add_command(label="Zoom Fit", command=self.zoom_fit)
        viewmenu.add_checkbutton(label="Follow Cursor", command=self.toggle_follow_cursor)
        menubar.add_cascade(label="View", menu=viewmenu)

        colormenu = tk.Menu(menubar, tearoff=0)
        colormenu.add_command(label="Set Code Background", command=self.set_code_bg)
        colormenu.add_command(label="Set Drawing Background", command=self.set_draw_bg)
        menubar.add_cascade(label="Colors", menu=colormenu)

        self.config(menu=menubar)

    def toggle_follow_cursor(self):
        self.follow_cursor = not self.follow_cursor

    def set_code_bg(self):
        color = colorchooser.askcolor(title="Choose Code Background Color")[1]
        if color:
            self.code_text.config(bg=color)

    def set_draw_bg(self):
        color = colorchooser.askcolor(title="Choose Canvas Background Color")[1]
        if color:
            self.canvas.config(bg=color)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("G-code files", "*.nc *.gcode"), ("All files", "*.*")])
        if not file_path:
            return
        with open(file_path, 'r') as f:
            self.gcode_lines = f.readlines()
        self.current_file = file_path
        self.code_text.config(state=tk.NORMAL)
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert("1.0", ''.join(self.gcode_lines))
        self.code_text.config(state=tk.NORMAL)
        self.draw_gcode()
        self.zoom_fit()

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w') as f:
                f.write(self.code_text.get("1.0", tk.END))
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".nc")
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.code_text.get("1.0", tk.END))
            self.current_file = file_path

    def adjust_zoom(self, factor):
        self.zoom *= factor
        self.draw_gcode()

    def on_mousewheel(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.adjust_zoom(factor)

    def on_drag_start(self, event):
        self.last_drag_x = event.x
        self.last_drag_y = event.y

    def on_drag(self, event):
        dx = event.x - self.last_drag_x
        dy = event.y - self.last_drag_y
        self.pan_x += dx
        self.pan_y += dy
        self.last_drag_x = event.x
        self.last_drag_y = event.y
        self.draw_gcode()

    def on_shift_press(self, event):
        self.follow_key_held = True

    def on_shift_release(self, event):
        self.follow_key_held = False

    def on_mouse_move(self, event):
        self.mouse_x, self.mouse_y = event.x, event.y

        if self.follow_cursor and self.follow_key_held:
            minx, miny, maxx, maxy = self.get_bounds()
            cx = (minx + maxx) / 2
            cy = (miny + maxy) / 2
            target_x = event.x - self.zoom * cx
            target_y = event.y + self.zoom * cy
            self.pan_x += (target_x - self.pan_x) * 0.2
            self.pan_y += (target_y - self.pan_y) * 0.2
            self.draw_gcode()

        self.draw_crosshair(event.x, event.y)

    def draw_crosshair(self, x, y):
        self.canvas.delete("crosshair")
        self.canvas.create_line(x - 10, y, x + 10, y, fill='red', tags="crosshair")
        self.canvas.create_line(x, y - 10, x, y + 10, fill='red', tags="crosshair")

    def zoom_fit(self):
        if not self.gcode_lines:
            return
        minx, miny, maxx, maxy = self.get_bounds()
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w == 1 or canvas_h == 1:
            self.after(100, self.zoom_fit)
            return
        self.zoom = min(canvas_w / (maxx - minx + 1), canvas_h / (maxy - miny + 1)) * 0.9
        self.pan_x = canvas_w / 2 - self.zoom * (minx + maxx) / 2
        self.pan_y = canvas_h / 2 - self.zoom * (miny + maxy) / 2
        self.draw_gcode()

    def get_bounds(self):
        x, y = 0, 0
        minx = miny = float('inf')
        maxx = maxy = float('-inf')
        for line in self.gcode_lines:
            if line.startswith("G01") or line.startswith("G1") or line.startswith("G0") or line.startswith("G00"):
                coords = self.extract_coords(line)
                if 'X' in coords: x = coords['X']
                if 'Y' in coords: y = coords['Y']
                minx = min(minx, x)
                maxx = max(maxx, x)
                miny = min(miny, y)
                maxy = max(maxy, y)
        return minx, miny, maxx, maxy

    def extract_coords(self, line):
        coords = {}
        match = re.findall(r"([XYZIJR])([-+]?[0-9]*\.?[0-9]+)", line.upper())
        for axis, val in match:
            coords[axis] = float(val)
        return coords

    def draw_gcode(self):
        self.canvas.delete("all")
        x = y = 0
        for line in self.gcode_lines:
            cmd = line.strip().upper()
            coords = self.extract_coords(cmd)
            if cmd.startswith("G0") or cmd.startswith("G1"):
                x1, y1 = x, y
                x2 = coords.get('X', x)
                y2 = coords.get('Y', y)
                self.draw_line(x1, y1, x2, y2)
                x, y = x2, y2
            elif cmd.startswith("G2") or cmd.startswith("G3"):
                clockwise = cmd.startswith("G2")
                x1, y1 = x, y
                x2 = coords.get('X', x1)
                y2 = coords.get('Y', y1)
                if 'I' in coords and 'J' in coords:
                    cx = x1 + coords['I']
                    cy = y1 + coords['J']
                    self.draw_arc(x1, y1, x2, y2, cx, cy, clockwise)
                    x, y = x2, y2

    def draw_line(self, x1, y1, x2, y2):
        self.canvas.create_line(
            x1 * self.zoom + self.pan_x,
            -y1 * self.zoom + self.pan_y,
            x2 * self.zoom + self.pan_x,
            -y2 * self.zoom + self.pan_y,
            fill="blue",
            width=1.5
        )

    def draw_arc(self, x1, y1, x2, y2, cx, cy, clockwise):
        start_angle = math.atan2(y1 - cy, x1 - cx)
        end_angle = math.atan2(y2 - cy, x2 - cx)
        radius = math.hypot(x1 - cx, y1 - cy)

        if clockwise and end_angle > start_angle:
            end_angle -= 2 * math.pi
        elif not clockwise and end_angle < start_angle:
            end_angle += 2 * math.pi

        steps = max(10, int(abs(end_angle - start_angle) * radius))
        points = []
        for i in range(steps + 1):
            angle = start_angle + (end_angle - start_angle) * i / steps
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append((x, y))

        for i in range(len(points) - 1):
            self.draw_line(*points[i], *points[i + 1])

if __name__ == "__main__":
    app = GCodeViewer()
    app.mainloop()