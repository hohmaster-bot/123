# gui_combat.py — боевые действия (v7)
# v7: «🔄 Нулевая инициатива», блокировка баланса в бафах,
#     TclError-защита, blocks: []

import tkinter as tk
from tkinter import messagebox, simpledialog

import gui_rest
from gui_shared import make_scrollable, ToolTip
from gui_windows import open_window
from gui_alphabet import TARGET_NAMES
import gui_dialogs


def build_combat_panel(app, parent_row1, parent_row2):
    # T-CHIPS-BUTTONS (v1.0): кнопки теперь в chips._buttons.
    # update_combat_status вызывается из gui._refresh (no-op, т.к. btn_ot = None).
    pass

def update_combat_status(app):
    if not app.c or not hasattr(app, "btn_ot") or app.btn_ot is None:
        return
    c = app.c
    pm = c.pain_max
    ot = c.injury_points
    pain = c.pain_level()
    morale = c.morale

    if ot > 0:
        app.btn_ot.config(text=f"🩹 ОТ {ot}", bg="#cc3333")
    else:
        app.btn_ot.config(text="🩹 ОТ 0", bg="#444")

    pain_txt = f"😣 Боль {pain}/{pm}"
    if c.pain_extra or c.pain_extra_temp:
        pain_txt = (f"😣 Боль {pain}/{pm} "
                    f"(+{c.pain_extra}"
                    + (f"/+{c.pain_extra_temp}"
                       if c.pain_extra_temp else "")
                    + ")")
    if c.ignore_pain:
        pain_txt += " 🚫"
    if pain >= pm:
        app.btn_pain.config(
            text=f"💀 Боль {pain}/{pm} СМЕРТЬ",
            bg="#660000")
    elif pain > 0:
        app.btn_pain.config(
            text=pain_txt,
            bg="#777" if c.ignore_pain else "#cc3333")
    else:
        app.btn_pain.config(text=pain_txt, bg="#444")

    mb = c.morale_bonus()
    morale_txt = f"💭 Мораль {morale}"
    if mb:
        morale_txt += f" ({mb:+d})"
    if c.ignore_negative_morale and c.morale < 0:
        morale_txt += " 🚫"
    if morale < 0:
        app.btn_morale.config(
            text=morale_txt,
            bg="#777" if c.ignore_negative_morale else "#cc3333")
    elif morale > 0:
        app.btn_morale.config(text=morale_txt, bg="#339933")
    else:
        app.btn_morale.config(text=morale_txt, bg="#444")


