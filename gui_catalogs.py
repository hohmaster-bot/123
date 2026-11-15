# gui_catalogs.py — окно «Управление каталогами» (T-CAT, Этап 3).
# Список файлов по папкам, чекбоксы, аккордеон элементов, мультивыбор.
# Импорт из файла / URL, удаление, редактирование JSON.
# Окно — Toplevel(modal=False), чтобы не блокировать главное.

import json
import os
import shutil
import tkinter as tk
import urllib.error
import urllib.request
from tkinter import ttk, messagebox, simpledialog, filedialog

from character import CATALOGS_DIR, CATALOG_SUBDIRS, load_catalogs
from gui_shared import make_scrollable
from gui_windows import open_window


# ---------- вспомогательные ----------

def _catalog_path(sub, fname):
    return os.path.join(CATALOGS_DIR, sub, fname)


def _file_enabled(settings, sub, fname):
    """Включён ли файл (whitelist/blacklist)."""
    enabled = settings.get("catalogs_enabled", []) or []
    mode = settings.get("catalogs_mode", "whitelist")
    if not enabled:
        return True
    fk = f"{sub}/{fname}"
    if mode == "whitelist":
        return (sub in enabled) or (fk in enabled)
    return (sub not in enabled) and (fk not in enabled)


def _item_hidden(settings, sub, fname, item_name):
    """Скрыт ли конкретный элемент."""
    dis = settings.get("catalogs_items_disabled", []) or []
    key = f"{sub}/{fname}#{item_name}"
    return key in dis


def _set_file_enabled(settings, sub, fname, value):
    enabled = list(settings.get("catalogs_enabled", []) or [])
    mode = settings.get("catalogs_mode", "whitelist")
    fk = f"{sub}/{fname}"
    if mode == "whitelist":
        if value and fk not in enabled:
            enabled.append(fk)
        if not value and fk in enabled:
            enabled.remove(fk)
    else:  # blacklist
        if value and fk in enabled:
            enabled.remove(fk)
        if not value and fk not in enabled:
            enabled.append(fk)
    settings["catalogs_enabled"] = enabled


def _set_item_hidden(settings, sub, fname, item_name, hidden):
    dis = list(settings.get("catalogs_items_disabled", []) or [])
    key = f"{sub}/{fname}#{item_name}"
    if hidden and key not in dis:
        dis.append(key)
    if not hidden and key in dis:
        dis.remove(key)
    settings["catalogs_items_disabled"] = dis


