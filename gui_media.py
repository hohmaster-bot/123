# gui_media.py — портрет, фон и медиа (T-SPLIT)
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from gui_shared import _load_image, _load_image_from_data
from gui_windows import open_window

def load_portrait(app):
    if not app.c:
        return
    path = filedialog.askopenfilename(
        filetypes=[("Картинки", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Все", "*.*")])
    if path:
        app.c.portrait = ""
        app.c.portrait_b64 = ""
        app.c.portrait = path
        app.c.embed_images()
        if not app.c.portrait_b64:
            messagebox.showerror("Ошибка", "Не удалось загрузить картинку. Возможно, она повреждена или формат не поддерживается.")
            return
        app.c.portrait = ""
        app._refresh()
        messagebox.showinfo("Портрет", "Портрет успешно загружен и вшит в сейв.")

def load_background(app):
    if not app.c:
        return
    path = filedialog.askopenfilename(
        filetypes=[("Картинки", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Все", "*.*")])
    if path:
        app.c.background_image = path
        app.c.background_b64 = ""
        app.c.embed_images()
        if not app.c.background_b64:
            messagebox.showerror("Ошибка", "Не удалось загрузить картинку. Возможно, она повреждена или формат не поддерживается.")
            return
        app.c.background_image = ""
        app._refresh()
        messagebox.showinfo("Фон", "Фон успешно загружен и вшит в сейв.")

def update_portrait_size(app):
    if not app.c:
        return
    show = not app.c.settings.get("hide_portrait", False)
    if not show:
        app.portrait_frame.pack_forget()
        return
    data_len = len(str(app.c.portrait_b64 or app.c.portrait or ""))
    if data_len == 0:
        print("[portrait] данных нет (portrait_b64 и portrait пусты)")
    if not app.portrait_frame.winfo_ismapped():
        # classic: portrait_frame над btn_container (левая панель)
        # split: portrait_frame уже упакован в окне меню (btn_container нет)
        btn_cont = getattr(app, "btn_container", None)
        if btn_cont is not None:
            app.portrait_frame.pack(fill="x", before=btn_cont)
        else:
            app.portrait_frame.pack(fill="x")
    # classic: высота/ширина левой панели PanedWindow (app.left)
    # split: левой панели нет — берём окно меню (menu_win) или сам portrait_frame
    left = getattr(app, "left", None)
    if left is not None:
        lh = left.winfo_height()
        lw = left.winfo_width()
    else:
        split = getattr(app, "_split", None)
        menu_win = getattr(split, "menu_win", None) if split is not None else None
        src = menu_win if (menu_win is not None and menu_win.winfo_exists()) \
              else app.portrait_frame
        lh = src.winfo_height()
        lw = src.winfo_width()
    if lh < 80 or lw < 80:
        return
    target_h = max(80, int(lh * 0.40))
    target_w = max(80, lw - 4)
    data = app.c.portrait_b64 or app.c.portrait
    app.portrait_frame.pack_propagate(False)
    app.portrait_frame.configure(height=target_h)
    if not data:
        app.lbl_portrait.config(text="[Портрет]", image="")
        return
    photo = _load_image_from_data(data, target_w, target_h, mode="fill")
    if photo:
        app._portrait_photo = photo
        app.lbl_portrait.config(image=photo, text="")
    else:
        if os.path.exists(str(data)):
            photo2 = _load_image(data, target_w, target_h, mode="fill")
            if photo2:
                app._portrait_photo = photo2
                app.lbl_portrait.config(image=photo2, text="")
                return
        app.lbl_portrait.config(text="[Ошибка]", image="")

def expand_portrait(app):
    if not app.c:
        return
    data = app.c.portrait_b64 or app.c.portrait
    if not data:
        return
    d = open_window(app, f"Портрет: {app.c.name}", 900, 700, mode="center")
    canvas = tk.Canvas(d, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    def redraw(event=None):
        canvas.delete("all")
        w = max(canvas.winfo_width(), 400)
        h = max(canvas.winfo_height(), 400)
        photo = _load_image_from_data(data, w, h, mode="fit")
        if photo:
            d._photo = photo
            canvas.create_image(w // 2, h // 2, image=photo, anchor="center")
    canvas.bind("<Configure>", redraw)
    d.after(100, redraw)

def force_taskbar_alt_tab(root):
    """Возвращает безрамочное окно в Alt-Tab / панель задач (Windows).

    overrideredirect(True) снимает WS_EX_APPWINDOW и ставит WS_EX_TOOLWINDOW —
    из-за этого окно не видно в Alt-Tab. Делаем:
      1) берём top-level HWND (GetParent, если есть — Tk отдаёт child);
      2) ставим WS_EX_APPWINDOW, снимаем WS_EX_TOOLWINDOW;
      3) SetWindowPos(SWP_FRAMECHANGED) — иначе оболочка не перечитает стиль.
    На не-Windows — no-op.
    """
    if os.name != "nt":
        return
    try:
        import ctypes
        root.update_idletasks()
        user32 = ctypes.windll.user32
        hwnd = user32.GetParent(root.winfo_id()) or root.winfo_id()

        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        SWP_NOZORDER = 0x0004
        SWP_FRAMECHANGED = 0x0020

        cur = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        new = (cur | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
        if new != cur:
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new)
        # Сообщаем оболочке, что стиль изменился (и даже если не менялся —
        # повторный вызов безопасен и заставляет перечитать)
        user32.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED,
        )
    except Exception as e:
        print(f"[force_taskbar_alt_tab] {e}")