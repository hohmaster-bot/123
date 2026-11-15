# gui_spells.py — редактор заклинаний (v4)
# v4: цена мастерства "за одно улучшение" + формула
import webbrowser
import tkinter as tk
from tkinter import messagebox

from character import SOURCE_NAMES, SOURCE_ICONS
from gui_shared import ToolTip, make_scrollable
from gui_windows import open_window
import purchases as P


def edit_spells(app):
    if not app.c:
        return

    def build(parent):
        top = tk.Frame(parent, bg="#f4f4f4")
        top.pack(fill="x", pady=4)
        lbl_pts = tk.Label(top, text="", bg="#f4f4f4",
                           fg="#c06000",
                           font=("Segoe UI", 10, "bold"))
        lbl_pts.pack(side="right", padx=10)
        outer, canvas, body = make_scrollable(parent)
        outer.pack(fill="both", expand=True)
        pending = [None]

        def do_rebuild():
            pending[0] = None
            try:
                lbl_pts.config(text=f"Тренировок: "
                                    f"{app.c.training['available']}")
                for w in body.winfo_children():
                    w.destroy()
                if not app.c.spells:
                    tk.Label(body, text="(заклинаний нет)",
                             bg="#f4f4f4", fg="#888",
                             font=("Segoe UI", 10, "italic")
                             ).pack(pady=20)
                    return
                by_circle = {}
                for i, s in enumerate(app.c.spells):
                    by_circle.setdefault(s["circle"],
                                         []).append((i, s))
                for circle in sorted(by_circle.keys()):
                    hdr = tk.Frame(body, bg="#c8c8c8")
                    hdr.pack(fill="x", pady=(8, 2))
                    tk.Label(hdr, text=f"Круг {circle}",
                             bg="#c8c8c8",
                             font=("Segoe UI", 10, "bold"),
                             anchor="w", padx=6).pack(fill="x")
                    for idx, s in by_circle[circle]:
                        _spell_row(app, body, idx, s,
                                    schedule_refresh)
            except Exception as e:
                print(f"[spells rebuild] {e}")

        def schedule_refresh():
            if pending[0] is not None:
                try:
                    app.root.after_cancel(pending[0])
                except Exception:
                    pass
            pending[0] = app.root.after(30, do_rebuild)

        tk.Button(top, text="＋ Добавить заклинание",
                  command=lambda: _spell_dialog(app, None,
                                                 schedule_refresh)
                  ).pack(side="left", padx=5)
        tk.Button(top, text="📚 Из каталога",
                  command=lambda: _spell_from_catalog(app, schedule_refresh),
                  bg="#446", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="left", padx=5)
        do_rebuild()

    app._show_editor("Заклинания", build)


