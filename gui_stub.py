# gui_stub.py — Драйвы/Квесты + Квирки/Дворы/Квесты
# Драйвы: 10 штук (0-5) + Принципы (Табу)
# Квирки/Дворы/Квесты: 3 вкладки

import tkinter as tk
from tkinter import ttk, messagebox

from character import (DRIVE_KEYS, DRIVE_LEVEL_NAMES, COURT_TIERS)
from gui_shared import make_scrollable
from gui_windows import open_window


def edit_lenses(app):
    """Редактор Линз (особых квестов)."""
    if not app.c:
        return

    def build(parent):
        c = app.c
        top = tk.Frame(parent, bg="#f4f4f4", pady=4)
        top.pack(fill="x", padx=5)
        tk.Button(top, text="＋ Добавить линзу",
                  command=lambda: _lens_dialog(app, None, rebuild),
                  bg="#4a7", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="left", padx=2)

        tk.Button(top, text="📚 Из каталога",
                  command=lambda: _lens_from_catalog(app, rebuild),
                  bg="#446", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="left", padx=2)

        outer, canvas, body = make_scrollable(parent)
        outer.pack(fill="both", expand=True, padx=4, pady=4)

        def rebuild():
            for w in body.winfo_children():
                w.destroy()
            if not c.lenses:
                tk.Label(body, text="(линз нет)",
                         bg="#f4f4f4", fg="#888",
                         font=("Segoe UI", 10, "italic")
                         ).pack(pady=20)
                return
            for i, ln in enumerate(c.lenses):
                row = tk.Frame(body, bg="#f8f8f8",
                                relief="solid", borderwidth=1)
                row.pack(fill="x", pady=1)
                info = tk.Frame(row, bg="#f8f8f8")
                info.pack(side="left", fill="x", expand=True,
                           padx=4, pady=2)
                cur = int(ln.get("current", 0) or 0)
                mx = int(ln.get("max", 0) or 0)
                status = c.lens_status(ln)
                status_txt = {"closed": " 🏁 ЗАКРЫТА",
                              "failed": " 💀 ПРОВАЛЕНА"}.get(status, "")
                panel_txt = " 📌" if ln.get("show_on_panel") else ""
                nl = tk.Label(
                    info,
                    text=f"• {ln.get('name','?')}  "
                         f"[{cur}/{mx}]{status_txt}{panel_txt}",
                    bg="#f8f8f8",
                    font=("Segoe UI", 10, "bold"),
                    anchor="w", cursor="hand2")
                nl.pack(anchor="w")
                if ln.get("desc"):
                    tk.Label(info, text=ln["desc"][:100],
                             bg="#f8f8f8", fg="#666",
                             font=("Segoe UI", 8),
                             anchor="w").pack(anchor="w")
                btns = tk.Frame(row, bg="#f8f8f8")
                btns.pack(side="right", padx=4)
                tk.Button(btns, text="✎", width=2,
                          command=lambda idx=i: _lens_dialog(
                              app, idx, rebuild)
                          ).pack(side="left", padx=1)
                tk.Button(btns, text="✖", width=2,
                          command=lambda idx=i: _lens_delete(
                              app, idx, rebuild)
                          ).pack(side="left", padx=1)

        rebuild()

    app._show_editor("Линзы", build)

def _lens_from_catalog(app, rebuild):
    """K2e: взять линзу из CUSTOM_CATALOG."""
    from character import CUSTOM_CATALOG
    if not CUSTOM_CATALOG:
        messagebox.showinfo("Каталог custom пуст",
                             "Создай файл в catalogs/custom/.",
                             parent=app.get_dialog_parent())
        return
    d = open_window(app, "Из каталога: линзы", 650, 500)
    tk.Label(d, text="Выбери линзу:",
             font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=6)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=4)

    for it in CUSTOM_CATALOG:
        if it.get("kind") != "lens" and "current" not in it:
            continue
        row = tk.Frame(body, bg="#f4f4f4", relief="solid", borderwidth=1)
        row.pack(fill="x", padx=2, pady=1)
        info = tk.Frame(row, bg="#f4f4f4")
        info.pack(side="left", fill="x", expand=True, padx=4, pady=2)
        tk.Label(info, text=it.get("name", "?"),
                 bg="#f4f4f4", font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(anchor="w")
        if it.get("desc"):
            tk.Label(info, text=it["desc"][:100],
                     bg="#f4f4f4", fg="#666",
                     font=("Segoe UI", 8), anchor="w").pack(anchor="w")

        def _take(it=it):
            ln = dict(it)
            ln.pop("kind", None)
            ln.setdefault("name", "Линза")
            ln.setdefault("desc", "")
            ln.setdefault("current", 0)
            ln.setdefault("max", 12)
            ln.setdefault("show_on_panel", False)
            app.c.lenses.append(ln)
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



def _lens_dialog(app, idx, rebuild):
    c = app.c
    is_new = idx is None
    if is_new:
        ln = {"name": "", "desc": "", "current": 0,
              "max": 12, "show_on_panel": False}
        c.lenses.append(ln)
        idx = len(c.lenses) - 1
    else:
        ln = c.lenses[idx]
    d = open_window(app, "Новая линза" if is_new else f"Линза: {ln.get('name','?')}", 520, 560)

    tk.Label(d, text="Название:", font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(10, 0))
    e_name = tk.Entry(d, font=("Segoe UI", 11))
    e_name.insert(0, ln.get("name", ""))
    e_name.pack(fill="x", padx=10)

    tk.Label(d, text="Описание:", font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(8, 0))
    t_desc = tk.Text(d, font=("Segoe UI", 10), height=6, wrap="word")
    t_desc.pack(fill="both", expand=True, padx=10)
    t_desc.insert("1.0", ln.get("desc", ""))

    fr_cm = tk.Frame(d)
    fr_cm.pack(fill="x", padx=10, pady=6)
    tk.Label(fr_cm, text="Текущее:",
             font=("Segoe UI", 10)).pack(side="left")
    cur_var = tk.IntVar(value=ln.get("current", 0))
    tk.Spinbox(fr_cm, from_=0, to=9999, textvariable=cur_var,
                width=6).pack(side="left", padx=4)
    tk.Label(fr_cm, text=" Максимум:",
             font=("Segoe UI", 10)).pack(side="left")
    max_var = tk.IntVar(value=ln.get("max", 12))
    tk.Spinbox(fr_cm, from_=0, to=9999, textvariable=max_var,
                width=6).pack(side="left", padx=4)

    panel_var = tk.BooleanVar(value=ln.get("show_on_panel", False))
    tk.Checkbutton(d, text="Показывать чип на панели",
                    variable=panel_var).pack(anchor="w", padx=10, pady=4)

    def save():
        ln["name"] = e_name.get().strip() or "Линза"
        ln["desc"] = t_desc.get("1.0", "end").strip()
        ln["current"] = max(0, int(cur_var.get() or 0))
        ln["max"] = max(0, int(max_var.get() or 0))
        ln["show_on_panel"] = panel_var.get()
        rebuild()
        d.destroy()

    def cancel():
        if is_new:
            c.lenses.pop(idx)
        d.destroy()

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=8, padx=10)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена", command=cancel
              ).pack(side="right")


