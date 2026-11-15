# gui_wiki.py — вики-ссылки на правила
import webbrowser
import os
import tkinter as tk
from tkinter import messagebox
from gui_shared import ToolTip, make_scrollable
from gui_windows import open_window


def edit_wiki(app):
    if not app.c:
        return

    def build(parent):
        c = app.c
        top = tk.Frame(parent, bg="#f4f4f4")
        top.pack(fill="x", pady=4)
        tk.Button(top, text="＋ Добавить ссылку",
                  command=lambda: _link_dialog(
                      app, None, rebuild)
                  ).pack(side="left", padx=5)
        outer, canvas, body = make_scrollable(parent)
        outer.pack(fill="both", expand=True)

        def rebuild():
            for w in body.winfo_children():
                w.destroy()
            if not c.wiki_links:
                info = tk.Frame(body, bg="#e8e8e8",
                                 pady=8, padx=10)
                info.pack(fill="x", padx=5, pady=5)
                tk.Label(info,
                         text="Здесь будут кнопки с ссылками на "
                              "правила (например, твои доки на "
                              "dnd.su, pathfinder и т.п.).\n"
                              "Нажми «＋ Добавить ссылку» и "
                              "добавь свои.",
                         bg="#e8e8e8", justify="left",
                         font=("Segoe UI", 10),
                         wraplength=700).pack(anchor="w")
                return
            # Сетка кнопок 2 колонки
            grid = tk.Frame(body, bg="#f4f4f4")
            grid.pack(fill="x", padx=5, pady=4)
            for i, link in enumerate(c.wiki_links):
                url = link.get("url", "")
                row_i = i // 2
                col_i = i % 2
                fr = tk.Frame(grid, bg="#3a3a3a",
                              padx=6, pady=6)
                fr.grid(row=row_i, column=col_i, padx=4, pady=4,
                         sticky="nsew")
                grid.grid_columnconfigure(col_i, weight=1)
                
                # Кнопка-ссылка
                btn = tk.Button(
                    fr, text=link.get("name", "?"),
                    command=(lambda u=url: _open_url(u))
                    if url else None,
                    bg="#3a3a3a", fg="white", relief="flat",
                    font=("Segoe UI", 10, "bold"),
                    activebackground="#555",
                    activeforeground="white",
                    anchor="w", padx=8, pady=6)
                btn.pack(fill="x")
                
                # Галочка "в меню" (если есть)
                if link.get("show_on_panel"):
                    tk.Label(fr, text="📌", bg="#3a3a3a", fg="#f0c040",
                             font=("Segoe UI", 9)).pack(side="left")
                             
                if link.get("desc"):
                    ToolTip(btn, link["desc"])
                sub = tk.Frame(fr, bg="#3a3a3a")
                sub.pack(fill="x", pady=(4, 0))
                tk.Label(sub, text=url[:40] + ("…" if len(url) > 40
                                                 else ""),
                         bg="#3a3a3a", fg="#aaa",
                         font=("Segoe UI", 8),
                         anchor="w").pack(side="left", padx=2)
                tk.Button(sub, text="✎", width=2,
                          command=lambda i=i: _link_dialog(
                              app, i, rebuild),
                          bg="#555", fg="white", relief="flat",
                          font=("Segoe UI", 8)
                          ).pack(side="right", padx=1)
                tk.Button(sub, text="✖", width=2,
                          command=lambda i=i: _delete(
                              app, i, rebuild),
                          bg="#855", fg="white", relief="flat",
                          font=("Segoe UI", 8)
                          ).pack(side="right", padx=1)

        rebuild()

    app._show_editor("Вики", build)


def _open_url(url):
    """Открывает ссылку в браузере по умолчанию (Windows)."""
    if not url:
        return
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    try:
        os.startfile(url)
    except Exception:
        webbrowser.open(url)


def _link_dialog(app, idx, rebuild):
    is_new = idx is None
    link = app.c.wiki_links[idx] if not is_new else None
    title = "Новая ссылка" if is_new else "Редактировать ссылку"
    d = open_window(app, title, 520, 540)
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="Название (что увидит игрок):"
             ).pack(anchor="w", padx=5, pady=(8, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    if link:
        e_name.insert(0, link.get("name", ""))
    e_name.pack(fill="x", padx=5)

    tk.Label(body, text="URL:").pack(anchor="w", padx=5,
                                       pady=(8, 0))
    e_url = tk.Entry(body, font=("Segoe UI", 10))
    if link:
        e_url.insert(0, link.get("url", ""))
    e_url.pack(fill="x", padx=5)

    tk.Label(body, text="Описание (подсказка при наведении):"
             ).pack(anchor="w", padx=5, pady=(8, 0))
    t_desc = tk.Text(body, font=("Segoe UI", 10), height=5,
                      wrap="word")
    if link:
        t_desc.insert("1.0", link.get("desc", ""))
    t_desc.pack(fill="both", expand=True, padx=5)

    # Восстановленная галочка
    show_var = tk.BooleanVar(value=link.get("show_on_panel", False) if link else False)
    tk.Checkbutton(body, text="Добавить в меню быстрого доступа (📌)",
                   variable=show_var, bg="#f4f4f4",
                   font=("Segoe UI", 10)).pack(anchor="w", padx=5, pady=8)

    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        url = e_url.get().strip()
        desc = t_desc.get("1.0", "end").strip()
        show_panel = show_var.get()
        
        if is_new:
            app.c.wiki_links.append({
                "name": name, "url": url, "desc": desc,
                "show_on_panel": show_panel})
        else:
            link["name"] = name
            link["url"] = url
            link["desc"] = desc
            link["show_on_panel"] = show_panel
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
    if idx < 0 or idx >= len(app.c.wiki_links):
        return
    link = app.c.wiki_links[idx]
    if not messagebox.askyesno(
            "Удалить",
            f"Удалить ссылку '{link.get('name','?')}'?"):
        return
    app.c.wiki_links.pop(idx)
    rebuild()