def _spell_row(app, parent, idx, s, rebuild):
    row = tk.Frame(parent, bg="#f4f4f4")
    row.pack(fill="x", pady=1, padx=5)

    src_name = SOURCE_NAMES.get(s.get("source", ""), "?")
    tk.Label(row, text=f"[{src_name}]", bg="#f4f4f4",
             font=("Consolas", 9), fg="#666").pack(side="left")

    link = s.get("link", "")
    from character import spell_display_name
    nl = tk.Label(row, text=spell_display_name(s), bg="#f4f4f4",
                  font=("Segoe UI", 10, "bold"),
                  fg="#0066cc" if link else "black",
                  cursor="hand2" if link else "arrow")
    nl.pack(side="left", padx=4)

    desc = s.get("desc", "")
    if desc or link:
        tip = desc + (f"\n\n🔗 {link}" if link else "")
        ToolTip(nl, tip)
    if link:
        nl.bind("<Button-1>", lambda e, u=link: webbrowser.open(u))

    # Звёзды мастерства
    masteries = s.get("masteries", [])
    stars_used = sum(m.get("stars", 1) for m in masteries)
    stars_str = "★" * stars_used + "☆" * (3 - stars_used)
    tk.Label(row, text=stars_str, bg="#f4f4f4", fg="#c06000",
             font=("Segoe UI", 11)).pack(side="left", padx=4)

    # Стоимость вложений
    inv = s.get("invested", 0)
    m_inv = sum(m.get("invested", 0) for m in masteries)
    inv_text = f"{inv} оч."
    if m_inv:
        inv_text += f" +маст.{m_inv}"
    tk.Label(row, text=inv_text, bg="#f4f4f4", fg="#c06000",
             font=("Segoe UI", 9)).pack(side="right", padx=5)

    tk.Button(row, text="✖", width=3,
              command=lambda: _spell_delete(app, s, rebuild)
              ).pack(side="right", padx=2)
    tk.Button(row, text="✎", width=3,
              command=lambda: _spell_dialog(app, s, rebuild)
              ).pack(side="right", padx=2)

    if masteries:
        tk.Button(row, text="★↓", width=4,
                  command=lambda: _spell_mastery_remove(
                      app, s, rebuild)
                  ).pack(side="right", padx=2)
    if stars_used < 3:
        cost = P.spell_mastery_cost(s["circle"])
        tk.Button(row, text=f"★↑ +1 ({cost})", width=11,
                  command=lambda: _spell_mastery_add(
                      app, s, rebuild)
                  ).pack(side="right", padx=2)

    # Строки мастерств под заклинанием
    for i, m in enumerate(masteries):
        mr = tk.Frame(parent, bg="#f9f9f9")
        mr.pack(fill="x", padx=20, pady=(0, 1))
        lbl = tk.Label(
            mr, text=f"    ⭐ {m.get('name','?')} "
                     f"({'★' * m.get('stars',1)})",
            bg="#f9f9f9", fg="#555",
            font=("Segoe UI", 9), anchor="w",
            cursor="hand2" if m.get("desc") else "arrow")
        lbl.pack(side="left", padx=4)
        if m.get("desc"):
            ToolTip(lbl, m["desc"])