def _ask_number(app, title, prompt, default=1):
    """T-SPLIT-4: диалог + трекер окна."""
    d = open_window(app, title, 320, 140)
    tk.Label(d, text=prompt, anchor="w", justify="left",
             wraplength=300, font=("Segoe UI", 10)
             ).pack(fill="x", padx=10, pady=(10, 4))
    v = tk.IntVar(value=default)
    e = tk.Entry(d, textvariable=v, font=("Segoe UI", 11), width=10)
    e.pack(padx=10, pady=2)
    e.focus_set()
    e.select_range(0, tk.END)
    result = {"val": None}

    def ok(event=None):
        try:
            result["val"] = max(0, int(v.get()))
        except Exception:
            result["val"] = None
        d.destroy()

    def cancel(event=None):
        result["val"] = None
        d.destroy()

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=6)
    tk.Button(bf, text="OK", command=ok, bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold"), width=8).pack(side="left", padx=8)
    tk.Button(bf, text="Отмена", command=cancel, width=8).pack(side="left")
    d.bind("<Return>", ok)
    d.bind("<Escape>", cancel)
    d.wait_window()
    return result["val"]


def action_damage(app):
    if not app.c:
        return
    n = _ask_number(app, "Урон", "Сколько урона?")
    if not n:
        return
    prev_hp = app.c.combat["hp_current"]
    prev_temp = app.c.combat.get("hp_temp", 0)
    prev_pain = app.c.pain_level()
    r = app.c.take_damage(n)
    pm = app.c.pain_max
    lines = [f"Получено: {n}"]
    if r["temp_loss"]:
        lines.append(f"Temp HP: {prev_temp} → {r['hp_temp']} "
                     f"(-{r['temp_loss']})")
    if r["hp_loss"]:
        lines.append(f"HP: {prev_hp} → {r['hp_current']} "
                     f"(-{r['hp_loss']})")
    lines.append(f"Баланс: -{r['balance_loss']}")
    lines.append(f"ОТ: +{r['injury']}")
    lines.append(f"Боль: {prev_pain} → {r['pain']}/{pm}")
    if r['pain'] >= pm and prev_pain < pm:
        lines.append(f"\n💀 ПЕРСОНАЖ МЁРТВ (Боль {pm}/{pm})")
    gui_dialogs.show_text(app, "Урон", "\n".join(lines),
                          width=360, height=260)
    app._refresh()


def action_set_temp_hp(app):
    if not app.c:
        return
    cur = app.c.combat.get("hp_temp", 0)
    n = gui_dialogs.ask_int(
        app, "Временные HP",
        f"Текущие: {cur}\nСколько установить?",
        default=cur, minvalue=0)
    if n is None:
        return
    app.c.set_temp_hp(n)
    app._refresh()


def action_heal(app):
    if not app.c:
        return
    n = _ask_number(app, "Лечение", "Сколько HP восстановить?")
    if not n:
        return
    app.c.restore_hp(n)
    app._refresh()


def action_lose_balance(app):
    if not app.c:
        return
    n = _ask_number(app, "Потеря баланса",
                     "Сколько баланса потерять?")
    if not n:
        return
    app.c.lose_balance(n)
    app._refresh()


def action_zero_initiative(app):
    if not app.c:
        return
    app.c.zero_initiative()
    app._refresh()


def action_restore_balance(app):
    if not app.c:
        return
    n = _ask_number(app, "Восстановление баланса",
                     "Сколько баланса восстановить?")
    if not n:
        return
    app.c.restore_balance(n)
    app._refresh()


def action_clear_injury(app):
    if not app.c:
        return
    n = gui_dialogs.ask_int(
        app, "ОТ",
        f"Текущие ОТ: {app.c.injury_points}\n"
        f"Сколько убрать (0 = все)?",
        default=0, minvalue=0)
    if n is None:
        return
    if n == 0:
        app.c.clear_injury()
    else:
        app.c.clear_injury(n)
    app._refresh()


def action_pain_dialog(app):
    if not app.c:
        return
    c = app.c
    pm = c.pain_max
    d = open_window(app, "Боль", 540, 620)
    
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)

    def refresh_labels():
        hp_pain = c.pain_from_hp()
        total = c.pain_level()
        penalty = c.pain_penalty()
        col = "#cc3333" if total >= pm else "#333"
        lbl_hp.config(text=f"От HP (в минусе): {hp_pain}")
        pen_note = ""
        if c.ignore_pain and total > 0:
            pen_note = "  [ИГНОРИРУЕТСЯ]"
        lbl_total.config(
            text=f"ИТОГО БОЛЬ: {total}/{pm}    "
                 f"Штраф: {penalty:+d}{pen_note}"
                 + ("   💀 СМЕРТЬ" if total >= pm else ""),
            fg=col)

    fr_hp = tk.Frame(body, bg="#f4f4f4", pady=4, padx=6)
    fr_hp.pack(fill="x", padx=5, pady=(8, 0))
    lbl_hp = tk.Label(fr_hp, text="", bg="#f4f4f4",
                       font=("Segoe UI", 10), anchor="w")
    lbl_hp.pack(fill="x")

    tk.Label(body, text="Неснимаемая боль (проклятия, травмы):",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(10, 2))
    fr_p = tk.Frame(body)
    fr_p.pack(fill="x", padx=5)
    extra_var = tk.IntVar(value=c.pain_extra)
    tk.Spinbox(fr_p, from_=0, to=pm,
                textvariable=extra_var, width=5).pack(side="left")

    def change_extra(*args):
        try:
            c.pain_extra = max(0, extra_var.get())
        except Exception:
            pass
        refresh_labels()
    extra_var.trace_add("write", change_extra)

    tk.Label(body, text="Боль (снимается вручную):",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(10, 2))
    fr_t = tk.Frame(body)
    fr_t.pack(fill="x", padx=5)
    temp_var = tk.IntVar(value=c.pain_extra_temp)
    tk.Spinbox(fr_t, from_=0, to=pm,
                textvariable=temp_var, width=5).pack(side="left")

    def change_temp(*args):
        try:
            c.pain_extra_temp = max(0, temp_var.get())
        except Exception:
            pass
        refresh_labels()
    temp_var.trace_add("write", change_temp)

    def clear_temp():
        c.clear_temp_pain()
        temp_var.set(0)
        refresh_labels()

    tk.Button(body, text="Сбросить эту боль",
              command=clear_temp).pack(anchor="w", padx=5, pady=4)

    ignore_var = tk.BooleanVar(value=c.ignore_pain)

    def toggle_ignore():
        c.ignore_pain = ignore_var.get()
        refresh_labels()
        update_combat_status(app)

    tk.Checkbutton(body,
                    text="Игнорировать боль (штраф d20 = 0)",
                    variable=ignore_var, command=toggle_ignore,
                    wraplength=500, justify="left",
                    font=("Segoe UI", 10)
                    ).pack(anchor="w", padx=5, pady=(10, 4))

    fr_total = tk.Frame(body, bg="#e8e8e8", pady=6, padx=6)
    fr_total.pack(fill="x", padx=5, pady=(10, 0))
    lbl_total = tk.Label(fr_total, text="", bg="#e8e8e8",
                          font=("Segoe UI", 11, "bold"),
                          anchor="w", justify="left")
    lbl_total.pack(fill="x")

    def close():
        try:
            d.grab_release()
        except Exception:
            pass
        app._refresh()
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Готово", command=close,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")

    refresh_labels()


