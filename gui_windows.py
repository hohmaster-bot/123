# gui_windows.py — ЕДИНСТВЕННАЯ фабрика окон (T-SPLIT-WINDOWS)
# Читает настройки позиционирования и управляет привязкой (магнитом).
import tkinter as tk

DEFAULT_MODE = "menu"

def open_window(app, title, width, height, mode=None):
    """
    Универсальная функция создания окна.
    mode: "pointer" (у мышки), "menu" (справа от меню), "center" (по центру).
    Если mode=None — берет из настроек app.c.settings["window_open_mode"].
    """
    parent = app.get_dialog_parent() if hasattr(app, "get_dialog_parent") else app.root
    
    # 1. Создаем окно. Важно: parent=None (или app.root), 
    # чтобы Toplevel не наследовал координаты меню и не улетал в левый угол.
    d = tk.Toplevel(parent if parent is not None else app.root)
    d.title(title)
    
    # 2. Читаем настройки
    if mode is None:
        mode = DEFAULT_MODE
        if app.c:
            mode = app.c.settings.get("window_open_mode", DEFAULT_MODE)
            
    # 3. Определяем координаты
    sw = d.winfo_screenwidth()
    sh = d.winfo_screenheight()
    
    if mode == "menu" and parent is not None:
        try:
            parent.update_idletasks()
            px = parent.winfo_rootx() + parent.winfo_width() + 8
            py = parent.winfo_rooty()
        except Exception:
            px, py = 100, 100
    elif mode == "center" and parent is not None:
        try:
            parent.update_idletasks()
            px = parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)
            py = parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)
        except Exception:
            px, py = 100, 100
    else:
        # pointer (у мышки)
        try:
            mx = d.winfo_pointerx()
            my = d.winfo_pointery()
        except Exception:
            mx, my = sw // 2, sh // 2
        px = mx + 15
        py = my + 15
        if px + width > sw: px = mx - width - 15
        if py + height > sh: py = my - height - 15
        
    px = max(0, min(px, sw - width))
    py = max(0, min(py, sh - height))

    if parent is not None:
        try:
            d.transient(parent)
        except Exception:
            pass
    
    d.geometry(f"{width}x{height}+{px}+{py}")
    try:
        d.deiconify()
    except Exception:
        pass
        
    # Закрытие по Escape
    d.bind("<Escape>", lambda e: d.destroy())
    
    # 4. Привязка (магнит) — уже сделана до geometry/deiconify
            
    # 5. Фокус
    try:
        d.focus_force()
        d.lift()
    except Exception:
        pass
        
    # 6. Если включен "магнит" — сообщаем сплиту, чтобы окно ездило за меню
    if mode == "menu":
        split = getattr(app, "_split", None)
        if split is not None and app.c and app.c.settings.get("pin_editor_to_menu", True):
            split.set_active_window(d)
    # mode="center" (диалоги подтверждения) НЕ трекаем: иначе
    # _ask_exit_custom уничтожает предыдущее окно и wait_window висит.
            
    return d