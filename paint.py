#!/usr/bin/env python3
import io
import os
import subprocess
import tempfile
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk


class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PaintMacOS")
        self.root.geometry("1100x750")
        self.root.minsize(700, 500)

        self.brush_color = "#000000"
        self.brush_size = 8
        self.drawing = False
        self.last_x = None
        self.last_y = None

        toolbar = tk.Frame(root, padx=8, pady=8)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="Цвет", command=self.choose_color).pack(side=tk.LEFT, padx=3)
        tk.Button(toolbar, text="Импорт", command=self.import_image).pack(side=tk.LEFT, padx=3)
        tk.Button(toolbar, text="Экспорт", command=self.export_image).pack(side=tk.LEFT, padx=3)
        tk.Button(toolbar, text="Очистить", command=self.clear_canvas).pack(side=tk.LEFT, padx=3)
        tk.Button(toolbar, text="Копировать", command=self.copy_canvas).pack(side=tk.LEFT, padx=3)

        tk.Label(toolbar, text="Размер:").pack(side=tk.LEFT, padx=(18, 3))
        self.size_var = tk.IntVar(value=8)
        self.size_scale = tk.Scale(
            toolbar, from_=1, to=80, orient=tk.HORIZONTAL,
            variable=self.size_var, command=self.set_brush_size,
            length=180, showvalue=True
        )
        self.size_scale.pack(side=tk.LEFT)

        self.color_preview = tk.Label(
            toolbar, bg=self.brush_color, width=3, relief=tk.SUNKEN
        )
        self.color_preview.pack(side=tk.RIGHT, padx=5)

        frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.canvas = tk.Canvas(frame, bg="white", cursor="crosshair",
                                highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

        self.image = None
        self.image_draw = None
        self.init_image()

    def init_image(self):
        self.root.update_idletasks()
        w = max(self.canvas.winfo_width(), 700)
        h = max(self.canvas.winfo_height(), 500)
        self.image = Image.new("RGB", (w, h), "white")
        self.image_draw = ImageDraw.Draw(self.image)

    def set_brush_size(self, value):
        self.brush_size = int(float(value))

    def choose_color(self):
        result = colorchooser.askcolor(
            color=self.brush_color, title="Цвет кисти"
        )
        if result and result[1]:
            self.brush_color = result[1]
            self.color_preview.config(bg=self.brush_color)

    def start_draw(self, event):
        self.drawing = True
        self.last_x, self.last_y = event.x, event.y
        r = self.brush_size / 2

        self.image_draw.ellipse(
            (event.x-r, event.y-r, event.x+r, event.y+r),
            fill=self.brush_color
        )
        self.canvas.create_oval(
            event.x-r, event.y-r, event.x+r, event.y+r,
            fill=self.brush_color, outline=self.brush_color
        )

    def draw(self, event):
        if not self.drawing:
            return

        x, y = event.x, event.y
        self.image_draw.line(
            (self.last_x, self.last_y, x, y),
            fill=self.brush_color,
            width=self.brush_size
        )
        r = self.brush_size / 2
        self.image_draw.ellipse(
            (x-r, y-r, x+r, y+r),
            fill=self.brush_color
        )

        self.canvas.create_line(
            self.last_x, self.last_y, x, y,
            fill=self.brush_color,
            width=self.brush_size,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND
        )

        self.last_x, self.last_y = x, y

    def stop_draw(self, _event):
        self.drawing = False
        self.last_x = None
        self.last_y = None

    def clear_canvas(self):
        self.canvas.delete("all")
        self.init_image()

    def import_image(self):
        path = filedialog.askopenfilename(
            title="Открыть изображение",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                ("Все файлы", "*.*")
            ]
        )
        if not path:
            return

        try:
            imported = Image.open(path).convert("RGB")
            self.root.update_idletasks()
            w = max(self.canvas.winfo_width(), 1)
            h = max(self.canvas.winfo_height(), 1)

            imported.thumbnail((w, h), Image.Resampling.LANCZOS)
            self.image = Image.new("RGB", (w, h), "white")
            x = (w - imported.width) // 2
            y = (h - imported.height) // 2
            self.image.paste(imported, (x, y))
            self.image_draw = ImageDraw.Draw(self.image)

            self.canvas.delete("all")
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, image=self.tk_image, anchor=tk.NW)
        except Exception as exc:
            messagebox.showerror("Ошибка импорта", str(exc))

    def export_image(self):
        path = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("BMP", "*.bmp"),
                ("WEBP", "*.webp")
            ]
        )
        if not path:
            return

        try:
            self.image.save(path)
        except Exception as exc:
            messagebox.showerror("Ошибка экспорта", str(exc))

    def copy_canvas(self):
        temp = None
        try:
            data = io.BytesIO()
            self.image.save(data, format="TIFF")
            data.close()

            with tempfile.NamedTemporaryFile(suffix=".tiff", delete=False) as f:
                temp = f.name
                self.image.save(f, format="TIFF")

            escaped = temp.replace("\\", "\\\\").replace('"', '\\"')
            script = (
                'use framework "AppKit"\n'
                'set img to current application\'s NSImage\'s '
                'alloc()\'s initWithContentsOfFile:"' + escaped + '"\n'
                'set pb to current application\'s NSPasteboard\'s '
                'generalPasteboard()\n'
                'pb\'s clearContents()\n'
                'pb\'s writeObjects:{img}\n'
            )
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip())

            messagebox.showinfo("Готово", "Холст скопирован в буфер обмена.")
        except Exception as exc:
            messagebox.showerror("Ошибка копирования", str(exc))
        finally:
            if temp:
                try:
                    os.unlink(temp)
                except OSError:
                    pass


if __name__ == "__main__":
    root = tk.Tk()
    PaintApp(root)
    root.mainloop()
