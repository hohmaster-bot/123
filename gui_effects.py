# gui_effects.py — единый UI для эффектов и временных полей.
# T-EFFECTS-UI (v18.5)
#
# Один шаблон для: черты, стойки, класс, раса, травмы, ситуативные бафы.
# Все секции — с галочками (свернуть/развернуть).
# Вызывается из gui_editors.py / gui_combat.py.

import tkinter as tk
from gui_alphabet import TARGET_NAMES, BONUS_TYPE_NAMES


# ============ СПИСОК ЭФФЕКТОВ ============

def render_effects_list(parent, effects_data, *,
                        title="Эффекты:",
                        default_target="ac",
                        default_value=0,
                        show_bonus_type=True,
                        show_resource_name=False,
                        on_change=None):
    """Рисует список эффектов. effects_data — list[dict] (мутируется).
    Возвращает frame (для pack/forget)."""
    frame = tk.Frame(parent, bg="#f4f4f4")
    all_targets = list(TARGET_NAMES.keys())
    all_btypes = list(BONUS_TYPE_NAMES.keys())

    def _set(idx, key, val):
        if 0 <= idx < len(effects_data):
            effects_data[idx][key] = val
        if on_change:
            on_change()

    def render():
        for w in frame.winfo_children():
            w.destroy()
        tk.Label(frame, text=title,
                 font=("Segoe UI", 10, "bold"), bg="#f4f4f4"
                 ).pack(anchor="w", pady=(4, 2))
        for i, eff in enumerate(effects_data):
            fr = tk.Frame(frame, bg="#f4f4f4")
            fr.pack(fill="x", pady=1)
            tk.Label(fr, text=f"  {i+1}.", width=4,
                     bg="#f4f4f4").pack(side="left")
            tgt_var = tk.StringVar(value=eff.get("target", default_target))
            tk.OptionMenu(fr, tgt_var, *all_targets,
                          command=lambda v, idx=i: _set(idx, "target", v)
                          ).pack(side="left", padx=2)
            tk.Label(fr, text=":", bg="#f4f4f4"
                     ).pack(side="left", padx=2)
            v_val = tk.StringVar(value=str(eff.get("value", default_value)))
            tk.Entry(fr, textvariable=v_val, width=8
                     ).pack(side="left", padx=2)

            def on_val(idx=i, var=v_val):
                raw = var.get().strip()
                if not raw:
                    _set(idx, "value", 0)
                    return
                try:
                    _set(idx, "value", int(raw))
                except ValueError:
                    _set(idx, "value", raw)
            v_val.trace_add("write", lambda *a, f=on_val: f())

            if show_bonus_type:
                btype_var = tk.StringVar(
                    value=eff.get("bonus_type", "flat"))
                tk.OptionMenu(fr, btype_var, *all_btypes,
                              command=lambda v, idx=i:
                              _set(idx, "bonus_type", v)
                              ).pack(side="left", padx=2)
                effects_data[i]["bonus_type"] = btype_var.get()

            if show_resource_name:
                rn = tk.Entry(fr, width=12)
                rn.insert(0, eff.get("resource_name", ""))
                rn.pack(side="left", padx=2)

                def on_rn(idx=i, ent=rn):
                    _set(idx, "resource_name", ent.get().strip())
                rn.bind("<FocusOut>", lambda e, f=on_rn: f())

            def del_eff(idx=i):
                effects_data.pop(idx)
                if not effects_data:
                    effects_data.append(
                        {"target": default_target, "value": default_value})
                render()
                if on_change:
                    on_change()
            tk.Button(fr, text="✖", width=3,
                      command=del_eff).pack(side="right", padx=2)

    def add():
        effects_data.append({
            "target": default_target, "value": default_value,
            "bonus_type": "flat",
        })
        render()
        if on_change:
            on_change()

    render()
    tk.Button(frame, text="＋ Строка эффекта", command=add
              ).pack(anchor="w", pady=2)
    return frame


def apply_effects_list(effects_data):
    """Возвращает list[dict] без пустых (value == 0)."""
    def _nonempty(e):
        v = e.get("value", 0)
        if isinstance(v, str):
            return v.strip() not in ("", "0")
        return v != 0
    return [dict(e) for e in effects_data if _nonempty(e)]