def action_morale(app):
    if not app.c:
        return
    c = app.c
    d = open_window(app, "Мораль", 500, 420)
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="Текущая мораль:",
             font=("Segoe UI", 10)).pack(anchor="w", padx=5,
                                           pady=(10, 2))
    morale_var = tk.IntVar(value=c.morale)
    tk.Spinbox(body, from_=-20, to=20, textvariable=morale_var,
                width=6).pack(anchor="w", padx=5)

    lbl_bonus = tk.Label(body, text="", fg="#c06000",
                          font=("Segoe UI", 11, "bold"), anchor="w")
    lbl_bonus.pack(fill="x", padx=5, pady=6)

    ignore_var = tk.BooleanVar(value=c.ignore_negative_morale)

    def upd(*args):
        try:
            m = morale_var.get()
        except Exception:
            return
        c.morale = m
        b = c.morale_bonus()
        note = ""
        if ignore_var.get() and m < 0:
            note = "  [ИГНОРИРУЕТСЯ]"
        lbl_bonus.config(text=f"Бонус (мораль // 2): {b:+d}{note}")
        update_combat_status(app)
    morale_var.trace_add("write", upd)
    ignore_var.trace_add("write", upd)

    def toggle_ignore():
        c.ignore_negative_morale = ignore_var.get()
        upd()

    tk.Checkbutton(body,
                    text="Игнорировать отрицательную мораль",
                    variable=ignore_var, command=toggle_ignore,
                    wraplength=460, justify="left",
                    font=("Segoe UI", 10)
                    ).pack(anchor="w", padx=5, pady=(10, 6))

    tk.Label(body,
             text="Формула: бонус = мораль // 2.\n"
                  "+4 → +2, -4 → -2.",
             fg="#666", font=("Segoe UI", 9),
             justify="left").pack(anchor="w", padx=5, pady=(0, 6))

    def close():
        try:
            c.morale = morale_var.get()
        except Exception:
            pass
        c.ignore_negative_morale = ignore_var.get()
        try:
            d.grab_release()
        except Exception:
            pass
        app._refresh()
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Готово", command=close,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")

    upd()


# ============ НОВЫЙ ХОД ============

