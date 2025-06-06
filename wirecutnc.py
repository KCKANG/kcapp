import tkinter as tk
from tkinter import filedialog, messagebox
import math
import os
from PIL import ImageGrab

COLOR_RAPID = "gray"
COLOR_CUT = "green"
COLOR_SAFE = "blue"
COLOR_ARC = "orange"

class GCodeViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NC Viewer")
        self.geometry("1200x700")

        self.gcode_lines = []
        self.parsed_lines = []

        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.text_frame = tk.Frame(self)
        self.text_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.open_button = tk.Button(self.text_frame, text="Open NC/G-code File", command=self.open_file)
        self.open_button.pack(pady=5)

        self.export_png_button = tk.Button(self.text_frame, text="Export PNG", command=self.export_png)
        self.export_png_button.pack(pady=5)

        self.export_pdf_button = tk.Button(self.text_frame, text="Export PDF", command=self.export_pdf)
        self.export_pdf_button.pack(pady=5)

        self.text_box = tk.Text(self.text_frame, width=50)
        self.text_box.pack(fill=tk.BOTH, expand=True)

        self.line_list = tk.Listbox(self.text_frame, width=50)
        self.line_list.pack(fill=tk.BOTH)

        self.scale = 5
        self.offset_x = 0
        self.offset_y = 0

        self.bind_events()

    def bind_events(self):
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<B1-Motion>", self.pan_start)
        self.canvas.bind("<ButtonRelease-1>", self.pan_end)

        self.last_pan = None

    def pan_start(self, event):
        self.last_pan = (event.x, event.y)

    def pan_end(self, event):
        if self.last_pan:
            dx = event.x - self.last_pan[0]
            dy = event.y - self.last_pan[1]
            self.offset_x += dx
            self.offset_y += dy
            self.last_pan = None
            self.redraw()

    def zoom(self, event):
        delta = 1.1 if event.delta > 0 else 0.9
        self.scale *= delta
        self.redraw()

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("G-code files", "*.nc *.gcode"), ("All files", "*.*")])
        if not filepath:
            return

        with open(filepath, "r") as f:
            self.gcode_lines = f.readlines()

        self.text_box.delete("1.0", tk.END)
        for line in self.gcode_lines:
            self.text_box.insert(tk.END, line)

        self.parse_gcode()
        self.redraw()

    def parse_gcode(self):
        self.parsed_lines = []
        x, y, z = 0, 0, 0
        for line in self.gcode_lines:
            parts = line.strip().split()
            if not parts:
                continue

            cmd = parts[0]
            args = {p[0]: float(p[1:]) for p in parts[1:] if len(p) > 1}

            new_x = args.get("X", x)
            new_y = args.get("Y", y)
            new_z = args.get("Z", z)

            if cmd in ("G0", "G1"):
                self.parsed_lines.append((cmd, x, y, z, new_x, new_y, new_z))
            elif cmd in ("G2", "G3"):
                i = args.get("I", 0)
                j = args.get("J", 0)
                r = args.get("R", None)
                self.parsed_lines.append((cmd, x, y, x + i, y + j, new_x, new_y, r))

            x, y, z = new_x, new_y, new_z

        self.line_list.delete(0, tk.END)
        for line in self.parsed_lines:
            if line[0] == "G1":
                self.line_list.insert(tk.END, f"G1 to ({line[4]:.2f}, {line[5]:.2f}, {line[6]:.2f})")

    def redraw(self):
        self.canvas.delete("all")
        for line in self.parsed_lines:
            if line[0] in ("G0", "G1"):
                _, x1, y1, z1, x2, y2, z2 = line
                color = COLOR_CUT if z2 < 0 else COLOR_SAFE if line[0] == "G1" else COLOR_RAPID
                self.draw_line(x1, y1, x2, y2, color)
            elif line[0] in ("G2", "G3"):
                self.draw_arc(*line)

    def draw_line(self, x1, y1, x2, y2, color):
        cx1, cy1 = self.to_canvas_coords(x1, y1)
        cx2, cy2 = self.to_canvas_coords(x2, y2)
        self.canvas.create_line(cx1, cy1, cx2, cy2, fill=color, width=2)

    def draw_arc(self, cmd, x1, y1, cx, cy, x2, y2, r):
        clockwise = cmd == "G2"
        if r is not None:
            cx, cy = self.center_from_radius(x1, y1, x2, y2, r, clockwise)

        radius = math.hypot(x1 - cx, y1 - cy)
        start_angle = math.atan2(y1 - cy, x1 - cx)
        end_angle = math.atan2(y2 - cy, x2 - cx)

        if clockwise:
            if end_angle >= start_angle:
                end_angle -= 2 * math.pi
        else:
            if end_angle <= start_angle:
                end_angle += 2 * math.pi

        segments = max(10, int(abs(end_angle - start_angle) * radius * self.scale / 5))

        prev_x, prev_y = x1, y1
        for step in range(1, segments + 1):
            angle = start_angle + (end_angle - start_angle) * step / segments
            nx = cx + radius * math.cos(angle)
            ny = cy + radius * math.sin(angle)
            self.draw_line(prev_x, prev_y, nx, ny, COLOR_ARC)
            prev_x, prev_y = nx, ny

    def center_from_radius(self, x1, y1, x2, y2, r, clockwise):
        dx = x2 - x1
        dy = y2 - y1
        chord_len = math.hypot(dx, dy)

        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        h = math.sqrt(abs(r**2 - (chord_len / 2)**2))
        ux = -dy / chord_len
        uy = dx / chord_len

        cx1 = mx + h * ux
        cy1 = my + h * uy
        cx2 = mx - h * ux
        cy2 = my - h * uy

        def cross_z(cx, cy):
            vx1 = x1 - cx
            vy1 = y1 - cy
            vx2 = x2 - cx
            vy2 = y2 - cy
            return vx1 * vy2 - vy1 * vx2

        if clockwise:
            return (cx1, cy1) if cross_z(cx1, cy1) < 0 else (cx2, cy2)
        else:
            return (cx1, cy1) if cross_z(cx1, cy1) > 0 else (cx2, cy2)

    def to_canvas_coords(self, x, y):
        canvas_height = self.canvas.winfo_height()
        cx = (x * self.scale) + self.offset_x + canvas_height / 2
        cy = canvas_height / 2 - (y * self.scale) + self.offset_y
        return cx, cy

    def export_png(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if not file_path:
                return
            self.update()
            x = self.canvas.winfo_rootx()
            y = self.canvas.winfo_rooty()
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            image = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            image.save(file_path)
            messagebox.showinfo("Saved", f"PNG saved: {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def export_pdf(self):
        try:
            from reportlab.pdfgen import canvas as pdf_canvas
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
            if not file_path:
                return
            ps_file = file_path + ".ps"
            self.canvas.postscript(file=ps_file, colormode='color')
            os.system(f"gs -sDEVICE=pdfwrite -o \"{file_path}\" \"{ps_file}\"")
            os.remove(ps_file)
            messagebox.showinfo("Saved", f"PDF saved: {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))


# 🔁 ✅ MAIN ENTRY POINT: this is required to show your window
if __name__ == "__main__":
    app = GCodeViewer()
    app.mainloop()
