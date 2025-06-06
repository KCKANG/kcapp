import tkinter as tk
from tkinter import filedialog
import math

class GCodeViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("G-code Viewer")
        self.geometry("1000x700")

        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.bind_events()

        self.scale = 10  # Zoom scale
        self.offset_x = 0
        self.offset_y = 0
        self.gcode = []
        self.z = 0
        self.prev = (0, 0)

        # Menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("G-code Files", "*.nc *.gcode")])
        if path:
            with open(path, 'r') as f:
                self.gcode = f.readlines()
            self.z = 0
            self.prev = (0, 0)
            self.canvas.delete("all")
            self.after(100, self.draw_gcode)

    def draw_gcode(self):
        for line in self.gcode:
            self.parse_line(line.strip())

    def parse_line(self, line):
        if line.startswith('(') or line == '':
            return
        tokens = line.split()
        cmd = tokens[0]
        x = y = z = None
        i = j = r = None
        for token in tokens[1:]:
            if token.startswith('X'):
                x = float(token[1:])
            elif token.startswith('Y'):
                y = float(token[1:])
            elif token.startswith('Z'):
                z = float(token[1:])
            elif token.startswith('I'):
                i = float(token[1:])
            elif token.startswith('J'):
                j = float(token[1:])
            elif token.startswith('R'):
                r = float(token[1:])

        if z is not None:
            self.z = z

        if cmd == 'G0' or cmd == 'G1':
            self.draw_line(x, y)
        elif cmd == 'G2' or cmd == 'G3':
            self.draw_arc(x, y, i, j, cmd)

    def to_canvas_coords(self, x, y):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        cx = (x * self.scale) + self.offset_x + width / 2
        cy = height / 2 - (y * self.scale) + self.offset_y
        return cx, cy

    def draw_line(self, x2, y2):
        x1, y1 = self.prev
        if x2 is None or y2 is None:
            return
        color = "green" if self.z < 0 else "gray"
        cx1, cy1 = self.to_canvas_coords(x1, y1)
        cx2, cy2 = self.to_canvas_coords(x2, y2)
        self.canvas.create_line(cx1, cy1, cx2, cy2, fill=color, width=2)
        self.prev = (x2, y2)

    def draw_arc(self, x, y, i, j, cmd):
        x1, y1 = self.prev
        x2, y2 = x, y
        if x2 is None or y2 is None or i is None or j is None:
            return
        cx = x1 + i
        cy = y1 + j
        radius = math.hypot(i, j)
        steps = 30
        angle_start = math.atan2(y1 - cy, x1 - cx)
        angle_end = math.atan2(y2 - cy, x2 - cx)

        if cmd == 'G2' and angle_end > angle_start:
            angle_end -= 2 * math.pi
        if cmd == 'G3' and angle_end < angle_start:
            angle_end += 2 * math.pi

        points = []
        for s in range(steps + 1):
            t = angle_start + (angle_end - angle_start) * s / steps
            px = cx + radius * math.cos(t)
            py = cy + radius * math.sin(t)
            points.append(self.to_canvas_coords(px, py))

        for i in range(len(points) - 1):
            self.canvas.create_line(*points[i], *points[i + 1], fill="cyan", width=2)
        self.prev = (x2, y2)

    def on_mouse_down(self, event):
        self.last_mouse = (event.x, event.y)

    def on_mouse_drag(self, event):
        dx = event.x - self.last_mouse[0]
        dy = event.y - self.last_mouse[1]
        self.offset_x += dx
        self.offset_y += dy
        self.last_mouse = (event.x, event.y)
        self.canvas.delete("all")
        self.draw_gcode()

    def on_mouse_wheel(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale *= factor
        self.canvas.delete("all")
        self.draw_gcode()

if __name__ == "__main__":
    app = GCodeViewer()
    app.mainloop()
