# gui_rest.py — окно "Отдых" + травмы (v1)
import tkinter as tk
from tkinter import messagebox

from character import INJURY_SEVERITIES
from gui_shared import ToolTip, make_scrollable
from gui_windows import open_window
from gui_alphabet import TARGET_NAMES
import purchases as P


def rest_dialog(app):
    if not app.c:
        return
    c = app.c
    d = open_window(app, f"Отдых — {c.name}", 680, 820)

    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True)

    def rebuild():
        for w in body.winfo_children():
            w.destroy()
        _build(app, body, d, rebuild)

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=6, padx=6)
    tk.Button(bf, text="Закрыть",
              command=lambda: (app._refresh(), d.destroy()),
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="right")

    rebuild()
    d.wait_window()


def _section(parent, title):
    f = tk.Frame(parent, bg="#c8c8c8")
    f.pack(fill="x", pady=(10, 2))
    tk.Label(f, text=title, font=("Segoe UI", 11, "bold"),
             bg="#c8c8c8", anchor="w", padx=8).pack(fill="x")


def _build(app, body, dialog, rebuild):
    c = app.c
    # ===== КОРОТКИЙ ОТДЫХ =====
    _section(body, "Короткий отдых")

    fr_vis_short = tk.Frame(body, bg="#f4f4f4")
    fr_vis_short.pack(fill="x", padx=5, pady=(2, 0))
    vis_short_var = tk.BooleanVar(
        value=c.settings.get("show_rest_short", True))

    def toggle_short_vis():
        c.settings["show_rest_short"] = vis_short_var.get()
        app._refresh()  # T-CHIPS: отдых в чипах, перерисовка через _refresh

    tk.Checkbutton(fr_vis_short,
                    text="Показывать в быстром доступе",
                    variable=vis_short_var,
                    command=toggle_short_vis,
                    bg="#f4f4f4",
                    font=("Segoe UI", 9, "italic")
                    ).pack(anchor="w", padx=4)

    fr = tk.Frame(body, bg="#f4f4f4")
    fr.pack(fill="x", padx=5, pady=2)

    tk.Label(fr, text=f"База: +(2+{c.level}) = +{2 + c.level} HP",
             bg="#f4f4f4",
             font=("Segoe UI", 10)).pack(side="left", padx=4)
    tk.Label(fr, text="Реген ХП:",
             bg="#f4f4f4",
             font=("Segoe UI", 10, "bold")
             ).pack(side="left", padx=(15, 2))
    regen_var = tk.StringVar(value=c.regen_modifier)
    tk.Entry(fr, textvariable=regen_var, width=10,
              font=("Segoe UI", 10)).pack(side="left", padx=2)
    if not c.settings.get("hide_hints", False):
        tk.Label(fr, text="(х2, +10, х3+10)", bg="#f4f4f4",
                 fg="#666", font=("Segoe UI", 9)
                 ).pack(side="left", padx=4)

    fr2 = tk.Frame(body, bg="#f4f4f4")
    fr2.pack(fill="x", padx=5, pady=2)

    preview_lbl = tk.Label(fr2, text="", bg="#f4f4f4",
                            fg="#666", font=("Segoe UI", 9))
    preview_lbl.pack(side="left", padx=6)

    def upd_preview(*args):
        c.regen_modifier = regen_var.get().strip()
        val = c.apply_regen_modifier(2 + c.level)
        preview_lbl.config(text=f"Даст: +{val} HP, +1 БП")

    regen_var.trace_add("write", upd_preview)
    upd_preview()

    def do_short():
        c.short_rest()
        app._refresh()
        rebuild()

    tk.Button(fr2, text="🛌 Короткий отдых",
              command=do_short, bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="right", padx=4)

    # ===== ДЛИННЫЙ ОТДЫХ =====
    _section(body, "Длинный отдых")

    fr_vis_long = tk.Frame(body, bg="#f4f4f4")
    fr_vis_long.pack(fill="x", padx=5, pady=(2, 0))
    vis_long_var = tk.BooleanVar(
        value=c.settings.get("show_rest_long", True))

    def toggle_long_vis():
        c.settings["show_rest_long"] = vis_long_var.get()
        app._refresh()  # T-CHIPS: отдых в чипах, перерисовка через _refresh

    tk.Checkbutton(fr_vis_long,
                    text="Показывать в быстром доступе",
                    variable=vis_long_var,
                    command=toggle_long_vis,
                    bg="#f4f4f4",
                    font=("Segoe UI", 9, "italic")
                    ).pack(anchor="w", padx=4)

    fr3 = tk.Frame(body, bg="#f4f4f4")
    fr3.pack(fill="x", padx=5, pady=2)
    tk.Label(fr3,
             text="Восстанавливает: HP, БП, Баланс, Дух, Ману, "
                  "слоты, ресурсы, способности, урон по статам, ОТ, "
                  "temp HP.\n"
                  "НЕ трогает: комфорт, внимание, экстра-боль, "
                  "травмы, бафы.",
             bg="#f4f4f4", fg="#666",
             font=("Segoe UI", 9), justify="left",
             wraplength=600).pack(anchor="w", padx=4, pady=(2, 4))

    def do_long():
        if not messagebox.askyesno(
                "Длинный отдых",
                "Восстановить всё до максимума?",
                parent=dialog):
            return
        c.long_rest()
        app._refresh()
        rebuild()

    tk.Button(fr3, text="🛏 Длинный отдых",
              command=do_long, bg="#855", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(anchor="w", padx=4, pady=(0, 4))
    # ===== БП =====
    _section(body, f"БП (текущий {c.pain_threshold['current']}/"
                    f"{c.pain_threshold['max']})")

    fr_vis_bp = tk.Frame(body, bg="#f4f4f4")
    fr_vis_bp.pack(fill="x", padx=5, pady=(2, 0))
    vis_bp_var = tk.BooleanVar(
        value=c.settings.get("show_bp_chip", True))

    def toggle_bp_vis():
        c.settings["show_bp_chip"] = vis_bp_var.get()
        app._refresh()

    tk.Checkbutton(fr_vis_bp,
                    text="Показывать в быстром доступе",
                    variable=vis_bp_var,
                    command=toggle_bp_vis,
                    bg="#f4f4f4",
                    font=("Segoe UI", 9, "italic")
                    ).pack(anchor="w", padx=4)

    fr4 = tk.Frame(body, bg="#f4f4f4")
    fr4.pack(fill="x", padx=5, pady=2)

    def bp_change(delta):
        c.pain_threshold["current"] = max(
            0, min(c.pain_threshold["max"],
                    c.pain_threshold["current"] + delta))
        app._refresh()
        rebuild()

    tk.Button(fr4, text="−1", width=3,
              command=lambda: bp_change(-1)
              ).pack(side="left", padx=2)
    tk.Button(fr4, text="+1", width=3,
              command=lambda: bp_change(1)
              ).pack(side="left", padx=2)

    tk.Label(fr4, text="  Ручной ввод:", bg="#f4f4f4",
             font=("Segoe UI", 10)
             ).pack(side="left", padx=(15, 2))
    bp_var = tk.IntVar(value=c.pain_threshold["current"])
    tk.Spinbox(fr4, from_=0, to=c.pain_threshold["max"],
                textvariable=bp_var, width=6
                ).pack(side="left", padx=2)

    def bp_set():
        try:
            val = bp_var.get()
        except tk.TclError:
            val = c.pain_threshold["current"]
        v = max(0, min(val, c.pain_threshold["max"]))
        c.pain_threshold["current"] = v
        app._refresh()
        rebuild()

    tk.Button(fr4, text="OK", command=bp_set,
              bg="#4a7", fg="white", width=3
              ).pack(side="left", padx=2)

    # ===== HP / ДУХ / СТАТЫ =====
    _section(body, "HP / Дух / Статы")

    # --- HP ---
    fr_hp = tk.Frame(body, bg="#f4f4f4")
    fr_hp.pack(fill="x", padx=5, pady=2)
    hp_cur = c.combat["hp_current"]
    hp_max = c.hp_max_actual()
    hp_temp = c.combat.get("hp_temp", 0)
    hp_missing = hp_max - hp_cur
    tk.Label(fr_hp, text="HP:", bg="#f4f4f4",
             font=("Segoe UI", 10, "bold"), width=6, anchor="w"
             ).pack(side="left", padx=(4, 2))
    hp_var = tk.IntVar(value=hp_cur)
    tk.Spinbox(fr_hp, from_=0, to=max(1, hp_max),
                textvariable=hp_var, width=6
                ).pack(side="left", padx=2)
    tk.Label(fr_hp, text=f"/ {hp_max}",
             bg="#f4f4f4",
             font=("Segoe UI", 10)).pack(side="left", padx=(0, 4))

    def hp_set():
        try:
            val = hp_var.get()
        except tk.TclError:
            val = c.combat["hp_current"]
        v = max(0, min(val, hp_max))
        c.combat["hp_current"] = v
        app._refresh()
        rebuild()

    def hp_up():
        c.combat["hp_current"] = min(
            hp_max, c.combat["hp_current"] + 1)
        app._refresh()
        rebuild()

    def hp_down():
        c.combat["hp_current"] = max(
            0, c.combat["hp_current"] - 1)
        app._refresh()
        rebuild()

    tk.Button(fr_hp, text="OK", command=hp_set,
              bg="#4a7", fg="white", width=3
              ).pack(side="left", padx=1)
    tk.Button(fr_hp, text="↑", command=hp_up, width=2
              ).pack(side="left", padx=1)
    tk.Button(fr_hp, text="↓", command=hp_down, width=2
              ).pack(side="left", padx=1)
    if hp_missing > 0:
        tk.Label(fr_hp, text=f"(не хватает {hp_missing})",
                 bg="#f4f4f4", fg="#cc3333",
                 font=("Segoe UI", 9)
                 ).pack(side="left", padx=6)
    if hp_temp > 0:
        tk.Label(fr_hp, text=f"+ 🛡 {hp_temp}",
                 bg="#f4f4f4", fg="#224466",
                 font=("Segoe UI", 9, "bold")
                 ).pack(side="left", padx=6)

    # --- Дух ---
    fr_sp = tk.Frame(body, bg="#f4f4f4")
    fr_sp.pack(fill="x", padx=5, pady=2)
    sp_cur = c.spirit["current"]
    sp_max = c.spirit["max"]
    sp_missing = sp_max - sp_cur
    tk.Label(fr_sp, text="Дух:", bg="#f4f4f4",
             font=("Segoe UI", 10, "bold"), width=6, anchor="w"
             ).pack(side="left", padx=(4, 2))
    sp_var = tk.IntVar(value=sp_cur)
    tk.Spinbox(fr_sp, from_=0, to=max(1, sp_max),
                textvariable=sp_var, width=6
                ).pack(side="left", padx=2)
    tk.Label(fr_sp, text=f"/ {sp_max}",
             bg="#f4f4f4",
             font=("Segoe UI", 10)).pack(side="left", padx=(0, 4))

    def sp_set():
        try:
            val = sp_var.get()
        except tk.TclError:
            val = c.spirit["current"]
        v = max(0, min(val, sp_max))
        c.spirit["current"] = v
        app._refresh()
        rebuild()

    def sp_up():
        c.spirit["current"] = min(
            sp_max, c.spirit["current"] + 1)
        app._refresh()
        rebuild()

    def sp_down():
        c.spirit["current"] = max(
            0, c.spirit["current"] - 1)
        app._refresh()
        rebuild()

    tk.Button(fr_sp, text="OK", command=sp_set,
              bg="#4a7", fg="white", width=3
              ).pack(side="left", padx=1)
    tk.Button(fr_sp, text="↑", command=sp_up, width=2
              ).pack(side="left", padx=1)
    tk.Button(fr_sp, text="↓", command=sp_down, width=2
              ).pack(side="left", padx=1)
    if sp_missing > 0:
        tk.Label(fr_sp, text=f"(не хватает {sp_missing})",
                 bg="#f4f4f4", fg="#cc3333",
                 font=("Segoe UI", 9)
                 ).pack(side="left", padx=6)

    # --- Статы ---
    tk.Label(body, text="Статы (урон/восстановление):",
             bg="#f4f4f4",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 2))

    ab_names = [("str", "СИЛ"), ("dex", "ЛОВ"), ("con", "ТЕЛ"),
                ("int", "ИНТ"), ("wis", "МДР"), ("cha", "ХАР")]

    for ab, ab_ru in ab_names:
        dmg = c.ability_damage.get(ab, 0)
        base = c.abilities.get(ab, 10)
        eff = base - dmg
        fr_ab = tk.Frame(body, bg="#f4f4f4")
        fr_ab.pack(fill="x", padx=10, pady=1)

        color = "#cc3333" if dmg > 0 else "#000"
        txt = f"{ab_ru}: {eff}/{base}"
        if dmg > 0:
            txt += f" (урон {dmg})"
        tk.Label(fr_ab, text=txt, bg="#f4f4f4",
                 font=("Segoe UI", 10), fg=color,
                 width=22, anchor="w"
                 ).pack(side="left")

        tk.Label(fr_ab, text="Урон:", bg="#f4f4f4",
                 font=("Segoe UI", 9)
                 ).pack(side="left", padx=(4, 2))
        dmg_var = tk.IntVar(value=dmg)
        tk.Spinbox(fr_ab, from_=0, to=max(1, base),
                    textvariable=dmg_var, width=4
                    ).pack(side="left", padx=1)

        def dmg_set(a=ab, var=dmg_var):
            try:
                target = max(0, min(var.get(),
                                     c.abilities.get(a, 10)))
                cur_dmg = c.ability_damage.get(a, 0)
                if target > cur_dmg:
                    P.damage_stat(c, a, target - cur_dmg)
                elif target < cur_dmg:
                    P.restore_stat_damage(c, a, cur_dmg - target)
                app._refresh()
                rebuild()
            except tk.TclError:
                pass
            except Exception as e:
                messagebox.showerror("Ошибка", str(e),
                                      parent=dialog)

        def dmg_up(a=ab):
            try:
                P.damage_stat(c, a, 1)
                app._refresh()
                rebuild()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e),
                                      parent=dialog)

        def dmg_down(a=ab):
            try:
                P.restore_stat_damage(c, a, 1)
                app._refresh()
                rebuild()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e),
                                      parent=dialog)

        tk.Button(fr_ab, text="OK", command=dmg_set,
                  bg="#4a7", fg="white", width=3
                  ).pack(side="left", padx=1)
        tk.Button(fr_ab, text="↑", command=dmg_up, width=2
                  ).pack(side="left", padx=1)
        tk.Button(fr_ab, text="↓", command=dmg_down, width=2
                  ).pack(side="left", padx=1)

        if dmg > 0:
            def heal_ab(a=ab):
                try:
                    P.heal_stat_for_bp(c, a, cost_bp=1)
                    app._refresh()
                    rebuild()
                except P.PurchaseError as e:
                    messagebox.showerror("Ошибка", str(e),
                                          parent=dialog)
            tk.Button(fr_ab, text="−1 урон за 1 БП",
                      command=heal_ab
                      ).pack(side="left", padx=(8, 2))

    # ===== ТРАВМЫ =====
    _section(body, f"Травмы (ОТ: {c.injury_points})")

    fr6 = tk.Frame(body, bg="#f4f4f4")
    fr6.pack(fill="x", padx=5, pady=2)

    def add_and_edit(severity=None):
        try:
            if severity is None:
                P.add_injury_manual(c)
            else:
                P.add_injury(c, severity)
            idx = len(c.injuries) - 1
            app._refresh()
            rebuild()
            injury_dialog(app, idx,
                           lambda: (app._refresh(), rebuild()))
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e), parent=dialog)

    for sev in ("light", "medium", "heavy"):
        info = INJURY_SEVERITIES[sev]
        tk.Button(
            fr6,
            text=f"−{info['cost']} {info['name']} "
                 f"(РЛ {info['heal_rating']})",
            command=lambda s=sev: add_and_edit(s)
        ).pack(side="left", padx=2)

    fr6b = tk.Frame(body, bg="#f4f4f4")
    fr6b.pack(fill="x", padx=5, pady=2)

    def comfort_to_ot():
        try:
            P.spend_comfort_for_ot(c)
            app._refresh()
            rebuild()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e), parent=dialog)

    def attention_to_ot():
        try:
            P.spend_attention_for_ot(c)
            app._refresh()
            rebuild()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e), parent=dialog)

    tk.Button(
        fr6b,
        text=f"1 комфорт → −3 ОТ "
             f"(есть: {c.comfort['current']})",
        command=comfort_to_ot
    ).pack(side="left", padx=2)

    att_bonus = max(2, c.ability_modifier("str"))
    tk.Button(
        fr6b,
        text=f"1 внимание → −{att_bonus} ОТ "
             f"(есть: {c.attention['current']})",
        command=attention_to_ot
    ).pack(side="left", padx=2)

    fr6c = tk.Frame(body, bg="#f4f4f4")
    fr6c.pack(fill="x", padx=5, pady=2)
    tk.Button(fr6c, text="＋ Добавить травму вручную",
              command=lambda: add_and_edit(None)
              ).pack(side="left", padx=2)

    tk.Button(fr6c, text="📚 Из каталога",
              command=lambda: _injury_from_catalog(app, rebuild),
              bg="#446", fg="white",
              font=("Segoe UI", 9, "bold")
              ).pack(side="left", padx=2)

    # Список травм
    if not c.injuries:
        tk.Label(body, text="(травм нет)",
                 bg="#f4f4f4", fg="#888",
                 font=("Segoe UI", 10, "italic")
                 ).pack(anchor="w", padx=15, pady=4)
        return

    sev_ru = {"light": "лёгкая", "medium": "средняя",
              "heavy": "тяжёлая", "custom": "своя"}

    for i, inj in enumerate(c.injuries):
        row = tk.Frame(body, bg="#f4f4f4")
        row.pack(fill="x", padx=10, pady=1)

        sev = inj.get("severity", "custom")
        sev_name = sev_ru.get(sev, "?")
        uses_txt = ""
        if inj.get("charges_max", 0) > 0:
            uses_txt = (f" [{inj.get('charges_current', 0)}/"
                        f"{inj['charges_max']}]")
        txt = (f"• {inj.get('name', 'Травма')} "
               f"({sev_name}, РЛ {inj.get('heal_rating', 1)})"
               f"{uses_txt}")
        lbl = tk.Label(row, text=txt, bg="#f4f4f4",
                        font=("Segoe UI", 10, "bold"),
                        anchor="w", cursor="hand2")
        lbl.pack(side="left", padx=4)
        if inj.get("desc"):
            ToolTip(lbl, inj["desc"])

        def del_inj(idx=i):
            ans = messagebox.askyesnocancel(
                "Удалить травму",
                f"Удалить '{c.injuries[idx].get('name', '?')}'?\n\n"
                f"Да — вернуть ОТ за неё\n"
                f"Нет — удалить без возврата\n"
                f"Отмена — не удалять",
                parent=dialog)
            if ans is None:
                return
            try:
                P.remove_injury(c, idx, refund_ot=ans)
                app._refresh()
                rebuild()
            except P.PurchaseError as e:
                messagebox.showerror("Ошибка", str(e),
                                      parent=dialog)

        def edit_inj(idx=i):
            injury_dialog(app, idx,
                           lambda: (app._refresh(), rebuild()))

        tk.Button(row, text="✖", width=3,
                  command=del_inj).pack(side="right", padx=2)
        tk.Button(row, text="✎", width=3,
                  command=edit_inj).pack(side="right", padx=2)