def _spell_mastery_add(app, s, rebuild):
    masteries = s.get("masteries", [])
    stars_used = sum(m.get("stars", 1) for m in masteries)
    avail = 3 - stars_used
    if avail <= 0:
        return
    cost = P.spell_mastery_cost(s["circle"])
    circle = s["circle"]
    formula = f"25 × (1 + {circle}²) = {cost}"

    d = open_window(app, f"Мастерство: {s['name']}", 500, 600)
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)

    # Заголовок "Купить мастерство для 'X'?"
    tk.Label(body,
             text=f"Купить мастерство для \"{s['name']}\"?",
             font=("Segoe UI", 12, "bold"),
             fg="#2b2b2b", wraplength=460,
             justify="left").pack(anchor="w", padx=8, pady=(10, 4))

    tk.Label(body, text=f"Слотов свободно: {avail}/3",
             fg="#c06000",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=8, pady=(0, 8))

    # Название мастерства
    tk.Label(body, text="Название мастерства:").pack(anchor="w",
                                                       padx=8,
                                                       pady=(4, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    e_name.pack(fill="x", padx=8)

    # Описание
    tk.Label(body, text="Описание эффекта:").pack(anchor="w",
                                                    padx=8,
                                                    pady=(8, 0))
    t_desc = tk.Text(body, font=("Segoe UI", 10), height=5,
                      wrap="word")
    t_desc.pack(fill="both", expand=True, padx=8)

    # Стоимость в звёздах
    tk.Label(body,
             text=f"Стоимость в звёздах (1-{avail}):"
             ).pack(anchor="w", padx=8, pady=(8, 0))
    stars_var = tk.IntVar(value=1)
    fr_stars = tk.Frame(body)
    fr_stars.pack(fill="x", padx=8)
    for i in range(1, avail + 1):
        tk.Radiobutton(fr_stars, text=f"★{i}", value=i,
                       variable=stars_var).pack(side="left", padx=4)

    # Цена за одно улучшение + формула
    price_frame = tk.Frame(body, bg="#e8e8e8",
                            pady=6, padx=8)
    price_frame.pack(fill="x", padx=8, pady=(8, 4))
    tk.Label(price_frame,
             text=f"Цена: {cost} очков за одно улучшение",
             bg="#e8e8e8", fg="#c06000",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w")
    if not app.c.settings.get("hide_hints", False):
        tk.Label(price_frame,
                 text=f"(формула: {formula})",
                 bg="#e8e8e8", fg="#666",
                 font=("Segoe UI", 9, "italic")
                 ).pack(anchor="w")

    # Бесплатно
    free_var = tk.BooleanVar(value=False)
    tk.Checkbutton(body,
                    text="Бесплатно (за класс/расу/лут/квирк)",
                    variable=free_var).pack(anchor="w", padx=8,
                                             pady=(6, 0))

    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        try:
            stars = int(stars_var.get())
        except (tk.TclError, ValueError):
            stars = 1
        stars = max(1, min(stars, avail))
        desc = t_desc.get("1.0", "end").strip()
        src = "training"
        if free_var.get():
            pd = open_window(app, "Источник", 280, 300, mode="center")
            result = {"src": None}
            tk.Label(pd, text="Откуда?",
                     font=("Segoe UI", 11)).pack(pady=10)
            for sc in ["race", "class", "loot", "quirk", "template"]:
                tk.Button(pd,
                          text=f"[{SOURCE_ICONS[sc]}] "
                               f"{SOURCE_NAMES[sc]}",
                          width=20,
                          command=lambda v=sc: (
                              result.update({"src": v}),
                              pd.destroy())
                          ).pack(pady=3)
            tk.Button(pd, text="Отмена",
                      command=pd.destroy).pack(pady=10)
            app.root.wait_window(pd)
            if not result["src"]:
                return
            src = result["src"]
        try:
            P.buy_spell_mastery(app.c, s["name"], name, desc,
                                 stars, free=(src != "training"),
                                 source=src)
            try:
                d.grab_release()
            except Exception:
                pass
            rebuild()
            d.destroy()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e), parent=d)

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=8)
    tk.Button(bf, text="Купить", command=save, bg="#4a7",
              fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")


def _spell_mastery_remove(app, s, rebuild):
    masteries = s.get("masteries", [])
    if not masteries:
        return
    last = masteries[-1]
    inv = last.get("invested", 0)
    if inv > 0:
        ans = messagebox.askyesnocancel(
            "Снять мастерство",
            f"Снять '{last.get('name','?')}'?\n\n"
            f"Вложено: {inv}\n\n"
            f"Да — вернуть\nНет — без возврата")
        if ans is None:
            return
        try:
            P.remove_spell_mastery(app.c, s["name"],
                                    return_points=ans)
            rebuild()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e))
    else:
        if not messagebox.askyesno(
                "Снять мастерство",
                f"Снять '{last.get('name','?')}'?"):
            return
        try:
            P.remove_spell_mastery(app.c, s["name"],
                                    return_points=False)
            rebuild()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e))


def _spell_delete(app, s, rebuild):
    total = s.get("invested", 0) + sum(
        m.get("invested", 0) for m in s.get("masteries", []))
    if total > 0:
        ans = messagebox.askyesnocancel(
            "Удаление",
            f"Удалить '{s['name']}'?\n\nВложено: {total}\n\n"
            f"Да — вернуть {total}\nНет — без возврата")
        if ans is None:
            return
        P.remove_spell(app.c, s["name"], ans)
    else:
        if not messagebox.askyesno("Удаление",
                                    f"Удалить '{s['name']}'?"):
            return
        P.remove_spell(app.c, s["name"], False)
    rebuild()

