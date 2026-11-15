# gui_training.py — окно "Редактирование" (v13)
# v13: основы оружия — выбор "за тренировки" / "бесплатно"

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from character import (WEAPON_LEVELS, ARMOR_LEVELS, SHIELD_LEVELS,
                       ARMOR_DISPLAY, SHIELD_DISPLAY, SIZES, SIZE_AC,
                       SOURCE_ICONS, SOURCE_NAMES,
                       WEAPON_BONUS_CATALOG, WEAPON_BONUS_SLOTS,
                       allowed_bonus_types_for_slot)
from gui_shared import make_scrollable
from gui_windows import open_window
import purchases as P

def _gi_int(var, default=0):
    """Безопасно читает IntVar; пусто/мусор -> default."""
    try:
        return int(var.get())
    except (tk.TclError, ValueError):
        return default


def _safe_set(var, value):
    """Безопасно пишет в IntVar (для Spinbox)."""
    try:
        var.set(int(value))
    except (tk.TclError, ValueError):
        pass

def edit_training(app):
    if not app.c:
        return

    def build(parent):
        c = app.c
        top = tk.Frame(parent, bg="#2b2b2b", pady=8, padx=10)
        top.pack(fill="x")
        tk.Label(top, text=f"{c.name} — {c.char_class['name']} "
                            f"{c.level}",
                 font=("Segoe UI", 12, "bold"), fg="white",
                 bg="#2b2b2b", anchor="w").pack(fill="x")
        lbl_pts = tk.Label(top, text="", font=("Segoe UI", 11),
                            fg="#f0c040", bg="#2b2b2b", anchor="w")
        lbl_pts.pack(fill="x")

        add_frame = tk.Frame(parent, bg="#3a3a3a", pady=4, padx=6)
        add_frame.pack(fill="x", pady=(0, 4))
        tk.Label(add_frame, text="Добавить/убавить тренировок:",
                 bg="#3a3a3a", fg="white",
                 font=("Segoe UI", 10)).pack(side="left")
        e_add = tk.Entry(add_frame, width=8,
                          font=("Segoe UI", 10))
        e_add.pack(side="left", padx=6)
        rate = (c.level + 1) * 5
        tk.Label(add_frame, text=f"(Enter. Можно -число. "
                                   f"1 комфорт = {rate} тренировок)",
                 bg="#3a3a3a", fg="#aaa",
                 font=("Segoe UI", 9)).pack(side="left", padx=6)

        outer, canvas, inner = make_scrollable(parent)
        outer.pack(fill="both", expand=True, pady=5)
        pending = [None]

        def do_rebuild():
            pending[0] = None
            try:
                for w in inner.winfo_children():
                    w.destroy()
                lbl_pts.config(
                    text=f"Осталось: {c.training['available']}  /  "
                         f"Потрачено: {c.training['spent']}")
                _fill_training(app, inner, schedule_refresh)
            except Exception as e:
                print(f"[training rebuild] {e}")

        def schedule_refresh():
            if pending[0] is not None:
                try:
                    app.root.after_cancel(pending[0])
                except Exception:
                    pass
            pending[0] = app.root.after(30, do_rebuild)

        def on_add(e=None):
            try:
                n = int(e_add.get().strip())
            except Exception:
                messagebox.showwarning("Ошибка", "Введите число")
                return
            P.add_training_points(c, n)
            e_add.delete(0, "end")
            schedule_refresh()
        e_add.bind("<Return>", on_add)

        lbl_pts.config(
            text=f"Осталось: {c.training['available']}  /  "
                 f"Потрачено: {c.training['spent']}")
        _fill_training(app, inner, schedule_refresh)

    app._show_editor("Редактирование", build)