def _lens_delete(app, idx, rebuild):
    if not messagebox.askyesno("Удалить", "Удалить линзу?"):
        return
    app.c.lenses.pop(idx)
    rebuild()


def _section(parent, title):
    f = tk.Frame(parent, bg="#c8c8c8")
    f.pack(fill="x", pady=(10, 2))
    tk.Label(f, text=title, font=("Segoe UI", 11, "bold"),
             bg="#c8c8c8", anchor="w", padx=8).pack(fill="x")


def _hint(parent, text):
    f = tk.Frame(parent, bg="#e8e8e8", pady=6, padx=8)
    f.pack(fill="x", padx=5, pady=4)
    tk.Label(f, text=text, bg="#e8e8e8",
             justify="left", wraplength=780,
             font=("Segoe UI", 9)).pack(anchor="w")


# ============ ДРАЙВЫ / КВЕСТЫ ============

DRIVES_RULES_URL = "https://example.com/drives"  # заглушка


def edit_drives(app):
    if not app.c:
        return

    def build(parent):
        c = app.c

        top = tk.Frame(parent, bg="#f4f4f4", pady=4, padx=6)
        top.pack(fill="x")
        tk.Button(top, text="📖 Правила драйвов (заглушка)",
                  command=lambda: _show_rules(app),
                  bg="#446", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="left", padx=2)
        tk.Label(top, text="  (ссылка появится позже)",
                 bg="#f4f4f4", fg="#888",
                 font=("Segoe UI", 9, "italic")
                 ).pack(side="left")

        outer, canvas, body = make_scrollable(parent)
        outer.pack(fill="both", expand=True, padx=4, pady=4)

        def rebuild():
            for w in body.winfo_children():
                w.destroy()
            _build_drives_body(app, body, rebuild)

        rebuild()

    app._show_editor("Драйвы / Квесты", build)


def _build_drives_body(app, body, rebuild):
    c = app.c

    # ----- Сводка -----
    summary = tk.Frame(body, bg="#e8e8e8", pady=6, padx=8)
    summary.pack(fill="x", padx=5, pady=4)
    total = c.drives_total()
    cycle = c.attention_per_cycle()
    lbl_total = tk.Label(summary,
             text=f"Распределено очков драйвов: {total} "
                  f"(на старте — 12)",
             bg="#e8e8e8", font=("Segoe UI", 10, "bold"))
    lbl_total.pack(anchor="w")
    lbl_crazy = None
    crazy = c.drives_at_crazy()
    if crazy:
        names = [dict(DRIVE_KEYS).get(k, k) for k in crazy]
        lbl_crazy = tk.Label(summary,
                 text=f"⚠ Драйвы 5 (мания): "
                      f"{', '.join(names)}",
                 bg="#e8e8e8", fg="#cc3333",
                 font=("Segoe UI", 10, "bold"))
        lbl_crazy.pack(anchor="w")
    lbl_cycle = tk.Label(summary,
             text=f"Внимание за цикл: {cycle}  "
                  f"(1 + {c.level}//3 + драйвы 4+)",
             bg="#e8e8e8", fg="#4a7",
             font=("Segoe UI", 10))
    lbl_cycle.pack(anchor="w")
    # T-B5: сохраняем лейблы для точечного обновления.
    app._drives_summary_lbl = {
        "frame": summary,
        "total": lbl_total,
        "crazy": lbl_crazy,
        "cycle": lbl_cycle,
    }

    # ----- Драйвы -----
    _section(body, "Драйвы (0-5)")
    for key, ru in DRIVE_KEYS:
        _drive_row(app, body, key, ru, rebuild)

    # ----- Принципы -----
    _section(body, "Принципы / Табу (для драйвов 2+)")
    _hint(body,
           "Каждый принцип привязан к драйву 2+. "
           "Название + описание. Игрок сам определяет условия.")
    _build_principles(app, body, rebuild)

    # ----- Квесты от Драйвов (T16) -----
    _section(body, "Квесты от Драйвов (для драйвов 3+)")
    _hint(body,
           "Квест привязан к драйву 3+. Название + описание. "
           "Попадает в court_quests с source='drive'.")
    _build_drive_quests(app, body, rebuild)