def _spell_from_catalog(app, rebuild):
    """K2d: взять заклинание из SPELLS_CATALOG."""
    from character import SPELLS_CATALOG
    if not SPELLS_CATALOG:
        messagebox.showinfo("Каталог заклинаний пуст",
                             "Создай файл в catalogs/spells/ через "
                             "«📚 Каталоги» в инвентаре.",
                             parent=app.get_dialog_parent())
        return
    d = open_window(app, "Из каталога: заклинания", 700, 550)
    tk.Label(d, text="Выбери заклинание:",
             font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=6)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=4)

    for it in SPELLS_CATALOG:
        row = tk.Frame(body, bg="#f4f4f4", relief="solid", borderwidth=1)
        row.pack(fill="x", padx=2, pady=1)
        info = tk.Frame(row, bg="#f4f4f4")
        info.pack(side="left", fill="x", expand=True, padx=4, pady=2)
        circle = it.get("circle", 0)
        tk.Label(info, text=f"[Кр.{circle}] {it.get('name', '?')}",
                 bg="#f4f4f4", font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(anchor="w")
        if it.get("desc"):
            tk.Label(info, text=it["desc"][:100],
                     bg="#f4f4f4", fg="#666",
                     font=("Segoe UI", 8), anchor="w").pack(anchor="w")

        def _take(it=it):
            sp = dict(it)
            sp.setdefault("source", "loot")
            sp.setdefault("invested", 0)
            sp.setdefault("masteries", [])
            sp.setdefault("mastery", False)
            app.c.spells.append(sp)
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



def _spell_dialog(app, spell, rebuild):
    is_new = spell is None
    d = open_window(app, "Новое заклинание" if is_new else "Редактировать", 540, 640)
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="Название:").pack(anchor="w", padx=5,
                                            pady=(5, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    if spell:
        e_name.insert(0, spell["name"])
    e_name.pack(fill="x", padx=5)

    tk.Label(body, text="Круг (0-9):").pack(anchor="w", padx=5,
                                              pady=(5, 0))
    circle_var = tk.IntVar(value=spell["circle"] if spell else 1)
    tk.Spinbox(body, from_=0, to=9, textvariable=circle_var,
                width=6).pack(anchor="w", padx=5)

    tk.Label(body, text="Описание:").pack(anchor="w", padx=5,
                                            pady=(5, 0))
    t_desc = tk.Text(body, font=("Segoe UI", 10), height=6,
                      wrap="word")
    if spell:
        t_desc.insert("1.0", spell.get("desc", ""))
    t_desc.pack(fill="both", expand=True, padx=5)

    tk.Label(body, text="Ссылка:").pack(anchor="w", padx=5,
                                          pady=(5, 0))
    e_link = tk.Entry(body, font=("Segoe UI", 10))
    if spell:
        e_link.insert(0, spell.get("link", ""))
    e_link.pack(fill="x", padx=5)

    # ===== Задача C: боевые параметры =====
    from character import (CASTING_ACTIONS, SPELL_CIRCLE_TABLE,
                           SPELL_ATTACK_SUFFIX, SPELL_AOE_NAMES)

    tk.Label(body, text="Тип атаки:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    at_var = tk.StringVar(value=(spell or {}).get("attack_type", ""))
    fr_at = tk.Frame(body)
    fr_at.pack(fill="x", padx=5)
    for v, label in [("", "— нет атаки —"),
                     ("ranged", "Ranged"),
                     ("ranged_touch", "Ranged touch"),
                     ("melee", "Melee"),
                     ("melee_finesse", "MeleeF")]:
        tk.Radiobutton(fr_at, text=label, value=v,
                        variable=at_var).pack(side="left", padx=2)

    tk.Label(body, text="Дистанция:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    fr_rng = tk.Frame(body)
    fr_rng.pack(fill="x", padx=5)
    rt_var = tk.StringVar(value=(spell or {}).get("range_type", "long"))
    for v, label in [("short", "Короткая"),
                     ("medium", "Средняя"),
                     ("long", "Длинная"),
                     ("custom", "Своя")]:
        tk.Radiobutton(fr_rng, text=label, value=v,
                        variable=rt_var).pack(side="left", padx=2)
    rc_var = tk.StringVar(
        value=str((spell or {}).get("range_custom", 0)))
    tk.Label(fr_rng, text=" своя:", bg="#f4f4f4").pack(side="left", padx=(6, 2))
    tk.Entry(fr_rng, textvariable=rc_var, width=10
             ).pack(side="left")

    tk.Label(body, text="АоЕ:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    fr_aoe = tk.Frame(body)
    fr_aoe.pack(fill="x", padx=5)
    aoe_var = tk.BooleanVar(value=(spell or {}).get("is_aoe", False))
    tk.Checkbutton(fr_aoe, text="АоЕ", variable=aoe_var
                   ).pack(side="left")
    shape_var = tk.StringVar(value=(spell or {}).get("aoe_shape", ""))
    aoe_opts = ["", "burst", "cone", "cylinder", "emanation",
                "line", "sphere", "spread"]
    shape_om = tk.OptionMenu(fr_aoe, shape_var, *aoe_opts)
    shape_om.config(width=14)
    shape_om.pack(side="left", padx=4)
    size_var = tk.StringVar(
        value=str((spell or {}).get("aoe_size", "")))
    tk.Entry(fr_aoe, textvariable=size_var, width=8
             ).pack(side="left", padx=2)

    tk.Label(body, text="Время сотворения:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    fr_ct = tk.Frame(body)
    fr_ct.pack(fill="x", padx=5)
    ct_var = tk.StringVar(
        value=(spell or {}).get("casting_time", "standard"))
    ct_opts = [("swift", "Быстрое (0)"),
               ("immediate", "Немедл. (0)"),
               ("move", "Движение (1)"),
               ("standard", "Стандарт (2)"),
               ("full_round", "Полный (3)"),
               ("one_round", "1 раунд (4)")]
    ct_om = tk.OptionMenu(fr_ct, ct_var, *[v for v, _ in ct_opts])
    ct_om.config(width=14)
    ct_om.pack(side="left")

    # Перегрузка (авто + ручная)
    tk.Label(body, text="Мана / Баланс / Перегрузка / Круг слота:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    fr_num = tk.Frame(body)
    fr_num.pack(fill="x", padx=5)
    tk.Label(fr_num, text="мана:").pack(side="left")
    mana_var = tk.IntVar(value=(spell or {}).get("mana_cost", 0))
    tk.Spinbox(fr_num, from_=0, to=99, textvariable=mana_var,
                width=4).pack(side="left", padx=2)
    tk.Label(fr_num, text=" баланс:").pack(side="left")
    bal_var = tk.IntVar(value=(spell or {}).get("balance_cost", 0))
    tk.Spinbox(fr_num, from_=0, to=99, textvariable=bal_var,
                width=4).pack(side="left", padx=2)
    tk.Label(fr_num, text=" перегрузка:").pack(side="left")
    ov_var = tk.IntVar(value=(spell or {}).get("overload", 0))
    tk.Spinbox(fr_num, from_=0, to=99, textvariable=ov_var,
                width=4).pack(side="left", padx=2)
    tk.Button(fr_num, text="−", width=2,
              command=lambda: ov_var.set(max(0, ov_var.get() - 1))
              ).pack(side="left")
    tk.Button(fr_num, text="+", width=2,
              command=lambda: ov_var.set(ov_var.get() + 1)
              ).pack(side="left")
    tk.Label(fr_num, text=" круг слота:").pack(side="left")
    sc_var = tk.IntVar(
        value=(spell or {}).get("slot_circle",
                                 (spell or {}).get("circle", 0)))
    tk.Spinbox(fr_num, from_=0, to=9, textvariable=sc_var,
                width=3).pack(side="left", padx=2)

    panel_var = tk.BooleanVar(
        value=(spell or {}).get("show_on_panel", False))
    tk.Checkbutton(body, text="Показывать чип на панели",
                    variable=panel_var
                    ).pack(anchor="w", padx=5, pady=(6, 0))

    def _auto_fill_circle(*args):
        try:
            circle = int(circle_var.get())
        except Exception:
            return
        t = SPELL_CIRCLE_TABLE.get(circle, {})
        if t:
            mana_var.set(t["mana"])
            bal_var.set(t["balance"])
            ov_var.set(t["overload"])
            sc_var.set(circle)
    circle_var.trace_add("write", _auto_fill_circle)

    if is_new:
        free_var = tk.BooleanVar(value=False)
        tk.Checkbutton(body,
                        text="Бесплатно (за класс/расу/лут/квирк)",
                        variable=free_var).pack(anchor="w", padx=5,
                                                 pady=(8, 0))
    else:
        tk.Label(body,
                 text=f"Источник: "
                      f"{SOURCE_NAMES.get(spell.get('source',''),'?')}, "
                      f"вложено: {spell.get('invested',0)}\n"
                      f"Мастерства: через ★↑ в списке",
                 fg="#666", justify="left").pack(anchor="w",
                                                  padx=5, pady=3)
        free_var = None

    def _gi_int(var, default=0):
        try:
            return int(var.get())
        except (tk.TclError, ValueError):
            return default

    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        circle = _gi_int(circle_var, 1)
        desc = t_desc.get("1.0", "end").strip()
        link = e_link.get().strip()
        if is_new:
            if getattr(app, "force_free", False):
                app.c.spells.append({
                    "name": name, "circle": circle,
                    "desc": desc, "link": link,
                    "mastery_level": 0, "masteries": [],
                    "mastery": False,
                    "source": "loot", "invested": 0,
                    "attack_type": at_var.get(),
                    "range_type": rt_var.get(),
                    "range_custom": rc_var.get(),
                    "is_aoe": aoe_var.get(),
                    "aoe_shape": shape_var.get(),
                    "aoe_size": size_var.get(),
                    "casting_time": ct_var.get(),
                    "mana_cost": int(mana_var.get() or 0),
                    "balance_cost": int(bal_var.get() or 0),
                    "overload": int(ov_var.get() or 0),
                    "slot_circle": int(sc_var.get() or 0),
                    "show_on_panel": panel_var.get(),
                })
            else:
                src = "training"
                if free_var.get():
                    pd = open_window(app, "Источник", 280, 300, mode="center")
                    result = {"src": None}
                    tk.Label(pd, text="Откуда?",
                             font=("Segoe UI", 11)).pack(pady=10)
                    for sc in ["race", "class", "loot", "quirk",
                                "template"]:
                        tk.Button(pd,
                                  text=f"[{SOURCE_ICONS[sc]}] "
                                       f"{SOURCE_NAMES[sc]}",
                                  width=20,
                                  command=lambda v=sc: (
                                      result.update({"src": v}),
                                      pd.destroy())
                                  ).pack(pady=3)
                    tk.Button(pd, text="Отмена",
                              command=pd.destroy).pack(pady=10)
                    app.root.wait_window(pd)
                    if not result["src"]:
                        return
                    src = result["src"]
                try:
                    P.buy_spell(app.c, name, circle, src,
                                 desc=desc, link=link)
                except P.PurchaseError as e:
                    messagebox.showerror("Ошибка", str(e), parent=d)
                    return
        else:
            spell["name"] = name
            spell["circle"] = circle
            spell["desc"] = desc
            spell["link"] = link

        # Задача C: боевые параметры (для обеих веток)
        target_spell = spell if not is_new else app.c.spells[-1]
        if target_spell:
            target_spell["attack_type"] = at_var.get()
            target_spell["range_type"] = rt_var.get()
            try:
                rc_raw = rc_var.get().strip()
                target_spell["range_custom"] = (
                    int(rc_raw) if rc_raw.isdigit() else rc_raw)
            except Exception:
                target_spell["range_custom"] = 0
            target_spell["is_aoe"] = aoe_var.get()
            target_spell["aoe_shape"] = shape_var.get()
            try:
                as_raw = size_var.get().strip()
                target_spell["aoe_size"] = (
                    int(as_raw) if as_raw.isdigit() else as_raw)
            except Exception:
                target_spell["aoe_size"] = ""
            target_spell["casting_time"] = ct_var.get()
            target_spell["mana_cost"] = max(0, int(mana_var.get() or 0))
            target_spell["balance_cost"] = max(0, int(bal_var.get() or 0))
            target_spell["overload"] = max(0, int(ov_var.get() or 0))
            target_spell["slot_circle"] = max(0, int(sc_var.get() or 0))
            target_spell["show_on_panel"] = panel_var.get()
        try:
            d.grab_release()
        except Exception:
            pass
        rebuild()
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Сохранить", command=save, bg="#4a7",
              fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")