def _fill_training(app, parent, refresh):
    c = app.c

    def section(title, subtitle=None):
        f = tk.Frame(parent, bg="#c8c8c8")
        f.pack(fill="x", pady=(10, 2))
        tk.Label(f, text=title, font=("Segoe UI", 11, "bold"),
                 bg="#c8c8c8", anchor="w", padx=8).pack(fill="x")
        if subtitle:
            sf = tk.Frame(parent, bg="#f4f4f4")
            sf.pack(fill="x")
            tk.Label(sf, text=subtitle, bg="#f4f4f4", fg="#666",
                     font=("Segoe UI", 9, "italic"), anchor="w",
                     justify="left", wraplength=700
                     ).pack(anchor="w", padx=10, pady=(2, 2))

    def info_label(text, fg="#555"):
        f = tk.Frame(parent, bg="#f4f4f4")
        f.pack(fill="x", pady=1, padx=5)
        tk.Label(f, text=text, bg="#f4f4f4", fg=fg,
                 font=("Segoe UI", 10, "bold"), anchor="w"
                 ).pack(anchor="w", padx=10)

    def add_btn(text, command):
        f = tk.Frame(parent, bg="#f4f4f4")
        f.pack(fill="x", pady=3, padx=5)
        tk.Button(f, text=text, command=command).pack(side="left")

    def row_actions(text, cost, buy_fn, free_fn, remove_fn,
                    down_fn=None, edit_fn=None):
        f = tk.Frame(parent, bg="#f4f4f4")
        f.pack(fill="x", pady=1, padx=5)
        tk.Label(f, text=text, anchor="w", bg="#f4f4f4",
                 font=("Segoe UI", 10)).pack(side="left", fill="x",
                                              expand=True)
        tk.Button(f, text="✖", width=3, command=remove_fn
                  ).pack(side="right", padx=1)
        if edit_fn:
            tk.Button(f, text="✎", width=3, command=edit_fn
                      ).pack(side="right", padx=1)
        if down_fn:
            tk.Button(f, text="↓", width=3, command=down_fn
                      ).pack(side="right", padx=1)
        tk.Label(f, text=str(cost), fg="#c06000", bg="#f4f4f4",
                 font=("Segoe UI", 10, "bold")).pack(side="right",
                                                      padx=5)
        tk.Button(f, text="↑", width=3,
                  command=lambda: _try(refresh, buy_fn)
                  ).pack(side="right", padx=1)
        if free_fn:
            tk.Button(f, text="★", width=3,
                      command=lambda: _free_buy(refresh, free_fn)
                      ).pack(side="right", padx=1)

    def row_remove(text, remove_fn):
        f = tk.Frame(parent, bg="#f4f4f4")
        f.pack(fill="x", pady=1, padx=5)
        tk.Label(f, text=text, anchor="w", bg="#f4f4f4",
                 font=("Segoe UI", 10)).pack(side="left", fill="x",
                                              expand=True)
        tk.Button(f, text="✖", width=3, command=remove_fn
                  ).pack(side="right", padx=1)

    # ============ ОПЫТ ============
    section("Опыт")
    f_xp = tk.Frame(parent, bg="#f4f4f4")
    f_xp.pack(fill="x", pady=1, padx=5)
    tk.Label(f_xp, text=f"XP: {c.xp}/{c.xp_threshold}",
             bg="#f4f4f4", font=("Segoe UI", 11, "bold")
             ).pack(side="left", padx=4)
    tk.Label(f_xp, text="   Изменить на:", bg="#f4f4f4",
             font=("Segoe UI", 10)).pack(side="left", padx=(10, 2))
    e_xp = tk.Entry(f_xp, width=8, font=("Segoe UI", 10))
    e_xp.pack(side="left", padx=4)

    def apply_xp(sign=1):
        try:
            n = abs(int(e_xp.get().strip()))
        except Exception:
            messagebox.showwarning("Ошибка", "Введите целое число")
            return
        c.add_xp(n * sign)
        e_xp.delete(0, "end")
        refresh()

    e_xp.bind("<Return>", lambda e: apply_xp(1))
    tk.Button(f_xp, text="+ добавить",
              command=lambda: apply_xp(1)).pack(side="left", padx=2)
    tk.Button(f_xp, text="− снять",
              command=lambda: apply_xp(-1)).pack(side="left", padx=2)
    tk.Label(f_xp, text="  (Enter — добавить)",
             bg="#f4f4f4", fg="#666",
             font=("Segoe UI", 9)).pack(side="left", padx=4)

    # T43: пояснение про Level Up (кнопка в верхней панели).
    tk.Label(parent,
             text="💡 При XP ≥ 1000 в верхней панели появляется "
                  "кнопка «⬆ Level Up». Она: +1 уровень, "
                  "+HP-бросок, +уровень×100 тренировок, "
                  "XP −= 1000.",
             bg="#f4f4f4", fg="#0066cc",
             font=("Segoe UI", 9, "italic"),
             wraplength=680, justify="left", anchor="w"
             ).pack(fill="x", padx=10, pady=(2, 6))

    # ============ ХАРАКТЕРИСТИКИ ============
    # ============ ХАРАКТЕРИСТИКИ ============
    section("Характеристики",
            subtitle="↑/★/↓/OK — покупка и понижение. "
                     "«Урон» — повреждение стата (атаки призраков "
                     "и т.п.). Эффективно = база − урон. "
                     "✚ — снять весь урон со стата.")
    for ab, full in [("str", "Сила"), ("dex", "Ловкость"),
                      ("con", "Телосложение"), ("int", "Интеллект"),
                      ("wis", "Мудрость"), ("cha", "Харизма")]:
        v = c.abilities[ab]
        dmg = c.ability_damage.get(ab, 0)
        eff = v - dmg
        cost = P.ability_up_cost(c, ab)

        row = tk.Frame(parent, bg="#f4f4f4")
        row.pack(fill="x", pady=1, padx=5)

        # Левая часть: имя и значение (с уроном если есть)
        if dmg > 0:
            txt = f"{full} {eff}/{v} (урон {dmg})"
            fg_col = "#cc3333"
        else:
            txt = f"{full} {v}"
            fg_col = "#000"
        tk.Label(row, text=txt, anchor="w",
                 bg="#f4f4f4", font=("Segoe UI", 10),
                 fg=fg_col, width=26).pack(side="left")

        # Спинбокс быстрого изменения базы
        tk.Label(row, text="→", bg="#f4f4f4",
                 font=("Segoe UI", 10, "bold")).pack(side="left",
                                                      padx=(2, 2))
        fast_var = tk.IntVar(value=v)
        tk.Spinbox(row, from_=1, to=50, textvariable=fast_var,
                    width=4, font=("Segoe UI", 10)
                    ).pack(side="left", padx=2)

        def fast_apply(ab=ab, var=fast_var):
            target = _gi_int(var, c.abilities[ab])
            cur = c.abilities[ab]
            if target == cur:
                return
            if target > cur:
                cost = P.ability_up_cost_total(c, ab, target)
                if not messagebox.askyesno(
                        "Подтверждение",
                        f"{ab.upper()}: {cur} → {target} "
                        f"за {cost} очков?"):
                    return
                try:
                    P.buy_ability_up_to(c, ab, target, "training")
                    refresh()
                except P.PurchaseError as e:
                    messagebox.showerror("Ошибка", str(e))
            else:
                diff = cur - target
                if diff <= 0:
                    return
                if not messagebox.askyesno(
                        "Подтверждение",
                        f"Понизить {ab.upper()} с {cur} до {target}? "
                        f"Вернуть очки (если платили)?"):
                    return
                try:
                    for _ in range(diff):
                        if c.abilities[ab] <= 1:
                            break
                        P.remove_ability_up(c, ab, True)
                    refresh()
                except P.PurchaseError as e:
                    messagebox.showerror("Ошибка", str(e))

        def fast_free(ab=ab, var=fast_var):
            target = _gi_int(var, c.abilities[ab])
            cur = c.abilities[ab]
            if target <= cur:
                messagebox.showinfo(
                    "Ничего",
                    f"Уже {cur}. Введи значение > текущего, чтобы "
                    f"получить бесплатно.")
                return
            src = _pick_source_dialog(app)
            if not src:
                return
            try:
                c.abilities[ab] = target
                c.recompute_derived()
                refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        def fast_down(ab=ab):
            _ability_decrease(app, ab, refresh)

        tk.Button(row, text="OK", command=fast_apply,
                  bg="#4a7", fg="white", width=3
                  ).pack(side="left", padx=2)
        tk.Button(row, text="↑", width=3,
                  command=lambda ab=ab: _try(
                      refresh,
                      lambda ab=ab: P.buy_ability_up(c, ab, "training"))
                  ).pack(side="left", padx=1)
        tk.Button(row, text="★", width=3,
                  command=lambda ab=ab, fv=fast_var: fast_free(ab, fv)
                  ).pack(side="left", padx=1)
        tk.Button(row, text="↓", width=3,
                  command=lambda ab=ab: fast_down(ab)
                  ).pack(side="left", padx=1)

        # Урон по стату
        tk.Label(row, text="   Урон:",
                 bg="#f4f4f4", font=("Segoe UI", 9)
                 ).pack(side="left", padx=(10, 2))
        dmg_var = tk.IntVar(value=dmg)
        tk.Spinbox(row, from_=0, to=v,
                    textvariable=dmg_var, width=3,
                    font=("Segoe UI", 10)).pack(side="left", padx=2)

        def apply_damage(ab=ab, var=dmg_var):
            target = _gi_int(var, c.ability_damage.get(ab, 0))
            target = max(0, min(target, c.abilities[ab]))
            cur_dmg = c.ability_damage.get(ab, 0)
            if target == cur_dmg:
                return
            try:
                if target > cur_dmg:
                    P.damage_stat(c, ab, target - cur_dmg)
                else:
                    P.restore_stat_damage(c, ab, cur_dmg - target)
                refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        def restore_all_damage(ab=ab):
            if c.ability_damage.get(ab, 0) == 0:
                return
            if not messagebox.askyesno(
                    "Восстановить",
                    f"Снять весь урон ({c.ability_damage[ab]}) "
                    f"с {ab.upper()}?"):
                return
            P.restore_stat_full(c, ab)
            refresh()

        tk.Button(row, text="✓", width=2,
                  command=apply_damage,
                  bg="#4a7", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="left", padx=1)
        tk.Button(row, text="✚", width=2,
                  command=restore_all_damage,
                  font=("Segoe UI", 9)
                  ).pack(side="left", padx=1)

        tk.Label(row, text=f"{cost}", fg="#c06000", bg="#f4f4f4",
                 font=("Segoe UI", 10, "bold")
                 ).pack(side="right", padx=8)

    # ============ КОМФОРТ ============
    section("Комфорт")
    rate = (c.level + 1) * 5
    f = tk.Frame(parent, bg="#f4f4f4")
    f.pack(fill="x", pady=1, padx=5)
    over = c.comfort["current"] > c.comfort["max"]
    txt_color = "#cc3333" if over else "#000"
    tk.Label(f, text=f"Комфорт: {c.comfort['current']}/"
                      f"{c.comfort['max']}   "
                      f"(1 комфорт = {rate} тренировок)",
             anchor="w", bg="#f4f4f4", fg=txt_color,
             font=("Segoe UI", 10, "bold")).pack(side="left",
                                                  fill="x", expand=True)

    def spend_comfort(n=1):
        try:
            gained = P.spend_comfort(c, n)
            messagebox.showinfo(
                "Комфорт",
                f"Потрачено {n} комфорта → +{gained} тренировок")
            refresh()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e))

    def lose_comfort(n=1):
        try:
            P.lose_comfort(c, n)
            refresh()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e))

    def set_comfort_dialog():
        cur = c.comfort["current"]
        n = simpledialog.askinteger(
            "Комфорт", f"Текущий: {cur}\nНовое значение "
                       f"(можно > максимума):",
            initialvalue=cur, minvalue=0, parent=app.get_dialog_parent())
        if n is None:
            return
        P.set_comfort(c, n)
        refresh()

    tk.Button(f, text="Потратить (даст тренировки)",
              command=lambda: spend_comfort(1)).pack(side="right",
                                                      padx=2)
    tk.Button(f, text="Потерять (без тренировок)",
              command=lambda: lose_comfort(1)).pack(side="right",
                                                     padx=2)
    tk.Button(f, text="✏ Установить",
              command=set_comfort_dialog).pack(side="right", padx=2)

    # ============ БАЗА ============
    section("База")
    cap = 10 * c.level
    info_label(f"Размер базы: {c.base['slots_max']}/{cap} слотов")
    if c.base["slots_max"] < cap:
        row_actions(
            f"Очко базы: {c.base['slots_max']} → "
            f"{c.base['slots_max']+1}", 100,
            buy_fn=lambda: P.buy_base_slot(c, "training"),
            free_fn=lambda src: P.buy_base_slot(c, src),
            remove_fn=lambda: _training_remove(
                refresh, "Очко базы -1",
                100 if c.base_invested > 0 else 0,
                lambda: P.remove_base_slot(c, True),
                lambda: P.remove_base_slot(c, False)))

    # ============ МОДИФИКАТОРЫ ============
    section("Модификаторы (ручные)",
            subtitle="Natural armor идёт в полный AC и flat, "
                     "не идёт в touch. AC bonus/misc — во все 4 типа.")
    mods = [
        ("balance_bonus", "Баланс (макс): +",
         "сверх pain_threshold + armor + shield"),
        ("balance_restore_bonus", "Восстановление баланса: +",
         "к 'нулевой инициативе'"),
        ("hp_bonus", "HP: +",
         "к максимуму (влияет на cap)"),
        ("spirit_bonus", "Дух (макс): +",
         "сверх 5+5×CHA"),
        ("natural_armor", "Natural armor: +",
         "природная броня"),
        ("ac_bonus", "AC bonus: +",
         "deflection и прочее"),
        ("ac_misc", "AC misc: +",
         "прочее"),
        ("pain_threshold_bonus", "БП (кап): +",
         "сверх ceil(HP/4)"),
        ("pain_extra", "Экстра-боль (проклятия):",
         "постоянная, не от HP. Может быть минусом"),
    ]
    for key, label, hint in mods:
        f = tk.Frame(parent, bg="#f4f4f4")
        f.pack(fill="x", pady=1, padx=5)
        tk.Label(f, text=label, width=32, anchor="w",
                 bg="#f4f4f4",
                 font=("Segoe UI", 10)).pack(side="left")
        v_val = tk.IntVar(value=getattr(c, key, 0))

        def on_change(*args, k=key, var=v_val):
            setattr(c, k, _gi_int(var, 0))
            c.recompute_derived()
        v_val.trace_add("write", on_change)

        tk.Spinbox(f, from_=-20, to=50, textvariable=v_val,
                    width=6).pack(side="left", padx=4)
        tk.Label(f, text=f"({hint})", fg="#666", bg="#f4f4f4",
                 font=("Segoe UI", 9)).pack(side="left", padx=4)

    # --- pain_max (смерть при боли N) ---
    f_pm = tk.Frame(parent, bg="#f4f4f4")
    f_pm.pack(fill="x", pady=1, padx=5)
    tk.Label(f_pm, text="Смерть при боли (pain_max):",
             width=32, anchor="w", bg="#f4f4f4",
             font=("Segoe UI", 10)).pack(side="left")
    pm_var = tk.IntVar(value=getattr(c, "pain_max", 8))

    def on_pm_change(*args, var=pm_var):
        v = max(1, _gi_int(var, 8))
        c.pain_max = v
        c.recompute_derived()
    pm_var.trace_add("write", on_pm_change)

    tk.Spinbox(f_pm, from_=1, to=30, textvariable=pm_var,
                width=6).pack(side="left", padx=4)
    tk.Label(f_pm, text="(базово 8; смерть при этой боли)",
             fg="#666", bg="#f4f4f4",
             font=("Segoe UI", 9)).pack(side="left", padx=4)


    f_size = tk.Frame(parent, bg="#f4f4f4")
    f_size.pack(fill="x", pady=1, padx=5)
    tk.Label(f_size, text="Размер персонажа:",
             width=32, anchor="w", bg="#f4f4f4",
             font=("Segoe UI", 10)).pack(side="left")
    size_var = tk.StringVar(value=c.combat.get("size", "Medium"))
    size_combo = tk.OptionMenu(
        f_size, size_var, *SIZES,
        command=lambda v: (
            c.combat.__setitem__("size", v),
            c.recompute_derived()))
    size_combo.config(width=15)
    size_combo.pack(side="left", padx=4)
    size_mod = SIZE_AC.get(c.combat.get("size", "Medium"), 0)
    tk.Label(f_size, text=f"(AC/CMB: {size_mod:+d})",
             fg="#666", bg="#f4f4f4",
             font=("Segoe UI", 9)).pack(side="left", padx=4)

    # ============ CMB / CMD ============
    section("CMB / CMD",
            subtitle="CMB = BAB + STR + size + моды. "
                     "CMD = 10 + BAB + STR + DEX + size + моды.")
    cmb_val = c.cmb_total()
    cmd_val = c.cmd_total()
    info_label(f"Текущие: CMB {cmb_val:+d}   CMD {cmd_val}",
               fg="#333")
    tk.Label(parent, text="CMB модификаторы (подпись | число):",
             font=("Segoe UI", 10, "bold"),
             bg="#f4f4f4").pack(anchor="w", padx=10, pady=(4, 2))
    cmb_container = tk.Frame(parent, bg="#f4f4f4")
    cmb_container.pack(fill="x")
    _render_mods_list(app, cmb_container, c, "cmb_mods", refresh)
    tk.Label(parent, text="CMD модификаторы (подпись | число):",
             font=("Segoe UI", 10, "bold"),
             bg="#f4f4f4").pack(anchor="w", padx=10, pady=(4, 2))
    cmd_container = tk.Frame(parent, bg="#f4f4f4")
    cmd_container.pack(fill="x")
    _render_mods_list(app, cmd_container, c, "cmd_mods", refresh)

    # ============ БРОНЯ ============
    section("Броня",
            subtitle="Стоимость: 250 за ступень. "
                     "Кнопка ↓ понижает.")
    cur_armor = c.proficiencies["armor"]
    idx = ARMOR_LEVELS.index(cur_armor)
    cur_display = ARMOR_DISPLAY.get(cur_armor, cur_armor)
    info_label(f"Текущее: {cur_display}   "
               f"[вложено: {c.armor_invested}]", fg="#333")
    if idx < len(ARMOR_LEVELS) - 1:
        nxt = ARMOR_LEVELS[idx + 1]
        nxt_display = ARMOR_DISPLAY.get(nxt, nxt)
        f = tk.Frame(parent, bg="#f4f4f4")
        f.pack(fill="x", pady=1, padx=5)
        tk.Label(f, text=f"↑ Повысить до: {nxt_display}",
                 anchor="w", bg="#f4f4f4",
                 font=("Segoe UI", 10)
                 ).pack(side="left", fill="x", expand=True)
        tk.Label(f, text="250", fg="#c06000", bg="#f4f4f4",
                 font=("Segoe UI", 10, "bold")
                 ).pack(side="right", padx=5)
        tk.Button(f, text="↑", width=3,
                  command=lambda: _try(
                      refresh,
                      lambda: P.buy_armor_grade(c, "training"))
                  ).pack(side="right", padx=1)
        tk.Button(f, text="★", width=3,
                  command=lambda: _free_buy(
                      refresh,
                      lambda src: P.buy_armor_grade(c, src))
                  ).pack(side="right", padx=1)
    else:
        info_label("  ✓ Достигнут максимум владения броней",
                   fg="#339933")
    if idx > 0:
        prev = ARMOR_LEVELS[idx - 1]
        prev_display = ARMOR_DISPLAY.get(prev, prev)
        f = tk.Frame(parent, bg="#f4f4f4")
        f.pack(fill="x", pady=1, padx=5)
        tk.Label(f, text=f"↓ Понизить до: {prev_display}",
                 anchor="w", bg="#f4f4f4",
                 font=("Segoe UI", 10), fg="#666"
                 ).pack(side="left", fill="x", expand=True)
        tk.Button(f, text="↓",
                  command=lambda: _training_remove(
                      refresh, "Броня -1",
                      250 if c.armor_invested > 0 else 0,
                      lambda: P.remove_armor(c, True),
                      lambda: P.remove_armor(c, False))
                  ).pack(side="right", padx=2)

    # ============ ЩИТ ============
    section("Щит",
            subtitle="Стоимость: 100 за ступень. Кнопка ↓ понижает.")
    cur_shield = c.proficiencies["shields"]
    sidx = SHIELD_LEVELS.index(cur_shield)
    cur_shield_display = SHIELD_DISPLAY.get(cur_shield, cur_shield)
    info_label(f"Текущее: {cur_shield_display}   "
               f"[вложено: {c.shield_invested}]", fg="#333")

    f_bal = tk.Frame(parent, bg="#f4f4f4")
    f_bal.pack(fill="x", pady=(2, 4), padx=5)
    add_bal_var = tk.BooleanVar(
        value=c.equipment.get("add_shield_ac_to_balance", True))

    def toggle_bal():
        c.equipment["add_shield_ac_to_balance"] = add_bal_var.get()
        c.recompute_derived()
        refresh()

    tk.Checkbutton(
        f_bal,
        text="Добавлять АЦ щита к Балансу",
        variable=add_bal_var, command=toggle_bal,
        bg="#f4f4f4", font=("Segoe UI", 10),
    ).pack(anchor="w", padx=6)

    if sidx < len(SHIELD_LEVELS) - 1:
        nxt = SHIELD_LEVELS[sidx + 1]
        nxt_display = SHIELD_DISPLAY.get(nxt, nxt)
        f = tk.Frame(parent, bg="#f4f4f4")
        f.pack(fill="x", pady=1, padx=5)
        tk.Label(f, text=f"↑ Повысить до: {nxt_display}",
                 anchor="w", bg="#f4f4f4",
                 font=("Segoe UI", 10)
                 ).pack(side="left", fill="x", expand=True)
        tk.Label(f, text="100", fg="#c06000", bg="#f4f4f4",
                 font=("Segoe UI", 10, "bold")
                 ).pack(side="right", padx=5)
        tk.Button(f, text="↑", width=3,
                  command=lambda: _try(
                      refresh,
                      lambda: P.buy_shield_grade(c, "training"))
                  ).pack(side="right", padx=1)
        tk.Button(f, text="★", width=3,
                  command=lambda: _free_buy(
                      refresh,
                      lambda src: P.buy_shield_grade(c, src))
                  ).pack(side="right", padx=1)
    else:
        info_label("  ✓ Достигнут максимум владения щитами",
                   fg="#339933")

    if sidx > 0:
        prev = SHIELD_LEVELS[sidx - 1]
        prev_display = SHIELD_DISPLAY.get(prev, prev)
        f = tk.Frame(parent, bg="#f4f4f4")
        f.pack(fill="x", pady=1, padx=5)
        tk.Label(f, text=f"↓ Понизить до: {prev_display}",
                 anchor="w", bg="#f4f4f4",
                 font=("Segoe UI", 10), fg="#666"
                 ).pack(side="left", fill="x", expand=True)
        tk.Button(f, text="↓",
                  command=lambda: _training_remove(
                      refresh, "Щит -1",
                      100 if c.shield_invested > 0 else 0,
                      lambda: P.remove_shield(c, True),
                      lambda: P.remove_shield(c, False))
                  ).pack(side="right", padx=2)

    # ============ ОРУЖЕЙНЫЕ ГРУППЫ ============
    section("Оружейные группы",
            subtitle="Формула: (30+5×X)×сложность×масштаб. "
                     "X — других групп на 8+ (Эксперт I+), "
                     "кроме текущей. «Основы» — toggle (+bump, "
                     "за тренировки или бесплатно). «★» — "
                     "бесплатно до N.")
    weapons = c.proficiencies["weapons"]
    if not weapons:
        info_label("(оружий нет — добавь через кнопку ниже)")
    else:
        for w in weapons:
            wname = w["name"]
            wlevel = w.get("level", 0)
            wdiff = w.get("difficulty", 1)
            wscale = w.get("scale", 1)
            has_basics = w.get("basics", False)
            x = P.weapon_x(c, wname)
            x_groups = P.weapon_x_groups(c, wname)

            desc_extra = f" — {w['desc']}" if w.get("desc") else ""
            cur_lvl_txt = WEAPON_LEVELS[wlevel] if wlevel < len(
                WEAPON_LEVELS) else "?"
            if x_groups:
                x_txt = f"X={x} ({', '.join(x_groups)})"
            else:
                x_txt = f"X={x} (других нет)"
            w_src_name = SOURCE_NAMES.get(w.get("source", ""), "?")
            header_txt = (f"[{w_src_name}] {wname}  "
                          f"(сложн. {wdiff}, масштаб {wscale}, "
                          f"{x_txt}){desc_extra}")
            info_label(header_txt, fg="#333")

            row = tk.Frame(parent, bg="#f4f4f4")
            row.pack(fill="x", pady=1, padx=5)
            tk.Label(row, text=f"    Уровень: {cur_lvl_txt} ({wlevel})",
                     anchor="w", bg="#f4f4f4",
                     font=("Segoe UI", 10), width=35
                     ).pack(side="left")

            if wlevel < 12:
                cost = P.weapon_grade_up_cost(c, wname)
                tk.Label(row, text=f"(30+5×{x})×{wdiff}×{wscale} = {cost}",
                         bg="#f4f4f4", fg="#c06000",
                         font=("Segoe UI", 9)).pack(side="left",
                                                     padx=4)
            else:
                tk.Label(row, text="— МАКСИМУМ (Мастер)",
                         bg="#f4f4f4", fg="#339933",
                         font=("Segoe UI", 9, "bold")
                         ).pack(side="left", padx=4)

            tk.Button(row, text="✖", width=3,
                      command=lambda w=w: _training_remove(
                          refresh, f"оружие '{w['name']}'",
                          w.get("invested", 0),
                          lambda: P.remove_weapon(c, w["name"], True),
                          lambda: P.remove_weapon(c, w["name"], False))
                      ).pack(side="right", padx=1)

            def down_weapon(w=w):
                if w.get("level", 0) <= 0:
                    messagebox.showinfo(
                        "Ничего",
                        f"'{w['name']}' уже на 0 уровне")
                    return
                invested = w.get("invested", 0)
                if invested > 0:
                    msg = (f"Понизить '{w['name']}' до "
                           f"{WEAPON_LEVELS[w['level']-1]}?\n\n"
                           f"Вложено: {invested}\n"
                           f"Да — вернуть вложенное\n"
                           f"Нет — без возврата")
                else:
                    msg = (f"Понизить '{w['name']}' до "
                           f"{WEAPON_LEVELS[w['level']-1]}?\n\n"
                           f"Качалось бесплатно — возврата не будет.")
                ans = messagebox.askyesnocancel(
                    "Понижение", msg)
                if ans is None:
                    return
                try:
                    P.remove_weapon_grade_up(c, w["name"],
                                              return_points=ans)
                    refresh()
                except P.PurchaseError as e:
                    messagebox.showerror("Ошибка", str(e))

            if wlevel > 0:
                tk.Button(row, text="↓", width=3,
                          command=down_weapon
                          ).pack(side="right", padx=1)

            if wlevel < 12:
                tk.Button(row, text="↑", width=3,
                          command=lambda w=w: _try(
                              refresh,
                              lambda: P.buy_weapon_grade_up(
                                  c, w["name"], "training"))
                          ).pack(side="right", padx=1)

            if wlevel < 12:
                tk.Label(row, text="до:", bg="#f4f4f4",
                         font=("Segoe UI", 9)
                         ).pack(side="right", padx=(10, 2))
                fast_lvl = tk.IntVar(value=wlevel)
                tk.Spinbox(row, from_=wlevel, to=12,
                            textvariable=fast_lvl, width=3
                            ).pack(side="right", padx=2)

                def fast_pay_weapon(w=w, var=fast_lvl):
                    """Купить до N за тренировки."""
                    target = _gi_int(var, w.get("level", 0))
                    cur = w.get("level", 0)
                    if target <= cur:
                        messagebox.showinfo(
                            "Ничего",
                            f"Уже level {cur}. Введи больше.")
                        return
                    cost = P.weapon_grade_up_cost_total(
                        c, w["name"], target)
                    avail = c.training["available"]
                    if cost > avail:
                        messagebox.showerror(
                            "Не хватает",
                            f"Нужно {cost}, есть {avail}")
                        return
                    if not messagebox.askyesno(
                            "Подтверждение",
                            f"'{w['name']}': {cur} → {target}\n"
                            f"Стоимость: {cost} тренировок"):
                        return
                    try:
                        P.buy_weapon_grade_up_to(
                            c, w["name"], target, "training")
                        refresh()
                    except P.PurchaseError as e:
                        messagebox.showerror("Ошибка", str(e))

                def fast_free_weapon(w=w, var=fast_lvl):
                    target = _gi_int(var, w.get("level", 0))
                    cur = w.get("level", 0)
                    if target <= cur:
                        messagebox.showinfo(
                            "Ничего",
                            f"Уже level {cur}. Введи больше, "
                            f"чтобы получить бесплатно.")
                        return
                    src = _pick_source_dialog(app)
                    if not src:
                        return
                    try:
                        w["level"] = min(12, target)
                        w["invested"] = w.get("invested", 0)
                        refresh()
                    except Exception as e:
                        messagebox.showerror("Ошибка", str(e))

                tk.Button(row, text="OK", width=3,
                          command=fast_pay_weapon,
                          bg="#4a7", fg="white",
                          font=("Segoe UI", 9, "bold")
                          ).pack(side="right", padx=1)
                tk.Button(row, text="★", width=3,
                          command=fast_free_weapon
                          ).pack(side="right", padx=1)

            # --- Бонусы владения (только с 5 уровня) ---
            if wlevel >= 5:
                bonus_row = tk.Frame(parent, bg="#f4f4f4")
                bonus_row.pack(fill="x", pady=0, padx=5)
                n_bonuses = len(w.get("bonuses", []))
                n_slots = sum(1 for lvl, _ in WEAPON_BONUS_SLOTS
                              if lvl <= wlevel)
                tk.Button(
                    bonus_row,
                    text=f"    ✦ Бонусы ({n_bonuses}/{n_slots})",
                    command=lambda wn=wname: _weapon_bonuses_dialog(
                        app, wn, refresh),
                    bg="#f4f4f4", relief="flat",
                    font=("Segoe UI", 9, "italic"),
                    fg="#8a2be2" if n_bonuses else "#666",
                    anchor="w",
                ).pack(side="left", padx=4, pady=1)



            # --- Основы ---
            basics_row = tk.Frame(parent, bg="#f4f4f4")
            basics_row.pack(fill="x", pady=0, padx=5)
            basics_cost = P.weapon_basics_cost(wscale)
            bump = max(0, 5 - wdiff)
            basics_mark = "☑" if has_basics else "☐"
            basics_status = (
                f"применены (bump +{w.get('bump_applied',0)})"
                if has_basics
                else f"не применены (+{bump} грейдов за {basics_cost})")

            def toggle_basics(w=w):
                if w.get("basics", False):
                    # СНЯТЬ
                    will_become = max(
                        0, w["level"] - w.get("bump_applied", 0))
                    msg = (
                        f"Снять основы с '{w['name']}'?\n"
                        f"Уровень: {w['level']} → {will_become}\n"
                        f"(bump был +{w.get('bump_applied', 0)})\n\n"
                        f"Вернуть {w.get('basics_invested', 0)} "
                        f"очков?")
                    ans = messagebox.askyesnocancel(
                        "Снять основы", msg)
                    if ans is None:
                        return
                    try:
                        P.remove_weapon_basics(c, w["name"],
                                                return_points=ans)
                        refresh()
                    except P.PurchaseError as e:
                        messagebox.showerror("Ошибка", str(e))
                else:
                    # ДОБАВИТЬ
                    cost = P.weapon_basics_cost(w["scale"])
                    avail = c.training["available"]
                    bump = max(0, 5 - w["difficulty"])

                    d_src = open_window(app, "Основы оружия", 440, 380)
                    b = tk.Frame(d_src)
                    b.pack(fill="both", expand=True)

                    tk.Label(b, text=f"Основы для '{w['name']}'",
                             font=("Segoe UI", 12, "bold")
                             ).pack(pady=(14, 6))
                    tk.Label(b,
                             text=f"Масштаб {w['scale']}, "
                                  f"сложность {w['difficulty']}\n"
                                  f"Даст +{bump} грейдов",
                             fg="#666", font=("Segoe UI", 9),
                             justify="center").pack(pady=4)
                    tk.Label(b,
                             text=f"Стоимость: {cost} тренировок\n"
                                  f"У тебя есть: {avail}",
                             font=("Segoe UI", 10, "bold"),
                             justify="center").pack(pady=10)

                    choice = {"src": None}

                    def pay_training():
                        if avail < cost:
                            messagebox.showerror(
                                "Не хватает",
                                f"Нужно {cost}, есть {avail}",
                                parent=d_src)
                            return
                        choice["src"] = "training"
                        d_src.destroy()

                    def pay_free():
                        d_src.destroy()
                        src = _pick_source_dialog(app)
                        if src:
                            choice["src"] = src

                    tk.Button(b,
                              text=f"📚 За тренировки ({cost})",
                              command=pay_training,
                              bg="#4a7", fg="white",
                              font=("Segoe UI", 10, "bold"),
                              width=28).pack(pady=4)
                    tk.Button(b,
                              text="🎁 Бесплатно (раса/класс/...)",
                              command=pay_free,
                              font=("Segoe UI", 10, "bold"),
                              width=28).pack(pady=4)
                    tk.Button(b, text="Отмена",
                              command=d_src.destroy,
                              width=28).pack(pady=4)

                    d_src.wait_window()

                    if not choice["src"]:
                        return
                    try:
                        P.buy_weapon_basics(c, w["name"],
                                              w["difficulty"],
                                              w["scale"],
                                              choice["src"],
                                              desc=w.get("desc", ""))
                        refresh()
                    except P.PurchaseError as e:
                        messagebox.showerror("Ошибка", str(e))

            tk.Button(basics_row,
                      text=f"    Основы: {basics_mark} "
                           f"{basics_status}",
                      command=toggle_basics,
                      bg="#f4f4f4", relief="flat",
                      font=("Segoe UI", 9, "italic"),
                      fg="#0066cc" if has_basics else "#666",
                      anchor="w").pack(side="left", padx=4, pady=1)

    add_btn("＋ Добавить оружие",
            lambda: _add_weapon_dialog(app, refresh))

    # ============ РЕСУРСЫ ============
    section("Ресурсы")
    avail = P.hp_up_available(c)
    if avail > 0:
        row_actions(
            f"HP +1 (можно ещё {avail})", 50,
            buy_fn=lambda: P.buy_hp_up(c, 1, "training"),
            free_fn=lambda src: P.buy_hp_up(c, 1, src),
            remove_fn=lambda: _training_remove(
                refresh, "HP -1", 50,
                lambda: P.remove_hp(c, 1, True),
                lambda: P.remove_hp(c, 1, False)))
    row_actions(
        f"Реакция {c.reactions} → {c.reactions+1}",
        P.reaction_up_cost(c),
        buy_fn=lambda: P.buy_reaction_up(c, "training"),
        free_fn=lambda src: P.buy_reaction_up(c, src),
        remove_fn=lambda: _training_remove(
            refresh, "Реакция -1",
            c.reactions_invested,
            lambda: P.remove_reaction(c, True),
            lambda: P.remove_reaction(c, False)))

    # ============ НАВЫКИ ============
    section("Навыки")
    f = tk.Frame(parent, bg="#f4f4f4")
    f.pack(fill="x", pady=3, padx=5)
    tk.Label(f, text="Навыки редактируются в отдельной вкладке "
                      "«Навыки» (в левом меню).",
             anchor="w", bg="#f4f4f4", fg="#666",
             font=("Segoe UI", 10, "italic")).pack(side="left")
    tk.Button(f, text="→ Открыть «Навыки»",
              command=lambda: __import__("gui_skills").edit_skills(app)
              ).pack(side="right", padx=4)

    # ============ ЯЗЫКИ ============
    section("Языки")
    for l in c.languages:
        native = "(р)" if l["native"] else ""
        f = tk.Frame(parent, bg="#f4f4f4")
        f.pack(fill="x", pady=1, padx=5)
        l_src_name = SOURCE_NAMES.get(l.get("source", ""), "?")
        tk.Label(f, text=f"[{l_src_name}] "
                          f"{l['name']} {native}",
                 anchor="w", bg="#f4f4f4",
                 font=("Segoe UI", 10)).pack(side="left",
                                              fill="x", expand=True)
        tk.Button(f, text="✖", width=3,
                  command=lambda l=l: _training_remove(
                      refresh, f"язык '{l['name']}'",
                      l.get("invested", 0),
                      lambda: P.remove_language(c, l["name"], True),
                      lambda: P.remove_language(c, l["name"], False))
                  ).pack(side="right", padx=1)
        if not l["native"]:
            tk.Button(f, text="→р",
                      command=lambda l=l: _lang_native(
                          app, l["name"], True, refresh)
                      ).pack(side="right", padx=1)
        else:
            tk.Button(f, text="→н",
                      command=lambda l=l: _lang_native(
                          app, l["name"], False, refresh)
                      ).pack(side="right", padx=1)
    add_btn("＋ Добавить язык",
            lambda: _add_language_dialog(app, refresh))