def _ensure_drive_extras(c, drive_key, old_v, new_v):
    """T16: авто-создание пустых принципа (2+) / квеста (3+).
    При уменьшении — не удалять. При увеличении — не дублировать."""
    # Принцип (2+)
    if new_v >= 2 and old_v < 2:
        has = any(p.get("drive_key") == drive_key
                  for p in c.drive_principles)
        if not has:
            c.drive_principles.append({
                "drive_key": drive_key,
                "name": "(пустой принцип)",
                "desc": "",
            })
    # Квест (3+)
    if new_v >= 3 and old_v < 3:
        has = any(q.get("drive_key") == drive_key
                  and q.get("source") == "drive"
                  for q in c.court_quests)
        if not has:
            c.court_quests.append({
                "drive_key": drive_key,
                "name": "(пустой квест)",
                "desc": "",
                "source": "drive",
                "court": "",
                "show_on_panel": False,
            })

def _drive_row(app, parent, key, ru, rebuild):
    c = app.c
    val = c.drives.get(key, 0)

    fr = tk.Frame(parent, bg="#f4f4f4", pady=2)
    fr.pack(fill="x", padx=5, pady=1)

    tk.Label(fr, text=ru, bg="#f4f4f4",
             font=("Segoe UI", 10, "bold"),
             width=18, anchor="w").pack(side="left")

    # Стрелки + спинбокс + уровень
    var = tk.IntVar(value=val)

    def on_change(*args):
        try:
            v = max(0, min(5, var.get()))
            old_v = c.drives.get(key, 0)
            c.drives[key] = v
            var.set(v)
            _update_bonus_label(lbl_bonus, v)
            _ensure_drive_extras(c, key, old_v, v)
            _update_drives_summary(app, rebuild)
        except Exception:
            pass
    var.trace_add("write", on_change)

    tk.Button(fr, text="−", width=2,
              command=lambda: var.set(max(0, var.get() - 1))
              ).pack(side="left", padx=1)
    tk.Spinbox(fr, from_=0, to=5, textvariable=var, width=4
                ).pack(side="left", padx=2)
    tk.Button(fr, text="+", width=2,
              command=lambda: var.set(min(5, var.get() + 1))
              ).pack(side="left", padx=1)

    level_ru = DRIVE_LEVEL_NAMES.get(val, "")
    tk.Label(fr, text=f"  {level_ru}",
             bg="#f4f4f4", fg="#666",
             font=("Segoe UI", 9)
             ).pack(side="left", padx=6)

    lbl_bonus = tk.Label(fr, text="", bg="#f4f4f4",
                          font=("Segoe UI", 9, "bold"))
    lbl_bonus.pack(side="left", padx=6)
    _update_bonus_label(lbl_bonus, val)


def _update_bonus_label(lbl, val):
    if val >= 5:
        lbl.config(text="Принцип, Квест, +1 Внимание, "
                        "⚠ сходите с ума! + можно тратить дух",
                    fg="#cc0000")
    elif val == 4:
        lbl.config(text="Принцип, Квест, +1 Внимание "
                        "+ можно тратить дух",
                    fg="#c06000")
    elif val == 3:
        lbl.config(text="Принцип, Квест + можно тратить дух",
                    fg="#446")
    elif val == 2:
        lbl.config(text="Принцип + можно тратить дух",
                    fg="#666")
    else:
        lbl.config(text="")


def _update_drives_summary(app, rebuild):
    """T-B5: обновляет только summary-лейблы, без полного rebuild.
    Если не удалось — fallback на rebuild."""
    try:
        c = app.c
        if not hasattr(app, "_drives_summary_lbl"):
            rebuild()
            return
        total = c.drives_total()
        cycle = c.attention_per_cycle()
        app._drives_summary_lbl["total"].config(
            text=f"Распределено очков драйвов: {total} "
                 f"(на старте — 12)")
        crazy = c.drives_at_crazy()
        crazy_lbl = app._drives_summary_lbl.get("crazy")
        if crazy:
            names = [dict(DRIVE_KEYS).get(k, k) for k in crazy]
            txt = f"⚠ Драйвы 5 (мания): {', '.join(names)}"
            if crazy_lbl is None:
                crazy_lbl = tk.Label(
                    app._drives_summary_lbl["frame"],
                    text=txt, bg="#e8e8e8", fg="#cc3333",
                    font=("Segoe UI", 10, "bold"))
                crazy_lbl.pack(anchor="w")
                app._drives_summary_lbl["crazy"] = crazy_lbl
            else:
                crazy_lbl.config(text=txt)
        else:
            if crazy_lbl is not None:
                crazy_lbl.destroy()
                app._drives_summary_lbl["crazy"] = None
        app._drives_summary_lbl["cycle"].config(
            text=f"Внимание за цикл: {cycle}  "
                 f"(1 + {c.level}//3 + драйвы 4+)")
    except Exception:
        rebuild()

