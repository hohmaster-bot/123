# gui_file_ops.py — операции с файлами персонажа (T-SPLIT)
import os
import json
import shutil
import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from character import Character, CHARACTERS_DIR
from gui_app_config import get_last_character, set_last_character
from gui_windows import open_window


def load_or_new(app):
    last_name = get_last_character()
    if last_name:
        path = os.path.join(CHARACTERS_DIR, f"{last_name}.json")
        if os.path.exists(path):
            try:
                app.c = Character.load(path)
                import chips
                chips.clean_order(app.c)
                app._refresh()
                return
            except Exception as e:
                print(f"[auto-open] {e}")
    new_character(app)


def new_character(app):
    name = simpledialog.askstring(
        "Новый персонаж", "Имя:",
        parent=app.get_dialog_parent())
    if not name:
        if app.c is None:
            name = "Безымянный"
        else:
            return
    if app.c is not None:
        save(app, silent=True)
    app.c = Character(name)
    app.c.init_defaults()
    set_last_character(app.c.name)
    import chips
    chips.clean_order(app.c)
    app._refresh()


def rename_character(app):
    if not app.c:
        return
    old_name = app.c.name
    new_name = simpledialog.askstring(
        "Переименовать персонажа",
        f"Текущее имя: {old_name}\nНовое имя:",
        initialvalue=old_name,
        parent=app.get_dialog_parent())
    if not new_name:
        return
    new_name = new_name.strip()
    if not new_name or new_name == old_name:
        return
    new_path = os.path.join(CHARACTERS_DIR, f"{new_name}.json")
    if os.path.exists(new_path):
        if not messagebox.askyesno(
                "Файл существует",
                f"Файл «{new_name}.json» уже есть. Заменить?",
                parent=app.get_dialog_parent()):
            return
    old_path = os.path.join(CHARACTERS_DIR, f"{old_name}.json")
    app.c.name = new_name
    app.c.save(new_path)
    if os.path.exists(old_path) and old_path != new_path:
        try:
            os.remove(old_path)
        except Exception:
            pass
    set_last_character(new_name)
    app._refresh()


def open_characters_folder(app):
    import subprocess
    os.makedirs(CHARACTERS_DIR, exist_ok=True)
    try:
        if os.name == "nt":
            os.startfile(CHARACTERS_DIR)
        elif os.name == "posix":
            subprocess.run(["xdg-open", CHARACTERS_DIR])
    except Exception as e:
        messagebox.showerror(
            "Ошибка", str(e),
            parent=app.get_dialog_parent())


def open_character(app):
    path = filedialog.askopenfilename(
        initialdir=CHARACTERS_DIR,
        filetypes=[("JSON", "*.json")])
    if not path:
        return
    try:
        app.c = Character.load(path)
        set_last_character(app.c.name)
        import chips
        chips.clean_order(app.c)
        app._refresh()
    except Exception as e:
        messagebox.showerror(
            "Ошибка", str(e),
            parent=app.get_dialog_parent())


def save(app, silent=False):
    if not app.c:
        return
    try:
        app.c.embed_images()
    except Exception as e:
        print(f"[_save embed] {e}")
    path = os.path.join(CHARACTERS_DIR, f"{app.c.name}.json")
    app.c.save(path)
    set_last_character(app.c.name)
    print(f"[save] {path}")


def import_character(app):
    path = filedialog.askopenfilename(
        title="Импортировать персонажа",
        filetypes=[("WP-файл", "*.json *.wp"), ("Все", "*.*")])
    if not path:
        return
    try:
        c = Character.load(path)
    except Exception as e:
        messagebox.showerror(
            "Ошибка импорта", str(e),
            parent=app.get_dialog_parent())
        return
    dest = os.path.join(CHARACTERS_DIR, f"{c.name}.json")
    if os.path.exists(dest):
        if not messagebox.askyesno(
                "Файл существует",
                f"Персонаж «{c.name}» уже есть.\nЗаменить?",
                parent=app.get_dialog_parent()):
            return
    try:
        if app.c:
            save(app, silent=True)
        shutil.copy(path, dest)
        app.c = Character.load(dest)
        set_last_character(app.c.name)
        import chips
        chips.clean_order(app.c)
        app._refresh()
        messagebox.showinfo(
            "Импорт",
            f"Импортирован: {c.name}",
            parent=app.get_dialog_parent())
    except Exception as e:
        messagebox.showerror(
            "Ошибка", str(e),
            parent=app.get_dialog_parent())


def export_character(app):
    if not app.c:
        return
    safe = "".join(
        ch for ch in app.c.name
        if ch.isalnum() or ch in " _-").strip() or "character"
    path = filedialog.asksaveasfilename(
        title="Экспортировать WP-файл",
        defaultextension=".json",
        initialfile=f"{safe}.wp.json",
        filetypes=[("WP-файл", "*.json")])
    if not path:
        return
    try:
        app.c.save(path)
        messagebox.showinfo(
            "Экспорт",
            f"Сохранено:\n{path}",
            parent=app.get_dialog_parent())
    except Exception as e:
        messagebox.showerror(
            "Ошибка", str(e),
            parent=app.get_dialog_parent())