# ============ Вспомогательные ============

def _render_mods_list(app, parent, character, attr_name, refresh):
    mods_list = getattr(character, attr_name, [])
    if not mods_list:
        mods_list = []
        setattr(character, attr_name, mods_list)

    def rebuild():
        for w in parent.winfo_children():
            w.destroy()
        if not mods_list:
            tk.Label(parent, text="(нет модификаторов)",
                     bg="#f4f4f4", fg="#888",
                     font=("Segoe UI", 9, "italic")
                     ).pack(anchor="w", padx=10)
        for i, row in enumerate(mods_list):
            fr = tk.Frame(parent, bg="#f4f4f4")
            fr.pack(fill="x", pady=1, padx=5)
            tk.Label(fr, text=f"  {i+1}.", width=4,
                     bg="#f4f4f4").pack(side="left")
            e_src = tk.Entry(fr)
            e_src.insert(0, row.get("source", ""))
            e_src.pack(side="left", fill="x", expand=True)

            def on_src(event=None, idx=i, entry=e_src):
                mods_list[idx]["source"] = entry.get()
            e_src.bind("<KeyRelease>", on_src)
            e_src.bind("<FocusOut>", on_src)

            tk.Label(fr, text="значение:", bg="#f4f4f4"
                     ).pack(side="left", padx=(6, 2))
            v_val = tk.IntVar(value=row.get("value", 0))
            tk.Spinbox(fr, from_=-20, to=20,
                        textvariable=v_val, width=5
                        ).pack(side="left", padx=2)

            def on_val(idx=i, var=v_val):
                mods_list[idx]["value"] = _gi_int(var, 0)
                character.recompute_derived()
            v_val.trace_add("write", lambda *a, f=on_val: f())

            def del_row(idx=i):
                mods_list.pop(idx)
                rebuild()
                refresh()
            tk.Button(fr, text="✖", width=3,
                      command=del_row).pack(side="right", padx=2)

        def add_row():
            mods_list.append({"source": "", "value": 0})
            rebuild()
        tk.Button(parent, text="＋ Строка",
                  command=add_row).pack(anchor="w", padx=10, pady=2)

    rebuild()


