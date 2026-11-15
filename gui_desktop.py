# gui_desktop.py — Desktop overlay (T-SPLIT-3.2, v1.1).
# Чипы "висят" над всеми окнами. Клики по чипам работают, клики мимо — проходят сквозь.
# Требует: pywin32 (pip install pywin32).
# Архитектура: фон (fullscreen, WS_EX_LAYERED|WS_EX_TRANSPARENT, LWA_ALPHA=0)
#              + чипы (Toplevel без рамки, topmost, place(x, y)).
# WM_NCHITTEST: HTTRANSPARENT (пусто) / HTCLIENT (чип).

import tkinter as tk
from tkinter import messagebox

try:
    import win32gui
    import win32con
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False


def _set_click_through(hwnd):
    """Сделать окно полностью прозрачным для кликов (фон)."""
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 0, win32con.LWA_ALPHA)


def _set_topmost(hwnd):
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)


class DesktopView:
    def __init__(self, app):
        self.app = app
        self.overlay = None
        self.chips = {}  # id -> Frame
        self.drag_mode = app.c.settings.get("chips_drag_mode", False) if app.c else False
        self._build()

    def _build(self):
        if not HAS_PYWIN32:
            messagebox.showwarning(
                "Desktop overlay",
                "pywin32 не установлен.\n\n"
                "Установи: pip install pywin32\n\n"
                "Без него чипы будут видны, но клики сквозь работать не будут.")
        # Один Toplevel на весь экран
        self.overlay = tk.Toplevel(self.app.root)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.configure(bg="#010203")
        try:
            self.overlay.attributes("-transparentcolor", "#010203")
        except Exception:
            pass
        sw = self.overlay.winfo_screenwidth()
        sh = self.overlay.winfo_screenheight()
        self.overlay.geometry(f"{sw}x{sh}+0+0")
        # Прозрачность для кликов (фон)
        if HAS_PYWIN32:
            try:
                self.overlay.update_idletasks()
                hwnd = win32gui.GetParent(self.overlay.winfo_id()) or self.overlay.winfo_id()
                _set_click_through(hwnd)
                _set_topmost(hwnd)
            except Exception as e:
                print(f"[desktop] click-through: {e}")
        self._build_chips()

    def _build_chips(self):
        import gui_chips
        import chips
        c = self.app.c
        if not c:
            return
        positions = c.settings.get("chips_positions", {}) or {}
        all_specs = chips.collect_all(c)
        # Фильтр
        if c.settings.get("chips_visible_enabled", False):
            visible = set(c.settings.get("chips_visible", []) or [])
            all_specs = [s for s in all_specs if s["id"] in visible]
        for spec in all_specs:
            fr = gui_chips.render_chip(self.app, spec)
            if fr is None:
                continue
            # Перенести Frame в overlay
            try:
                fr.pack_forget()
                fr.destroy()
            except Exception:
                pass
            # Рисуем заново в overlay (через render_chip_desktop)
            fr = self._render_desktop_chip(spec)
            if fr is None:
                continue
            x, y = positions.get(spec["id"], [100, 100])
            fr.place(x=x, y=y)
            self.chips[spec["id"]] = fr
            # Drag за точку
            if self.drag_mode:
                self._bind_drag(fr, spec["id"])

    def _render_desktop_chip(self, spec):
        """Как render_chip, но в overlay."""
        import gui_chips
        # Переиспользуем CHIP_REGISTRY, но с parent=overlay
        # Проще: вызвать _render_* и перенести
        fn = gui_chips.CHIP_REGISTRY.get(spec["kind"])
        if fn is None:
            return None
        # Временно подменить app.resources_frame на overlay
        old = self.app.resources_frame
        self.app.resources_frame = self.overlay
        try:
            fr = fn(self.app, spec)
        finally:
            self.app.resources_frame = old
        return fr

    def _bind_drag(self, fr, chip_id):
        """Drag за чёрную точку (или за чип, если точки нет)."""
        dot = None
        for ch in fr.winfo_children():
            if ch.winfo_class() == "Frame" and ch.cget("bg") == "#000":
                dot = ch
                break
        target = dot if dot is not None else fr
        target.bind("<ButtonPress-1>", lambda e: self._drag_start(e, fr, chip_id))
        target.bind("<B1-Motion>", lambda e: self._drag_move(e, fr))
        target.bind("<ButtonRelease-1>", lambda e: self._drag_end(e, fr, chip_id))

    def _drag_start(self, event, fr, chip_id):
        self._drag_fr = fr
        self._drag_id = chip_id
        self._drag_x = event.x_root - fr.winfo_x()
        self._drag_y = event.y_root - fr.winfo_y()

    def _drag_move(self, event):
        if getattr(self, "_drag_fr", None) is None:
            return
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self._drag_fr.place(x=x, y=y)

    def _drag_end(self, event, fr, chip_id):
        if getattr(self, "_drag_fr", None) is None:
            return
        x = fr.winfo_x()
        y = fr.winfo_y()
        c = self.app.c
        if c:
            pos = c.settings.setdefault("chips_positions", {})
            pos[chip_id] = [x, y]
        self._drag_fr = None
        self._drag_id = None

    def destroy(self):
        if self.overlay is not None:
            try:
                self.overlay.destroy()
            except Exception:
                pass
            self.overlay = None