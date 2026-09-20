#!/usr/bin/env python3
"""Simple Paint-like drawing app for macOS using Tkinter + Pillow."""

from __future__ import annotations

import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from pathlib import Path
from typing import Optional

from PIL import Image, ImageTk, ImageDraw, ImageGrab


class PaintApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PaintMacOS")
        self.root.geometry("1100x750")
        self.root.minsize(700, 500)

        self.bg_color = "white"
        self.brush_color = "#000000"
        self.brush_size = 8
        self.last_x: Optional[int] = None
        self.last_y: Optional[int] = None
        self.drawing = False

        self.image = Image.new("RGB", (1000, 650), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)

        self._build_ui()
        self._resize_canvas_image()

    def _build_ui(self) -> None:
        toolbar = tk.Frame(self.root, padx=8, pady=8)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="🎨 Цвет", command=self.choose_color).pack(side=tk.LEFT, padx=4)
        tk.Button(toolbar, text="🖼 Импорт", command=self.import_image).pack(side=tk.LEFT, padx=4)
        tk.Button(toolbar, text="💾 Экспорт", command=self.export_image).pack(side=tk.LEFT, padx=4)
        tk.Button(toolbar, text="🗑 Очистить", command=self.clear_canvas).pack(side=tk.LEFT, padx=4)
        tk.Button(toolbar, text="📋 Копировать", command=self.copy_canvas).pack(side=tk.LEFT, padx=4)

        tk.Label(toolbar, text="Размер:").pack(side=tk.LEFT, padx=(20, 4))
        self.size_var = tk.IntVar(value=self.brush_size)
        size_scale = tk.Scale(
            toolbar,
            from_=1,
            to=80,
            orient=tk.HORIZONTAL,
            variable=self.size_var,
            command=self._set_brush_size,
            showvalue=True,
            length=180,
        )
        size_scale.pack(side=tk.LEFT)

        self.color_preview = tk.Label(
            toolbar,
            text="  ",
            bg=self.brush_color,
            relief=tk.SUNKEN,
            width=3,
        )
        self.color_preview.pack(side=tk.RIGHT, padx=8)

        canvas_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.canvas = tk.Canvas(canvas_frame, bg=self.bg_color, cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self._start_draw)
        self.canvas.bind("<B1-Motion>", self._draw)
        self.canvas.bind("<ButtonRelease-1>", self._stop_draw)
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, _event: tk.Event) -> None:
        self._resize_canvas_image()

    def _resize_canvas_image(self) -> None:
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)

        # Keep the actual image at the canvas size so exported files contain
        # exactly what the user sees.
        if self.image.size != (width, height):
            new_image = Image.new("RGB", (width, height), self.bg_color)
            copy = self.image.copy()
            copy.thumbnail((width, height))
            new_image.paste(copy, (0, 0))
            self.image = new_image
            self.draw = ImageDraw.Draw(self.image)

        self._refresh_canvas()

    def _refresh_canvas(self) -> None:
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_image, anchor=tk.NW)

    def _set_brush_size(self, value: str) -> None:
        self.brush_size = max(1, int(float(value)))

    def choose_color(self) -> None:
        color = colorchooser.askcolor(color=self.brush_color, title="Выберите цвет кисти")
        if color and color[1]:
            self.brush_color = color[1]
            self.color_preview.configure(bg=self.brush_color)

    def _start_draw(self, event: tk.Event) -> None:
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
        radius = self.brush_size / 2
        self.draw.ellipse(
            (event.x - radius, event.y - radius, event.x + radius, event.y + radius),
            fill=self.brush_color,
        )
        self._refresh_canvas()

    def _draw(self, event: tk.Event) -> None:
        if not self.drawing or self.last_x is None or self.last_y is None:
            return

        self.draw.line(
            (self.last_x, self.last_y, event.x, event.y),
            fill=self.brush_color,
            width=self.brush_size,
        )
        radius = self.brush_size / 2
        self.draw.ellipse(
            (event.x - radius, event.y - radius, event.x + radius, event.y + radius),
            fill=self.brush_color,
        )

        self.last_x = event.x
        self.last_y = event.y
        self._refresh_canvas()

    def _stop_draw(self, _event: tk.Event) -> None:
        self.drawing = False
        self.last_x = None
        self.last_y = None

    def clear_canvas(self) -> None:
        self.image = Image.new("RGB", self.image.size, self.bg_color)
        self.draw = ImageDraw.Draw(self.image)
        self._refresh_canvas()

    def import_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Открыть изображение",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                ("Все файлы", "*.*"),
            ],
        )
        if not path:
            return

        try:
            imported = Image.open(path).convert("RGB")
            canvas_size = self.image.size
            imported.thumbnail(canvas_size)
            new_image = Image.new("RGB", canvas_size, self.bg_color)
            x = (canvas_size[0] - imported.width) // 2
            y = (canvas_size[1] - imported.height) // 2
            new_image.paste(imported, (x, y))
            self.image = new_image
            self.draw = ImageDraw.Draw(self.image)
            self._refresh_canvas()
        except Exception as exc:
            messagebox.showerror("Ошибка импорта", f"Не удалось открыть изображение:\n{exc}")

    def export_image(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("BMP", "*.bmp"),
                ("WEBP", "*.webp"),
            ],
        )
        if not path:
            return

        try:
            image = self.image
            suffix = Path(path).suffix.lower()
            if suffix in {".jpg", ".jpeg"}:
                image = image.convert("RGB")
            image.save(path)
            messagebox.showinfo("Готово", f"Изображение сохранено:\n{path}")
        except Exception as exc:
            messagebox.showerror("Ошибка экспорта", f"Не удалось сохранить изображение:\n{exc}")

    def copy_canvas(self) -> None:
        try:
            # Tkinter has no portable native image clipboard API on macOS.
            # Use macOS's pbcopy via a temporary TIFF representation.
            import subprocess
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".tiff", delete=False) as temp:
                temp_path = temp.name

            try:
                self.image.save(temp_path, format="TIFF")
                script = f'''
                    set imageFile to POSIX file "{temp_path}"
                    set theImage to read imageFile as «class TIFF»
                    set the clipboard to theImage
                '''
                subprocess.run(["osascript", "-e", script], check=True)
            finally:
                Path(temp_path).unlink(missing_ok=True)

            messagebox.showinfo("Готово", "Холст скопирован в буфер обмена.")
        except Exception as exc:
            # Fallback: macOS also allows clipboard images through Preview/other
            # apps, so provide a useful diagnostic rather than silently failing.
            messagebox.showerror("Ошибка копирования", f"Не удалось скопировать холст:\n{exc}")


def main() -> None:
    root = tk.Tk()
    PaintApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