def _try(refresh, fn):
    if not messagebox.askyesno("Подтверждение", "Вы уверены?"):
        return
    try:
        fn()
        refresh()
    except P.PurchaseError as e:
        messagebox.showerror("Ошибка", str(e))


def _free_buy(refresh, fn):
    src = _pick_source_dialog(None)
    if not src:
        return
    try:
        ret = fn(src)
        if callable(ret):
            try:
                ret(src)
            except TypeError:
                ret()
        refresh()
    except P.PurchaseError as e:
        messagebox.showerror("Ошибка", str(e))
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def _pick_source_dialog(app=None):
    d = open_window(app, "Источник", 280, 340, mode="center")
    result = {"src": None}
    tk.Label(d, text="Откуда?",
             font=("Segoe UI", 11)).pack(pady=10)
    for src in ["race", "class", "loot", "quirk", "template"]:
        tk.Button(d, text=f"[{SOURCE_ICONS[src]}] {SOURCE_NAMES[src]}",
                  width=20,
                  command=lambda s=src: (
                      result.update({"src": s}), d.destroy())
                  ).pack(pady=3)
    tk.Button(d, text="Отмена", command=d.destroy).pack(pady=10)
    try:
        d.grab_set()
    except Exception:
        pass
    d.wait_window(d)
    return result["src"]