def export_pdf(app):
    if not app.c:
        return
    try:
        from pdf_export import export_pdf
    except ImportError as e:
        messagebox.showerror(
            "PDF",
            f"Модуль PDF не найден:\n{e}",
            parent=app.get_dialog_parent())
        return
    safe = "".join(
        ch for ch in app.c.name
        if ch.isalnum() or ch in " _-").strip() or "character"
    path = filedialog.asksaveasfilename(
        title="Экспортировать в PDF",
        defaultextension=".pdf",
        initialfile=f"{safe}.pdf",
        filetypes=[("PDF", "*.pdf")])
    if not path:
        return
    try:
        export_pdf(app.c, path)
        messagebox.showinfo(
            "PDF",
            f"Готово:\n{path}",
            parent=app.get_dialog_parent())
    except Exception as e:
        messagebox.showerror(
            "Ошибка PDF", str(e),
            parent=app.get_dialog_parent())


def _ask_exit_custom(app):
    """Кастомное окно выхода с тремя кнопками."""
    d = open_window(app, "Выход", 340, 160, mode="center")
    d.resizable(False, False)
    d.configure(bg="#2b2b2b")

    result = {"action": None}

    tk.Label(d, text="Сохранить изменения перед выходом?",
             font=("Segoe UI", 11, "bold"),
             fg="white", bg="#2b2b2b").pack(pady=(20, 10))

    tk.Label(d, text="Несохранённые данные будут потеряны.",
             font=("Segoe UI", 9),
             fg="#aaa", bg="#2b2b2b").pack(pady=(0, 20))

    bf = tk.Frame(d, bg="#2b2b2b")
    bf.pack(fill="x", padx=20)

    def _set(act):
        result["action"] = act
        d.destroy()

    tk.Button(bf, text="Сохранить", command=lambda: _set("save"),
              bg="#4a7", fg="white", font=("Segoe UI", 10, "bold"),
              width=10, relief="flat").pack(side="left", padx=5)

    tk.Button(bf, text="Не сохранять", command=lambda: _set("discard"),
              bg="#855", fg="white", font=("Segoe UI", 10, "bold"),
              width=12, relief="flat").pack(side="left", padx=5)

    tk.Button(bf, text="Отмена", command=lambda: _set("cancel"),
              bg="#555", fg="white", font=("Segoe UI", 10),
              width=8, relief="flat").pack(side="left", padx=5)

    # Позицию уже выставил open_window(mode="center").
    # Ручной пересчёт через app.root ломается в сплите (root withdrawn).
    # wait_window БЕЗ grab_set: grab_set в сплите скрывает окно (CONTRACT §4 T-WINDOW).
    d.wait_window()
    return result["action"]


def on_close(app):
    split = getattr(app, "_split", None)

    # Показываем окно (меню в сплите или root в классике),
    # чтобы диалог был виден.
    try:
        if (split and getattr(split, "menu_win", None)
                and split.menu_win.winfo_exists()):
            split.menu_win.deiconify()
            split.menu_win.lift()
            split.menu_win.focus_force()
        else:
            app.root.deiconify()
            app.root.lift()
            app.root.focus_force()
        app.root.update_idletasks()
    except Exception:
        pass

    if app.c:
        try:
            app.c.embed_images()
        except Exception as e:
            print(f"[_on_close embed] {e}")

        action = _ask_exit_custom(app)

        if action is None:
            return  # окно закрылось без ответа — не выходим

        if action == "cancel":
            if split:
                try:
                    app.root.withdraw()
                except Exception:
                    pass
            return

        elif action == "save":
            try:
                app.c.embed_images()
                path = os.path.join(
                    CHARACTERS_DIR, f"{app.c.name}.json")
                app.c.save(path)
                set_last_character(app.c.name)
            except Exception as e:
                print(f"[_on_close save] {e}")
        # action == "discard" → просто идём дальше и закрываемся

    try:
        app._stop_tray()
    except Exception:
        pass
    try:
        app.root.quit()
    except Exception:
        pass
    try:
        app.root.destroy()
    except Exception:
        pass


def copy_sheet(app):
    """Скопировать текст чарника в буфер обмена."""
    if not app.c:
        return
    try:
        lines = app._lines or []
        text = "\n".join(lines)
        app.root.clipboard_clear()
        app.root.clipboard_append(text)
        app.root.update()
        messagebox.showinfo(
            "Скопировать лист",
            f"Текст чарника скопирован ({len(text)} символов).",
            parent=app.get_dialog_parent())
    except Exception as e:
        messagebox.showerror(
            "Скопировать лист",
            f"Ошибка: {e}",
            parent=app.get_dialog_parent())