def _build_drive_quests(app, body, rebuild):
    """T16: квесты от драйвов (в court_quests, source='drive')."""
    c = app.c
    top = tk.Frame(body, bg="#f4f4f4", pady=3)
    top.pack(fill="x", padx=5)
    tk.Button(top, text="＋ Добавить квест от драйва",
              command=lambda: _drive_quest_dialog(app, None, rebuild),
              bg="#4a7", fg="white",
              font=("Segoe UI", 9, "bold")
              ).pack(side="left", padx=2)

    drive_quests = [q for q in c.court_quests
                    if q.get("source") == "drive"]
    if not drive_quests:
        tk.Label(body, text="(квестов от драйвов нет)",
                 bg="#f4f4f4", fg="#888",
                 font=("Segoe UI", 10, "italic")
                 ).pack(anchor="w", padx=15, pady=6)
        return
    for i, q in enumerate(c.court_quests):
        if q.get("source") != "drive":
            continue
        row = tk.Frame(body, bg="#f8f8f8",
                        relief="solid", borderwidth=1)
        row.pack(fill="x", padx=5, pady=1)
        info = tk.Frame(row, bg="#f8f8f8")
        info.pack(side="left", fill="x", expand=True,
                   padx=4, pady=2)
        dk = q.get("drive_key", "")
        dr = dict(DRIVE_KEYS).get(dk, "?")
        lvl = c.drives.get(dk, 0)
        tk.Label(info,
                 text=f"• [{dr} {lvl}] {q.get('name','?')}",
                 bg="#f8f8f8",
                 font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(anchor="w")
        if q.get("desc"):
            tk.Label(info, text=q["desc"][:100],
                     bg="#f8f8f8", fg="#666",
                     font=("Segoe UI", 8),
                     anchor="w").pack(anchor="w")
        btns = tk.Frame(row, bg="#f8f8f8")
        btns.pack(side="right", padx=4)
        tk.Button(btns, text="✎", width=2,
                  command=lambda idx=i: _drive_quest_dialog(
                      app, idx, rebuild)
                  ).pack(side="left", padx=1)
        tk.Button(btns, text="✖", width=2,
                  command=lambda idx=i: _delete_drive_quest(
                      app, idx, rebuild)
                  ).pack(side="left", padx=1)


def _drive_quest_dialog(app, idx, rebuild):
    """T16: диалог квеста от драйва."""
    c = app.c
    is_new = idx is None
    if is_new:
        q = {"name": "", "desc": "", "drive_key": "idealism",
             "source": "drive", "court": "",
             "show_on_panel": False}
        c.court_quests.append(q)
        idx = len(c.court_quests) - 1
    else:
        q = c.court_quests[idx]

    d = open_window(app, "Новый квест от драйва" if is_new
            else f"Квест: {q.get('name', '?')}", 540, 500)

    tk.Label(d, text="Драйв (3+):",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(8, 0))
    drive_var = tk.StringVar(value=q.get("drive_key", "idealism"))
    drive_keys = [k for k, _ in DRIVE_KEYS]
    drive_names = {k: ru for k, ru in DRIVE_KEYS}
    om = tk.OptionMenu(d, drive_var, *drive_keys)
    om.config(width=25)
    om.pack(anchor="w", padx=10)

    def _upd(*args):
        om.config(text=drive_names.get(drive_var.get(),
                                         drive_var.get()))
    drive_var.trace_add("write", _upd)
    _upd()

    lvl_lbl = tk.Label(d, text="", fg="#c06000",
                        font=("Segoe UI", 9, "italic"))
    lvl_lbl.pack(anchor="w", padx=10)

    def _upd_lvl(*args):
        lvl = c.drives.get(drive_var.get(), 0)
        if lvl < 3:
            lvl_lbl.config(
                text=f"⚠ у драйва сейчас уровень {lvl}, "
                     f"квесты положены для 3+",
                fg="#cc3333")
        else:
            lvl_lbl.config(
                text=f"Уровень драйва: {lvl}", fg="#666")
    drive_var.trace_add("write", _upd_lvl)
    _upd_lvl()

    tk.Label(d, text="Название квеста:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(10, 0))
    e_name = tk.Entry(d, font=("Segoe UI", 11))
    e_name.insert(0, q.get("name", ""))
    e_name.pack(fill="x", padx=10)

    tk.Label(d, text="Описание:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(10, 0))
    t_desc = tk.Text(d, font=("Segoe UI", 10), height=6,
                      wrap="word")
    t_desc.pack(fill="both", expand=True, padx=10)
    t_desc.insert("1.0", q.get("desc", ""))

    show_var = tk.BooleanVar(value=q.get("show_on_panel", False))
    tk.Checkbutton(d, text="Показывать в быстром доступе",
                    variable=show_var
                    ).pack(anchor="w", padx=10, pady=6)

    def save():
        q["drive_key"] = drive_var.get()
        q["name"] = e_name.get().strip() or "Без названия"
        q["desc"] = t_desc.get("1.0", "end").strip()
        q["source"] = "drive"
        q["show_on_panel"] = show_var.get()
        rebuild()
        d.destroy()

    def cancel():
        if is_new:
            c.court_quests.pop(idx)
        d.destroy()

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=8, padx=10)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=cancel).pack(side="right")


def _delete_drive_quest(app, idx, rebuild):
    if not messagebox.askyesno("Удалить",
                                 "Удалить квест от драйва?"):
        return
    app.c.court_quests.pop(idx)
    rebuild()

def _build_principles(app, body, rebuild):
    c = app.c
    top = tk.Frame(body, bg="#f4f4f4", pady=3)
    top.pack(fill="x", padx=5)
    tk.Button(top, text="＋ Добавить принцип",
              command=lambda: _principle_dialog(app, None, rebuild),
              bg="#4a7", fg="white",
              font=("Segoe UI", 9, "bold")
              ).pack(side="left", padx=2)

    if not c.drive_principles:
        tk.Label(body, text="(принципов нет)",
                 bg="#f4f4f4", fg="#888",
                 font=("Segoe UI", 10, "italic")
                 ).pack(anchor="w", padx=15, pady=6)
        return

    for i, p in enumerate(c.drive_principles):
        row = tk.Frame(body, bg="#f8f8f8",
                        relief="solid", borderwidth=1)
        row.pack(fill="x", padx=5, pady=1)
        info = tk.Frame(row, bg="#f8f8f8")
        info.pack(side="left", fill="x", expand=True,
                   padx=4, pady=2)
        drive_key = p.get("drive_key", "")
        drive_ru = dict(DRIVE_KEYS).get(drive_key, "?")
        lvl = c.drives.get(drive_key, 0)
        tk.Label(info,
                 text=f"• [{drive_ru} {lvl}] "
                      f"{p.get('name','?')}",
                 bg="#f8f8f8",
                 font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(anchor="w")
        if p.get("desc"):
            tk.Label(info, text=p["desc"][:100],
                     bg="#f8f8f8", fg="#666",
                     font=("Segoe UI", 8),
                     anchor="w").pack(anchor="w")

        btns = tk.Frame(row, bg="#f8f8f8")
        btns.pack(side="right", padx=4)
        tk.Button(btns, text="✎", width=2,
                  command=lambda idx=i: _principle_dialog(
                      app, idx, rebuild)
                  ).pack(side="left", padx=1)
        tk.Button(btns, text="✖", width=2,
                  command=lambda idx=i: _delete_principle(
                      app, idx, rebuild)
                  ).pack(side="left", padx=1)


def _principle_dialog(app, idx, rebuild):
    c = app.c
    is_new = idx is None
    if is_new:
        p = {"drive_key": "idealism", "name": "", "desc": ""}
        c.drive_principles.append(p)
        idx = len(c.drive_principles) - 1
    else:
        p = c.drive_principles[idx]

    d = open_window(app, "Новый принцип" if is_new
            else f"Принцип: {p.get('name', '?')}", 540, 460)

    tk.Label(d, text="Драйв (2+):",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(8, 0))
    drive_var = tk.StringVar(value=p.get("drive_key", "idealism"))
    drive_keys = [k for k, _ in DRIVE_KEYS]
    drive_names = {k: ru for k, ru in DRIVE_KEYS}
    om = tk.OptionMenu(d, drive_var, *drive_keys)
    om.config(width=25)
    om.pack(anchor="w", padx=10)

    def _upd(*args):
        om.config(text=drive_names.get(drive_var.get(),
                                         drive_var.get()))
    drive_var.trace_add("write", _upd)
    _upd()

    lvl_lbl = tk.Label(d, text="", fg="#c06000",
                        font=("Segoe UI", 9, "italic"))
    lvl_lbl.pack(anchor="w", padx=10)

    def _upd_lvl(*args):
        lvl = c.drives.get(drive_var.get(), 0)
        if lvl < 2:
            lvl_lbl.config(
                text=f"⚠ у драйва сейчас уровень {lvl}, "
                     f"принципы положены для 2+",
                fg="#cc3333")
        else:
            lvl_lbl.config(
                text=f"Уровень драйва: {lvl}",
                fg="#666")
    drive_var.trace_add("write", _upd_lvl)
    _upd_lvl()

    tk.Label(d, text="Название принципа:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(10, 0))
    e_name = tk.Entry(d, font=("Segoe UI", 11))
    e_name.insert(0, p.get("name", ""))
    e_name.pack(fill="x", padx=10)

    tk.Label(d, text="Описание / условия:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(10, 0))
    t_desc = tk.Text(d, font=("Segoe UI", 10), height=6,
                      wrap="word")
    t_desc.pack(fill="both", expand=True, padx=10)
    t_desc.insert("1.0", p.get("desc", ""))

    def save():
        p["drive_key"] = drive_var.get()
        p["name"] = e_name.get().strip() or "Без названия"
        p["desc"] = t_desc.get("1.0", "end").strip()
        rebuild()
        d.destroy()

    def cancel():
        if is_new:
            c.drive_principles.pop(idx)
        d.destroy()

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=8, padx=10)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=cancel).pack(side="right")


def _delete_principle(app, idx, rebuild):
    if not messagebox.askyesno(
            "Удалить принцип",
            "Точно удалить принцип?"):
        return
    app.c.drive_principles.pop(idx)
    rebuild()


def _show_rules(app):
    d = open_window(app, "Правила драйвов (кратко)", 700, 600, mode="center")

    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True)

    text = (
        "У каждого персонажа есть мотивация, ради которой он "
        "стал авантюристом. Она распределяется по десяти "
        "драйвам, каждый от 0 до 5.\n\n"
        "0 — низкая (нет потребности)\n"
        "1 — средняя (слабый интерес)\n"
        "2 — высокая (нужен принцип/табу, можно тратить дух "
        "на +1 к броскам)\n"
        "3 — очень высокая (нужен квест + принцип, +2 к броскам, "
        "выполнение даёт комфорт, -1 мощь истории/цикл)\n"
        "4 — экстремальная (+3 к броскам, +1 внимание, "
        "-2 мощи/цикл)\n"
        "5 — мания (неиграбельно при долгом удержании)\n\n"
        "На старте — 12 очков.\n\n"
        "Понизить драйв: 2 комфорта. Повысить: 3 комфорта.\n"
        "При получении уровня случайный драйв ±1.\n\n"
        "Драйвы (список):\n" +
        "\n".join(f"• {ru}" for _, ru in DRIVE_KEYS)
    )
    tk.Label(body, text=text, bg="#f4f4f4",
             justify="left", wraplength=650,
             font=("Segoe UI", 10),
             anchor="w").pack(anchor="w", padx=10, pady=10)

    tk.Button(body, text="Закрыть",
              command=d.destroy).pack(pady=8)


# ============ КВИРКИ / ДВОРЫ / КВЕСТЫ ============

def edit_courts(app):
    if not app.c:
        return

    def build(parent):
        c = app.c
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=5, pady=5)

        # Вкладка 1: Дворы и Квесты
        t1_outer, _, t1 = make_scrollable(nb)
        nb.add(t1_outer, text="Дворы и Квесты")
        _build_courts_tab(app, t1)

        # Вкладка 2: Квирки
        t2_outer, _, t2 = make_scrollable(nb)
        nb.add(t2_outer, text="Квирки")
        _build_quirks_tab(app, t2)

        # Вкладка 3: Зёрна
        t3_outer, _, t3 = make_scrollable(nb)
        nb.add(t3_outer, text="Зёрна")
        _build_seeds_tab(app, t3)

    app._show_editor("Квирки / Дворы / Квесты", build)