def action_new_turn(app):
    """🔄 Нулевая инициатива: тик бафов/кулдаунов/зарядов +
    перегрузка + баланс. Показывает отчёт (свой Toplevel от мышки)."""
    if not app.c:
        return
    try:
        report = app.c.tick_initiative(apply_balance=True)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e),
                             parent=app.get_dialog_parent())
        return
    app._refresh()
    if not report:
        return
    gui_dialogs.show_text(app, "🔄 Нулевая инициатива",
                          "\n".join(report), width=420, height=360)


# обратная совместимость
def action_tick_initiative(app):
    action_new_turn(app)


# ============ ДИАЛОГ БАФОВ ============

def _describe_effects(effects):
    from gui_alphabet import BONUS_TYPE_NAMES as _BTN
    parts = []
    for e in effects:
        t = e.get("target", "")
        v = e.get("value", 0)
        nm = TARGET_NAMES.get(t, t)
        v_str = str(v)
        bt = e.get("bonus_type", "flat") or "flat"
        bt_ru = _BTN.get(bt, bt)
        if t == "speed_mult":
            try:
                parts.append(f"×{int(v)/100:.2f}")
            except Exception:
                parts.append(f"×{v_str}")
        elif t == "speed":
            try:
                parts.append(f"{int(v):+d} фт ({bt_ru})")
            except Exception:
                parts.append(f"{v_str} фт ({bt_ru})")
        else:
            try:
                parts.append(f"{int(v):+d} {nm} ({bt_ru})")
            except Exception:
                parts.append(f"{v_str} {nm} ({bt_ru})")
    return ", ".join(parts)