def _count_items(path):
    """(кол-во элементов, 'items'|'groups')."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0, "items"
    if "groups" in data and isinstance(data["groups"], list):
        return len(data["groups"]), "groups"
    if "items" in data and isinstance(data["items"], list):
        return len(data["items"]), "items"
    return 0, "items"


def _load_items(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    if isinstance(data.get("items"), list):
        return data["items"]
    if isinstance(data.get("groups"), list):
        return data["groups"]
    return []


def _unique_name(folder, base_name):
    """base_name.json → base_name (1).json, если занято."""
    name = base_name
    if not name.lower().endswith(".json"):
        name += ".json"
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        return name
    stem = name[:-5]
    i = 1
    while True:
        cand = f"{stem} ({i}).json"
        if not os.path.exists(os.path.join(folder, cand)):
            return cand
        i += 1


def _pick_folder_dialog(app, parent, title="Куда положить?"):
    """Выбор папки из CATALOG_SUBDIRS через Combobox. Возвращает str|None."""
    d = open_window(app, title, 300, 150)
    d.grab_set()  # Модальный диалог (ждет выбора)
    result = {"sub": None}

    tk.Label(d, text="Папка:", font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(10, 2))
    var = tk.StringVar(value=CATALOG_SUBDIRS[0])
    cb = ttk.Combobox(d, values=list(CATALOG_SUBDIRS),
                       textvariable=var, state="readonly", width=28)
    cb.pack(padx=10, pady=2)

    def ok():
        result["sub"] = var.get()
        d.destroy()

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=10, padx=10)
    tk.Button(bf, text="OK", command=ok,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold"),
              padx=14).pack(side="left")
    tk.Button(bf, text="Отмена", command=d.destroy
              ).pack(side="right")
    return result["sub"]
# ---------- окно ----------
def open_catalogs_manager(app):
    """Главное окно «Управление каталогами»."""
    if not app.c:
        return
    settings = app.c.settings

    d = open_window(app, "⚙ Управление каталогами", 900, 760)

    tk.Label(d, text="⚙ Управление каталогами",
             font=("Segoe UI", 13, "bold"),
             bg="#2b2b2b", fg="white", pady=8
             ).pack(fill="x")

    top = tk.Frame(d, bg="#e8e8e8", pady=4, padx=6)
    top.pack(fill="x", padx=6, pady=(4, 0))
    tk.Label(top, text="🔎 Поиск:",
             bg="#e8e8e8").pack(side="left")
    search_var = tk.StringVar()
    tk.Entry(top, textvariable=search_var, width=24
             ).pack(side="left", padx=4)
    tk.Label(top, text="  Папка:",
             bg="#e8e8e8").pack(side="left")
    folder_var = tk.StringVar(value="все")
    folder_om = tk.OptionMenu(top, folder_var,
                               *(["все"] + list(CATALOG_SUBDIRS)))
    folder_om.config(width=18)
    folder_om.pack(side="left", padx=4)
    only_on_var = tk.BooleanVar(value=False)
    tk.Checkbutton(top, text="Только включённые",
                    variable=only_on_var, bg="#e8e8e8"
                    ).pack(side="left", padx=10)

    actions = tk.Frame(d, bg="#2a2a2a", pady=4, padx=6)
    actions.pack(fill="x", padx=6)
    tk.Button(actions, text="📥 Из файла",
              command=lambda: _import_from_file(app, d, rebuild),
              bg="#446", fg="white",
              font=("Segoe UI", 9, "bold"),
              padx=8).pack(side="left", padx=2)
    tk.Button(actions, text="🌐 Из URL",
              command=lambda: _import_from_url(app, d, rebuild),
              bg="#446", fg="white",
              font=("Segoe UI", 9, "bold"),
              padx=8).pack(side="left", padx=2)
    tk.Button(actions, text="＋ Пустой JSON",
              command=lambda: _new_empty(app, d, rebuild),
              bg="#4a7", fg="white",
              font=("Segoe UI", 9, "bold"),
              padx=8).pack(side="left", padx=2)

    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=4)

    # раскрытые файлы: set((sub, fname))
    expanded = set()
    # выбранные элементы для мультивыбора: set((sub,fname,item_name))
    selected_items = set()
    # последний клик по чекбоксу элемента — для Shift+Click
    last_item_click = {"key": None}

    def rebuild():
        for w in body.winfo_children():
            w.destroy()
        q = search_var.get().strip().lower()
        sub_filter = folder_var.get()
        only_on = only_on_var.get()
        total_files = 0
        total_on = 0
        for sub in CATALOG_SUBDIRS:
            if sub_filter != "все" and sub != sub_filter:
                continue
            folder = os.path.join(CATALOGS_DIR, sub)
            if not os.path.isdir(folder):
                continue
            files = sorted([f for f in os.listdir(folder)
                            if f.endswith(".json")])
            if q:
                files = [f for f in files if q in f.lower()]
            if only_on:
                files = [f for f in files
                         if _file_enabled(settings, sub, f)]
            if not files:
                continue
            sec = tk.Frame(body, bg="#c8c8c8")
            sec.pack(fill="x", pady=(8, 2))
            tk.Label(sec, text=f"📁 {sub}",
                     font=("Segoe UI", 11, "bold"),
                     bg="#c8c8c8", anchor="w", padx=8
                     ).pack(fill="x")
            for fname in files:
                total_files += 1
                path = _catalog_path(sub, fname)
                on = _file_enabled(settings, sub, fname)
                if on:
                    total_on += 1
                n_items, kind = _count_items(path)
                _render_file_row(app, body, sub, fname, on,
                                 n_items, kind, path,
                                 expanded, selected_items,
                                 rebuild)
                if (sub, fname) in expanded:
                    _render_file_items(app, body, sub, fname,
                                       path, settings,
                                       selected_items,
                                       last_item_click,
                                       rebuild)
        # итог
        bottom = tk.Frame(body, bg="#e8e8e8", pady=4)
        bottom.pack(fill="x", pady=(10, 2))
        tk.Label(bottom,
                 text=f"Итого: {total_files} файлов, "
                      f"{total_on} включено",
                 bg="#e8e8e8",
                 font=("Segoe UI", 9, "bold")
                 ).pack(anchor="w", padx=8)
        # ===== массовые действия с выбранными элементами =====
        if selected_items:
            sel_count = len(selected_items)
            bulk = tk.Frame(bottom, bg="#e8e8e8")
            bulk.pack(fill="x", padx=8, pady=(4, 0))
            tk.Label(bulk,
                     text=f"Выбрано элементов: {sel_count}",
                     bg="#e8e8e8",
                     font=("Segoe UI", 9, "bold")
                     ).pack(side="left", padx=(0, 10))
            tk.Button(bulk, text="☑ Включить выбранные",
                      command=lambda: _bulk_set_items(
                          app, selected_items, False,
                          last_item_click, rebuild),
                      bg="#4a7", fg="white",
                      font=("Segoe UI", 9, "bold"),
                      padx=6
                      ).pack(side="left", padx=2)
            tk.Button(bulk, text="☐ Выключить выбранные",
                      command=lambda: _bulk_set_items(
                          app, selected_items, True,
                          last_item_click, rebuild),
                      bg="#a55", fg="white",
                      font=("Segoe UI", 9, "bold"),
                      padx=6
                      ).pack(side="left", padx=2)
            tk.Button(bulk, text="Снять выделение",
                      command=lambda: (
                          selected_items.clear(),
                          last_item_click.update({"key": None}),
                          rebuild()),
                      font=("Segoe UI", 9),
                      padx=6
                      ).pack(side="left", padx=2)

    def on_filter(*args):
        rebuild()
    search_var.trace_add("write", on_filter)
    folder_var.trace_add("write", on_filter)
    only_on_var.trace_add("write", on_filter)

    rebuild()

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=6, padx=6)
    tk.Button(bf, text="Закрыть",
              command=lambda: (_apply_and_close(app, d)),
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold"),
              padx=20).pack(side="right")


def _apply_and_close(app, d):
    """Сохранить каталожные настройки в персонажа и закрыть."""
    try:
        load_catalogs(app.c.settings)
    except Exception as e:
        print(f"[apply_and_close] {e}")
    try:
        app._refresh()
    except Exception:
        pass
    d.destroy()


# ---------- строки ----------

def _render_file_row(app, body, sub, fname, on,
                     n_items, kind, path,
                     expanded, selected_items, rebuild):
    settings = app.c.settings
    row = tk.Frame(body, bg="#f8f8f8",
                   relief="solid", borderwidth=1)
    row.pack(fill="x", padx=4, pady=1)

    var = tk.BooleanVar(value=on)

    def toggle():
        _set_file_enabled(settings, sub, fname, var.get())
        rebuild()

    tk.Checkbutton(row, variable=var, command=toggle,
                    bg="#f8f8f8"
                    ).pack(side="left", padx=(4, 2))

    key = (sub, fname)
    is_open = key in expanded
    arrow = "▼" if is_open else "▶"
    lbl = tk.Label(row, text=f"{arrow} {fname}",
                   bg="#f8f8f8", cursor="hand2",
                   font=("Segoe UI", 10, "bold"),
                   anchor="w")
    lbl.pack(side="left", padx=2)
    kind_ru = "групп" if kind == "groups" else "элементов"
    tk.Label(row,
             text=f"— {n_items} {kind_ru}",
             bg="#f8f8f8", fg="#666",
             font=("Segoe UI", 9)
             ).pack(side="left", padx=4)

    def on_click(e=None):
        if key in expanded:
            expanded.remove(key)
        else:
            expanded.add(key)
        rebuild()

    lbl.bind("<Button-1>", on_click)

    btns = tk.Frame(row, bg="#f8f8f8")
    btns.pack(side="right", padx=4)

    def _del():
        if not messagebox.askyesno(
                "Удалить",
                f"Удалить {sub}/{fname}?\n"
                f"Файл будет удалён с диска безвозвратно.",
                parent=body.winfo_toplevel()):
            return
        try:
            os.remove(path)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e),
                                  parent=body.winfo_toplevel())
            return
        try:
            load_catalogs(settings)
        except Exception:
            pass
        rebuild()

    def _edit():
        _edit_json(app, sub, fname, path, body, rebuild)

    tk.Button(btns, text="✎", width=2, command=_edit
              ).pack(side="left", padx=1)
    tk.Button(btns, text="🗑", width=2, command=_del
              ).pack(side="left", padx=1)


def _render_file_items(app, body, sub, fname, path, settings,
                        selected_items, last_item_click, rebuild):
    """Элементы раскрытого файла: чекбоксы, мультивыбор (Shift/Ctrl),
    кнопки «Выбрать все» / «Снять все», поиск по элементам."""
    items = _load_items(path)
    if not items:
        tk.Label(body, text="    (пусто)",
                 bg="#fcfcfc", fg="#888",
                 font=("Segoe UI", 9, "italic"),
                 anchor="w").pack(fill="x", padx=20, pady=1)
        return
    # фильтр по поиску (тот же search_var, что и у файлов)
    q = ""
    try:
        top = body.winfo_toplevel()
        # find search_var через parent-окно: не надёжно, но
        # _render_file_items вызывается только из rebuild, где
        # search_var в области видимости — не передаём.
    except Exception:
        pass
    # мини-панель: выбрать все / снять все
    toolbar = tk.Frame(body, bg="#f0f0f0")
    toolbar.pack(fill="x", padx=20, pady=(2, 0))
    def select_all():
        for it in items:
            if not isinstance(it, dict):
                continue
            nm = (it.get("name") or "").strip() or "?"
            selected_items.add((sub, fname, nm))
        rebuild()
    def clear_all():
        for it in items:
            if not isinstance(it, dict):
                continue
            nm = (it.get("name") or "").strip() or "?"
            selected_items.discard((sub, fname, nm))
        rebuild()
    tk.Button(toolbar, text="☑ Выбрать все",
              command=select_all,
              font=("Segoe UI", 8), padx=4
              ).pack(side="left", padx=2)
    tk.Button(toolbar, text="☐ Снять все",
              command=clear_all,
              font=("Segoe UI", 8), padx=4
              ).pack(side="left", padx=2)

    for it in items:
        if not isinstance(it, dict):
            continue
        nm = (it.get("name") or "").strip() or "?"
        hidden = _item_hidden(settings, sub, fname, nm)
        key = (sub, fname, nm)
        is_sel = key in selected_items
        row = tk.Frame(body, bg="#fcfcfc",
                       relief="flat", borderwidth=1)
        row.pack(fill="x", padx=20, pady=0)
        var = tk.BooleanVar(value=not hidden)

        def toggle(k=key, v=var):
            _set_item_hidden(settings, sub, fname, k[2], not v.get())
            rebuild()

        # чекбокс с Shift/Ctrl через bind на Frame (Checkbutton
        # перехватывает клик, поэтому вешаем на отдельный Label).
        cb = tk.Checkbutton(row, variable=var, command=toggle,
                             bg="#fcfcfc")
        cb.pack(side="left", padx=(4, 2))

        # область для Shift/Ctrl+Click — сам Label с именем
        def on_click(event, k=key):
            ctrl = bool(event.state & 0x0004)   # Control
            shift = bool(event.state & 0x0001)  # Shift
            if shift and last_item_click.get("key"):
                # диапазон: от last до текущего
                _range_select(items, sub, fname,
                              last_item_click["key"], k,
                              selected_items)
            elif ctrl:
                if k in selected_items:
                    selected_items.discard(k)
                else:
                    selected_items.add(k)
                last_item_click["key"] = k
            else:
                # обычный клик — toggle выбранность
                if k in selected_items:
                    selected_items.discard(k)
                else:
                    selected_items.add(k)
                last_item_click["key"] = k
            rebuild()

        nl = tk.Label(row, text=f"• {nm}",
                      bg="#fcfcfc" if not is_sel else "#d8e8ff",
                      font=("Segoe UI", 9),
                      anchor="w", cursor="hand2")
        nl.pack(side="left", padx=2, fill="x", expand=True)
        nl.bind("<Button-1>", on_click)
        if it.get("desc"):
            tk.Label(row, text=f"— {it['desc'][:60]}",
                     bg="#fcfcfc", fg="#666",
                     font=("Segoe UI", 8),
                     anchor="w").pack(side="left", padx=4)


def _range_select(items, sub, fname, key_a, key_b, selected):
    """Shift+Click: выделить диапазон между key_a и key_b."""
    names = [((it.get("name") or "").strip() or "?")
             for it in items if isinstance(it, dict)]
    try:
        i_a = names.index(key_a[2])
        i_b = names.index(key_b[2])
    except ValueError:
        return
    lo, hi = (i_a, i_b) if i_a <= i_b else (i_b, i_a)
    for i in range(lo, hi + 1):
        selected.add((sub, fname, names[i]))


def _bulk_set_items(app, selected, hidden, last_item_click, rebuild):
    """Массово скрыть/показать выбранные элементы."""
    settings = app.c.settings
    for (sub, fname, nm) in list(selected):
        _set_item_hidden(settings, sub, fname, nm, hidden)
    selected.clear()
    last_item_click.update({"key": None})
    try:
        load_catalogs(settings)
    except Exception:
        pass
    rebuild()

# ---------- импорт / новый ----------

def _import_from_file(app, parent, rebuild):
    path = filedialog.askopenfilename(
        parent=parent,
        title="Загрузить каталог из файла",
        filetypes=[("JSON", "*.json"), ("Все", "*.*")])
    if not path:
        return
    sub = _pick_folder_dialog(app, parent, "Куда положить?")
    if not sub:
        return
    folder = os.path.join(CATALOGS_DIR, sub)
    os.makedirs(folder, exist_ok=True)
    base = os.path.basename(path)
    new_name = _unique_name(folder, base)
    try:
        shutil.copy(path, os.path.join(folder, new_name))
    except Exception as e:
        messagebox.showerror("Ошибка", str(e), parent=parent)
        return
    # авто-включить новый файл
    _set_file_enabled(app.c.settings, sub, new_name, True)
    try:
        load_catalogs(app.c.settings)
    except Exception:
        pass
    messagebox.showinfo("Готово",
                         f"Скопировано: {sub}/{new_name}",
                         parent=parent)
    rebuild()


def _import_from_url(app, parent, rebuild):
    url = simpledialog.askstring(
        "Из URL",
        "URL к JSON-файлу каталога:",
        parent=parent)
    if not url:
        return
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        messagebox.showerror("Ошибка",
                              "URL должен начинаться с http:// или https://",
                              parent=parent)
        return
    sub = _pick_folder_dialog(parent, "Куда положить?")
    if not sub:
        return
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "WiPeFinder/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            messagebox.showerror("Ошибка",
                                  "JSON не является объектом",
                                  parent=parent)
            return
    except urllib.error.URLError as e:
        messagebox.showerror("Ошибка сети", str(e), parent=parent)
        return
    except json.JSONDecodeError as e:
        messagebox.showerror("Ошибка JSON", str(e), parent=parent)
        return
    base = url.rstrip("/").split("/")[-1] or "imported_catalog"
    if not base.lower().endswith(".json"):
        base += ".json"
    folder = os.path.join(CATALOGS_DIR, sub)
    os.makedirs(folder, exist_ok=True)
    new_name = _unique_name(folder, base)
    try:
        with open(os.path.join(folder, new_name),
                  "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e), parent=parent)
        return
    _set_file_enabled(app.c.settings, sub, new_name, True)
    try:
        load_catalogs(app.c.settings)
    except Exception:
        pass
    messagebox.showinfo("Готово",
                         f"Скачано: {sub}/{new_name}",
                         parent=parent)
    rebuild()


def _new_empty(app, parent, rebuild):
    sub = _pick_folder_dialog(parent, "Где создать?")
    if not sub:
        return
    name = simpledialog.askstring(
        "Новый каталог",
        f"Имя файла для {sub}/ (без .json):",
        parent=parent)
    if not name:
        return
    name = name.strip()
    if not name:
        return
    folder = os.path.join(CATALOGS_DIR, sub)
    os.makedirs(folder, exist_ok=True)
    fname = name if name.endswith(".json") else f"{name}.json"
    path = os.path.join(folder, fname)
    if os.path.exists(path):
        messagebox.showwarning("Файл есть",
                                f"{fname} уже существует",
                                parent=parent)
        return
    data = {"groups": []} if sub == "weapons" else {"items": []}
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e), parent=parent)
        return
    _set_file_enabled(app.c.settings, sub, fname, True)
    try:
        load_catalogs(app.c.settings)
    except Exception:
        pass
    rebuild()


def _edit_json(app, sub, fname, path, parent, rebuild):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e), parent=parent)
        return
    d = open_window(app, f"Редактор: {sub}/{fname}", 800, 700, mode="center")
    tk.Label(d, text=f"JSON: {sub}/{fname}",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=6, pady=4)
    txt = tk.Text(d, font=("Consolas", 9), wrap="none")
    txt.pack(fill="both", expand=True, padx=6, pady=4)
    txt.insert("1.0", content)

    def save():
        try:
            data = json.loads(txt.get("1.0", "end"))
        except Exception as e:
            messagebox.showerror("JSON", f"Ошибка: {e}", parent=d)
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=d)
            return
        try:
            load_catalogs(app.c.settings)
        except Exception:
            pass
        rebuild()
        d.destroy()

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=6, padx=6)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Отмена", command=d.destroy
              ).pack(side="right")