# gui_editors.py — редакторы (v12)
# v12: перегрузка, авто-баланс, тик/кулдаун в способностях,
#      ranged/thrown в редакторе атак

import math
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from character import (SOURCE_NAMES, SAVE_STATS, SKILL_TIER_NAMES,
                       WEAPON_LEVELS, WEAPON_BONUS_CATALOG)
from gui_shared import make_scrollable, ToolTip
from gui_windows import open_window
from gui_inventory import _row_entry
from gui_alphabet import BONUS_TYPE_NAMES
import gui_media
import gui_buttons
import purchases as P


# ============ Раса ============

def edit_race(app):
    if not app.c:
        return

    def build(parent):
        outer, canvas, body = make_scrollable(parent)
        outer.pack(fill="both", expand=True)
        c = app.c
        f = tk.Frame(body, bg="#f4f4f4")
        f.pack(fill="x", padx=5, pady=5)
        tk.Label(f, text="Название:", bg="#f4f4f4"
                 ).grid(row=0, column=0, sticky="w")
        e_name = tk.Entry(f)
        e_name.insert(0, c.race.get("name", ""))
        e_name.grid(row=0, column=1, sticky="we")
        tk.Label(f, text="Тип:", bg="#f4f4f4"
                 ).grid(row=1, column=0, sticky="w")
        e_type = tk.Entry(f)
        e_type.insert(0, c.race.get("type", ""))
        e_type.grid(row=1, column=1, sticky="we")
        tk.Label(f, text="Скорость:", bg="#f4f4f4"
                 ).grid(row=2, column=0, sticky="w")
        e_speed = tk.Entry(f)
        e_speed.insert(0, str(c.race.get("speed", 30)))
        e_speed.grid(row=2, column=1, sticky="we")
        f.grid_columnconfigure(1, weight=1)

        abil_hdr = tk.Frame(body, bg="#c8c8c8")
        abil_hdr.pack(fill="x", pady=(10, 2))
        tk.Label(abil_hdr, text="Способности расы:",
                 font=("Segoe UI", 11, "bold"), bg="#c8c8c8",
                 anchor="w", padx=6).pack(side="left", fill="x",
                                          expand=True)
        abil_body = tk.Frame(body, bg="#f4f4f4")
        abil_body.pack(fill="both", expand=True, padx=5, pady=4)

        def do_rebuild():
            for w in abil_body.winfo_children():
                w.destroy()
            abils = c.race.get("abilities", [])
            if not abils:
                tk.Label(abil_body, text="(нет способностей)",
                         bg="#f4f4f4", fg="#888",
                         font=("Segoe UI", 10, "italic")
                         ).pack(pady=10)
                return
            for i, a in enumerate(abils):
                row = tk.Frame(abil_body, bg="#f4f4f4")
                row.pack(fill="x", pady=1)
                uses_txt = ""
                if a.get("uses"):
                    uses_txt = (f" [{a.get('uses_current', 0)}/"
                                 f"{a.get('uses_max', 0)}]")
                panel_tag = ""
                if a.get("uses") and a.get("show_on_panel", True):
                    panel_tag = " 📌"
                nl = tk.Label(row,
                              text=f"• {a['name']}{uses_txt}{panel_tag}",
                              bg="#f4f4f4",
                              font=("Segoe UI", 10, "bold"),
                              anchor="w", cursor="hand2")
                nl.pack(side="left", padx=4)
                tip_parts = []
                if a.get("desc"): 
                    tip_parts.append(a["desc"])
                _effects = a.get("effects", [])
                if _effects:
                    from gui_alphabet import TARGET_NAMES as _TN
                    eff_lines = []
                    for e in _effects:
                        tgt = _TN.get(e.get("target"), e.get("target"))
                        val = e.get("value", 0)
                        btype = e.get("bonus_type", "flat")
                        eff_lines.append(f"{val:+d} {tgt} ({btype})")
                    tip_parts.append("Эффекты: " + ", ".join(eff_lines))
                if tip_parts:
                    ToolTip(nl, "\n\n".join(tip_parts))
                tk.Button(row, text="✖", width=3,
                          command=lambda i=i: (
                              c.race["abilities"].pop(i),
                              do_rebuild())
                          ).pack(side="right", padx=2)
                tk.Button(row, text="✎", width=3,
                          command=lambda i=i: _race_abil_edit(
                              app, i, do_rebuild)
                          ).pack(side="right", padx=2)

        def add_abil():
            c.race.setdefault("abilities", [])
            c.race["abilities"].append(
                {"name": "Новая способность", "desc": "",
                 "uses": False, "uses_current": 0, "uses_max": 0,
                 "show_on_panel": True,
                 "tick_mode": "none",
                 "cooldown_rounds": 0,
                 "cooldown_current": 0})
            idx = len(c.race["abilities"]) - 1
            _race_abil_edit(app, idx, do_rebuild)

        tk.Button(abil_hdr, text="＋ Создать абилку",
                  command=add_abil).pack(side="right", padx=4)
        tk.Button(abil_hdr, text="📚 Из каталога",
                  command=lambda: _race_abil_from_catalog(
                      app, do_rebuild),
                  bg="#446", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="right", padx=4)
        do_rebuild()

        def save():
            c.race["name"] = e_name.get().strip()
            c.race["type"] = e_type.get().strip()
            try:
                c.race["speed"] = int(e_speed.get() or 30)
            except Exception:
                pass
            app._show_main()

        tk.Button(body, text="Сохранить", command=save,
                  bg="#4a7", fg="white",
                  font=("Segoe UI", 10, "bold")).pack(pady=8)

    app._show_editor("Раса", build)

