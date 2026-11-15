# gui_editors_window.py — окно "Редакторы" с вкладками (Задача R2).
import tkinter as tk
from tkinter import ttk, messagebox

from gui_shared import make_scrollable
from gui_windows import open_window
import gui_registry


def open_editors_window(app, paid=None):
    """Окно "Редакторы": вкладки Редактирование (бесплатно) / Прокачка (платно)."""
    if not app.c:
        return
    d = open_window(app, "Редакторы", 860, 660)

    tk.Label(d, text="🗂 Редакторы",
             font=("Segoe UI", 13, "bold"),
             bg="#2b2b2b", fg="white", pady=8
             ).pack(fill="x")

    nb = ttk.Notebook(d)
    nb.pack(fill="both", expand=True, padx=6, pady=6)

    # Вкладка 1: Редактирование (бесплатно)
    frame_free = tk.Frame(nb, bg="#f4f4f4")
    nb.add(frame_free, text="🛠 Редактирование (бесплатно)")
    _build_editor_tab(app, frame_free, d, paid=False)

    # Вкладка 2: Прокачка (платно)
    frame_paid = tk.Frame(nb, bg="#f4f4f4")
    nb.add(frame_paid, text="💰 Прокачка! (платно)")
    _build_editor_tab(app, frame_paid, d, paid=True)

    if paid is not None:
        nb.select(1 if paid else 0)

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=6, padx=6)
    tk.Button(bf, text="Закрыть",
              command=lambda: (setattr(app, "force_free", False),
                               app._refresh(), d.destroy()),
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold"),
              padx=20).pack(side="right")


def _build_editor_tab(app, parent, dialog, paid):
    """Строит вкладку: список групп + кнопки редакторов."""
    outer, canvas, body = make_scrollable(parent)
    outer.pack(fill="both", expand=True)

    for grp in gui_registry.groups():
        sec = tk.Frame(body, bg="#c8c8c8")
        sec.pack(fill="x", pady=(8, 2))
        tk.Label(sec, text=f"📁 {grp}",
                 font=("Segoe UI", 10, "bold"),
                 bg="#c8c8c8", anchor="w", padx=8
                 ).pack(fill="x")

        for key, title, _g, fn in gui_registry.by_group(grp):
            row = tk.Frame(body, bg="#f4f4f4")
            row.pack(fill="x", padx=10, pady=2)
            tk.Button(row, text=title, anchor="w",
                      font=("Segoe UI", 10),
                      bg="#4a7" if not paid else "#855",
                      fg="white", relief="flat",
                      padx=12, pady=4,
                      command=lambda f=fn, dd=dialog, p=paid:
                      _run_editor(app, f, dd, p)
                      ).pack(fill="x")


def _run_editor(app, fn, dialog, paid=False):
    try:
        app.force_free = not paid
        fn(app)
    except Exception as e:
        messagebox.showerror("Ошибка редактора", str(e),
                              parent=dialog)