def _injury_from_catalog(app, rebuild):
    """K2d: взять травму из BUFFS_CATALOG (травмы = бафы)."""
    from character import BUFFS_CATALOG
    if not BUFFS_CATALOG:
        messagebox.showinfo("Каталог травм пуст",
                             "Создай файл в catalogs/buffs/ через "
                             "«📚 Каталоги» в инвентаре.",
                             parent=app.get_dialog_parent())
        return
    d = open_window(app, "Из каталога: травмы/бафы", 700, 550)
    tk.Label(d, text="Выбери травму/баф:",
             font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=6)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=4)

    for it in BUFFS_CATALOG:
        row = tk.Frame(body, bg="#f4f4f4", relief="solid", borderwidth=1)
        row.pack(fill="x", padx=2, pady=1)
        info = tk.Frame(row, bg="#f4f4f4")
        info.pack(side="left", fill="x", expand=True, padx=4, pady=2)
        sev = it.get("severity", "custom")
        tk.Label(info, text=f"[{sev}] {it.get('name', '?')}",
                 bg="#f4f4f4", font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(anchor="w")
        if it.get("desc"):
            tk.Label(info, text=it["desc"][:100],
                     bg="#f4f4f4", fg="#666",
                     font=("Segoe UI", 8), anchor="w").pack(anchor="w")

        def _take(it=it):
            inj = dict(it)
            inj.setdefault("name", "Травма")
            inj.setdefault("severity", "custom")
            inj.setdefault("heal_rating", 1)
            inj.setdefault("desc", "")
            from modifiers import apply_effects_defaults
            apply_effects_defaults(inj)
            app.c.injuries.append(inj)
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



def injury_dialog(app, idx, refresh):
    c = app.c
    if idx < 0 or idx >= len(c.injuries):
        return
    inj = c.injuries[idx]
    d = open_window(app, f"Травма: {inj.get('name', '?')}", 560, 680)

    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True)

    # Название
    tk.Label(body, text="Название:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    e_name.insert(0, inj.get("name", ""))
    e_name.pack(fill="x", padx=5)

    # Тяжесть
    tk.Label(body, text="Тяжесть:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    sev_var = tk.StringVar(value=inj.get("severity", "custom"))
    fr_sev = tk.Frame(body)
    fr_sev.pack(fill="x", padx=5)
    for val, label in [("light", "Лёгкая"),
                        ("medium", "Средняя"),
                        ("heavy", "Тяжёлая"),
                        ("custom", "Своя")]:
        tk.Radiobutton(fr_sev, text=label, value=val,
                        variable=sev_var).pack(side="left", padx=4)

    # РЛ
    tk.Label(body, text="Рейтинг лечения:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(8, 0))
    fr_rl = tk.Frame(body)
    fr_rl.pack(fill="x", padx=5)
    rl_var = tk.IntVar(value=inj.get("heal_rating", 1))
    tk.Spinbox(fr_rl, from_=0, to=50,
                textvariable=rl_var, width=6
                ).pack(side="left")

    def spend_attention():
        try:
            P.upgrade_heal_rating(c, idx)
            rl_var.set(c.injuries[idx]["heal_rating"])
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e), parent=d)

    att_bonus = max(2, c.ability_modifier("str"))
    tk.Button(
        fr_rl,
        text=f"Потратить 1 внимание (+{att_bonus} РЛ)",
        command=spend_attention
    ).pack(side="left", padx=10)
    if not c.settings.get("hide_hints", False):
        tk.Label(body,
                 text=f"(внимание: {c.attention['current']}/"
                      f"{c.attention['max']})",
                 fg="#666", font=("Segoe UI", 9)
                 ).pack(anchor="w", padx=5, pady=(2, 0))

    # Описание
    tk.Label(body, text="Описание:",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w", padx=5, pady=(10, 0))
    t_desc = tk.Text(body, font=("Segoe UI", 10), height=5,
                      wrap="word")
    t_desc.pack(fill="both", expand=True, padx=5)
    t_desc.insert("1.0", inj.get("desc", ""))

    # ===== T-EFFECTS-UI (v18.5): единый шаблон =====
    from gui_effects import (render_effects_list, apply_effects_list,
                             render_temporal_fields, apply_temporal_fields)
    effects_data = [dict(e) for e in inj.get("effects", [])]
    if not effects_data:
        effects_data = [{"target": "ac", "value": 0, "bonus_type": "flat"}]
    eff_frame = render_effects_list(body, effects_data,
                                    title="Эффекты травмы (постоянные):")
    eff_frame.pack(fill="x", padx=5)
    on_act_data = [dict(e) for e in inj.get("on_activate_effects", [])]
    on_act_frame = render_effects_list(
        body, on_act_data,
        title="Разовые эффекты (при активации):",
        default_target="restore_hp")
    on_act_frame.pack(fill="x", padx=5)

    _temporal = render_temporal_fields(body, inj)
    _temporal["frame"].pack(fill="x", padx=5, pady=(6, 0))
    temporal_data = _temporal["data"]

    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание",
                                    "Введите название", parent=d)
            return
        inj["name"] = name
        inj["severity"] = sev_var.get()
        try:
            inj["heal_rating"] = max(0, rl_var.get())
        except tk.TclError:
            inj["heal_rating"] = inj.get("heal_rating", 1)
        inj["desc"] = t_desc.get("1.0", "end").strip()
        inj["effects"] = apply_effects_list(effects_data)
        inj["on_activate_effects"] = apply_effects_list(on_act_data)
        apply_temporal_fields(inj, temporal_data)
        try:
            d.grab_release()
        except Exception:
            pass
        refresh()
        d.destroy()

    def delete():
        ans = messagebox.askyesnocancel(
            "Удалить травму",
            f"Удалить '{inj.get('name', '?')}'?\n\n"
            f"Да — вернуть ОТ за неё\n"
            f"Нет — удалить без возврата",
            parent=d)
        if ans is None:
            return
        try:
            P.remove_injury(c, idx, refund_ot=ans)
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
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Удалить", command=delete
              ).pack(side="left", padx=8)
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")