# ============ ВРЕМЕННЫЕ ПОЛЯ ============

def render_temporal_fields(parent, obj, *,
                            show_charges=True,
                            show_duration=True,
                            show_cooldown=True,
                            show_on_activate=True,
                            show_blocks=True,
                            on_change=None):
    """Временные поля: duration_*, charges_*, cooldown_*,
    on_activate_effects, permanent, keep_at_zero, allow_toggle, enabled.
    Возвращает dict с Tk-переменными (для save)."""
    frame = tk.Frame(parent, bg="#f4f4f4")
    data = {}

    if show_duration:
        fr = tk.Frame(frame, bg="#f4f4f4")
        fr.pack(fill="x", padx=5, pady=2)
        tk.Label(fr, text="Длительность (раундов):",
                 bg="#f4f4f4").pack(side="left")
        data["duration_rounds"] = tk.IntVar(
            value=int(obj.get("duration_rounds", 0) or 0))
        tk.Spinbox(fr, from_=0, to=999,
                    textvariable=data["duration_rounds"], width=5
                    ).pack(side="left", padx=4)
        tk.Label(fr, text="текущее:", bg="#f4f4f4"
                 ).pack(side="left", padx=(8, 2))
        data["duration_current"] = tk.IntVar(
            value=int(obj.get("duration_current", 0) or 0))
        tk.Spinbox(fr, from_=0, to=999,
                    textvariable=data["duration_current"], width=5
                    ).pack(side="left")

    if show_charges:
        fr = tk.Frame(frame, bg="#f4f4f4")
        fr.pack(fill="x", padx=5, pady=2)
        tk.Label(fr, text="Заряды (макс):",
                 bg="#f4f4f4").pack(side="left")
        data["charges_max"] = tk.IntVar(
            value=int(obj.get("charges_max", 0) or 0))
        tk.Spinbox(fr, from_=0, to=999,
                    textvariable=data["charges_max"], width=5
                    ).pack(side="left", padx=4)
        tk.Label(fr, text="текущее:", bg="#f4f4f4"
                 ).pack(side="left", padx=(8, 2))
        data["charges_current"] = tk.IntVar(
            value=int(obj.get("charges_current", 0) or 0))
        tk.Spinbox(fr, from_=0, to=999,
                    textvariable=data["charges_current"], width=5
                    ).pack(side="left")
        tk.Label(fr, text="  тик:", bg="#f4f4f4"
                 ).pack(side="left", padx=(8, 2))
        data["charges_tick_mode"] = tk.StringVar(
            value=obj.get("charges_tick_mode", "none"))
        for v, lbl in [("none", "нет"), ("decrement", "−1"),
                        ("increment", "+1")]:
            tk.Radiobutton(fr, text=lbl, value=v,
                            variable=data["charges_tick_mode"],
                            bg="#f4f4f4"
                            ).pack(side="left", padx=2)

    if show_cooldown:
        fr = tk.Frame(frame, bg="#f4f4f4")
        fr.pack(fill="x", padx=5, pady=2)
        tk.Label(fr, text="Кулдаун (раундов):",
                 bg="#f4f4f4").pack(side="left")
        data["cooldown_rounds"] = tk.IntVar(
            value=int(obj.get("cooldown_rounds", 0) or 0))
        tk.Spinbox(fr, from_=0, to=999,
                    textvariable=data["cooldown_rounds"], width=5
                    ).pack(side="left", padx=4)
        tk.Label(fr, text="осталось:", bg="#f4f4f4"
                 ).pack(side="left", padx=(8, 2))
        data["cooldown_current"] = tk.IntVar(
            value=int(obj.get("cooldown_current", 0) or 0))
        tk.Spinbox(fr, from_=0, to=999,
                    textvariable=data["cooldown_current"], width=5
                    ).pack(side="left")

    fr2 = tk.Frame(frame, bg="#f4f4f4")
    fr2.pack(fill="x", padx=5, pady=2)
    tk.Label(fr2, text="Тик инициативы:", bg="#f4f4f4"
             ).pack(side="left")
    data["tick_mode"] = tk.StringVar(
        value=obj.get("tick_mode", "none"))
    for v, lbl in [("none", "нет"), ("restore", "восст."),
                    ("decrease", "−1 заряд")]:
        tk.Radiobutton(fr2, text=lbl, value=v,
                        variable=data["tick_mode"],
                        bg="#f4f4f4"
                        ).pack(side="left", padx=2)

    data["tick_on_initiative"] = tk.BooleanVar(
        value=bool(obj.get("tick_on_initiative", True)))
    tk.Checkbutton(frame, text="Тик на новой инициативе",
                    variable=data["tick_on_initiative"],
                    bg="#f4f4f4"
                    ).pack(anchor="w", padx=5, pady=2)

    data["permanent"] = tk.BooleanVar(
        value=bool(obj.get("permanent", True)))
    tk.Checkbutton(frame, text="Вечный (не тикает, без +/−)",
                    variable=data["permanent"],
                    bg="#f4f4f4"
                    ).pack(anchor="w", padx=5, pady=2)

    data["keep_at_zero"] = tk.BooleanVar(
        value=bool(obj.get("keep_at_zero", True)))
    tk.Checkbutton(frame, text="Не удалять при 0 длительности",
                    variable=data["keep_at_zero"],
                    bg="#f4f4f4"
                    ).pack(anchor="w", padx=5, pady=2)

    data["allow_toggle"] = tk.BooleanVar(
        value=bool(obj.get("allow_toggle", True)))
    tk.Checkbutton(frame, text="Разрешить вкл/выкл (ON/OFF)",
                    variable=data["allow_toggle"],
                    bg="#f4f4f4"
                    ).pack(anchor="w", padx=5, pady=2)

    data["enabled"] = tk.BooleanVar(
        value=bool(obj.get("enabled", True)))
    tk.Checkbutton(frame, text="Включено (бонус применяется)",
                    variable=data["enabled"],
                    bg="#f4f4f4"
                    ).pack(anchor="w", padx=5, pady=2)

    data["is_buff"] = tk.BooleanVar(
        value=bool(obj.get("is_buff", True)))
    tk.Checkbutton(frame, text="Ситуативный (в «Ситуативно»)",
                    variable=data["is_buff"],
                    bg="#f4f4f4"
                    ).pack(anchor="w", padx=5, pady=2)

    data["show_on_panel"] = tk.BooleanVar(
        value=bool(obj.get("show_on_panel", True)))
    tk.Checkbutton(frame, text="Показывать на панели (чип)",
                    variable=data["show_on_panel"],
                    bg="#f4f4f4"
                    ).pack(anchor="w", padx=5, pady=2)

    data["is_stance"] = tk.BooleanVar(
        value=bool(obj.get("is_stance", True)))
    tk.Checkbutton(frame, text="Стойка (показывать в «Стойка»)",
                    variable=data["is_stance"],
                    bg="#f4f4f4"
                    ).pack(anchor="w", padx=5, pady=2)

    if show_blocks:
        fr3 = tk.Frame(frame, bg="#f4f4f4")
        fr3.pack(fill="x", padx=5, pady=2)
        tk.Label(fr3, text="Запрещает тебе:",
                 bg="#f4f4f4", font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w")

        BLOCK_OPTIONS = [
            ("do:balance_restore", "[Действие] Восстанавливать баланс"),
            ("do:attack",          "[Действие] Атаковать"),
            ("do:move",            "[Действие] Двигаться"),
            ("do:spell_cast",      "[Действие] Сотворять заклинания"),
            ("do:heal",            "[Действие] Лечиться"),
            ("bonus:dodge",        "[Бонус] Уклонение"),
            ("bonus:morale",       "[Бонус] Мораль"),
            ("bonus:luck",         "[Бонус] Удача"),
            ("bonus:insight",      "[Бонус] Предвидение"),
            ("bonus:deflection",   "[Бонус] Отражение"),
            ("bonus:armor",        "[Бонус] Доспех"),
            ("bonus:shield",       "[Бонус] Щит"),
            ("bonus:natural",      "[Бонус] Натуральный"),
            ("bonus:circumstance", "[Бонус] Обстоятельства"),
            ("res:restore_hp",     "[Ресурс] HP"),
            ("res:restore_mana",   "[Ресурс] Мана"),
            ("res:restore_spirit", "[Ресурс] Дух"),
            ("res:restore_balance","[Ресурс] Баланс"),
            ("res:restore_resource","[Ресурс] Классовый ресурс"),
        ]
        all_keys = [k for k, _ in BLOCK_OPTIONS]
        key_to_label = dict(BLOCK_OPTIONS)
        label_to_key = {lbl: k for k, lbl in BLOCK_OPTIONS}
        all_labels = [lbl for _, lbl in BLOCK_OPTIONS] + ["Свой вариант..."]

        data["blocks_list"] = list(obj.get("blocks", []))
        blocks_frame = tk.Frame(fr3, bg="#f4f4f4")
        blocks_frame.pack(fill="x", padx=5)

        def _render_blocks():
            for w in blocks_frame.winfo_children():
                w.destroy()
            for i, key in enumerate(data["blocks_list"]):
                row = tk.Frame(blocks_frame, bg="#f4f4f4")
                row.pack(fill="x", pady=1)
                cur_label = key_to_label.get(key, "Свой вариант...")
                var = tk.StringVar(value=cur_label)

                def on_select(v, idx=i):
                    if v == "Свой вариант...":
                        data["blocks_list"][idx] = ""
                    else:
                        data["blocks_list"][idx] = label_to_key.get(v, v)
                    _render_blocks()

                opt = tk.OptionMenu(row, var, *all_labels, command=on_select)
                opt.config(width=36)
                opt.pack(side="left", padx=2)

                if key not in key_to_label:
                    e = tk.Entry(row, width=18)
                    e.insert(0, key)
                    e.pack(side="left", padx=2)
                    def on_custom(idx=i, ent=e):
                        if 0 <= idx < len(data["blocks_list"]):
                            data["blocks_list"][idx] = ent.get().strip()
                    e.bind("<FocusOut>", lambda ev, f=on_custom: f())

                def del_block(idx=i):
                    data["blocks_list"].pop(idx)
                    _render_blocks()
                tk.Button(row, text="✖", width=3,
                          command=del_block).pack(side="right", padx=2)

        def add_block():
            data["blocks_list"].append("")
            _render_blocks()

        _render_blocks()
        tk.Button(fr3, text="＋ Добавить запрет", command=add_block
                  ).pack(anchor="w", padx=10, pady=2)

    if on_change:
        for var in data.values():
            try:
                var.trace_add("write", lambda *a: on_change())
            except Exception:
                pass
    return {"frame": frame, "data": data}


def apply_temporal_fields(obj, data):
    """Сохраняет временные поля в obj (dict)."""
    def _int(key, default=0):
        try:
            return max(0, int(data[key].get()))
        except Exception:
            return default

    obj["duration_rounds"] = _int("duration_rounds")
    obj["duration_current"] = _int("duration_current")
    obj["charges_max"] = _int("charges_max")
    obj["charges_current"] = min(
        _int("charges_current"), obj["charges_max"])
    obj["charges_tick_mode"] = data["charges_tick_mode"].get()
    obj["cooldown_rounds"] = _int("cooldown_rounds")
    obj["cooldown_current"] = _int("cooldown_current")
    obj["tick_mode"] = data["tick_mode"].get()
    obj["tick_on_initiative"] = bool(data["tick_on_initiative"].get())
    obj["permanent"] = bool(data["permanent"].get())
    obj["keep_at_zero"] = bool(data["keep_at_zero"].get())
    obj["allow_toggle"] = bool(data["allow_toggle"].get())
    obj["enabled"] = bool(data["enabled"].get())
    obj["is_buff"] = bool(data["is_buff"].get())
    obj["show_on_panel"] = bool(data["show_on_panel"].get())
    obj["is_stance"] = bool(data["is_stance"].get())
    if "blocks_list" in data:
        obj["blocks"] = [x for x in data["blocks_list"] if x.strip()]
    return obj