def action_situational(app):
    if not app.c:
        return
    c = app.c
    d = open_window(app, "Ситуативные бафы", 720, 720)
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="Активные бафы:",
             font=("Segoe UI", 11, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 4))
    tk.Label(body,
             text="Везде = только броски (атаки/урон/спас/навыки). "
                  "Не влияет на AC, скорость, статы.",
             fg="#666", font=("Segoe UI", 9), wraplength=680,
             justify="left").pack(anchor="w", padx=5, pady=(0, 6))

    outer, canvas, list_body = make_scrollable(body)
    outer.pack(fill="both", expand=True, padx=5, pady=4)

    def rebuild():
        for w in list_body.winfo_children():
            w.destroy()
        if not c.situational_bonuses:
            tk.Label(list_body, text="(нет бафов)",
                     fg="#888", bg="#f4f4f4",
                     font=("Segoe UI", 10, "italic")
                     ).pack(pady=10)
        else:
            for i, b in enumerate(c.situational_bonuses):
                row = tk.Frame(list_body, bg="#f4f4f4")
                row.pack(fill="x", pady=2)
                tk.Label(row, text=f"• {b.get('name','?')}",
                         bg="#f4f4f4", width=20, anchor="w",
                         font=("Segoe UI", 10, "bold")
                         ).pack(side="left")
                eff_txt = _describe_effects(b.get("effects", []))
                tk.Label(row, text=eff_txt, bg="#f4f4f4",
                         fg="#0066cc", anchor="w",
                         font=("Segoe UI", 9)
                         ).pack(side="left", padx=4)
                tags = []
                if b.get("duration_rounds", 0) > 0:
                    tags.append(f"⏱ {b.get('duration_current', 0)}/"
                                f"{b['duration_rounds']}р")
                if b.get("charges_max", 0) > 0:
                    tags.append(f"⚡ {b.get('charges_current', 0)}/"
                                f"{b['charges_max']}")
                if b.get("tick_on_initiative"):
                    tags.append("tick")
                if b.get("blocks"):
                    tags.append("⛔")
                if tags:
                    tk.Label(row, text=" ".join(tags),
                             bg="#f4f4f4", fg="#c06000",
                             font=("Segoe UI", 9, "bold")
                             ).pack(side="left", padx=4)

                def del_bonus(i=i):
                    c.situational_bonuses.pop(i)
                    rebuild()
                    app._refresh()
                tk.Button(row, text="✖", width=3, command=del_bonus
                          ).pack(side="right", padx=2)

                def edit_bonus(i=i):
                    _edit_buff_dialog(app, i, rebuild)
                tk.Button(row, text="✎", width=3, command=edit_bonus
                          ).pack(side="right", padx=2)

        # ===== T47: класс-бафы =====
        class_buffs = [(i, a) for i, a in
                       enumerate(c.char_class.get("abilities", []))
                       if isinstance(a, dict) and a.get("is_buff")]
        if class_buffs:
            tk.Label(list_body, text="📘 Класс-бафы:",
                     bg="#f4f4f4", fg="#2a5a3a",
                     font=("Segoe UI", 10, "bold"),
                     anchor="w").pack(fill="x", pady=(10, 2))
            for idx, a in class_buffs:
                row = tk.Frame(list_body, bg="#f4f4f4")
                row.pack(fill="x", pady=2)
                cc = int(a.get("charges_current", 0) or 0)
                cm = int(a.get("charges_max", 0) or 0)
                charges_txt = (f" [{cc}/{cm}]" if cm > 0 else "")
                lbl = tk.Label(row,
                               text=f"• {a.get('name','?')}{charges_txt}",
                               bg="#f4f4f4", width=24, anchor="w",
                               font=("Segoe UI", 10, "bold"))
                lbl.pack(side="left")
                if a.get("desc"):
                    ToolTip(lbl, a["desc"])
                eff_txt = _describe_effects(a.get("effects", []))
                if eff_txt:
                    tk.Label(row, text=eff_txt, bg="#f4f4f4",
                             fg="#2a5a3a", anchor="w",
                             font=("Segoe UI", 9)
                             ).pack(side="left", padx=4)
                can_use = (cm == 0 or cc > 0)

                def _act_class(i=idx):
                    if c.activate_ability_buff("class", i):
                        app._refresh()
                        rebuild()
                tk.Button(row, text="+ активировать",
                          command=_act_class,
                          state=("normal" if can_use else "disabled"),
                          bg="#4a7", fg="white",
                          font=("Segoe UI", 8, "bold")
                          ).pack(side="right", padx=2)

        # ===== T47: раса-бафы =====
        race_buffs = [(i, a) for i, a in
                      enumerate(c.race.get("abilities", []))
                      if isinstance(a, dict) and a.get("is_buff")]
        if race_buffs:
            tk.Label(list_body, text="🧬 Раса-бафы:",
                     bg="#f4f4f4", fg="#5a3a2a",
                     font=("Segoe UI", 10, "bold"),
                     anchor="w").pack(fill="x", pady=(10, 2))
            for idx, a in race_buffs:
                row = tk.Frame(list_body, bg="#f4f4f4")
                row.pack(fill="x", pady=2)
                cc = int(a.get("charges_current", 0) or 0)
                cm = int(a.get("charges_max", 0) or 0)
                charges_txt = (f" [{cc}/{cm}]" if cm > 0 else "")
                lbl = tk.Label(row,
                               text=f"• {a.get('name','?')}{charges_txt}",
                               bg="#f4f4f4", width=24, anchor="w",
                               font=("Segoe UI", 10, "bold"))
                lbl.pack(side="left")
                if a.get("desc"):
                    ToolTip(lbl, a["desc"])
                eff_txt = _describe_effects(a.get("effects", []))
                if eff_txt:
                    tk.Label(row, text=eff_txt, bg="#f4f4f4",
                             fg="#5a3a2a", anchor="w",
                             font=("Segoe UI", 9)
                             ).pack(side="left", padx=4)
                can_use = (cm == 0 or cc > 0)

                def _act_race(i=idx):
                    if c.activate_ability_buff("race", i):
                        app._refresh()
                        rebuild()
                tk.Button(row, text="+ активировать",
                          command=_act_race,
                          state=("normal" if can_use else "disabled"),
                          bg="#4a7", fg="white",
                          font=("Segoe UI", 8, "bold")
                          ).pack(side="right", padx=2)


        # ===== T-EFFECTS-UI: Травмы (enabled) =====
        active_injuries = [
            (idx, inj) for idx, inj in enumerate(c.injuries)
            if inj.get("enabled", True)
        ]
        if active_injuries:
            tk.Label(list_body, text="🩹 Травмы (активные):",
                     bg="#f4f4f4", fg="#8b2e2e",
                     font=("Segoe UI", 10, "bold"),
                     anchor="w").pack(fill="x", pady=(10, 2))
            for idx, inj in active_injuries:
                row = tk.Frame(list_body, bg="#f4f4f4")
                row.pack(fill="x", pady=2)
                sev = inj.get("severity", "custom")
                sev_ru = {"light": "лёгкая", "medium": "средняя",
                          "heavy": "тяжёлая", "custom": "своя"
                          }.get(sev, "?")
                tk.Label(row,
                         text=f"• {inj.get('name','Травма')} ({sev_ru})",
                         bg="#f4f4f4", width=24, anchor="w",
                         font=("Segoe UI", 10, "bold")
                         ).pack(side="left")
                eff_txt = _describe_effects(inj.get("effects", []))
                if eff_txt:
                    tk.Label(row, text=eff_txt, bg="#f4f4f4",
                             fg="#8b2e2e", anchor="w",
                             font=("Segoe UI", 9)
                             ).pack(side="left", padx=4)
                var = tk.BooleanVar(value=True)

                def toggle_active(idx=idx, var=var):
                    c.injuries[idx]["enabled"] = var.get()
                    app._refresh()
                    rebuild()
                tk.Checkbutton(row, text="вкл", variable=var,
                               command=toggle_active,
                               bg="#f4f4f4",
                               font=("Segoe UI", 9)
                               ).pack(side="right", padx=2)

    def add():
        c.situational_bonuses.append({
            "name": "Новый баф",
            "desc": "",
            "duration_rounds": 0,
            "duration_current": 0,
            "charges_max": 0,
            "charges_current": 0,
            "tick_on_initiative": False,
            "blocks": [],
            "effects": [{"target": "ac", "value": 0}],
        })
        idx = len(c.situational_bonuses) - 1
        _edit_buff_dialog(app, idx, rebuild)
        app._refresh()

    tk.Button(body, text="＋ Добавить баф", command=add,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(pady=6)
    rebuild()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Готово",
              command=lambda: (app._refresh(), d.destroy()),
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Убрать все",
              command=lambda: (c.situational_bonuses.clear(),
                                rebuild(), app._refresh())
              ).pack(side="left", padx=8)