def _build_courts_tab(app, parent):
    c = app.c

    # ===== Дворы =====
    _section(parent, "Дворы")
    top = tk.Frame(parent, bg="#f4f4f4", pady=3)
    top.pack(fill="x", padx=5)
    tk.Button(top, text="＋ Добавить двор",
              command=lambda: _court_dialog(
                  app, None, lambda: _refresh_courts(
                      app, parent)),
              bg="#4a7", fg="white",
              font=("Segoe UI", 9, "bold")
              ).pack(side="left", padx=2)

    courts_body = tk.Frame(parent, bg="#f4f4f4")
    courts_body.pack(fill="x", padx=5, pady=2)

    def render_courts():
        for w in courts_body.winfo_children():
            w.destroy()
        if not c.courts:
            tk.Label(courts_body, text="(дворов нет)",
                     bg="#f4f4f4", fg="#888",
                     font=("Segoe UI", 10, "italic")
                     ).pack(anchor="w", padx=10, pady=4)
            return
        for i, ct in enumerate(c.courts):
            row = tk.Frame(courts_body, bg="#f8f8f8",
                            relief="solid", borderwidth=1)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=ct.get("name", "?"),
                     bg="#f8f8f8",
                     font=("Segoe UI", 10, "bold"),
                     width=24, anchor="w"
                     ).pack(side="left", padx=4, pady=2)
            tk.Label(row,
                     text=f"Репутация: {ct.get('reputation', 0)}",
                     bg="#f8f8f8", fg="#c06000",
                     font=("Segoe UI", 10),
                     width=18, anchor="w"
                     ).pack(side="left")
            tk.Label(row,
                     text=f"Тир {ct.get('tier', 'I')}",
                     bg="#f8f8f8", fg="#446",
                     font=("Segoe UI", 10, "bold"),
                     width=10, anchor="w"
                     ).pack(side="left")

            btns = tk.Frame(row, bg="#f8f8f8")
            btns.pack(side="right", padx=4)
            tk.Button(btns, text="✎", width=2,
                      command=lambda idx=i: _court_dialog(
                          app, idx, lambda: _refresh_courts(
                              app, parent))
                      ).pack(side="left", padx=1)
            tk.Button(btns, text="✖", width=2,
                      command=lambda idx=i: _delete_court(
                          app, idx, lambda: _refresh_courts(
                              app, parent))
                      ).pack(side="left", padx=1)

    def _refresh_courts(app_, parent_):
        # Просто пересобираем всё содержимое parent
        for w in parent_.winfo_children():
            w.destroy()
        _build_courts_tab(app_, parent_)

    render_courts()

    # ===== Задания =====
    _section(parent, "Задания")
    top2 = tk.Frame(parent, bg="#f4f4f4", pady=3)
    top2.pack(fill="x", padx=5)
    tk.Button(top2, text="＋ Добавить задание",
              command=lambda: _quest_dialog(
                  app, None, _refresh_courts, parent),
              bg="#4a7", fg="white",
              font=("Segoe UI", 9, "bold")
              ).pack(side="left", padx=2)

    quests_body = tk.Frame(parent, bg="#f4f4f4")
    quests_body.pack(fill="x", padx=5, pady=2)

    def render_quests():
        for w in quests_body.winfo_children():
            w.destroy()
        if not c.court_quests:
            tk.Label(quests_body, text="(заданий нет)",
                     bg="#f4f4f4", fg="#888",
                     font=("Segoe UI", 10, "italic")
                     ).pack(anchor="w", padx=10, pady=4)
            return
        for i, q in enumerate(c.court_quests):
            row = tk.Frame(quests_body, bg="#f8f8f8",
                            relief="solid", borderwidth=1)
            row.pack(fill="x", pady=1)
            panel_tag = " 📌" if q.get("show_on_panel") else ""
            nl = tk.Label(row,
                          text=f"• {q.get('name','?')}{panel_tag}",
                          bg="#f8f8f8",
                          font=("Segoe UI", 10, "bold"),
                          anchor="w")
            nl.pack(side="left", padx=4, pady=2)
            if q.get("desc"):
                from gui_shared import ToolTip
                ToolTip(nl, q["desc"])
            tk.Label(row, text=f"  [{q.get('court','?')}]",
                     bg="#f8f8f8", fg="#666",
                     font=("Segoe UI", 9)
                     ).pack(side="left", padx=4)

            btns = tk.Frame(row, bg="#f8f8f8")
            btns.pack(side="right", padx=4)
            tk.Button(btns, text="✎", width=2,
                      command=lambda idx=i: _quest_dialog(
                          app, idx, _refresh_courts, parent)
                      ).pack(side="left", padx=1)
            tk.Button(btns, text="✖", width=2,
                      command=lambda idx=i: _delete_quest(
                          app, idx, _refresh_courts, parent)
                      ).pack(side="left", padx=1)

    render_quests()


