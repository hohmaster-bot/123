# gui_templates.py — шаблоны (name/type/desc)
import tkinter as tk
from tkinter import messagebox
from gui_shared import ToolTip, make_scrollable
from gui_windows import open_window


def edit_templates(app):
    if not app.c:
        return

    def build(parent):
        c = app.c
        top = tk.Frame(parent, bg="#f4f4f4")
        top.pack(fill="x", pady=4)
        tk.Button(top, text="＋ Добавить шаблон",
                  command=lambda: _template_dialog(
                      app, None, rebuild)
                  ).pack(side="left", padx=5)
        tk.Button(top, text="📚 Из каталога",
                  command=lambda: _template_from_catalog(app, rebuild),
                  bg="#446", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="left", padx=5)
        outer, canvas, body = make_scrollable(parent)
        outer.pack(fill="both", expand=True)

        def rebuild():
            for w in body.winfo_children():
                w.destroy()
            if not c.templates:
                info = tk.Frame(body, bg="#e8e8e8",
                                 pady=8, padx=10)
                info.pack(fill="x", padx=5, pady=5)
                tk.Label(info,
                         text="Шаблоны — как черты, но с полем "
                              "«Тип». Например: «Боевой стиль: "
                              "Защита», «Архетип: Мастер меча».\n"
                              "Наведи мышку на название в чарнике "
                              "— увидишь описание.",
                         bg="#e8e8e8", justify="left",
                         font=("Segoe UI", 10),
                         wraplength=700).pack(anchor="w")
                return
            for i, t in enumerate(c.templates):
                row = tk.Frame(body, bg="#f4f4f4")
                row.pack(fill="x", pady=2, padx=5)
                type_tag = t.get("type", "") or "?"
                tk.Label(row, text=f"[{type_tag}]",
                         bg="#f4f4f4", font=("Consolas", 9),
                         fg="#666").pack(side="left")
                desc = t.get("desc", "")
                nl = tk.Label(row,
                              text=t.get("name", "?"),
                              bg="#f4f4f4",
                              font=("Segoe UI", 10, "bold"),
                              anchor="w",
                              cursor="hand2" if desc else "arrow")
                nl.pack(side="left", padx=4)
                if desc:
                    ToolTip(nl, desc)
                tk.Button(row, text="✖", width=3,
                          command=lambda i=i: _delete(
                              app, i, rebuild)
                          ).pack(side="right", padx=2)
                tk.Button(row, text="✎", width=3,
                          command=lambda i=i: _template_dialog(
                              app, i, rebuild)
                          ).pack(side="right", padx=2)

        rebuild()

    app._show_editor("Шаблоны", build)


def _template_from_catalog(app, rebuild):
    """K2e: взять шаблон из TEMPLATES_CATALOG."""
    from character import TEMPLATES_CATALOG
    if not TEMPLATES_CATALOG:
        messagebox.showinfo("Каталог шаблонов пуст",
                             "Создай файл в catalogs/templates/ через "
                             "«📚 Каталоги» в инвентаре.",
                             parent=app.get_dialog_parent())
        return

    # Заменили app.top на app.get_dialog_parent() для надежности
    d = open_window(app, "Из каталога: шаблоны", 600, 500)

    tk.Label(d, text="Выбери шаблон:",
             font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=6)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=4)

    for it in TEMPLATES_CATALOG:
        row = tk.Frame(body, bg="#f4f4f4", relief="solid", borderwidth=1)
        row.pack(fill="x", padx=2, pady=1)
        info = tk.Frame(row, bg="#f4f4f4")
        info.pack(side="left", fill="x", expand=True, padx=4, pady=2)
        tk.Label(info, text=f"[{it.get('type', '?')}] {it.get('name', '?')}",
                 bg="#f4f4f4", font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(anchor="w")
        if it.get("desc"):
            tk.Label(info, text=it["desc"][:100],
                     bg="#f4f4f4", fg="#666",
                     font=("Segoe UI", 8), anchor="w").pack(anchor="w")

        def _take(it=it):
            app.c.templates.append({
                "name": it.get("name", "?"),
                "type": it.get("type", ""),
                "desc": it.get("desc", ""),
            })
            app._refresh()
            rebuild()
            d.destroy()
        tk.Button(row, text="＋ Взять",
                  command=_take,
                  bg="#4a7", fg="white",
                  font=("Segoe UI", 8, "bold")
                  ).pack(side="right", padx=4)

    tk.Button(d, text="Закрыть",
              command=d.destroy).pack(pady=6)


def _template_dialog(app, idx, rebuild):
    is_new = idx is None
    t = app.c.templates[idx] if not is_new else None
    
    title = "Новый шаблон" if is_new else "Редактировать шаблон"
    d = open_window(app, title, 520, 540)
    
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="Название:").pack(anchor="w", padx=5,
                                            pady=(8, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    if t:
        e_name.insert(0, t.get("name", ""))
    e_name.pack(fill="x", padx=5)

    tk.Label(body, text="Тип (например: Боевой стиль, Архетип, "
                          "Школа, Происхождение):"
             ).pack(anchor="w", padx=5, pady=(8, 0))
    e_type = tk.Entry(body, font=("Segoe UI", 11))
    if t:
        e_type.insert(0, t.get("type", ""))
    e_type.pack(fill="x", padx=5)

    tk.Label(body, text="Описание:").pack(anchor="w", padx=5,
                                            pady=(8, 0))
    t_desc = tk.Text(body, font=("Segoe UI", 10), height=8,
                      wrap="word")
    if t:
        t_desc.insert("1.0", t.get("desc", ""))
    t_desc.pack(fill="both", expand=True, padx=5)

    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        type_ = e_type.get().strip()
        desc = t_desc.get("1.0", "end").strip()
        if is_new:
            app.c.templates.append({
                "name": name, "type": type_, "desc": desc})
        else:
            t["name"] = name
            t["type"] = type_
            t["desc"] = desc
        try:
            d.grab_release()
        except Exception:
            pass
        rebuild()
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")


def _delete(app, idx, rebuild):
    if idx < 0 or idx >= len(app.c.templates):
        return
    t = app.c.templates[idx]
    if not messagebox.askyesno(
            "Удалить", f"Удалить шаблон '{t.get('name','?')}'?",
            parent=app.get_dialog_parent()):
        return
    app.c.templates.pop(idx)
    rebuild()