def _race_abil_from_catalog(app, rebuild):
    """K2e: взять абилку расы из RACE_ABILITIES_CATALOG."""
    from character import RACE_ABILITIES_CATALOG
    if not RACE_ABILITIES_CATALOG:
        messagebox.showinfo("Каталог абилок расы пуст",
                             "Создай файл в catalogs/race_abilities/.",
                             parent=app.get_dialog_parent())
        return
    d = open_window(app, "Из каталога: абилки расы", 700, 550)
    tk.Label(d, text="Выбери абилку:",
             font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=6)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=4)

    for it in RACE_ABILITIES_CATALOG:
        row = tk.Frame(body, bg="#f4f4f4", relief="solid", borderwidth=1)
        row.pack(fill="x", padx=2, pady=1)
        info = tk.Frame(row, bg="#f4f4f4")
        info.pack(side="left", fill="x", expand=True, padx=4, pady=2)
        buff_tag = " [баф]" if it.get("is_buff") else ""
        tk.Label(info, text=f"{it.get('name', '?')}{buff_tag}",
                 bg="#f4f4f4", font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(anchor="w")
        if it.get("desc"):
            tk.Label(info, text=it["desc"][:100],
                     bg="#f4f4f4", fg="#666",
                     font=("Segoe UI", 8), anchor="w").pack(anchor="w")

        def _take(it=it):
            a = dict(it)
            a.setdefault("name", "Способность")
            a.setdefault("desc", "")
            a.setdefault("uses", False)
            a.setdefault("uses_current", 0)
            a.setdefault("uses_max", 0)
            a.setdefault("show_on_panel", True)
            a.setdefault("tick_mode", "none")
            a.setdefault("cooldown_rounds", 0)
            a.setdefault("cooldown_current", 0)
            app.c.race.setdefault("abilities", []).append(a)
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


def _race_abil_edit(app, idx, refresh):
    c = app.c
    if idx < 0 or idx >= len(c.race.get("abilities", [])):
        return
    a = c.race["abilities"][idx]
    d = open_window(app, "Способность расы", 500, 720)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True)

    tk.Label(body, text="Название:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    e_name.insert(0, a.get("name", ""))
    e_name.pack(fill="x", padx=5)
    tk.Label(body, text="Описание:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    t = tk.Text(body, font=("Segoe UI", 10), wrap="word", height=6)
    t.pack(fill="both", expand=True, padx=5)
    t.insert("1.0", a.get("desc", ""))

    uses_var = tk.BooleanVar(value=a.get("uses", False))
    fr_uses = tk.Frame(body)
    fr_uses.pack(fill="x", padx=5, pady=(8, 0))
    tk.Checkbutton(fr_uses, text="Трата использований",
                   variable=uses_var).pack(side="left")
    tk.Label(fr_uses, text="Максимум:").pack(side="left",
                                                padx=(10, 2))
    uses_max_var = tk.IntVar(value=a.get("uses_max", 0))
    tk.Spinbox(fr_uses, from_=0, to=999,
                textvariable=uses_max_var, width=6).pack(side="left")

    panel_var = tk.BooleanVar(value=a.get("show_on_panel", True))
    tk.Checkbutton(body, text="Показывать заряды на верхней панели",
                    variable=panel_var).pack(anchor="w", padx=5,
                                              pady=(4, 0))

    # Тик на новой инициативе
    tk.Label(body, text="Тик на новой инициативе:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(10, 0))
    tick_mode_var = tk.StringVar(value=a.get("tick_mode", "none"))
    fr_tick = tk.Frame(body)
    fr_tick.pack(fill="x", padx=5)
    tk.Radiobutton(fr_tick, text="Не трогать",
                    value="none", variable=tick_mode_var
                    ).pack(side="left", padx=4)
    tk.Radiobutton(fr_tick, text="−1 заряд",
                    value="decrease", variable=tick_mode_var
                    ).pack(side="left", padx=4)
    tk.Radiobutton(fr_tick, text="Восстанавливать",
                    value="restore", variable=tick_mode_var
                    ).pack(side="left", padx=4)

    # Кулдаун
    fr_cd = tk.Frame(body)
    fr_cd.pack(fill="x", padx=5, pady=(6, 0))
    tk.Label(fr_cd, text="Кулдаун (раундов, 0=нет):",
             font=("Segoe UI", 10)).pack(side="left")
    cd_rounds_var = tk.IntVar(
        value=a.get("cooldown_rounds", 0))
    tk.Spinbox(fr_cd, from_=0, to=99,
                textvariable=cd_rounds_var, width=5
                ).pack(side="left", padx=4)
    tk.Label(fr_cd, text="осталось:",
             font=("Segoe UI", 10)).pack(side="left", padx=(10, 2))
    cd_current_var = tk.IntVar(
        value=a.get("cooldown_current", 0))
    tk.Spinbox(fr_cd, from_=0, to=99,
                textvariable=cd_current_var, width=5
                ).pack(side="left")

    # T48: поля бафа
    from gui_alphabet import TARGET_NAMES as _TN
    buff_data = _render_ability_buff_fields(body, a, _TN)

    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        a["name"] = name
        a["desc"] = t.get("1.0", "end").strip()
        a["uses"] = uses_var.get()
        a["show_on_panel"] = panel_var.get()
        a["tick_mode"] = tick_mode_var.get()
        try:
            a["cooldown_rounds"] = max(0, cd_rounds_var.get())
            a["cooldown_current"] = max(0, cd_current_var.get())
        except Exception:
            a["cooldown_rounds"] = 0
            a["cooldown_current"] = 0
        if a["uses"]:
            try:
                new_max = int(uses_max_var.get())
            except Exception:
                new_max = 0
            old_max = a.get("uses_max", 0)
            a["uses_max"] = new_max
            if "uses_current" not in a or old_max != new_max:
                a["uses_current"] = new_max
        else:
            a["uses_max"] = 0
            a["uses_current"] = 0
        # T48: сохранить поля бафа
        _apply_ability_buff_fields(a, buff_data)
        try:
            d.grab_release()
        except Exception:
            pass
        refresh()
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")

# ============ Класс ============

def edit_class(app):
    if not app.c:
        return

    def build(parent):
        c = app.c
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=5, pady=5)

        t1_outer, _, t1 = make_scrollable(nb)
        nb.add(t1_outer, text="Основное")

        def field(p, label, init):
            fr = tk.Frame(p)
            fr.pack(fill="x", pady=3)
            tk.Label(fr, text=label, width=24, anchor="w"
                     ).pack(side="left")
            e = tk.Entry(fr)
            e.insert(0, str(init))
            e.pack(side="left", fill="x", expand=True)
            return e

        e_name = field(t1, "Название:", c.char_class.get("name", ""))
        e_level = field(t1, "Уровень:",
                        c.char_class.get("level", 1))

        # T43: тултип + подпись «без тренировок»
        _lvl_tip = (
            "Ручное изменение уровня НЕ даёт тренировок.\n\n"
            "Тренировки начисляются только через кнопку "
            "«⬆ Level Up» в верхней панели "
            "(появляется при XP ≥ 1000):\n"
            "  • +1 уровень\n"
            "  • +HP-бросок в «Броски HP»\n"
            "  • +уровень × 100 тренировок\n"
            "  • XP −= 1000"
        )
        try:
            ToolTip(e_level, _lvl_tip)
        except Exception:
            pass
        from gui_shared import hint as _hint
        _hint(t1,
              "⚠ Ручная правка уровня — без тренировок. "
              "Тренировки — через «⬆ Level Up» "
              "(XP ≥ 1000, верхняя панель).",
              character=c,
              fg="#c06000",
              font=("Segoe UI", 9, "italic"),
              wraplength=680, justify="left")

        fr_die_hdr = tk.Frame(t1)
        fr_die_hdr.pack(fill="x", pady=(6, 0))
        tk.Label(fr_die_hdr, text="Кубик хитов (КХП):",
                 width=24, anchor="w",
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        hp_die_var = tk.IntVar(value=c.char_class.get("hp_die", 8))
        fr_die = tk.Frame(t1)
        fr_die.pack(fill="x", padx=5)
        for die in (4, 6, 8, 10, 12):
            tk.Radiobutton(fr_die, text=f"d{die}", value=die,
                           variable=hp_die_var,
                           font=("Segoe UI", 10)
                           ).pack(side="left", padx=6)
        lbl_khp = tk.Label(
            t1, text=f"Текущий КХП: d{c.char_class.get('hp_die', 8)}",
            font=("Segoe UI", 9, "italic"), fg="#666")
        lbl_khp.pack(anchor="w", padx=5, pady=(0, 4))
        e_hp_rolls = field(
            t1, "Броски HP (через запятую):",
            ",".join(map(str, c.char_class.get("hp_rolls", []))))
        e_disc = field(
            t1, "Доп. скидка заклинаний:",
            c.char_class.get("spell_discount_extra", 0))

        fr_bab = tk.Frame(t1)
        fr_bab.pack(fill="x", pady=8)
        tk.Label(fr_bab, text="Прогрессия ББА:",
                 width=24, anchor="w",
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        bab_var = tk.StringVar(
            value=c.char_class.get("bab_type", "good"))
        for val, label in [
                ("good", "Хорошее (1×ур)"),
                ("medium", "Среднее (3/4 ур)"),
                ("poor", "Плохое (1/2 ур)")]:
            tk.Radiobutton(fr_bab, text=label, value=val,
                           variable=bab_var,
                           font=("Segoe UI", 9)
                           ).pack(side="left", padx=4)

        fr_sv = tk.Frame(t1)
        fr_sv.pack(fill="x", pady=8)
        tk.Label(fr_sv, text="Хорошие спасброски:",
                 width=24, anchor="w",
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        good_saves = c.char_class.get("good_saves", [])
        sv_vars = {}
        for key, label, stat in [("fort", "Fort", "CON"),
                                  ("ref", "Ref", "DEX"),
                                  ("will", "Will", "WIS")]:
            v = tk.BooleanVar(value=(key in good_saves))
            tk.Checkbutton(fr_sv, text=f"{label} ({stat})",
                           variable=v).pack(side="left", padx=4)
            sv_vars[key] = v

        v_book = tk.BooleanVar(
            value=c.char_class.get("has_spellbook", False))
        tk.Checkbutton(t1, text="Книга заклинаний (скидка ×2)",
                       variable=v_book).pack(anchor="w", pady=4)

        # Способности
        t2 = tk.Frame(nb)
        nb.add(t2, text="Способности")
        ab_body = tk.Frame(t2, bg="#f4f4f4")
        ab_body.pack(fill="both", expand=True)

        def rebuild_ab():
            for w in ab_body.winfo_children():
                w.destroy()
            abils = c.char_class.get("abilities", [])
            if not abils:
                tk.Label(ab_body, text="(способностей нет)",
                         bg="#f4f4f4", fg="#888",
                         font=("Segoe UI", 10, "italic")
                         ).pack(pady=20)
                return
            for i, a in enumerate(abils):
                row = tk.Frame(ab_body, bg="#f4f4f4")
                row.pack(fill="x", pady=2, padx=5)
                uses_txt = ""
                if a.get("uses"):
                    uses_txt = (f" [{a.get('uses_current', 0)}/"
                                 f"{a.get('uses_max', 0)}]")
                panel_tag = ""
                if a.get("uses") and a.get("show_on_panel", True):
                    panel_tag = " 📌"
                tm = a.get("tick_mode", "none")
                tick_tag = ""
                if tm == "restore":
                    tick_tag = " 🔄"
                elif tm == "decrease":
                    tick_tag = " ⏬"
                cd = a.get("cooldown_current", 0)
                cd_tag = f" ⏳{cd}" if cd > 0 else ""
                nl = tk.Label(
                    row,
                    text=f"• {a['name']}{uses_txt}{tick_tag}{cd_tag}"
                         f"{panel_tag}",
                    bg="#f4f4f4",
                    font=("Segoe UI", 10, "bold"),
                    anchor="w", cursor="hand2")
                nl.pack(side="left", padx=4)
                tip_parts = []
                if a.get("desc"): 
                    tip_parts.append(a["desc"])
                _effects = a.get("effects", [])
                if _effects:
                    from gui_alphabet import TARGET_NAMES as _TN
                    eff_lines = []
                    for e in _effects:
                        tgt = _TN.get(e.get("target"), e.get("target"))
                        val = e.get("value", 0)
                        btype = e.get("bonus_type", "flat")
                        eff_lines.append(f"{val:+d} {tgt} ({btype})")
                    tip_parts.append("Эффекты: " + ", ".join(eff_lines))
                if tip_parts:
                    ToolTip(nl, "\n\n".join(tip_parts))
                tk.Button(row, text="✖", width=3,
                          command=lambda i=i: _ab_delete(
                              app, i, rebuild_ab)
                          ).pack(side="right", padx=2)
                tk.Button(row, text="✎", width=3,
                          command=lambda i=i: _ab_edit(
                              app, i, rebuild_ab)
                          ).pack(side="right", padx=2)

        def add_ab():
            c.char_class.setdefault("abilities", [])
            c.char_class["abilities"].append(
                {"name": "Новая способность", "desc": "",
                 "uses": False, "uses_current": 0, "uses_max": 0,
                 "show_on_panel": True,
                 "tick_mode": "none",
                 "cooldown_rounds": 0,
                 "cooldown_current": 0})
            idx = len(c.char_class["abilities"]) - 1
            _ab_edit(app, idx, rebuild_ab)

        tk.Button(t2, text="＋ Добавить способность",
                  command=add_ab).pack(pady=6)
        tk.Button(t2, text="📚 Из каталога",
                  command=lambda: _class_abil_from_catalog(
                      app, rebuild_ab),
                  bg="#446", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(pady=2)
        rebuild_ab()

        # Магия
        t3_outer, _, t3 = make_scrollable(nb)
        nb.add(t3_outer, text="Особые и Магия")
        magic_holder = {"fn": None}
        _build_magic_tab(app, t3, magic_holder)

        def save():
            if magic_holder["fn"]:
                try:
                    ok = magic_holder["fn"](silent=True)
                    if ok is False:
                        return
                except Exception as e:
                    messagebox.showerror(
                        "Магия", f"Ошибка при сохранении магии:\n{e}",
                        parent=app.get_dialog_parent())
                    return
            c.char_class["name"] = e_name.get().strip()
            try:
                c.char_class["level"] = int(e_level.get() or 1)
            except Exception:
                pass
            new_die = hp_die_var.get()
            rolls = []
            for x in e_hp_rolls.get().split(","):
                x = x.strip()
                if x.isdigit():
                    rolls.append(int(x))
            bad = [r for r in rolls if r > new_die]
            if bad:
                messagebox.showerror(
                    "Ошибка КХП",
                    f"У вас КХП d{new_die}, а бросок "
                    f"{', '.join(map(str, bad))} — больше кубика.\n"
                    f"Максимум для броска: {new_die}.\n"
                    f"Исправь поле «Броски HP».",
                    parent=app.get_dialog_parent())
                return
            c.char_class["hp_die"] = new_die
            c.char_class["hp_rolls"] = rolls
            c.char_class["has_spellbook"] = v_book.get()
            c.char_class["bab_type"] = bab_var.get()
            c.char_class["good_saves"] = [
                k for k, v in sv_vars.items() if v.get()]
            try:
                c.char_class["spell_discount_extra"] = int(
                    e_disc.get() or 0)
            except Exception:
                pass
            c.recompute_derived()
            app._show_main()

        tk.Button(parent, text="Сохранить всё", command=save,
                  bg="#4a7", fg="white",
                  font=("Segoe UI", 10, "bold")).pack(pady=6)

    app._show_editor("Класс", build)

def _render_ability_buff_fields(parent, a, target_names, on_change=None):
    """T48: поля бафа для AbilityDef (класс/раса).
    Возвращает dict с BooleanVar/IntVar/списками для save()."""
    from tkinter import messagebox as _mb
    is_buff_var = tk.BooleanVar(value=a.get("is_buff", False))
    tk.Checkbutton(parent, text="Это баф (виден в «Ситуативно»)",
                    variable=is_buff_var,
                    font=("Segoe UI", 10, "bold")
                    ).pack(anchor="w", padx=5, pady=(8, 2))

    fr_dur = tk.Frame(parent)
    fr_dur.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_dur, text="Длительность (раундов):",
             font=("Segoe UI", 9)).pack(side="left")
    dur_var = tk.IntVar(value=int(a.get("duration_rounds", 0) or 0))
    tk.Spinbox(fr_dur, from_=0, to=100, textvariable=dur_var,
                width=5).pack(side="left", padx=4)
    tk.Label(fr_dur, text="  Заряды:",
             font=("Segoe UI", 9)).pack(side="left")
    ch_max_var = tk.IntVar(value=int(a.get("charges_max", 0) or 0))
    tk.Spinbox(fr_dur, from_=0, to=99, textvariable=ch_max_var,
                width=4).pack(side="left", padx=2)
    tk.Label(fr_dur, text="текущие:",
             font=("Segoe UI", 9)).pack(side="left")
    ch_cur_var = tk.IntVar(value=int(a.get("charges_current", 0) or 0))
    tk.Spinbox(fr_dur, from_=0, to=99, textvariable=ch_cur_var,
                width=4).pack(side="left", padx=2)

    tk.Label(parent, text="Постоянные эффекты:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    effects_data = [dict(e) for e in a.get("effects", [])]
    if not effects_data:
        effects_data = [{"target": "ac", "value": 0}]
    eff_frame = tk.Frame(parent, bg="#f4f4f4")
    eff_frame.pack(fill="x", padx=5)
    all_targets = list(target_names.keys())

    def _set_eff(idx, key, val):
        if 0 <= idx < len(effects_data):
            effects_data[idx][key] = val

    def render_effects():
        for w in eff_frame.winfo_children():
            w.destroy()
        for i, eff in enumerate(effects_data):
            fr = tk.Frame(eff_frame, bg="#f4f4f4")
            fr.pack(fill="x", pady=1)
            tk.Label(fr, text=f"  {i+1}.", width=4,
                     bg="#f4f4f4").pack(side="left")
            tgt_var = tk.StringVar(value=eff.get("target", "ac"))
            opt = tk.OptionMenu(fr, tgt_var, *all_targets,
                                 command=lambda v, idx=i:
                                 _set_eff(idx, "target", v))
            opt.config(width=14)
            opt.pack(side="left", padx=2)
            tk.Label(fr, text=":", bg="#f4f4f4"
                     ).pack(side="left", padx=2)
            v_val = tk.StringVar(value=str(eff.get("value", 0)))
            tk.Entry(fr, textvariable=v_val, width=8
                     ).pack(side="left", padx=2)

            def on_val(idx=i, var=v_val):
                raw = var.get().strip()
                if not raw:
                    effects_data[idx]["value"] = 0
                    return
                try:
                    effects_data[idx]["value"] = int(raw)
                except ValueError:
                    effects_data[idx]["value"] = raw
            v_val.trace_add("write", lambda *a, f=on_val: f())

            def del_eff(idx=i):
                effects_data.pop(idx)
                if not effects_data:
                    effects_data.append({"target": "ac", "value": 0})
                render_effects()
            tk.Button(fr, text="✖", width=3,
                      command=del_eff).pack(side="right", padx=2)

    def add_effect():
        effects_data.append({"target": "ac", "value": 0})
        render_effects()
    render_effects()
    tk.Button(parent, text="＋ Строка эффекта",
              command=add_effect
              ).pack(anchor="w", padx=10, pady=2)

    tk.Label(parent, text="Разовые эффекты (при активации):",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    on_act_data = [dict(e) for e in a.get("on_activate_effects", [])]
    on_act_frame = tk.Frame(parent, bg="#f4f4f4")
    on_act_frame.pack(fill="x", padx=5)

    def _set_onact(idx, key, val):
        if 0 <= idx < len(on_act_data):
            on_act_data[idx][key] = val

    def render_on_act():
        for w in on_act_frame.winfo_children():
            w.destroy()
        for i, eff in enumerate(on_act_data):
            fr = tk.Frame(on_act_frame, bg="#f4f4f4")
            fr.pack(fill="x", pady=1)
            tk.Label(fr, text=f"  {i+1}.", width=4,
                     bg="#f4f4f4").pack(side="left")
            tgt_var = tk.StringVar(value=eff.get("target", "restore_hp"))
            opt = tk.OptionMenu(fr, tgt_var, *all_targets,
                                 command=lambda v, idx=i:
                                 _set_onact(idx, "target", v))
            opt.config(width=14)
            opt.pack(side="left", padx=2)
            tk.Label(fr, text=":", bg="#f4f4f4"
                     ).pack(side="left", padx=2)
            v_val = tk.StringVar(value=str(eff.get("value", 0)))
            tk.Entry(fr, textvariable=v_val, width=8
                     ).pack(side="left", padx=2)

            def on_val(idx=i, var=v_val):
                raw = var.get().strip()
                if not raw:
                    on_act_data[idx]["value"] = 0
                    return
                try:
                    on_act_data[idx]["value"] = int(raw)
                except ValueError:
                    on_act_data[idx]["value"] = raw
            v_val.trace_add("write", lambda *a, f=on_val: f())

            def del_eff(idx=i):
                on_act_data.pop(idx)
                render_on_act()
            tk.Button(fr, text="✖", width=3,
                      command=del_eff).pack(side="right", padx=2)

    def add_on_act():
        on_act_data.append({"target": "restore_hp", "value": 0})
        render_on_act()
    render_on_act()
    tk.Button(parent, text="＋ Строка разового эффекта",
              command=add_on_act
              ).pack(anchor="w", padx=10, pady=2)

    return {
        "is_buff": is_buff_var,
        "duration_rounds": dur_var,
        "charges_max": ch_max_var,
        "charges_current": ch_cur_var,
        "effects_data": effects_data,
        "on_act_data": on_act_data,
    }


def _apply_ability_buff_fields(a, data):
    """T48: сохранить поля бафа в AbilityDef."""
    a["is_buff"] = data["is_buff"].get()
    try:
        a["duration_rounds"] = max(0, int(data["duration_rounds"].get()))
    except Exception:
        a["duration_rounds"] = 0
    try:
        a["charges_max"] = max(0, int(data["charges_max"].get()))
    except Exception:
        a["charges_max"] = 0
    try:
        a["charges_current"] = max(0, min(
            int(data["charges_current"].get()),
            a["charges_max"]))
    except Exception:
        a["charges_current"] = 0
    def _nonempty(e):
        v = e.get("value", 0)
        if isinstance(v, str):
            return v.strip() != "" and v.strip() != "0"
        return v != 0
    a["effects"] = [dict(e) for e in data["effects_data"] if _nonempty(e)]
    a["on_activate_effects"] = [dict(e) for e in data["on_act_data"]
                                if isinstance(e, dict)]

def _class_abil_from_catalog(app, rebuild):
    """K2e: взять абилку класса из CLASS_ABILITIES_CATALOG."""
    from character import CLASS_ABILITIES_CATALOG
    if not CLASS_ABILITIES_CATALOG:
        messagebox.showinfo("Каталог абилок класса пуст",
                             "Создай файл в catalogs/class_abilities/.",
                             parent=app.get_dialog_parent())
        return
    d = open_window(app, "Из каталога: абилки класса", 700, 550)
    tk.Label(d, text="Выбери абилку:",
             font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=6)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=4)

    for it in CLASS_ABILITIES_CATALOG:
        row = tk.Frame(body, bg="#f4f4f4", relief="solid", borderwidth=1)
        row.pack(fill="x", padx=2, pady=1)
        info = tk.Frame(row, bg="#f4f4f4")
        info.pack(side="left", fill="x", expand=True, padx=4, pady=2)
        buff_tag = " [баф]" if it.get("is_buff") else ""
        tk.Label(info, text=f"{it.get('name', '?')}{buff_tag}",
                 bg="#f4f4f4", font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(anchor="w")
        if it.get("desc"):
            tk.Label(info, text=it["desc"][:100],
                     bg="#f4f4f4", fg="#666",
                     font=("Segoe UI", 8), anchor="w").pack(anchor="w")

        def _take(it=it):
            a = dict(it)
            a.setdefault("name", "Способность")
            a.setdefault("desc", "")
            a.setdefault("uses", False)
            a.setdefault("uses_current", 0)
            a.setdefault("uses_max", 0)
            a.setdefault("show_on_panel", True)
            a.setdefault("tick_mode", "none")
            a.setdefault("cooldown_rounds", 0)
            a.setdefault("cooldown_current", 0)
            app.c.char_class.setdefault("abilities", []).append(a)
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



def _ab_edit(app, idx, refresh):
    c = app.c
    abils = c.char_class.get("abilities", [])
    if idx < 0 or idx >= len(abils):
        return
    a = abils[idx]
    d = open_window(app, "Способность класса", 500, 720)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True)

    tk.Label(body, text="Название:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    e_name.insert(0, a.get("name", ""))
    e_name.pack(fill="x", padx=5)
    tk.Label(body, text="Описание:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    t_desc = tk.Text(body, font=("Segoe UI", 10), height=6,
                      wrap="word")
    t_desc.pack(fill="both", expand=True, padx=5)
    t_desc.insert("1.0", a.get("desc", ""))

    uses_var = tk.BooleanVar(value=a.get("uses", False))
    fr_uses = tk.Frame(body)
    fr_uses.pack(fill="x", padx=5, pady=(8, 0))
    tk.Checkbutton(fr_uses, text="Трата использований",
                   variable=uses_var).pack(side="left")
    tk.Label(fr_uses, text="Максимум:").pack(side="left",
                                                padx=(10, 2))
    uses_max_var = tk.IntVar(value=a.get("uses_max", 0))
    tk.Spinbox(fr_uses, from_=0, to=999,
                textvariable=uses_max_var, width=6).pack(side="left")

    panel_var = tk.BooleanVar(value=a.get("show_on_panel", True))
    tk.Checkbutton(body, text="Показывать заряды на верхней панели",
                    variable=panel_var).pack(anchor="w", padx=5,
                                              pady=(4, 0))

    # Тик на новой инициативе
    tk.Label(body, text="Тик на новой инициативе:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(10, 0))
    tick_mode_var = tk.StringVar(value=a.get("tick_mode", "none"))
    fr_tick = tk.Frame(body)
    fr_tick.pack(fill="x", padx=5)
    tk.Radiobutton(fr_tick, text="Не трогать",
                    value="none", variable=tick_mode_var
                    ).pack(side="left", padx=4)
    tk.Radiobutton(fr_tick, text="−1 заряд",
                    value="decrease", variable=tick_mode_var
                    ).pack(side="left", padx=4)
    tk.Radiobutton(fr_tick, text="Восстанавливать",
                    value="restore", variable=tick_mode_var
                    ).pack(side="left", padx=4)

    # Кулдаун
    fr_cd = tk.Frame(body)
    fr_cd.pack(fill="x", padx=5, pady=(6, 0))
    tk.Label(fr_cd, text="Кулдаун (раундов, 0=нет):",
             font=("Segoe UI", 10)).pack(side="left")
    cd_rounds_var = tk.IntVar(
        value=a.get("cooldown_rounds", 0))
    tk.Spinbox(fr_cd, from_=0, to=99,
                textvariable=cd_rounds_var, width=5
                ).pack(side="left", padx=4)
    tk.Label(fr_cd, text="осталось:",
             font=("Segoe UI", 10)).pack(side="left", padx=(10, 2))
    cd_current_var = tk.IntVar(
        value=a.get("cooldown_current", 0))
    tk.Spinbox(fr_cd, from_=0, to=99,
                textvariable=cd_current_var, width=5
                ).pack(side="left")

    # T48: поля бафа
    from gui_alphabet import TARGET_NAMES as _TN
    buff_data = _render_ability_buff_fields(body, a, _TN)

    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        a["name"] = name
        a["desc"] = t_desc.get("1.0", "end").strip()
        a["uses"] = uses_var.get()
        a["show_on_panel"] = panel_var.get()
        a["tick_mode"] = tick_mode_var.get()
        try:
            a["cooldown_rounds"] = max(0, cd_rounds_var.get())
            a["cooldown_current"] = max(0, cd_current_var.get())
        except Exception:
            a["cooldown_rounds"] = 0
            a["cooldown_current"] = 0
        if a["uses"]:
            try:
                new_max = int(uses_max_var.get())
            except Exception:
                new_max = 0
            old_max = a.get("uses_max", 0)
            a["uses_max"] = new_max
            if "uses_current" not in a or old_max != new_max:
                a["uses_current"] = new_max
        else:
            a["uses_max"] = 0
            a["uses_current"] = 0
        # T48: сохранить поля бафа
        _apply_ability_buff_fields(a, buff_data)
        try:
            d.grab_release()
        except Exception:
            pass
        refresh()
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")


def _ab_delete(app, idx, refresh):
    abils = app.c.char_class.get("abilities", [])
    if idx < 0 or idx >= len(abils):
        return
    if not messagebox.askyesno(
            "Удалить", f"Удалить '{abils[idx]['name']}'?"):
        return
    abils.pop(idx)
    refresh()


def _build_magic_tab(app, parent, magic_holder):
    c = app.c
    mana_hdr = tk.Frame(parent, bg="#c8c8c8")
    mana_hdr.pack(fill="x", pady=(4, 2))
    tk.Label(mana_hdr, text="Мана",
             font=("Segoe UI", 11, "bold"), bg="#c8c8c8",
             anchor="w", padx=6).pack(fill="x")

    mana_var = tk.BooleanVar(value=c.mana.get("enabled", False))
    fr_mana = tk.Frame(parent, bg="#f4f4f4")
    fr_mana.pack(fill="x", padx=5, pady=4)
    tk.Checkbutton(fr_mana, text="Включить ману",
                   variable=mana_var, bg="#f4f4f4").pack(side="left")

    fr_class = tk.Frame(parent, bg="#f4f4f4")
    fr_class.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_class, text="Мана за класс:",
             bg="#f4f4f4", width=16, anchor="w"
             ).pack(side="left")
    class_max_var = tk.IntVar(value=c.mana.get("class_max", 0))
    tk.Spinbox(fr_class, from_=0, to=999,
                textvariable=class_max_var, width=6
                ).pack(side="left", padx=4)

    bonus_rows = []
    cur_sources = list(c.mana.get("bonus_sources", []))
    while len(cur_sources) < 2:
        cur_sources.append({"name": "", "value": 0})
    for i in range(2):
        src = cur_sources[i]
        fr_b = tk.Frame(parent, bg="#f4f4f4")
        fr_b.pack(fill="x", padx=5, pady=2)
        tk.Label(fr_b, text=f"Источник {i+1}:",
                 bg="#f4f4f4", width=16, anchor="w"
                 ).pack(side="left")
        e_name = tk.Entry(fr_b, width=22)
        e_name.insert(0, src.get("name", ""))
        e_name.pack(side="left", padx=2)
        tk.Label(fr_b, text="+", bg="#f4f4f4"
                 ).pack(side="left", padx=(4, 2))
        v_val = tk.IntVar(value=src.get("value", 0))
        tk.Spinbox(fr_b, from_=0, to=999,
                    textvariable=v_val, width=5).pack(side="left")
        bonus_rows.append({"name": e_name, "value": v_val})

    lbl_total = tk.Label(parent, text="",
                          fg="#c06000", bg="#f4f4f4",
                          font=("Segoe UI", 10, "bold"))
    lbl_total.pack(anchor="w", padx=5, pady=4)
    def upd_total(*args):
        if not mana_var.get():
            lbl_total.config(text="(мана выключена)")
            return
        total = class_max_var.get()
        parts = []
        if class_max_var.get():
            parts.append(f"класс {class_max_var.get()}")
        for i, r in enumerate(bonus_rows):
            v = r["value"].get()
            if v:
                nm = r["name"].get().strip() or f"источник {i+1}"
                parts.append(f"{nm} {v}")
                total += v
        detail = f"  ({', '.join(parts)})" if parts else ""
        lbl_total.config(text=f"Итого: {total}{detail}")

    mana_var.trace_add("write", upd_total)
    class_max_var.trace_add("write", upd_total)
    for r in bonus_rows:
        r["value"].trace_add("write", upd_total)
        r["name"].bind("<KeyRelease>", upd_total)
    upd_total()

    # ===== Перегрузка =====
    ov_hdr = tk.Frame(parent, bg="#c8c8c8")
    ov_hdr.pack(fill="x", pady=(10, 2))
    tk.Label(ov_hdr, text="Перегрузка",
             font=("Segoe UI", 11, "bold"), bg="#c8c8c8",
             anchor="w", padx=6).pack(fill="x")

    ov_enabled_var = tk.BooleanVar(
        value=getattr(c, "overload_enabled", False))
    tk.Checkbutton(parent,
                    text="Использовать счётчик перегрузки",
                    variable=ov_enabled_var, bg="#f4f4f4"
                    ).pack(anchor="w", padx=5, pady=2)

    fr_ov = tk.Frame(parent, bg="#f4f4f4")
    fr_ov.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_ov, text="Текущее значение:",
             bg="#f4f4f4", width=20, anchor="w"
             ).pack(side="left")
    ov_val_var = tk.IntVar(value=getattr(c, "overload", 0))
    tk.Spinbox(fr_ov, from_=0, to=99,
                textvariable=ov_val_var, width=5
                ).pack(side="left", padx=4)

    def set_overload_now():
        try:
            c.overload = max(0, ov_val_var.get())
        except Exception:
            c.overload = 0
        c.overload_enabled = ov_enabled_var.get()
        app._refresh()
    tk.Button(fr_ov, text="OK", command=set_overload_now,
              bg="#4a7", fg="white", width=3
              ).pack(side="left", padx=4)

    ov_hint = tk.Frame(parent, bg="#e8e8e8", pady=4, padx=6)
    ov_hint.pack(fill="x", padx=5, pady=(2, 4))
    from gui_shared import hint as _hint
    _hint(ov_hint,
          "Каждый «🔁 Нулевая инициатива» −1. "
          "Пока > 0 — баланс не восстанавливается.",
          character=app.c,
          fg="#666", font=("Segoe UI", 9, "italic"),
          wraplength=700, justify="left")

    # Слоты
    slot_hdr = tk.Frame(parent, bg="#c8c8c8")
    slot_hdr.pack(fill="x", pady=(10, 2))
    tk.Label(slot_hdr, text="Слоты заклинаний",
             font=("Segoe UI", 11, "bold"), bg="#c8c8c8",
             anchor="w", padx=6).pack(fill="x")
    slot_var = tk.BooleanVar(value=c.spell_slots_enabled)
    tk.Checkbutton(parent, text="Включить слоты",
                    variable=slot_var, bg="#f4f4f4"
                    ).pack(anchor="w", padx=5)
    slots_frame = tk.Frame(parent, bg="#f4f4f4")
    slots_frame.pack(fill="x", padx=5, pady=2)
    slot_vars = {}
    for circle in range(10):
        fr = tk.Frame(slots_frame, bg="#f4f4f4")
        fr.pack(side="left", padx=3)
        tk.Label(fr, text=f"Кр.{circle}:", bg="#f4f4f4",
                 font=("Segoe UI", 9)).pack()
        cur_slot = c.spell_slots.get(str(circle), {"max": 0})
        v = tk.IntVar(value=cur_slot.get("max", 0))
        tk.Spinbox(fr, from_=0, to=20, textvariable=v,
                    width=3).pack()
        slot_vars[circle] = v

    # Особые
    res_hdr = tk.Frame(parent, bg="#c8c8c8")
    res_hdr.pack(fill="x", pady=(10, 2))
    tk.Label(res_hdr, text="Особые способности (до 3)",
             font=("Segoe UI", 11, "bold"), bg="#c8c8c8",
             anchor="w", padx=6).pack(fill="x")
    res_enabled = tk.BooleanVar(value=bool(c.class_resources))
    tk.Checkbutton(parent, text="Включить особые",
                    variable=res_enabled, bg="#f4f4f4"
                    ).pack(anchor="w", padx=5)

    res_rows = []
    for i in range(3):
        fr = tk.Frame(parent, bg="#f4f4f4")
        fr.pack(fill="x", padx=5, pady=2)
        tk.Label(fr, text=f"Строка {i+1}:", width=10,
                 bg="#f4f4f4").pack(side="left")
        e_n = tk.Entry(fr, width=20)
        e_n.pack(side="left", padx=2)
        tk.Label(fr, text="макс:", bg="#f4f4f4"
                 ).pack(side="left", padx=(6, 2))
        v_max = tk.IntVar(value=0)
        tk.Spinbox(fr, from_=0, to=999, textvariable=v_max,
                    width=5).pack(side="left")
        res_rows.append({"name": e_n, "max": v_max})

    for i, r in enumerate(c.class_resources[:3]):
        res_rows[i]["name"].insert(0, r.get("name", ""))
        res_rows[i]["max"].set(r.get("max", 0))

    def save_magic(silent=False):
        try:
            c.mana["enabled"] = mana_var.get()
            c.mana["class_max"] = class_max_var.get()
            new_sources = []
            for r in bonus_rows:
                nm = r["name"].get().strip()
                vl = r["value"].get()
                if nm or vl:
                    new_sources.append({"name": nm, "value": vl})
            while len(new_sources) < 2:
                new_sources.append({"name": "", "value": 0})
            c.mana["bonus_sources"] = new_sources

            # Перегрузка
            c.overload_enabled = ov_enabled_var.get()
            try:
                c.overload = max(0, ov_val_var.get())
            except Exception:
                c.overload = 0

            c.recompute_derived()
            if c.mana["enabled"]:
                c.mana["current"] = c.mana["max"]

            c.spell_slots_enabled = slot_var.get()
            new_slots = {}
            if c.spell_slots_enabled:
                for circle, v in slot_vars.items():
                    mx = v.get()
                    if mx > 0:
                        old = c.spell_slots.get(str(circle), {})
                        cur = old.get("current", mx)
                        new_slots[str(circle)] = {
                            "current": min(cur, mx), "max": mx}
            c.spell_slots = new_slots

            new_res = []
            if res_enabled.get():
                for r in res_rows:
                    nm = r["name"].get().strip()
                    mx = r["max"].get()
                    if nm and mx > 0:
                        old = next((x for x in c.class_resources
                                    if x["name"] == nm), {})
                        cur = old.get("current", mx)
                        new_res.append({"name": nm,
                                        "current": min(cur, mx),
                                        "max": mx})
            c.class_resources = new_res
            return True
        except Exception as e:
            print(f"[save_magic] {e}")
            return False

    magic_holder["fn"] = save_magic

    hint = tk.Frame(parent, bg="#e8e8e8", pady=6, padx=6)
    hint.pack(fill="x", padx=5, pady=(10, 4))
    tk.Label(hint,
             text="Изменения магии, слотов, перегрузки и особых "
                  "применятся при нажатии кнопки «Сохранить всё» "
                  "внизу окна.",
             bg="#e8e8e8", fg="#333",
             font=("Segoe UI", 9, "italic"),
             wraplength=600, justify="left"
             ).pack(anchor="w")

# ============ Черты ============

def edit_feats(app):
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
                # Показываем ВСЕ черты, включая стойки
                visible = [(i, f) for i, f in enumerate(app.c.feats)]
                if not visible:
                    tk.Label(body, text="(черт нет)",
                             bg="#f4f4f4", fg="#888",
                             font=("Segoe UI", 10, "italic")
                             ).pack(pady=20)
                    return
                for i, f in visible:
                    row = tk.Frame(body, bg="#f4f4f4")
                    row.pack(fill="x", pady=1, padx=2)
                    src_name = SOURCE_NAMES.get(
                        f.get("source", ""), "?")
                    tk.Label(row, text=f"[{src_name}]",
                             bg="#f4f4f4", font=("Consolas", 9),
                             fg="#666").pack(side="left")
                    link = f.get("link", "")
                    desc = f.get("desc", "")
                    type_tag = "[Стойка] " if f.get("is_stance") else "[Черта] "
                    nl = tk.Label(
                        row, text=f"{type_tag}{f['name']}", bg="#f4f4f4",
                        font=("Segoe UI", 10, "bold"),
                        fg="#0066cc" if link else "black",
                        cursor="hand2" if (link or desc) else "arrow")
                    nl.pack(side="left", padx=4)
                    
                    tip_parts = []
                    if desc: 
                        tip_parts.append(desc)
                    
                    # Добавляем эффекты в тултип (если есть)
                    _effects = f.get("effects", []) if not f.get("is_stance") else f.get("stance_effects", [])
                    if _effects:
                        from gui_alphabet import TARGET_NAMES as _TN, BONUS_TYPE_NAMES as _BTN
                        eff_lines = []
                        for e in _effects:
                            tgt = _TN.get(e.get("target"), e.get("target"))
                            val = e.get("value", 0)
                            btype = e.get("bonus_type", "flat")
                            btype_ru = _BTN.get(btype, btype)
                            eff_lines.append(f"{val:+d} {tgt} ({btype_ru})")
                        tip_parts.append("Эффекты: " + ", ".join(eff_lines))

                    if link:
                        tip_parts.append(f"🔗 {link}")
                        
                    if tip_parts:
                        ToolTip(nl, "\n\n".join(tip_parts))
                    if link:
                        nl.bind("<Button-1>",
                                lambda e, u=link: webbrowser.open(u))
                    inv = f.get("invested", 0)
                    tk.Label(row,
                             text=f"{inv} оч." if inv else "бесплатно",
                             bg="#f4f4f4", fg="#c06000",
                             font=("Segoe UI", 9)
                             ).pack(side="right", padx=5)
                    tk.Button(row, text="✖", width=3,
                              command=lambda i=i: _feat_delete(
                                  app, i, schedule_refresh)
                              ).pack(side="right", padx=2)
                    tk.Button(row, text="✎", width=3,
                              command=lambda i=i: _feat_dialog(
                                  app, i, schedule_refresh)
                              ).pack(side="right", padx=2)
            except Exception as e:
                print(f"[feats rebuild] {e}")

        def schedule_refresh():
            if pending[0] is not None:
                try:
                    app.root.after_cancel(pending[0])
                except Exception:
                    pass
            pending[0] = app.root.after(30, do_rebuild)

        tk.Button(top, text="＋ Добавить черту",
                  command=lambda: _feat_dialog(app, None,
                                                schedule_refresh)
                  ).pack(side="left", padx=5)
        tk.Button(top, text="📚 Из каталога",
                  command=lambda: _feat_from_catalog(app, schedule_refresh),
                  bg="#446", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="left", padx=5)
        # T-STANCE-BTN: отдельная кнопка для стоек
        tk.Button(top, text="🗡 Добавить стойку",
                  command=lambda: _feat_dialog(app, None, schedule_refresh, is_stance=True),
                  bg="#644", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="left", padx=5)
        do_rebuild()

    app._show_editor("Черты", build)

def _feat_from_catalog(app, rebuild):
    """K2d: взять черту из FEATS_CATALOG."""
    from character import FEATS_CATALOG
    if not FEATS_CATALOG:
        messagebox.showinfo("Каталог черт пуст",
                             "Создай файл в catalogs/feats/ через "
                             "«📚 Каталоги» в инвентаре.",
                             parent=app.get_dialog_parent())
        return
    d = open_window(app, "Из каталога: черты", 600, 500)
    tk.Label(d, text="Выбери черту:",
             font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=6)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=4)

    for it in FEATS_CATALOG:
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
            try:
                P.buy_feat(app.c, it.get("name", "?"),
                           it.get("desc", ""), 200, "training",
                           link=it.get("link", ""))
            except P.PurchaseError as e:
                messagebox.showerror("Ошибка", str(e), parent=d)
                return
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


def _feat_dialog(app, idx, rebuild, is_stance=False):
    is_new = idx is None
    f = app.c.feats[idx] if not is_new else None
    title = "Новая стойка" if is_stance else ("Новая черта" if is_new else "Редактировать черту")
    if is_stance and f is None:
        f = {"name": "", "desc": "", "is_stance": True} # Заглушка для галочки
    d = open_window(app, title, 540, 620)
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)
    tk.Label(body, text="Название:").pack(anchor="w", padx=5,
                                            pady=(8, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    if f:
        e_name.insert(0, f["name"])
    e_name.pack(fill="x", padx=5)

    # T-STANCE: короткое имя для чипа (только для стоек)
    tk.Label(body, text="Отображаемое имя (для чипа):").pack(anchor="w", padx=5,
                                            pady=(8, 0))
    e_disp = tk.Entry(body, font=("Segoe UI", 11))
    if f and f.get("display_name"):
        e_disp.insert(0, f["display_name"])
    e_disp.pack(fill="x", padx=5)
    tk.Label(body, text="Описание:").pack(anchor="w", padx=5,
                                            pady=(8, 0))
    t_desc = tk.Text(body, font=("Segoe UI", 10), height=8,
                      wrap="word")
    if f:
        t_desc.insert("1.0", f.get("desc", ""))
    t_desc.pack(fill="both", expand=True, padx=5)
    tk.Label(body, text="Ссылка:").pack(anchor="w", padx=5,
                                          pady=(8, 0))
    e_link = tk.Entry(body, font=("Segoe UI", 10))
    if f:
        e_link.insert(0, f.get("link", ""))
    e_link.pack(fill="x", padx=5)
    src_var = tk.StringVar(value=(f or {}).get("source", "training"))
    cost_var = tk.IntVar(
        value=(f or {}).get("invested", 200) if not is_new else 200)

    def _on_src_change(*a):
        if src_var.get() != "training":
            cost_var.set(0)
    src_var.trace_add("write", _on_src_change)
    if is_new:
        fr = tk.Frame(body)
        fr.pack(fill="x", padx=5, pady=5)
        tk.Label(fr, text="Источник:").pack(side="left")
        for src in ["training", "race", "class", "loot", "quirk",
                     "template"]:
            tk.Radiobutton(fr, text=SOURCE_NAMES[src], value=src,
                           variable=src_var).pack(side="left", padx=1)
        fr2 = tk.Frame(body)
        fr2.pack(fill="x", padx=5)
        tk.Label(fr2, text="Цена:").pack(side="left")
        tk.Entry(fr2, textvariable=cost_var, width=8).pack(
            side="left", padx=5)
    else:
        tk.Label(body,
                 text=f"Источник: "
                      f"{SOURCE_NAMES.get(f.get('source',''),'?')}, "
                      f"вложено: {f.get('invested', 0)}",
                 fg="#666").pack(anchor="w", padx=5, pady=5)

    # ===== T-EFFECTS-UI (v18.5): единый шаблон =====
    from gui_alphabet import TARGET_NAMES as _TN
    from gui_effects import (render_effects_list, apply_effects_list,
                             render_temporal_fields, apply_temporal_fields)
    is_stance_var = tk.BooleanVar(
        value=bool((f or {}).get("is_stance", False)) or is_stance)

    # Контейнер для стойки (создаём ДО использования)
    stance_frame = tk.Frame(body, bg="#f4f4f4",
                            relief="solid", borderwidth=1)
    stance_inner = tk.Frame(stance_frame, bg="#f4f4f4")
    eff_frame2 = tk.Frame(stance_inner, bg="#f4f4f4")

    # Данные эффектов (единый шаблон)
    stance_effects_data = [dict(e) for e in
                           (f or {}).get("effects", [])]
    if not stance_effects_data:
        stance_effects_data = [{"target": "ac", "value": 0,
                                 "bonus_type": "flat"}]
    stance_blocks_list = list((f or {}).get("blocks", []))
    all_targets = list(_TN.keys())

    # Рендер эффектов стойки (одна функция)
    def _render_stance_inner():
        for w in eff_frame2.winfo_children():
            w.destroy()
        render_effects_list(eff_frame2, stance_effects_data,
                            title="Эффекты (общие):")

    # Переключение видимости стойки
    def _toggle_stance_frame():
        if is_stance_var.get():
            stance_frame.pack(fill="x", padx=5, pady=(6, 0))
            stance_inner.pack(fill="x")
            _render_stance_inner()
        else:
            stance_frame.pack_forget()

    tk.Checkbutton(stance_inner,
                   text="🗡 Это стойка (показывать в «Стойка»)",
                   variable=is_stance_var,
                   command=_toggle_stance_frame,
                   font=("Segoe UI", 10, "bold"),
                   bg="#f4f4f4").pack(anchor="w", pady=(4, 0))
    eff_frame2.pack(fill="x")

    # Блок эффектов для обычных черт (не стоек)
    feat_effects_data = [dict(e) for e in (f or {}).get("effects", [])]
    if not feat_effects_data and f and not f.get("is_stance"):
        pass # не создаём пустую строку, чтобы не спамить
    feat_eff_frame = tk.Frame(body, bg="#f4f4f4")

    # Рендер эффектов обычной черты (одна функция)
    def _render_feat_inner():
        for w in feat_eff_frame.winfo_children():
            w.destroy()
        render_effects_list(feat_eff_frame, feat_effects_data,
                            title="Эффекты (общие):")

    # Показать/скрыть эффекты черты в зависимости от стойки
    def _toggle_feat_effects():
        if not is_stance_var.get():
            feat_eff_frame.pack(fill="x", padx=5, pady=(6, 0))
            _render_feat_inner()
        else:
            feat_eff_frame.pack_forget()
    is_stance_var.trace_add("write", lambda *a: _toggle_feat_effects())
    _toggle_feat_effects()

    # T-EFFECTS-UI: временные поля (общие для всех)
    _temporal = render_temporal_fields(body, f or {},
                                        on_change=None)
    _temporal["frame"].pack(fill="x", padx=5, pady=(6, 0))
    temporal_data = _temporal["data"]

    def _safe_int(var, default=0):
        try:
            return int(var.get())
        except Exception:
            return default
        
    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        desc = t_desc.get("1.0", "end").strip()
        link = e_link.get().strip()
        _is_stance = is_stance_var.get()
        _s_effects = apply_effects_list(stance_effects_data)
        _f_effects = apply_effects_list(feat_effects_data)
        _use_effects = _s_effects if _is_stance else _f_effects

        disp_name = e_disp.get().strip()
        
        if is_new:
            if getattr(app, "force_free", False):
                _new_feat = {
                    "name": name, "display_name": disp_name,
                    "desc": desc, "link": link,
                    "source": "loot", "invested": 0,
                    "is_stance": _is_stance,
                    "effects": _use_effects,
                }
                apply_temporal_fields(_new_feat, temporal_data)
                app.c.feats.append(_new_feat)
            else:
                try:
                    src = src_var.get()
                    cost = _safe_int(cost_var, 200)
                    if src == "training" and cost < 200:
                        messagebox.showwarning("Внимание", "Мин. 200",
                                                parent=d)
                        return
                    cost = max(0, cost)
                    if not messagebox.askyesno(
                            "Подтверждение",
                            f"Купить черту '{name}'?", parent=d):
                        return
                    P.buy_feat(app.c, name, desc, cost, src, link=link)
                    app.c.feats[-1]["display_name"] = disp_name
                    app.c.feats[-1]["is_stance"] = _is_stance
                    app.c.feats[-1]["effects"] = _use_effects
                    apply_temporal_fields(app.c.feats[-1], temporal_data)
                except P.PurchaseError as e:
                    messagebox.showerror("Ошибка", str(e), parent=d)
                    return
        else:
            f["name"] = name
            f["display_name"] = disp_name
            f["desc"] = desc
            f["link"] = link
            f["is_stance"] = _is_stance
            f["effects"] = _use_effects
            apply_temporal_fields(f, temporal_data)

        try:
            d.grab_release()
        except Exception:
            pass
        rebuild()
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Сохранить", command=save, bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")
    # T-STANCE (v18): показать/скрыть блок в зависимости от галочки.
    _toggle_stance_frame()

def _feat_delete(app, idx, rebuild):
    f = app.c.feats[idx]
    inv = f.get("invested", 0)
    if inv > 0:
        ans = messagebox.askyesnocancel(
            "Удаление",
            f"Удалить '{f['name']}'?\n\nВложено: {inv}\n\n"
            f"Да — вернуть {inv}\nНет — без возврата")
        if ans is None:
            return
        P.remove_feat(app.c, idx, ans)
    else:
        if not messagebox.askyesno("Удаление",
                                    f"Удалить '{f['name']}'?"):
            return
        P.remove_feat(app.c, idx, False)
    rebuild()


# ============ Квирки ============

def edit_quirks(app):
    if not app.c:
        return

    def build(parent):
        c = app.c
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=5, pady=5)

        t1_outer, _, t1 = make_scrollable(nb)
        nb.add(t1_outer, text="Росток")
        tk.Label(t1, text="Ростки — квирки (зерно/двор/фокус/"
                            "название/описание)",
                 bg="#f4f4f4", fg="#666",
                 font=("Segoe UI", 9, "italic")).pack(anchor="w",
                                                     padx=6, pady=4)
        top1 = tk.Frame(t1, bg="#f4f4f4")
        top1.pack(fill="x")
        body1 = tk.Frame(t1, bg="#f4f4f4")
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

        t2_outer, _, t2 = make_scrollable(nb)
        nb.add(t2_outer, text="Зёрна")
        tk.Label(t2, text="Справочник зёрен (просто названия). "
                            "Редактируются прямо в списке.",
                 bg="#f4f4f4", fg="#666",
                 font=("Segoe UI", 9, "italic")).pack(anchor="w",
                                                     padx=6, pady=4)
        top2 = tk.Frame(t2, bg="#f4f4f4")
        top2.pack(fill="x")
        body2 = tk.Frame(t2, bg="#f4f4f4")
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

    app._show_editor("Квирки", build)


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
        try:
            d.grab_release()
        except Exception:
            pass
        refresh()
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")


def _quirk_delete(app, idx, refresh):
    q = app.c.quirks[idx]
    if not messagebox.askyesno(
            "Удалить", f"Удалить росток '{q.get('name','?')}'?"):
        return
    app.c.quirks.pop(idx)
    refresh()

# ============ Атаки ============

def edit_attacks(app):
    if not app.c:
        return

    def build(parent):
        c = app.c
        top = tk.Frame(parent, bg="#f4f4f4")
        top.pack(fill="x", pady=4)
        tk.Button(top, text="＋ Добавить атаку",
                  command=lambda: _attack_dialog(app, None, rebuild)
                  ).pack(side="left", padx=5)
        outer, canvas, body = make_scrollable(parent)
        outer.pack(fill="both", expand=True)

        def rebuild():
            for w in body.winfo_children():
                w.destroy()
            if not c.attacks:
                tk.Label(body, text="(атак нет)",
                         bg="#f4f4f4", fg="#888",
                         font=("Segoe UI", 10, "italic")
                         ).pack(pady=20)
                return
            for i, a in enumerate(c.attacks):
                row = tk.Frame(body, bg="#f4f4f4")
                row.pack(fill="x", pady=2, padx=5)

                if i > 0:
                    tk.Button(row, text="↑", width=2,
                              command=lambda i=i: _move_attack(
                                  app, i, -1, rebuild)
                              ).pack(side="left", padx=1)
                if i < len(c.attacks) - 1:
                    tk.Button(row, text="↓", width=2,
                              command=lambda i=i: _move_attack(
                                  app, i, 1, rebuild)
                              ).pack(side="left", padx=1)

                bonus = c.attack_bonus(a)
                dmg_mod = c.attack_damage_bonus(a)
                ct, cm = c.attack_crit(a)
                dmg = a.get("damage_dice", "") or "—"
                dmg_disp = dmg
                if dmg_mod:
                    dmg_disp += f" ({dmg_mod:+d})"
                tags = []
                if a.get("is_maneuver"):
                    tags.append("прием")
                if a.get("from_item"):
                    tags.append("⚔")
                if a.get("ranged"):
                    tags.append("↗")
                elif a.get("thrown"):
                    tags.append("⟿")
                if a.get("proficiency"):
                    w_obj = c.weapon_by_name(a["proficiency"])
                    if w_obj and w_obj.get("bonuses"):
                        tags.append("✦")
                if a.get("master_ability"):
                    tags.append(f"маст {a.get('uses_current', 0)}/"
                                f"{a.get('uses_max', 0)}")
                if a.get("show_on_panel"):
                    tags.append("📌")
                tag_txt = ("  [" + ", ".join(tags) + "]"
                           if tags else "")

                nl = tk.Label(
                    row,
                    text=f"• {a['name']}{tag_txt}  "
                         f"({bonus:+d} / {dmg_disp} / "
                         f"крит {ct}+ x{cm})",
                    bg="#f4f4f4",
                    font=("Segoe UI", 10, "bold"),
                    anchor="w", cursor="hand2")
                nl.pack(side="left", padx=4, fill="x", expand=True)
                if a.get("desc"):
                    ToolTip(nl, a["desc"])
                tk.Button(row, text="✖", width=3,
                          command=lambda i=i: (
                              P.remove_attack(c, i), rebuild())
                          ).pack(side="right", padx=2)
                tk.Button(row, text="✎", width=3,
                          command=lambda i=i: _attack_dialog(
                              app, i, rebuild)
                          ).pack(side="right", padx=2)

        rebuild()

    app._show_editor("Атаки", build)


def _move_attack(app, idx, delta, rebuild):
    c = app.c
    if idx < 0 or idx >= len(c.attacks):
        return
    new_idx = idx + delta
    if new_idx < 0 or new_idx >= len(c.attacks):
        return
    c.attacks[idx], c.attacks[new_idx] = (
        c.attacks[new_idx], c.attacks[idx])
    rebuild()


def _attack_dialog(app, idx, rebuild):
    from tkinter import ttk
    c = app.c
    is_new = idx is None
    if is_new:
        a = {"name": "", "use_bab": True, "stat": "str",
             "damage_stat": "str", "damage_mult": 1.0,
             "damage_stat_auto": True,
             "finesse": False, "two_handed": False,
             "ranged": False, "thrown": False,
             "range_ft": 0,
             "extra_bonus": 0, "manual_bonus": 0,
             "damage_dice": "", "crit_threshold": 20,
             "crit_mult": 2, "desc": "", "source": "training",
             "is_maneuver": False, "from_item": None,
             "proficiency": "",
             "master_ability": False, "master_ability_id": "",
             "show_on_panel": False,
             "uses": False, "uses_max": 0, "uses_current": 0,
             "tick_on_initiative": False, "tick_mode": "none",
             "cooldown_rounds": 0, "cooldown_current": 0}
    else:
        a = c.attacks[idx]

    d = open_window(app, "Новая атака" if is_new else "Редактировать атаку", 660, 960)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True)

    def section(title):
        f = tk.Frame(body, bg="#c8c8c8")
        f.pack(fill="x", pady=(10, 2))
        tk.Label(f, text=title, font=("Segoe UI", 10, "bold"),
                 bg="#c8c8c8", anchor="w", padx=8).pack(fill="x")

    # ===== Связь с инвентарём =====
    section("Оружие из инвентаря")
    weapons_in_inv = [it for it in c.items.values()
                      if it.get("category") == "weapon"]
    w_options = [("", "— без оружия (ручная атака) —")]
    for it in weapons_in_inv:
        loc_ru = {"equipped": "надето", "bag": "сумка",
                  "unload": "разгрузка", "base": "база"
                  }.get(it["location"], "?")
        w_options.append((it["id"],
                          f"{it.get('name','?')} [{loc_ru}]"))
    w_labels = [o[1] for o in w_options]
    w_ids = [o[0] for o in w_options]
    fr_w = tk.Frame(body, bg="#f4f4f4")
    fr_w.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_w, text="Привязать к:", width=16, anchor="w",
             bg="#f4f4f4").pack(side="left")
    w_var = tk.StringVar()
    cur_iid = a.get("from_item") or ""
    try:
        w_var.set(w_labels[w_ids.index(cur_iid)])
    except (ValueError, IndexError):
        w_var.set(w_labels[0])
    w_combo = ttk.Combobox(fr_w, values=w_labels, state="readonly",
                            width=42, textvariable=w_var)
    w_combo.pack(side="left", padx=4)

    from gui_shared import hint as _hint
    _hint(body,
          "При выборе оружия — урон, крит, фехтование, "
          "двуручность, ranged/thrown и диапазон "
          "подтянутся автоматически.",
          character=c,
          fg="#666", font=("Segoe UI", 8, "italic"),
          wraplength=620, justify="left")

    # ===== Основное =====
    section("Основное")
    e_name = _row_entry(body, "Название:", a.get("name", ""))

    # ===== Попадание =====
    section("Попадание")
    use_bab_var = tk.BooleanVar(value=a.get("use_bab", True))
    tk.Checkbutton(body,
                    text="Считать автоматически (ББА + стат + доп)",
                    variable=use_bab_var, bg="#f4f4f4"
                    ).pack(anchor="w", padx=10, pady=2)

    fr_hs = tk.Frame(body, bg="#f4f4f4")
    fr_hs.pack(fill="x", padx=10, pady=2)
    tk.Label(fr_hs, text="Стат попадания:",
             bg="#f4f4f4", width=16, anchor="w"
             ).pack(side="left")
    stat_var = tk.StringVar(
        value=(a.get("stat") or "str") if a.get("use_bab") else "str")
    for ab in ("str", "dex", "con", "int", "wis", "cha"):
        tk.Radiobutton(fr_hs, text=ab.upper(), value=ab,
                        variable=stat_var,
                        bg="#f4f4f4"
                        ).pack(side="left", padx=2)

    fr_eb = tk.Frame(body, bg="#f4f4f4")
    fr_eb.pack(fill="x", padx=10, pady=2)
    tk.Label(fr_eb, text="Доп. бонус попадания:",
             bg="#f4f4f4", width=22, anchor="w"
             ).pack(side="left")
    extra_var = tk.IntVar(value=a.get("extra_bonus", 0))
    tk.Spinbox(fr_eb, from_=-20, to=20,
                textvariable=extra_var, width=5).pack(side="left")
    tk.Label(fr_eb, text="  или ручной (если выкл):",
             bg="#f4f4f4").pack(side="left")
    manual_var = tk.IntVar(value=a.get("manual_bonus", 0))
    tk.Spinbox(fr_eb, from_=-20, to=40,
                textvariable=manual_var, width=5
                ).pack(side="left", padx=4)

    # ===== Урон =====
    section("Урон")
    fr_ds = tk.Frame(body, bg="#f4f4f4")
    fr_ds.pack(fill="x", padx=10, pady=2)
    tk.Label(fr_ds, text="Стат урона:",
             bg="#f4f4f4", width=16, anchor="w"
             ).pack(side="left")
    dstat_var = tk.StringVar(
        value=a.get("damage_stat") or a.get("stat") or "str")
    for ab in ("str", "dex", "con", "int", "wis", "cha"):
        tk.Radiobutton(fr_ds, text=ab.upper(), value=ab,
                        variable=dstat_var,
                        bg="#f4f4f4"
                        ).pack(side="left", padx=2)

    auto_var = tk.BooleanVar(
        value=a.get("damage_stat_auto", True))
    tk.Checkbutton(body,
                    text="Добавлять мод стата к урону автоматически",
                    variable=auto_var, bg="#f4f4f4"
                    ).pack(anchor="w", padx=10, pady=2)

    fr_mult = tk.Frame(body, bg="#f4f4f4")
    fr_mult.pack(fill="x", padx=10, pady=2)
    tk.Label(fr_mult, text="Множитель стата:",
             bg="#f4f4f4", width=20, anchor="w"
             ).pack(side="left")
    mult_var = tk.DoubleVar(
        value=float(a.get("damage_mult", 1.0)))
    for v, label in [(0.5, "×0.5 (off-hand)"),
                      (1.0, "×1.0 (одноручное)"),
                      (1.5, "×1.5 (двуручное)")]:
        tk.Radiobutton(fr_mult, text=label, value=v,
                        variable=mult_var,
                        bg="#f4f4f4"
                        ).pack(side="left", padx=4)

    e_dmg = _row_entry(body, "Кубик урона (1d8+3):",
                        a.get("damage_dice", ""))

    fr_cr = tk.Frame(body, bg="#f4f4f4")
    fr_cr.pack(fill="x", padx=10, pady=2)
    tk.Label(fr_cr, text="Крит порог:",
             bg="#f4f4f4", width=14, anchor="w"
             ).pack(side="left")
    crit_var = tk.IntVar(value=a.get("crit_threshold", 20))
    tk.Spinbox(fr_cr, from_=2, to=20, textvariable=crit_var,
                width=4).pack(side="left", padx=2)
    tk.Label(fr_cr, text="  Множитель:",
             bg="#f4f4f4").pack(side="left")
    cmult_var = tk.IntVar(value=a.get("crit_mult", 2))
    tk.Spinbox(fr_cr, from_=2, to=10, textvariable=cmult_var,
                width=3).pack(side="left", padx=2)

    # ===== Свойства оружия =====
    section("Свойства оружия (ручная настройка)")
    fr_f = tk.Frame(body, bg="#f4f4f4")
    fr_f.pack(fill="x", padx=10, pady=2)
    finesse_var = tk.BooleanVar(value=a.get("finesse", False))
    tk.Checkbutton(fr_f,
                    text="Фехтовальное (hit от ЛОВ, урон от СИЛ)",
                    variable=finesse_var, bg="#f4f4f4"
                    ).pack(side="left", padx=4)
    twohand_var = tk.BooleanVar(value=a.get("two_handed", False))
    tk.Checkbutton(fr_f, text="Двуручное (×1.5)",
                    variable=twohand_var, bg="#f4f4f4"
                    ).pack(side="left", padx=10)

    fr_r = tk.Frame(body, bg="#f4f4f4")
    fr_r.pack(fill="x", padx=10, pady=2)
    ranged_var = tk.BooleanVar(value=a.get("ranged", False))
    tk.Checkbutton(fr_r,
                    text="Стрелковое (hit от ЛОВ, урон без мода)",
                    variable=ranged_var, bg="#f4f4f4"
                    ).pack(side="left", padx=4)
    thrown_var = tk.BooleanVar(value=a.get("thrown", False))
    tk.Checkbutton(fr_r,
                    text="Метательное (hit от ЛОВ, урон с мод СИЛ)",
                    variable=thrown_var, bg="#f4f4f4"
                    ).pack(side="left", padx=10)

    fr_rng = tk.Frame(body, bg="#f4f4f4")
    fr_rng.pack(fill="x", padx=10, pady=2)
    tk.Label(fr_rng, text="Диапазон (фт):",
             bg="#f4f4f4", width=20, anchor="w"
             ).pack(side="left")
    rng_var = tk.IntVar(value=int(a.get("range_ft", 0) or 0))
    tk.Spinbox(fr_rng, from_=0, to=1000,
                textvariable=rng_var, width=6
                ).pack(side="left", padx=4)

    # ===== Владение =====
    section("Владение (бонусы)")
    profs = c.proficiencies.get("weapons", [])
    p_options = [("", "— без владения —")]
    for w in profs:
        lvl_idx = w.get("level", 0)
        lvl = (WEAPON_LEVELS[lvl_idx]
               if lvl_idx < len(WEAPON_LEVELS) else "?")
        n_b = len(w.get("bonuses", []))
        p_options.append((w["name"],
                          f"{w['name']} — {lvl}, бонусов {n_b}"))
    p_labels = [o[1] for o in p_options]
    p_ids = [o[0] for o in p_options]
    fr_p = tk.Frame(body, bg="#f4f4f4")
    fr_p.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_p, text="Группа:", width=16, anchor="w",
             bg="#f4f4f4").pack(side="left")
    prof_var = tk.StringVar()
    cur_p = a.get("proficiency", "")
    try:
        prof_var.set(p_labels[p_ids.index(cur_p)])
    except (ValueError, IndexError):
        prof_var.set(p_labels[0])
    p_combo = ttk.Combobox(fr_p, values=p_labels, state="readonly",
                            width=42, textvariable=prof_var)
    p_combo.pack(side="left", padx=4)

    # ===== Способность мастера =====
    section("Способность мастера")
    ma_var = tk.BooleanVar(value=a.get("master_ability", False))
    tk.Checkbutton(body,
                    text="Использовать способность мастера",
                    variable=ma_var, bg="#f4f4f4"
                    ).pack(anchor="w", padx=10, pady=2)

    fr_ma = tk.Frame(body, bg="#f4f4f4")
    fr_ma.pack(fill="x", padx=10, pady=2)
    tk.Label(fr_ma, text="Способность:",
             bg="#f4f4f4", width=14, anchor="w"
             ).pack(side="left")
    ma_opts = [("", "— выбери —")]
    for bid in ("master_reroll", "master_no_attack_tag",
                 "master_full_balance"):
        bdef = WEAPON_BONUS_CATALOG.get(bid)
        if bdef:
            ma_opts.append((bid, bdef["name"]))
    ma_labels = [o[1] for o in ma_opts]
    ma_ids = [o[0] for o in ma_opts]
    ma_var_select = tk.StringVar()
    cur_ma = a.get("master_ability_id", "")
    try:
        ma_var_select.set(ma_labels[ma_ids.index(cur_ma)])
    except (ValueError, IndexError):
        ma_var_select.set(ma_labels[0])
    ma_combo = ttk.Combobox(fr_ma, values=ma_labels,
                             state="readonly", width=32,
                             textvariable=ma_var_select)
    ma_combo.pack(side="left", padx=4)

    fr_use = tk.Frame(body, bg="#f4f4f4")
    fr_use.pack(fill="x", padx=10, pady=2)
    tk.Label(fr_use, text="Заряды:",
             bg="#f4f4f4", width=14, anchor="w"
             ).pack(side="left")
    umax_var = tk.IntVar(value=a.get("uses_max", 1))
    tk.Spinbox(fr_use, from_=0, to=99,
                textvariable=umax_var, width=4
                ).pack(side="left")
    tk.Label(fr_use, text=" из:",
             bg="#f4f4f4").pack(side="left")
    ucur_var = tk.IntVar(value=a.get("uses_current", 1))
    tk.Spinbox(fr_use, from_=0, to=99,
                textvariable=ucur_var, width=4
                ).pack(side="left", padx=4)

    fr_tm = tk.Frame(body, bg="#f4f4f4")
    fr_tm.pack(fill="x", padx=10, pady=2)
    tk.Label(fr_tm, text="Тик инициативы:",
             bg="#f4f4f4", width=16, anchor="w"
             ).pack(side="left")
    tick_mode_var = tk.StringVar(value=a.get("tick_mode", "none"))
    for v, label in [("none", "не трогать"),
                      ("restore", "восстанавливать"),
                      ("decrease", "−1 заряд")]:
        tk.Radiobutton(fr_tm, text=label, value=v,
                        variable=tick_mode_var,
                        bg="#f4f4f4"
                        ).pack(side="left", padx=2)

    show_var = tk.BooleanVar(value=a.get("show_on_panel", False))
    tk.Checkbutton(body,
                    text="Показывать на быстрой панели доступа",
                    variable=show_var, bg="#f4f4f4"
                    ).pack(anchor="w", padx=10, pady=(6, 2))

    maneuver_var = tk.BooleanVar(value=a.get("is_maneuver", False))
    tk.Checkbutton(body,
                    text="Приём (считает CMD вместо AC)",
                    variable=maneuver_var, bg="#f4f4f4"
                    ).pack(anchor="w", padx=10, pady=2)

    # ===== Описание =====
    section("Описание")
    t_desc = tk.Text(body, font=("Segoe UI", 10), height=4,
                      wrap="word")
    t_desc.pack(fill="both", expand=True, padx=10, pady=4)
    t_desc.insert("1.0", a.get("desc", ""))

    # ===== Превью =====
    lbl_preview = tk.Label(body, text="", fg="#c06000",
                            bg="#f4f4f4",
                            font=("Segoe UI", 10, "bold"),
                            wraplength=620, justify="left")
    lbl_preview.pack(pady=6, padx=10)

    def _safe_int(var, default=0):
        try:
            return int(var.get())
        except Exception:
            return default

    def upd_preview(*args):
        tmp = dict(a)
        tmp["use_bab"] = use_bab_var.get()
        tmp["stat"] = stat_var.get() if use_bab_var.get() else None
        tmp["extra_bonus"] = extra_var.get()
        tmp["manual_bonus"] = manual_var.get()
        tmp["damage_stat"] = dstat_var.get()
        tmp["damage_stat_auto"] = auto_var.get()
        tmp["damage_mult"] = mult_var.get()
        tmp["crit_threshold"] = crit_var.get()
        tmp["crit_mult"] = cmult_var.get()
        tmp["damage_dice"] = e_dmg.get().strip()
        tmp["ranged"] = ranged_var.get()
        tmp["thrown"] = thrown_var.get()
        tmp["range_ft"] = _safe_int(rng_var)
        try:
            tmp["proficiency"] = p_ids[p_labels.index(prof_var.get())] \
                if prof_var.get() in p_labels else ""
        except Exception:
            tmp["proficiency"] = ""
        iid_now = ""
        try:
            iid_now = w_ids[w_labels.index(w_var.get())]
        except (ValueError, IndexError):
            pass
        tmp["from_item"] = iid_now or None
        bonus = c.attack_bonus(tmp)
        dmg_mod = c.attack_damage_bonus(tmp)
        ct, cm = c.attack_crit(tmp)
        rng = c.attack_range(tmp) if hasattr(c, "attack_range") else 0
        dmg_disp = (e_dmg.get().strip() or "—")
        if dmg_mod:
            dmg_disp += f" ({dmg_mod:+d})"

        b_parts = _attack_bonus_breakdown(c, tmp)
        d_parts = _attack_damage_breakdown(c, tmp)
        b_line = (" (" + ", ".join(b_parts) + ")") if b_parts else ""
        d_line = (" (" + ", ".join(d_parts) + ")") if d_parts else ""
        rng_line = ""
        if tmp["ranged"] or tmp["thrown"]:
            if rng > 0:
                kind = "Стрелковое" if tmp["ranged"] else "Метательное"
                rng_line = f"\n{kind}: {rng} фт"

        lbl_preview.config(
            text=f"Атака: {bonus:+d}{b_line}\n"
                 f"Урон: {dmg_disp}{d_line}\n"
                 f"Крит: {ct}+ ×{cm}{rng_line}")

    for v in (use_bab_var, stat_var, auto_var, dstat_var,
              mult_var, crit_var, cmult_var, maneuver_var,
              ranged_var, thrown_var, rng_var):
        v.trace_add("write", upd_preview)
    e_dmg.bind("<KeyRelease>", upd_preview)
    prof_var.trace_add("write", upd_preview)
    w_var.trace_add("write", upd_preview)

    # ===== Автосинхронизация с оружием =====
    def on_weapon_change(*args):
        try:
            iid = w_ids[w_labels.index(w_var.get())]
        except (ValueError, IndexError):
            return
        if not iid:
            return
        it = c.items.get(iid)
        if not it:
            return
        e_dmg.delete(0, "end")
        e_dmg.insert(0, it.get("damage", ""))
        crit_var.set(it.get("crit_threshold", 20))
        cmult_var.set(it.get("crit_mult", 2))
        finesse_var.set(bool(it.get("finesse")))
        twohand_var.set(bool(it.get("two_handed")))
        ranged_var.set(bool(it.get("ranged")))
        thrown_var.set(bool(it.get("thrown")))
        rng_var.set(int(it.get("range_ft", 0) or 0))
        if it.get("two_handed"):
            mult_var.set(1.5)
        elif it.get("slot") == "weapon_off":
            mult_var.set(0.5)
        else:
            mult_var.set(1.0)
        if it.get("finesse"):
            stat_var.set("dex")
            dstat_var.set("str")
        elif it.get("ranged"):
            stat_var.set("dex")
            dstat_var.set("str")
            auto_var.set(False)
        elif it.get("thrown"):
            stat_var.set("dex")
            dstat_var.set("str")
            auto_var.set(True)
        if not e_name.get().strip():
            e_name.insert(0, it.get("name", ""))
        wg = (it.get("weapon_group") or "").strip()
        if wg and wg in p_ids:
            prof_var.set(p_labels[p_ids.index(wg)])
        upd_preview()
    w_var.trace_add("write", on_weapon_change)

    upd_preview()

    # ===== Кнопки =====
    bf = tk.Frame(body)
    bf.pack(fill="x", pady=10, padx=10)

    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        iid = ""
        try:
            iid = w_ids[w_labels.index(w_var.get())]
        except (ValueError, IndexError):
            pass
        prof = ""
        if prof_var.get() in p_labels:
            prof = p_ids[p_labels.index(prof_var.get())]
        ma_id = ""
        if ma_var_select.get() in ma_labels:
            ma_id = ma_ids[ma_labels.index(ma_var_select.get())]
        data = dict(a)
        data.update({
            "name": name,
            "use_bab": use_bab_var.get(),
            "stat": (stat_var.get() if use_bab_var.get()
                     else None),
            "damage_stat": dstat_var.get(),
            "damage_stat_auto": auto_var.get(),
            "damage_mult": float(mult_var.get()),
            "finesse": finesse_var.get(),
            "two_handed": twohand_var.get(),
            "ranged": ranged_var.get(),
            "thrown": thrown_var.get(),
            "range_ft": _safe_int(rng_var),
            "extra_bonus": extra_var.get() if use_bab_var.get() else 0,
            "manual_bonus": manual_var.get(),
            "damage_dice": e_dmg.get().strip(),
            "crit_threshold": max(2, min(20, crit_var.get())),
            "crit_mult": max(2, cmult_var.get()),
            "desc": t_desc.get("1.0", "end").strip(),
            "source": a.get("source", "training"),
            "is_maneuver": maneuver_var.get(),
            "from_item": iid or None,
            "proficiency": prof,
            "master_ability": ma_var.get(),
            "master_ability_id": ma_id,
            "show_on_panel": show_var.get(),
            "uses": ma_var.get(),
            "uses_max": max(0, umax_var.get()) if ma_var.get() else 0,
            "uses_current": (max(0, ucur_var.get())
                             if ma_var.get() else 0),
            "tick_mode": tick_mode_var.get() if ma_var.get() else "none",
            "tick_on_initiative": (tick_mode_var.get() == "restore"
                                    if ma_var.get() else False),
        })
        if is_new:
            c.attacks.append(data)
        else:
            c.attacks[idx] = data
        try:
            d.grab_release()
        except Exception:
            pass
        rebuild()
        app._refresh()
        d.destroy()

    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")


def _attack_bonus_breakdown(c, a):
    parts = []
    if a.get("use_bab"):
        parts.append(f"ББА {c.bab_base():+d}")
        st = a.get("stat")
        if st:
            parts.append(
                f"{st.upper()} {c.ability_modifier(st):+d}")
        eb = a.get("extra_bonus", 0)
        if eb:
            parts.append(f"доп {eb:+d}")
    else:
        parts.append(f"ручной {a.get('manual_bonus', 0):+d}")

    iid = a.get("from_item")
    if iid:
        ib = c._item_bonus(iid, "attack")
        if ib:
            parts.append(f"предмет {ib:+d}")

    w = c.weapon_by_name(a.get("proficiency"))
    if w:
        wb = c.weapon_attack_bonus(w)
        if wb:
            parts.append(f"мастерство {wb:+d}")

    pen = c.pain_penalty()
    if pen:
        parts.append(f"боль {pen:+d}")
    mb = c.morale_bonus()
    if mb:
        parts.append(f"мораль {mb:+d}")
    sit = c.situational_bonus("attack")
    if sit:
        parts.append(f"ситуативка {sit:+d}")
    unprof = c.unprof_attack_penalty()
    if unprof:
        parts.append(f"невладение {unprof:+d}")
    wup = c.weapon_unprof_penalty_for_attack(a)
    if wup:
        parts.append(f"оружие не владеет {wup:+d}")
    return parts


def _attack_damage_breakdown(c, a):
    parts = []
    if a.get("damage_stat_auto", True):
        ds = a.get("damage_stat") or a.get("stat") or "str"
        dm = float(a.get("damage_mult", 1.0))
        mod = c.ability_modifier(ds)
        val = int(math.floor(mod * dm))
        if dm != 1.0:
            parts.append(f"{ds.upper()} {mod:+d} ×{dm:g} "
                         f"= {val:+d}")
        else:
            parts.append(f"{ds.upper()} {val:+d}")

    iid = a.get("from_item")
    if iid:
        ib = c._item_bonus(iid, "damage")
        if ib:
            parts.append(f"предмет {ib:+d}")

    w = c.weapon_by_name(a.get("proficiency"))
    if w:
        wb = c.weapon_damage_bonus(w)
        if wb:
            parts.append(f"мастерство {wb:+d}")

    pen = c.pain_penalty()
    if pen:
        parts.append(f"боль {pen:+d}")
    mb = c.morale_bonus()
    if mb:
        parts.append(f"мораль {mb:+d}")
    sit = c.situational_bonus("damage")
    if sit:
        parts.append(f"ситуативка {sit:+d}")
    return parts


# ============ Спасброски ============

def edit_saves(app):
    if not app.c:
        return

    def build(parent):
        c = app.c
        outer, canvas, content = make_scrollable(parent)
        outer.pack(fill="both", expand=True)
        info = tk.Frame(content, bg="#e8e8e8", pady=6, padx=6)
        info.pack(fill="x", padx=5, pady=5)
        tk.Label(info,
                 text="Автоматический расчёт (класс + стат). "
                      "Меняй только бонусы ниже. "
                      "✖ удаляет строку, «＋ Строка» добавляет.",
                 bg="#e8e8e8", fg="#333",
                 font=("Segoe UI", 9, "italic"),
                 wraplength=600, justify="left").pack(anchor="w")

        save_data = {}
        for key in ("fort", "ref", "will"):
            mods = list(c.save_mods(key))
            while len(mods) < 5:
                mods.append({"source": "", "value": 0})
            save_data[key] = mods[:]

        containers = {}
        for key in ("fort", "ref", "will"):
            cont = tk.Frame(content, bg="#f4f4f4")
            cont.pack(fill="x")
            containers[key] = cont

        def render_save(key, label):
            cont = containers[key]
            for w in cont.winfo_children():
                w.destroy()
            b = c.save_breakdown(key)
            stat_up = SAVE_STATS.get(key, "con").upper()
            good = ("хороший"
                    if key in c.char_class.get("good_saves", [])
                    else "плохой")
            hdr = tk.Frame(cont, bg="#c8c8c8")
            hdr.pack(fill="x", padx=5, pady=(10, 2))
            tk.Label(hdr,
                     text=f"═══ {label}  итого {b['total']:+d} ═══",
                     bg="#c8c8c8",
                     font=("Segoe UI", 11, "bold"),
                     anchor="w", padx=6).pack(fill="x")
            ro = tk.Frame(cont, bg="#f4f4f4")
            ro.pack(fill="x", padx=5, pady=2)
            pen_txt = ""
            if b.get("penalty"):
                pen_txt = f"   |   боль/мораль {b['penalty']:+d}"
            tk.Label(ro,
                     text=f"Класс ({good}): {b['auto']:+d}   |   "
                          f"{stat_up}: {b['ability']:+d}{pen_txt}",
                     bg="#f4f4f4", font=("Segoe UI", 10),
                     fg="#555").pack(anchor="w")

            rows = save_data[key]
            for i, row in enumerate(rows):
                fr = tk.Frame(cont, bg="#f4f4f4")
                fr.pack(fill="x", padx=5, pady=1)
                tk.Label(fr, text=f"  {i+1}.", width=4,
                         bg="#f4f4f4").pack(side="left")
                e_src = tk.Entry(fr)
                e_src.insert(0, row.get("source", ""))
                e_src.pack(side="left", fill="x", expand=True)

                def on_src(event=None, idx=i, entry=e_src, k=key):
                    save_data[k][idx]["source"] = entry.get()
                e_src.bind("<KeyRelease>", on_src)
                e_src.bind("<FocusOut>", on_src)

                tk.Label(fr, text="бонус:", bg="#f4f4f4"
                         ).pack(side="left", padx=(6, 2))
                v_val = tk.IntVar(value=row.get("value", 0))
                tk.Spinbox(fr, from_=-20, to=20,
                            textvariable=v_val, width=5
                            ).pack(side="left", padx=2)

                def on_val(idx=i, var=v_val, k=key):
                    try:
                        save_data[k][idx]["value"] = var.get()
                    except Exception:
                        pass
                v_val.trace_add("write",
                                 lambda *a, f=on_val: f())

                def del_row(idx=i, k=key, lbl=label):
                    save_data[k].pop(idx)
                    if not save_data[k]:
                        save_data[k].append({"source": "",
                                              "value": 0})
                    render_save(k, lbl)
                tk.Button(fr, text="✖", width=3,
                          command=del_row).pack(side="right", padx=2)

            def add_row(k=key, lbl=label):
                save_data[k].append({"source": "", "value": 0})
                render_save(k, lbl)
            tk.Button(cont, text="＋ Строка", command=add_row
                      ).pack(anchor="w", padx=10, pady=4)

        def save():
            for key in ("fort", "ref", "will"):
                mods = []
                for row in save_data[key]:
                    src = row.get("source", "").strip()
                    val = row.get("value", 0)
                    if src:
                        mods.append({"source": src, "value": val})
                c.combat["saves"][key] = {"base": 0, "mods": mods}
            app._show_main()

        for key, label in [("fort", "Fort"), ("ref", "Ref"),
                            ("will", "Will")]:
            render_save(key, label)

        tk.Button(content, text="Сохранить", command=save,
                  bg="#4a7", fg="white",
                  font=("Segoe UI", 10, "bold")).pack(pady=8)

    app._show_editor("Спасброски", build)


# ============ Настройки (v12) ============

def edit_settings(app):
    if not app.c:
        return

    def build(parent):
        c = app.c
        outer, canvas, body = make_scrollable(parent)
        outer.pack(fill="both", expand=True)

        tk.Label(body, text="Показывать в чарнике:",
                 font=("Segoe UI", 11, "bold"),
                 bg="#f4f4f4").pack(anchor="w", padx=10, pady=8)
        v_portrait = tk.BooleanVar(
            value=c.settings.get("hide_portrait", False))
        tk.Checkbutton(body, text="Скрыть портрет",
                       variable=v_portrait, bg="#f4f4f4"
                       ).pack(anchor="w", padx=20)

        tk.Label(body, text="Опции отдыха сверху:",
                 font=("Segoe UI", 11, "bold"),
                 bg="#f4f4f4").pack(anchor="w", padx=10,
                                      pady=(12, 4))
        v_rest_short = tk.BooleanVar(
            value=c.settings.get("show_rest_short", True))
        tk.Checkbutton(body, text="🛌 Короткий отдых",
                       variable=v_rest_short, bg="#f4f4f4"
                       ).pack(anchor="w", padx=20)
        v_rest_long = tk.BooleanVar(
            value=c.settings.get("show_rest_long", True))
        tk.Checkbutton(body, text="🛏 Длинный отдых",
                       variable=v_rest_long, bg="#f4f4f4"
                       ).pack(anchor="w", padx=20)
        v_bp_chip = tk.BooleanVar(
            value=c.settings.get("show_bp_chip", True))
        tk.Checkbutton(body, text="🩹 Чип БП в панели ресурсов",
                       variable=v_bp_chip, bg="#f4f4f4"
                       ).pack(anchor="w", padx=20)

        v_hide_hints = tk.BooleanVar(
            value=c.settings.get("hide_hints", False))
        tk.Checkbutton(body,
                       text="🙈 Скрыть примечания в редакторах",
                       variable=v_hide_hints, bg="#f4f4f4"
                       ).pack(anchor="w", padx=20)

        fr_regen = tk.Frame(body, bg="#f4f4f4")
        fr_regen.pack(fill="x", padx=20, pady=(4, 0))
        tk.Label(fr_regen, text="HP-реген за тик:",
                 bg="#f4f4f4").pack(side="left")
        regen_var = tk.IntVar(
            value=int(c.settings.get("hp_regen_per_tick", 0) or 0))
        tk.Spinbox(fr_regen, from_=0, to=99,
                    textvariable=regen_var, width=5
                    ).pack(side="left", padx=4)

        # T38.1: отключение каталогов
        from character import CATALOG_SUBDIRS
        tk.Label(body, text="Каталоги (отключить):",
                 font=("Segoe UI", 11, "bold"),
                 bg="#f4f4f4").pack(anchor="w", padx=10,
                                      pady=(10, 2))
        catalogs_vars = {}
        cur_enabled = list(c.settings.get("catalogs_enabled", []))
        for sub in CATALOG_SUBDIRS:
            v = tk.BooleanVar(value=(sub in cur_enabled))
            tk.Checkbutton(body, text=sub, variable=v,
                           bg="#f4f4f4"
                           ).pack(anchor="w", padx=20)
            catalogs_vars[sub] = v

        tk.Label(body, text="Тик инициативы:",
                 font=("Segoe UI", 11, "bold"),
                 bg="#f4f4f4").pack(anchor="w", padx=10,
                                      pady=(12, 4))
        v_auto_bal = tk.BooleanVar(
            value=getattr(c, "auto_balance_on_tick", True))
        tk.Checkbutton(body,
                       text="🔁 Авто-восстановление баланса "
                            "на тике инициативы",
                       variable=v_auto_bal, bg="#f4f4f4"
                       ).pack(anchor="w", padx=20)

        # ===== T-CHIPS: чипы (v18.6) =====
        tk.Label(body, text="Чипы (панель ресурсов):",
                 font=("Segoe UI", 11, "bold"),
                 bg="#f4f4f4").pack(anchor="w", padx=10, pady=(12, 4))

        v_chips_enabled = tk.BooleanVar(
            value=c.settings.get("chips_visible_enabled", False))
        tk.Checkbutton(body,
                       text="🎛 Фильтр чипов включён (показывать только выбранные)",
                       variable=v_chips_enabled, bg="#f4f4f4"
                       ).pack(anchor="w", padx=20)

        fr_chips_btns = tk.Frame(body, bg="#f4f4f4")
        fr_chips_btns.pack(fill="x", padx=20, pady=(4, 2))

        def _toggle_all_chips():
            """Спрятать/показать все чипы (toggle)."""
            enabled = c.settings.get("chips_visible_enabled", False)
            if enabled:
                # сейчас спрятаны → показать все
                c.settings["chips_visible_enabled"] = False
                c.settings["chips_visible"] = []
            else:
                # сейчас видны → спрятать все
                c.settings["chips_visible_enabled"] = True
                c.settings["chips_visible"] = []
            v_chips_enabled.set(c.settings["chips_visible_enabled"])
            app._refresh()

        def _reset_chips():
            """Сбросить все чипы: базовое местоположение + все включены."""
            if not messagebox.askyesno(
                    "Сбросить чипы",
                    "Сбросить порядок и видимость всех чипов?\n"
                    "(Все чипы вернутся на свои места по умолчанию.)",
                    parent=app.get_dialog_parent()):
                return
            c.settings["chips_order"] = []
            c.settings["chips_visible"] = []
            c.settings["chips_visible_enabled"] = False
            v_chips_enabled.set(False)
            app._refresh()

        tk.Button(fr_chips_btns, text="👁 Спрятать/показать все",
                  command=_toggle_all_chips,
                  bg="#555", fg="white", relief="flat",
                  font=("Segoe UI", 9)).pack(side="left", padx=2)
        tk.Button(fr_chips_btns, text="🔄 Сбросить все чипы",
                  command=_reset_chips,
                  bg="#855", fg="white", relief="flat",
                  font=("Segoe UI", 9)).pack(side="left", padx=2)

        # ===== T-CHIPS: цвета чипов =====
        tk.Label(body, text="Цвета чипов (кастомные):",
                 font=("Segoe UI", 10, "bold"),
                 bg="#f4f4f4").pack(anchor="w", padx=20, pady=(8, 2))

        import chips as _chips
        all_specs = _chips.collect_all(c)
        colors = c.settings.get("chips_colors", {}) or {}
        chip_choices = [f"{s['id']}  |  {s['label']}" for s in all_specs]
        if not chip_choices:
            chip_choices = ["(нет чипов)"]

        fr_color = tk.Frame(body, bg="#f4f4f4")
        fr_color.pack(fill="x", padx=20, pady=2)

        color_chip_var = tk.StringVar(value=chip_choices[0])
        opt_color = tk.OptionMenu(fr_color, color_chip_var, *chip_choices)
        opt_color.config(width=32, font=("Segoe UI", 9), anchor="w")
        opt_color.pack(side="left")

        tk.Label(fr_color, text="цвет:", bg="#f4f4f4",
                 font=("Segoe UI", 9)).pack(side="left", padx=(8, 2))
        color_hex_var = tk.StringVar(value="")
        e_color = tk.Entry(fr_color, textvariable=color_hex_var,
                           width=9, font=("Segoe UI", 10))
        e_color.pack(side="left")
        e_color.insert(0, "")

        def _get_selected_id():
            txt = color_chip_var.get()
            return txt.split("  |  ")[0].strip() if "  |  " in txt else txt.strip()

        def _apply_color():
            cid = _get_selected_id()
            hexval = color_hex_var.get().strip()
            if not hexval:
                # удалить кастомный цвет
                if cid in colors:
                    del colors[cid]
                    c.settings["chips_colors"] = colors
                app._refresh()
                return
            # простая валидация
            if not hexval.startswith("#"):
                hexval = "#" + hexval
            if len(hexval) not in (4, 7):
                messagebox.showwarning(
                    "Цвет", "Введите цвет в формате #RRGGBB\n"
                            "(например #ff0000).", parent=app.get_dialog_parent())
                return
            colors[cid] = hexval
            c.settings["chips_colors"] = colors
            app._refresh()

        def _reset_color():
            cid = _get_selected_id()
            if cid in colors:
                del colors[cid]
                c.settings["chips_colors"] = colors
            color_hex_var.set("")
            app._refresh()

        def _on_pick_color(*_):
            cid = _get_selected_id()
            color_hex_var.set(colors.get(cid, ""))

        color_chip_var.trace_add("write", _on_pick_color)

        tk.Button(fr_color, text="Применить", command=_apply_color,
                  bg="#4a7", fg="white", relief="flat",
                  font=("Segoe UI", 9)).pack(side="left", padx=(8, 2))
        tk.Button(fr_color, text="Сбросить", command=_reset_color,
                  bg="#855", fg="white", relief="flat",
                  font=("Segoe UI", 9)).pack(side="left", padx=2)

        _on_pick_color()

        # ===== Ручной бонус инициативы =====
        tk.Label(body, text="Инициатива:",
                 font=("Segoe UI", 11, "bold"),
                 bg="#f4f4f4").pack(anchor="w", padx=10,
                                      pady=(12, 4))
        fr_init = tk.Frame(body, bg="#f4f4f4")
        fr_init.pack(fill="x", padx=20, pady=2)
        tk.Label(fr_init,
                 text="Ручной бонус к инициативе:",
                 bg="#f4f4f4").pack(side="left")
        init_var = tk.IntVar(
            value=int(c.combat.get("initiative", 0) or 0))
        tk.Spinbox(fr_init, from_=-20, to=20,
                    textvariable=init_var, width=5
                    ).pack(side="left", padx=6)
        tk.Label(fr_init,
                 text="(прибавляется к ЛОВ + ситуативка)",
                 bg="#f4f4f4", fg="#666",
                 font=("Segoe UI", 8)
                 ).pack(side="left", padx=4)

        tk.Frame(body, height=10, bg="#f4f4f4").pack()

        fr_port = tk.Frame(body, bg="#f4f4f4")
        fr_port.pack(fill="x", padx=10, pady=4)
        tk.Label(fr_port, text="Портрет:",
                 font=("Segoe UI", 10, "bold"),
                 bg="#f4f4f4", anchor="w").pack(anchor="w")
        row_port = tk.Frame(fr_port, bg="#f4f4f4")
        row_port.pack(fill="x", pady=(2, 4))
        lbl_port_status = tk.Label(
            row_port,
            text=("загружен" if c.portrait_b64 or c.portrait
                  else "не задан"),
            bg="#f4f4f4", fg="#666",
            font=("Segoe UI", 9, "italic"))
        lbl_port_status.pack(side="left", padx=4)

        def load_port():
            from tkinter import filedialog as fd
            path = fd.askopenfilename(
                parent=app.get_dialog_parent(),
                filetypes=[("Картинки",
                            "*.png *.jpg *.jpeg *.gif *.bmp"),
                            ("Все", "*.*")])
            if not path:
                return
            c.portrait = path
            c.portrait_b64 = ""
            c.embed_images()
            lbl_port_status.config(text="загружен")
            gui_media.update_portrait_size(app)
            app._refresh()

        def remove_port():
            if not messagebox.askyesno(
                    "Убрать портрет",
                    "Удалить портрет персонажа?",
                    parent=app.get_dialog_parent()):
                return
            c.portrait = ""
            c.portrait_b64 = ""
            lbl_port_status.config(text="не задан")
            gui_media.update_portrait_size(app)
            app._refresh()

        tk.Button(row_port, text="📷 Загрузить",
                  command=load_port).pack(side="left", padx=2)
        tk.Button(row_port, text="🗑 Удалить",
                  command=remove_port).pack(side="left", padx=2)

        fr_bg = tk.Frame(body, bg="#f4f4f4")
        fr_bg.pack(fill="x", padx=10, pady=4)
        tk.Label(fr_bg, text="Фон чарника:",
                 font=("Segoe UI", 10, "bold"),
                 bg="#f4f4f4", anchor="w").pack(anchor="w")
        row_bg = tk.Frame(fr_bg, bg="#f4f4f4")
        row_bg.pack(fill="x", pady=(2, 4))
        lbl_bg_status = tk.Label(
            row_bg,
            text=("загружен" if c.background_b64
                  or c.background_image else "не задан"),
            bg="#f4f4f4", fg="#666",
            font=("Segoe UI", 9, "italic"))
        lbl_bg_status.pack(side="left", padx=4)

        def load_bg():
            from tkinter import filedialog as fd
            path = fd.askopenfilename(
                parent=app.get_dialog_parent(),
                filetypes=[("Картинки",
                            "*.png *.jpg *.jpeg *.gif *.bmp"),
                            ("Все", "*.*")])
            if not path:
                return
            c.background_image = path
            c.background_b64 = ""
            c.embed_images()
            lbl_bg_status.config(text="загружен")
            app._refresh()

        def remove_bg():
            if not messagebox.askyesno(
                    "Убрать фон",
                    "Удалить фон персонажа?",
                    parent=app.get_dialog_parent()):
                return
            c.background_image = ""
            c.background_b64 = ""
            lbl_bg_status.config(text="не задан")
            app._refresh()

        tk.Button(row_bg, text="🖼 Загрузить",
                  command=load_bg).pack(side="left", padx=2)
        tk.Button(row_bg, text="🗑 Удалить",
                  command=remove_bg).pack(side="left", padx=2)

        # ===== Окна и меню (T-WINDOW) =====
        tk.Label(body, text="Окна редакторов:",
                 font=("Segoe UI", 11, "bold"),
                 bg="#f4f4f4").pack(anchor="w", padx=10, pady=(12, 4))
                 
        open_mode_var = tk.StringVar(value=c.settings.get("window_open_mode", "pointer"))
        fr_mode = tk.Frame(body, bg="#f4f4f4")
        fr_mode.pack(fill="x", padx=20, pady=2)
        tk.Radiobutton(fr_mode, text="У курсора (мышки)", value="pointer",
                       variable=open_mode_var, bg="#f4f4f4").pack(side="left", padx=4)
        tk.Radiobutton(fr_mode, text="Справа от меню", value="menu",
                       variable=open_mode_var, bg="#f4f4f4").pack(side="left", padx=4)
        tk.Radiobutton(fr_mode, text="По центру", value="center",
                       variable=open_mode_var, bg="#f4f4f4").pack(side="left", padx=4)

        v_pin = tk.BooleanVar(value=c.settings.get("pin_editor_to_menu", True))
        tk.Checkbutton(body, text="📌 Привязывать окна к меню (магнит)",
                       variable=v_pin, bg="#f4f4f4").pack(anchor="w", padx=20, pady=(2, 0))

        v_close_prev = tk.BooleanVar(value=c.settings.get("close_prev_window", True))
        tk.Checkbutton(body, text="❌ Закрывать предыдущее окно при открытии нового",
                       variable=v_close_prev, bg="#f4f4f4").pack(anchor="w", padx=20, pady=(0, 4))

        tk.Frame(body, height=12, bg="#f4f4f4").pack()

        tk.Label(body, text="Кнопки в левом меню:",
                 font=("Segoe UI", 11, "bold"),
                 bg="#f4f4f4").pack(anchor="w", padx=10, pady=8)
        tk.Label(body,
                 text="Отключи галочку — кнопка исчезнет из "
                      "боковой панели.",
                 fg="#666", font=("Segoe UI", 9, "italic")
                 ).pack(anchor="w", padx=10)

        vars_buttons = {}
        try:
            buttons_list = app._buttons()
        except Exception:
            buttons_list = []
        from gui_buttons import FORCED_VISIBLE_BUTTONS
        for text, cmd, key in buttons_list:
            if cmd is None or key is None:
                continue
            if key in FORCED_VISIBLE_BUTTONS:
                continue
            v = tk.BooleanVar(value=app._is_visible(key))
            tk.Checkbutton(body, text=text, variable=v,
                           bg="#f4f4f4").pack(anchor="w", padx=20)
            vars_buttons[key] = v

        def apply():
            c.settings["hide_portrait"] = v_portrait.get()
            c.settings["window_open_mode"] = open_mode_var.get()
            c.settings["pin_editor_to_menu"] = v_pin.get()
            c.settings["close_prev_window"] = v_close_prev.get()
            c.settings["show_rest_short"] = v_rest_short.get()
            c.settings["show_rest_long"] = v_rest_long.get()
            c.settings["show_bp_chip"] = v_bp_chip.get()
            c.settings["hide_hints"] = v_hide_hints.get()
            c.settings["chips_visible_enabled"] = v_chips_enabled.get()
            try:
                c.settings["hp_regen_per_tick"] = max(
                    0, int(regen_var.get() or 0))
            except Exception:
                c.settings["hp_regen_per_tick"] = 0
            c.settings["catalogs_enabled"] = [
                sub for sub, v in catalogs_vars.items() if v.get()]
            c.auto_balance_on_tick = v_auto_bal.get()
            try:
                c.combat["initiative"] = int(init_var.get())
            except Exception:
                c.combat["initiative"] = 0
            vb = c.settings.setdefault("visible_buttons", {})
            for k, v in vars_buttons.items():
                vb[k] = v.get()
            gui_media.update_portrait_size(app)
            gui_buttons.rebuild_side_buttons(app)
            app._refresh()

        tk.Button(body, text="Применить", command=apply,
                  bg="#4a7", fg="white",
                  font=("Segoe UI", 10, "bold")
                  ).pack(pady=14)

    app._show_editor("Настройки", build)
# ============ CMB / CMD модификаторы ============
def edit_cmb_mods(app):
    _edit_mod_list(app, "cmb_mods", "CMB-модификаторы",
                   "Бонусы и штрафы к CMB (боевые манёвры).")


def edit_cmd_mods(app):
    _edit_mod_list(app, "cmd_mods", "CMD-модификаторы",
                   "Бонусы и штрафы к CMD (защита от манёвров).")


def _edit_mod_list(app, attr, title, hint):
    if not app.c:
        return
    c = app.c

    def build(parent):
        outer, canvas, body = make_scrollable(parent)
        outer.pack(fill="both", expand=True)
        info = tk.Frame(body, bg="#e8e8e8", pady=6, padx=6)
        info.pack(fill="x", padx=5, pady=5)
        tk.Label(info, text=hint, bg="#e8e8e8", fg="#333",
                 font=("Segoe UI", 9, "italic"),
                 wraplength=600, justify="left").pack(anchor="w")

        rows = [dict(m) for m in getattr(c, attr, [])]
        if not rows:
            rows = [{"source": "", "value": 0}]

        cont = tk.Frame(body, bg="#f4f4f4")
        cont.pack(fill="x", padx=5, pady=4)

        def render():
            for w in cont.winfo_children():
                w.destroy()
            total = sum(r.get("value", 0) for r in rows
                        if r.get("source", "").strip())
            tk.Label(cont,
                     text=f"Итого: {total:+d}",
                     bg="#f4f4f4", fg="#c06000",
                     font=("Segoe UI", 10, "bold")
                     ).pack(anchor="w", pady=(0, 4))
            for i, row in enumerate(rows):
                fr = tk.Frame(cont, bg="#f4f4f4")
                fr.pack(fill="x", pady=1)
                tk.Label(fr, text=f"  {i+1}.", width=4,
                         bg="#f4f4f4").pack(side="left")
                e_src = tk.Entry(fr)
                e_src.insert(0, row.get("source", ""))
                e_src.pack(side="left", fill="x", expand=True)

                def on_src(event=None, idx=i, ent=e_src):
                    rows[idx]["source"] = ent.get()
                    total_lbl.config(
                        text=f"Итого: "
                             f"{sum(r.get('value', 0) for r in rows if r.get('source', '').strip()):+d}")
                e_src.bind("<KeyRelease>", on_src)
                e_src.bind("<FocusOut>", on_src)

                tk.Label(fr, text="бонус:", bg="#f4f4f4"
                         ).pack(side="left", padx=(6, 2))
                v_val = tk.IntVar(value=row.get("value", 0))
                tk.Spinbox(fr, from_=-50, to=50,
                            textvariable=v_val, width=5
                            ).pack(side="left", padx=2)

                def on_val(idx=i, var=v_val):
                    try:
                        rows[idx]["value"] = int(var.get())
                    except Exception:
                        rows[idx]["value"] = 0
                    total_lbl.config(
                        text=f"Итого: "
                             f"{sum(r.get('value', 0) for r in rows if r.get('source', '').strip()):+d}")
                v_val.trace_add("write", lambda *a, f=on_val: f())

                def del_row(idx=i):
                    rows.pop(idx)
                    if not rows:
                        rows.append({"source": "", "value": 0})
                    render()
                tk.Button(fr, text="✖", width=3,
                          command=del_row).pack(side="right", padx=2)

        total_lbl = tk.Label(cont, text="", bg="#f4f4f4",
                              fg="#c06000",
                              font=("Segoe UI", 10, "bold"))
        total_lbl.pack(anchor="w", pady=(0, 4))
        render()

        def add_row():
            rows.append({"source": "", "value": 0})
            render()
        tk.Button(body, text="＋ Строка", command=add_row
                  ).pack(anchor="w", padx=10, pady=4)

        def save():
            clean = [{"source": r["source"].strip(),
                      "value": int(r.get("value", 0))}
                     for r in rows if r.get("source", "").strip()]
            setattr(c, attr, clean)
            c.recompute_derived()
            app._show_main()

        tk.Button(body, text="Сохранить", command=save,
                  bg="#4a7", fg="white",
                  font=("Segoe UI", 10, "bold")
                  ).pack(pady=8)

    app._show_editor(title, build)