def _court_dialog(app, idx, refresh_fn):
    c = app.c
    is_new = idx is None
    if is_new:
        ct = {"name": "", "reputation": 0, "tier": "I"}
        c.courts.append(ct)
        idx = len(c.courts) - 1
    else:
        ct = c.courts[idx]

    d = open_window(app, "Новый двор" if is_new
            else f"Двор: {ct.get('name', '?')}", 500, 400)

    tk.Label(d, text="Название двора:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(10, 0))
    e_name = tk.Entry(d, font=("Segoe UI", 11))
    e_name.insert(0, ct.get("name", ""))
    e_name.pack(fill="x", padx=10)

    fr_rep = tk.Frame(d)
    fr_rep.pack(fill="x", padx=10, pady=8)
    tk.Label(fr_rep, text="Репутация:",
             font=("Segoe UI", 10, "bold")).pack(side="left")
    rep_var = tk.IntVar(value=ct.get("reputation", 0))
    tk.Spinbox(fr_rep, from_=-100, to=100,
                textvariable=rep_var, width=6
                ).pack(side="left", padx=6)

    fr_tier = tk.Frame(d)
    fr_tier.pack(fill="x", padx=10, pady=4)
    tk.Label(fr_tier, text="Тир:",
             font=("Segoe UI", 10, "bold")).pack(side="left")
    tier_var = tk.StringVar(value=ct.get("tier", "I"))
    for t in COURT_TIERS:
        tk.Radiobutton(fr_tier, text=t, value=t,
                        variable=tier_var).pack(side="left",
                                                 padx=4)

    def save():
        ct["name"] = e_name.get().strip() or "Без названия"
        ct["reputation"] = rep_var.get()
        ct["tier"] = tier_var.get()
        refresh_fn()
        d.destroy()

    def cancel():
        if is_new:
            c.courts.pop(idx)
        d.destroy()

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=8, padx=10)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=cancel).pack(side="right")