def _edit_buff_dialog(app, idx, refresh):
    c = app.c
    if idx < 0 or idx >= len(c.situational_bonuses):
        return
    b = c.situational_bonuses[idx]
    d = open_window(app, f"Баф: {b.get('name','?')}", 760, 760)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True)

    tk.Label(body, text="Название:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    e_name.insert(0, b.get("name", ""))
    e_name.pack(fill="x", padx=5)

    tk.Label(body, text="Описание:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    t_desc = tk.Text(body, font=("Segoe UI", 10), height=3,
                      wrap="word")
    t_desc.pack(fill="x", padx=5)
    t_desc.insert("1.0", b.get("desc", ""))

    fr_dur = tk.Frame(body)
    fr_dur.pack(fill="x", padx=5, pady=(8, 0))
    tk.Label(fr_dur, text="Длительность (раундов, 0 = ∞):",
             font=("Segoe UI", 10)).pack(side="left")
    dur_var = tk.IntVar(value=b.get("duration_rounds", 0))
    tk.Spinbox(fr_dur, from_=0, to=100, textvariable=dur_var,
                width=5).pack(side="left", padx=4)
    tk.Label(fr_dur, text="текущее:",
             font=("Segoe UI", 10)).pack(side="left", padx=(10, 2))
    dur_cur_var = tk.IntVar(value=b.get("duration_current", 0))
    tk.Spinbox(fr_dur, from_=0, to=100, textvariable=dur_cur_var,
                width=5).pack(side="left")

    fr_ch = tk.Frame(body)
    fr_ch.pack(fill="x", padx=5, pady=(4, 0))
    tk.Label(fr_ch, text="Заряды (макс, 0 = нет):",
             font=("Segoe UI", 10)).pack(side="left")
    ch_max_var = tk.IntVar(value=b.get("charges_max", 0))
    tk.Spinbox(fr_ch, from_=0, to=100, textvariable=ch_max_var,
                width=5).pack(side="left", padx=4)
    tk.Label(fr_ch, text="текущее:",
             font=("Segoe UI", 10)).pack(side="left", padx=(10, 2))
    ch_cur_var = tk.IntVar(value=b.get("charges_current", 0))
    tk.Spinbox(fr_ch, from_=0, to=100, textvariable=ch_cur_var,
                width=5).pack(side="left")

    # T34.1: тик зарядов
    fr_ctm = tk.Frame(body)
    fr_ctm.pack(fill="x", padx=5, pady=(4, 0))
    tk.Label(fr_ctm, text="Тик зарядов:",
             font=("Segoe UI", 10)).pack(side="left")
    ctm_var = tk.StringVar(
        value=b.get("charges_tick_mode", "none"))
    for v, label in [("none", "не тикать"),
                      ("decrement", "−1"),
                      ("increment", "+1")]:
        tk.Radiobutton(fr_ctm, text=label, value=v,
                        variable=ctm_var).pack(side="left", padx=4)

    tick_var = tk.BooleanVar(value=b.get("tick_on_initiative", False))
    tk.Checkbutton(body,
                    text="Уменьшать на тике инициативы",
                    variable=tick_var,
                    font=("Segoe UI", 10)
                    ).pack(anchor="w", padx=5, pady=(6, 0))

    blocks_list = list(b.get("blocks", []))
    bal_var = tk.BooleanVar(value=("balance_restore" in blocks_list))

    def _toggle_bal_block():
        if bal_var.get():
            if "balance_restore" not in blocks_list:
                blocks_list.append("balance_restore")
        else:
            if "balance_restore" in blocks_list:
                blocks_list.remove("balance_restore")

    tk.Checkbutton(body,
                    text="⛔ Блокирует восстановление баланса "
                         "(напр. «Перегрузка»)",
                    variable=bal_var, command=_toggle_bal_block,
                    font=("Segoe UI", 10)
                    ).pack(anchor="w", padx=5, pady=(4, 0))

    # T-EFFECTS-UI: единый шаблон
    from gui_effects import (render_effects_list, apply_effects_list,
                             render_temporal_fields, apply_temporal_fields)
    effects_data = [dict(e) for e in b.get("effects", [])]
    if not effects_data:
        effects_data = [{"target": "ac", "value": 0, "bonus_type": "flat"}]
    eff_frame = render_effects_list(body, effects_data,
                                    title="Постоянные эффекты:")
    eff_frame.pack(fill="x", padx=5)
    on_act_data = [dict(e) for e in b.get("on_activate_effects", [])]
    on_act_frame = render_effects_list(
        body, on_act_data,
        title="Разовые эффекты (при активации):",
        default_target="restore_hp")
    on_act_frame.pack(fill="x", padx=5)

    # T-EFFECTS-UI: временные поля
    _temporal = render_temporal_fields(body, b)
    _temporal["frame"].pack(fill="x", padx=5, pady=(6, 0))
    temporal_data = _temporal["data"]

    def save():
        nm = e_name.get().strip()
        if not nm:
            messagebox.showwarning("Внимание",
                                    "Введите название", parent=d)
            return
        b["name"] = nm
        b["desc"] = t_desc.get("1.0", "end").strip()
        # T-EFFECTS-UI: единый шаблон
        b["effects"] = apply_effects_list(effects_data)
        if not b["effects"]:
            b["effects"] = [{"target": "ac", "value": 0,
                             "bonus_type": "flat"}]
        b["on_activate_effects"] = apply_effects_list(on_act_data)
        apply_temporal_fields(b, temporal_data)
        try:
            d.grab_release()
        except Exception:
            pass
        refresh()
        app._refresh()
        d.destroy()

    def delete():
        if not messagebox.askyesno("Удалить",
                                     f"Удалить «{b.get('name','?')}»?"):
            return
        c.situational_bonuses.pop(idx)
        try:
            d.grab_release()
        except Exception:
            pass
        refresh()
        app._refresh()
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Удалить", command=delete
              ).pack(side="left", padx=8)
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")