def _training_remove(refresh, what, invested, with_return, without):
    if invested > 0:
        ans = messagebox.askyesnocancel(
            "Удаление",
            f"Удалить {what}?\n\nВложено: {invested}\n\n"
            f"Да — вернуть {invested}\nНет — без возврата")
        if ans is None:
            return
        try:
            (with_return if ans else without)()
            refresh()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e))
    else:
        if not messagebox.askyesno("Удаление", f"Удалить {what}?"):
            return
        try:
            without()
            refresh()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e))


def _ability_decrease(app, ab, refresh):
    c = app.c
    if c.abilities[ab] <= 1:
        messagebox.showinfo("Нельзя",
                             f"{ab.upper()} уже на минимуме")
        return
    old_val = c.abilities[ab]
    refund = 150 * max(1, (old_val - 10) // 2)
    ans = messagebox.askyesnocancel(
        "Понижение",
        f"Понизить {ab.upper()}: {old_val} → {old_val-1}?\n\n"
        f"Вернуть {refund} очков?\n\n"
        f"Да — вернуть\nНет — без возврата")
    if ans is None:
        return
    try:
        P.remove_ability_up(c, ab, return_points=ans)
        refresh()
    except P.PurchaseError as e:
        messagebox.showerror("Ошибка", str(e))


def _weapon_bonuses_dialog(app, wname, refresh):
    """Диалог выбора бонусов по слотам 5..12."""
    c = app.c
    w = c.weapon_by_name(wname)
    if not w:
        return
    level = w.get("level", 0)
    if level < 5:
        messagebox.showinfo(
            "Бонусы",
            "Бонусы доступны с 5 уровня владения (Спец I).")
        return

    d = open_window(app, f"Бонусы владения: {wname}", 900, 780)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True)

    tk.Label(body, text=f"Оружие: {wname} (уровень {level})",
             font=("Segoe UI", 13, "bold"),
             bg="#f4f4f4").pack(pady=(8, 4))

    hint = tk.Frame(body, bg="#e8e8e8", padx=8, pady=6)
    hint.pack(fill="x", padx=5, pady=4)
    tk.Label(hint,
             text="Спец. бонусы: доступны на Спец I-III, "
                  "Эксперт I-IV, Мастер (макс 3 раза).\n"
                  "Эксперт. бонусы: Эксперт I-IV, Мастер "
                  "(макс 2 раза).\n"
                  "Мастер. бонусы: только слот Мастер (1 раз).",
             bg="#e8e8e8", justify="left", wraplength=850,
             font=("Segoe UI", 9)).pack(anchor="w")

    current = {e.get("slot"): e.get("id")
               for e in w.get("bonuses", [])}

    by_type = {}
    for bid, bdef in WEAPON_BONUS_CATALOG.items():
        by_type.setdefault(bdef["type"], []).append((bid, bdef))

    slot_combos = {}

    for slot_lvl, slot_name in WEAPON_BONUS_SLOTS:
        if slot_lvl > level:
            continue
        fr = tk.Frame(body, bg="#f8f8f8",
                      relief="solid", borderwidth=1)
        fr.pack(fill="x", padx=5, pady=2)

        top = tk.Frame(fr, bg="#f8f8f8")
        top.pack(fill="x", padx=4, pady=(4, 2))
        tk.Label(top, text=f"Слот {slot_lvl}: {slot_name}",
                 font=("Segoe UI", 10, "bold"),
                 bg="#f8f8f8", width=20, anchor="w"
                 ).pack(side="left")

        allowed = allowed_bonus_types_for_slot(slot_lvl)
        options = [("", "— не выбрано —")]
        for t in allowed:
            for bid, bdef in by_type.get(t, []):
                options.append((bid, f"{bdef['name']} [{t}]"))

        labels = [o[1] for o in options]
        ids = [o[0] for o in options]

        combo = ttk.Combobox(top, values=labels,
                              state="readonly", width=42,
                              font=("Segoe UI", 10))
        cur_id = current.get(slot_lvl, "")
        try:
            idx = ids.index(cur_id)
        except ValueError:
            idx = 0
        combo.current(idx)
        combo.pack(side="left", padx=4)
        slot_combos[slot_lvl] = (combo, labels, ids)

        desc_lbl = tk.Label(fr, text="", bg="#f8f8f8",
                             fg="#666", anchor="w",
                             font=("Segoe UI", 8),
                             wraplength=850, justify="left")
        desc_lbl.pack(fill="x", padx=8, pady=(0, 4))

        def _upd_desc(combo=combo, ids=ids, lbl=desc_lbl):
            i = combo.current()
            if i < 0 or not ids[i]:
                lbl.config(text="")
                return
            bdef = WEAPON_BONUS_CATALOG.get(ids[i])
            if bdef:
                lbl.config(
                    text=f"Тип: {bdef['type']}, "
                         f"макс: {bdef['max_stacks']}  —  "
                         f"{bdef['desc']}")
        combo.bind("<<ComboboxSelected>>",
                    lambda e, f=_upd_desc: f())
        _upd_desc()

    def save():
        bonuses = []
        for slot_lvl, (combo, labels, ids) in slot_combos.items():
            i = combo.current()
            if i < 0:
                continue
            bid = ids[i]
            if not bid:
                continue
            bonuses.append({"slot": slot_lvl, "id": bid})
        try:
            P.set_weapon_bonuses(c, wname, bonuses)
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e), parent=d)
            return
        app._refresh()
        refresh()
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=10, padx=5)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=d.destroy).pack(side="right")