def _delete_court(app, idx, refresh_fn):
    if not messagebox.askyesno("Удалить",
                                 "Удалить двор?"):
        return
    app.c.courts.pop(idx)
    refresh_fn()


def _quest_dialog(app, idx, refresh_fn, parent):
    c = app.c
    is_new = idx is None
    if is_new:
        q = {"name": "", "court": "",
             "desc": "", "show_on_panel": False}
        c.court_quests.append(q)
        idx = len(c.court_quests) - 1
    else:
        q = c.court_quests[idx]

    d = open_window(app, "Новое задание" if is_new
            else f"Задание: {q.get('name', '?')}", 540, 500)

    tk.Label(d, text="Задание:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(10, 0))
    e_name = tk.Entry(d, font=("Segoe UI", 11))
    e_name.insert(0, q.get("name", ""))
    e_name.pack(fill="x", padx=10)

    tk.Label(d, text="Двор:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(8, 0))
    court_names = [ct.get("name", "?") for ct in c.courts]
    court_var = tk.StringVar(value=q.get("court", ""))
    if court_names:
        om = tk.OptionMenu(d, court_var, *court_names)
        om.config(width=30)
        om.pack(anchor="w", padx=10)
    else:
        tk.Label(d, text="(нет дворов — сначала добавь двор)",
                 fg="#cc3333",
                 font=("Segoe UI", 9, "italic")
                 ).pack(anchor="w", padx=10)

    tk.Label(d, text="Описание (видно при наведении):",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=10, pady=(8, 0))
    t_desc = tk.Text(d, font=("Segoe UI", 10), height=6,
                      wrap="word")
    t_desc.pack(fill="both", expand=True, padx=10)
    t_desc.insert("1.0", q.get("desc", ""))

    show_var = tk.BooleanVar(value=q.get("show_on_panel", False))
    tk.Checkbutton(d,
                    text="Показывать в быстром доступе (в панели сверху)",
                    variable=show_var
                    ).pack(anchor="w", padx=10, pady=6)

    def save():
        q["name"] = e_name.get().strip() or "Задание"
        q["court"] = court_var.get()
        q["desc"] = t_desc.get("1.0", "end").strip()
        q["show_on_panel"] = show_var.get()
        refresh_fn()
        d.destroy()

    def cancel():
        if is_new:
            c.court_quests.pop(idx)
        d.destroy()

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=8, padx=10)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=cancel).pack(side="right")


def _delete_quest(app, idx, refresh_fn, parent):
    if not messagebox.askyesno("Удалить",
                                 "Удалить задание?"):
        return
    app.c.court_quests.pop(idx)
    refresh_fn()


# ============ КВИРКИ (старая логика) ============

def _build_quirks_tab(app, parent):
    c = app.c
    top1 = tk.Frame(parent, bg="#f4f4f4")
    top1.pack(fill="x")
    body1 = tk.Frame(parent, bg="#f4f4f4")
    body1.pack(fill="both", expand=True)

    def rebuild_quirks():
        for w in body1.winfo_children():
            w.destroy()
        if not c.quirks:
            tk.Label(body1, text="(ростков нет)",
                     bg="#f4f4f4", fg="#888",
                     font=("Segoe UI", 10, "italic")
                     ).pack(pady=20)
            return
        for i, q in enumerate(c.quirks):
            row = tk.Frame(body1, bg="#f4f4f4")
            row.pack(fill="x", pady=2, padx=5)
            parts = [q.get("seed", ""), q.get("court", ""),
                     q.get("focus", "")]
            parts = [p for p in parts if p]
            prefix = f"[{'/'.join(parts)}] " if parts else ""
            nl = tk.Label(
                row,
                text=f"• {prefix}{q.get('name','(без имени)')}",
                bg="#f4f4f4",
                font=("Segoe UI", 10, "bold"),
                anchor="w", cursor="hand2")
            nl.pack(side="left", padx=4)
            if q.get("desc"):
                from gui_shared import ToolTip
                ToolTip(nl, q["desc"])
            tk.Button(row, text="✖", width=3,
                      command=lambda i=i: _quirk_delete(
                          app, i, rebuild_quirks)
                      ).pack(side="right", padx=2)
            tk.Button(row, text="✎", width=3,
                      command=lambda i=i: _quirk_dialog(
                          app, i, rebuild_quirks)
                      ).pack(side="right", padx=2)

    def add_quirk():
        c.quirks.append({"seed": "", "court": "", "focus": "",
                         "name": "Новый росток", "desc": "",
                         "source": "quirk"})
        idx = len(c.quirks) - 1
        _quirk_dialog(app, idx, rebuild_quirks)

    tk.Button(top1, text="＋ Добавить росток",
              command=add_quirk).pack(side="left", padx=5, pady=4)
    rebuild_quirks()


def _quirk_dialog(app, idx, refresh):
    c = app.c
    if idx < 0 or idx >= len(c.quirks):
        return
    q = c.quirks[idx]
    d = open_window(app, "Росток", 520, 640)
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)
    fields = {}
    for key, label in [
            ("seed", "1. Зерно:"),
            ("court", "2. Двор:"),
            ("focus", "3. Фокус:"),
            ("name", "4. Название квирка:")]:
        tk.Label(body, text=label).pack(anchor="w", padx=5,
                                         pady=(6, 0))
        e = tk.Entry(body, font=("Segoe UI", 11))
        e.insert(0, q.get(key, ""))
        e.pack(fill="x", padx=5)
        fields[key] = e
    tk.Label(body, text="5. Описание работы:").pack(anchor="w",
                                                     padx=5,
                                                     pady=(6, 0))
    t = tk.Text(body, font=("Segoe UI", 10), height=8, wrap="word")
    t.pack(fill="both", expand=True, padx=5)
    t.insert("1.0", q.get("desc", ""))

    def save():
        name = fields["name"].get().strip()
        if not name:
            messagebox.showwarning("Внимание",
                                    "Введите название квирка",
                                    parent=d)
            return
        for k, e in fields.items():
            q[k] = e.get().strip()
        q["desc"] = t.get("1.0", "end").strip()
        refresh()
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=d.destroy).pack(side="right")


def _quirk_delete(app, idx, refresh):
    if not messagebox.askyesno(
            "Удалить",
            f"Удалить росток "
            f"'{app.c.quirks[idx].get('name','?')}'?"):
        return
    app.c.quirks.pop(idx)
    refresh()


# ============ ЗЁРНА ============

def _build_seeds_tab(app, parent):
    c = app.c
    top2 = tk.Frame(parent, bg="#f4f4f4")
    top2.pack(fill="x")
    body2 = tk.Frame(parent, bg="#f4f4f4")
    body2.pack(fill="both", expand=True)
    seeds = c.seeds

    def rebuild_seeds():
        for w in body2.winfo_children():
            w.destroy()
        if not seeds:
            tk.Label(body2, text="(зёрен нет)",
                     bg="#f4f4f4", fg="#888",
                     font=("Segoe UI", 10, "italic")
                     ).pack(pady=20)
            return
        for i, s in enumerate(seeds):
            row = tk.Frame(body2, bg="#f4f4f4")
            row.pack(fill="x", pady=2, padx=5)
            e = tk.Entry(row, font=("Segoe UI", 10))
            e.insert(0, s.get("name", ""))
            e.pack(side="left", fill="x", expand=True, padx=4)

            def _on_change(event=None, i=i, entry=e):
                seeds[i]["name"] = entry.get()
            e.bind("<KeyRelease>", _on_change)
            e.bind("<FocusOut>", _on_change)
            tk.Button(row, text="✖", width=3,
                      command=lambda i=i: (
                          seeds.pop(i), rebuild_seeds())
                      ).pack(side="right", padx=2)

    def add_seed():
        seeds.append({"name": ""})
        rebuild_seeds()
        try:
            last_row = body2.winfo_children()[-1]
            entry = last_row.winfo_children()[0]
            entry.focus_set()
        except Exception:
            pass

    tk.Button(top2, text="＋ Добавить зерно",
              command=add_seed).pack(side="left", padx=5, pady=4)
    rebuild_seeds()