def _add_weapon_dialog(app, refresh):
    d = open_window(app, "Добавить оружие", 540, 440)
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)

    tk.Label(body,
             text="Создаёт оружие на 0 уровне (бесплатно).\n"
                  "Потом качаешь в секции «Оружейные группы» "
                  "или покупаешь основы отдельной кнопкой.",
             fg="#666", font=("Segoe UI", 9, "italic"),
             justify="left", wraplength=500
             ).pack(anchor="w", padx=5, pady=(8, 6))

    tk.Label(body, text="Название:").pack(anchor="w", padx=5)
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    e_name.pack(fill="x", padx=5)
    tk.Label(body, text="Сложность изучения (1-10):"
             ).pack(anchor="w", padx=5, pady=(8, 0))
    diff_var = tk.IntVar(value=1)
    tk.Spinbox(body, from_=1, to=10, textvariable=diff_var,
                width=6).pack(anchor="w", padx=5)
    tk.Label(body,
             text="Масштаб (1=именное / 2=разновидность / "
                  "3=группа страны-школы):",
             font=("Segoe UI", 9), fg="#666", wraplength=500,
             justify="left").pack(anchor="w", padx=5, pady=(4, 0))
    scale_var = tk.IntVar(value=1)
    tk.Spinbox(body, from_=1, to=3, textvariable=scale_var,
                width=6).pack(anchor="w", padx=5)
    tk.Label(body, text="Описание:").pack(anchor="w", padx=5,
                                            pady=(8, 0))
    t_desc = tk.Text(body, font=("Segoe UI", 10), height=3,
                      wrap="word")
    t_desc.pack(fill="both", expand=True, padx=5)

    lbl_hint = tk.Label(body, text="", fg="#c06000",
                         font=("Segoe UI", 9),
                         wraplength=500, justify="left")
    lbl_hint.pack(pady=4, padx=5)

    def update_hint(*args):
        diff = diff_var.get()
        scale = scale_var.get()
        bump = max(0, 5 - diff)
        basics_cost = P.weapon_basics_cost(scale)
        first_cost = (30 + 5 * 0) * diff * scale
        lbl_hint.config(
            text=f"Начальный уровень: 0 (бесплатно). "
                 f"Основы: +{bump} грейдов за {basics_cost}. "
                 f"Прокачка ↑: {first_cost} за шаг (X=0).")

    diff_var.trace_add("write", update_hint)
    scale_var.trace_add("write", update_hint)
    update_hint()

    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        desc = t_desc.get("1.0", "end").strip()
        try:
            P.add_weapon(app.c, name, diff_var.get(),
                          scale_var.get(), 0, "training", desc)
            try:
                d.grab_release()
            except Exception:
                pass
            refresh()
            d.destroy()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e), parent=d)

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Создать (level 0)", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")


def _add_language_dialog(app, refresh):
    d = open_window(app, "Добавить язык", 440, 340)
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)
    tk.Label(body, text="Название:").pack(anchor="w", padx=5,
                                            pady=(8, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    e_name.pack(fill="x", padx=5)
    native_var = tk.BooleanVar(value=False)
    tk.Checkbutton(body, text="Родной",
                    variable=native_var).pack(anchor="w", padx=5,
                                               pady=(8, 0))
    free_var = tk.BooleanVar(value=False)
    tk.Checkbutton(body,
                    text="Бесплатно (за расу/класс/лут/квирк)",
                    variable=free_var).pack(anchor="w", padx=5,
                                             pady=(4, 0))

    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        src = "training"
        if free_var.get():
            src = _pick_source_dialog(app)
            if not src:
                return
        try:
            P.buy_language(app.c, name, native_var.get(), src)
            try:
                d.grab_release()
            except Exception:
                pass
            refresh()
            d.destroy()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e), parent=d)

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Добавить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")


def _lang_native(app, name, native, refresh):
    what = "родным" if native else "неродным"
    ans = messagebox.askyesnocancel(
        "Изменение языка",
        f"Сделать '{name}' {what}?\n\n"
        f"Да — бесплатно\nНет — за очки (~20)\n"
        f"Отмена — не менять")
    if ans is None:
        return
    try:
        P.set_language_native(app.c, name, native, free=ans)
        refresh()
    except P.PurchaseError as e:
        messagebox.showerror("Ошибка", str(e))