# chips.py — дескрипторы чипов (ChipSpec): данные → чипы. Без tkinter.
# Источник: character.py / gui_*.py. Рендер: gui_chips.py (CHIP_REGISTRY).

from character import WEAPON_BONUS_CATALOG

def _make_id(kind, name, idx):
    """Стабильный id: kind:name. Если имя пустое — kind_idx."""
    return f"{kind}:{name}" if name else f"{kind}_{idx}"


def _dedup(ids):
    """Убирает дубли id (одинаковые имена), оставляя первый. Второй+ получает суффикс #N."""
    seen, out = {}, []
    for i in ids:
        if i in seen:
            seen[i] += 1
            out.append(f"{i}#{seen[i]}")
        else:
            seen[i] = 0
            out.append(i)
    return out


def ChipSpec(id, kind, label, cur=0, mx=0, color="#3a3a3a",
             tip=None, icon="", group="misc", widgets=None, edit=None, data=None):
    """Единый формат чипа. id — стабильный ключ (для chips_order)."""
    return {
        "id": id, "kind": kind, "label": label,
        "cur": cur, "max": mx, "color": color, "tip": tip,
        "icon": icon, "group": group, "widgets": widgets or [],
        "edit": edit, "data": data or {},
    }


def clean_order(c):
    """Убрать из settings.chips_order id, которых больше нет в collect_all.
    Вызывать при загрузке персонажа (один раз), не при каждом refresh."""
    cur_ids = {s["id"] for s in collect_all(c)}
    order = c.settings.get("chips_order", []) or []
    cleaned = [x for x in order if x in cur_ids]
    if cleaned != order:
        c.settings["chips_order"] = cleaned
        return True
    return False


def collect_all(c):
    """ВСЕ доступные чипы (не только видимые). Панель = фильтр по settings.chips_visible."""
    out = []
    out += _resources(c)
    out += _abilities(c)
    out += _items(c)
    out += _attacks(c)
    out += _buffs(c)
    out += _feats(c)
    out += _buttons(c)
    out += _rest(c)
    out += _quests(c)
    out += _spells(c)
    out += _overload(c)
    out += _comfort(c)
    out += _lenses(c)
    out += _stances(c)
    # Уникальные id (одинаковые имена → #1, #2, ...)
    ids = _dedup([s["id"] for s in out])
    for s, new_id in zip(out, ids):
        s["id"] = new_id
    # T-CHIPS: кастомный цвет из settings.chips_colors (перекрывает spec["color"])
    custom = c.settings.get("chips_colors", {}) or {}
    for s in out:
        if s["id"] in custom:
            s["color"] = custom[s["id"]]
    return out


# ===== Источники (по одному, заполняем по шагам) =====

def _rest(c):
    """Кнопки отдыха (короткий / длинный)."""
    out = []
    if c.settings.get("show_rest_short", True):
        out.append(ChipSpec(id="rest:short", kind="button",
                            label="🛌 Короткий отдых", color="#4a7",
                            group="rest", tip="Короткий отдых",
                            data={"command": "_do_short_rest"}))
    if c.settings.get("show_rest_long", True):
        out.append(ChipSpec(id="rest:long", kind="button",
                            label="🛏 Длинный отдых", color="#855",
                            group="rest", tip="Длинный отдых",
                            data={"command": "_do_long_rest"}))
    return out


def _buttons(c):
    """Базовые кнопки (gui_combat). command — имя функции (ленивый вызов)."""
    def _injury_color():
        return "#cc3333" if c.injury_points > 0 else "#5a5a5a"
    def _pain_color():
        return "#cc3333" if c.pain_level() > 0 else "#5a5a5a"
    def _morale_color():
        if c.morale > 0: return "#339933"
        if c.morale < 0: return "#cc3333"
        return "#5a5a5a"

    out = [
        ChipSpec(id="btn:damage", kind="button", label="⚔ Урон",
                 color="#5a5a5a", group="buttons", tip="Нанести урон",
                 data={"command": "action_damage"}),
        ChipSpec(id="btn:heal", kind="button", label="💚 Лечить",
                 color="#4a7", group="buttons", tip="Восстановить HP",
                 data={"command": "action_heal"}),
        ChipSpec(id="btn:temp_hp", kind="button", label="🛡 Temp HP",
                 color="#224466", group="buttons", tip="Временные HP",
                 data={"command": "action_set_temp_hp"}),
        ChipSpec(id="btn:lose_balance", kind="button", label="⚖ Потерять баланс",
                 color="#855", group="buttons", tip="Потерять баланс",
                 data={"command": "action_lose_balance"}),
        ChipSpec(id="btn:new_turn", kind="button", label="🔄 Нулевая инициатива",
                 color="#5a5a5a", group="buttons", tip="Тик инициативы",
                 data={"command": "action_new_turn"}),
        ChipSpec(id="btn:injury", kind="button", label="🩹 ОТ",
                 color="#5a5a5a", group="buttons", tip="Очки травм",
                 data={"command": "action_clear_injury",
                       "label_fn": lambda: f"🩹 ОТ {c.injury_points}",
                       "color_fn": _injury_color}),
        ChipSpec(id="btn:pain", kind="button", label="😣 Боль",
                 color="#5a5a5a", group="buttons", tip="Боль",
                 data={"command": "action_pain_dialog",
                       "label_fn": lambda: f"😣 Боль {c.pain_level()}/{c.pain_max}",
                       "color_fn": _pain_color}),
        ChipSpec(id="btn:morale", kind="button", label="💭 Мораль",
                 color="#5a5a5a", group="buttons", tip="Мораль",
                 data={"command": "action_morale",
                       "label_fn": lambda: f"💭 Мораль {c.morale}",
                       "color_fn": _morale_color}),
        ChipSpec(id="btn:restore_balance", kind="button", label="✨ Восст. баланс",
                 color="#4a7", group="buttons", tip="Восстановить баланс",
                 data={"command": "action_restore_balance"}),
        ChipSpec(id="btn:situational", kind="button", label="🎲 Ситуация",
                 color="#5a5a5a", group="buttons", tip="Ситуативные бафы",
                 data={"command": "action_situational"}),
        ChipSpec(id="btn:refresh", kind="button", label="🔁 Обновить",
                 color="#5a5a5a", group="buttons", tip="Обновить",
                 data={"command": "_hard_refresh"}),
    ]
    return out

def _stances(c):
    """Чип «Стойка» (один, если есть is_stance)."""
    st = c.stances()
    if not st:
        return []
    names = [s.get("name", "?") for s in st]
    cur = c.active_stance or (names[0] if names else None)
    disp = {s.get("name"): (s.get("display_name") or s.get("name")) for s in st}
    return [ChipSpec(
        id="stance", kind="stance", label="Стойка",
        color="#4a3a2a", tip="Активная стойка", group="stance",
        data={"names": names, "current": cur, "display": disp,
              "on_pick": lambda v: c.set_active_stance(v),
              "on_toggle": lambda: c.set_active_stance(
                  None if c.active_stance is not None else cur)},
    )]


def _resources(c):
    """HP, AC×4, мана, BP, дух, баланс, слоты, класс-ресурсы."""
    out = []

    # HP (cur/max)
    out.append(ChipSpec(
        id="hp", kind="resource", label="HP",
        cur=c.combat["hp_current"], mx=c.hp_max_actual(),
        color="#5a3a3a", icon="❤", group="resources",
        tip="Здоровье",
        edit={"get": lambda: c.combat["hp_current"],
              "set": lambda v: setattr(c.combat, "hp_current", v) or c.__dict__.update(combat=c.combat),
              "title": "HP"},
    ))

    # AC ×4 — каждый отдельный чип (пользователь выберет через chips_visible)
    out.append(ChipSpec(
        id="ac_full", kind="resource", label="AC",
        cur=c.ac_full(), color="#3a4a5a", icon="🛡", group="resources",
        tip=f"AC full {c.ac_full()} / touch {c.ac_touch()} / flat {c.ac_flat()} / parry {c.ac_parry()}",
    ))
    out.append(ChipSpec(
        id="ac_touch", kind="resource", label="AC touch",
        cur=c.ac_touch(), color="#3a4a5a", icon="🛡", group="resources",
        tip="AC touch",
    ))
    out.append(ChipSpec(
        id="ac_flat", kind="resource", label="AC flat",
        cur=c.ac_flat(), color="#3a4a5a", icon="🛡", group="resources",
        tip="AC flat",
    ))
    out.append(ChipSpec(
        id="ac_parry", kind="resource", label="AC parry",
        cur=c.ac_parry(), color="#3a4a5a", icon="🛡", group="resources",
        tip="AC parry",
    ))

    # Temp HP (если есть)
    temp = c.combat.get("hp_temp", 0)
    if temp > 0:
        out.append(ChipSpec(
            id="hp_temp", kind="resource", label="Temp HP",
            cur=temp, mx=temp, color="#224466", icon="🛡", group="resources",
            tip="Временные HP съедаются первыми при уроне, баланс не тратится.",
            edit={"get": lambda: c.combat.get("hp_temp", 0),
                  "set": lambda v: c.set_temp_hp(v),
                  "title": "Temp HP"},
        ))

    # BP
    out.append(ChipSpec(
        id="bp", kind="resource", label="БП",
        cur=c.pain_threshold["current"], mx=c.pain_threshold["max"],
        color="#5a3a4a", icon="🩹", group="resources",
        tip="Болевой порог. Тратится, например, на лечение статов (1 БП = снять весь урон с одного стата).",
        edit={"get": lambda: c.pain_threshold["current"],
              "set": lambda v: c.pain_threshold.__setitem__("current", v),
              "title": "БП"},
    ))

    # Мана
    if c.mana.get("enabled") and c.mana["max"] > 0:
        out.append(ChipSpec(
            id="mana", kind="resource", label="Мана",
            cur=c.mana["current"], mx=c.mana["max"],
            color="#4a2a6a", icon="✨", group="resources",
            tip="Мана = класс + бонусные источники.",
            edit={"get": lambda: c.mana["current"],
                  "set": lambda v: c.mana.__setitem__("current", v),
                  "title": "Мана"},
        ))

    # Дух
    out.append(ChipSpec(
        id="spirit", kind="resource", label="Дух",
        cur=c.spirit["current"], mx=c.spirit["max"],
        color="#2a4a3a", icon="🌿", group="resources",
        tip="Дух",
        edit={"get": lambda: c.spirit["current"],
              "set": lambda v: c.spirit.__setitem__("current", v),
              "title": "Дух"},
    ))

    # Баланс
    out.append(ChipSpec(
        id="balance", kind="resource", label="Баланс",
        cur=c.balance["current"], mx=c.balance["max"],
        color="#4a3a2a", icon="⚖", group="resources",
        tip="Баланс",
        edit={"get": lambda: c.balance["current"],
              "set": lambda v: c.balance.__setitem__("current", v),
              "title": "Баланс"},
    ))

    # Слоты заклинаний
    if c.spell_slots_enabled:
        for circle in sorted(c.spell_slots.keys(), key=lambda x: int(x)):
            s = c.spell_slots[circle]
            if s["max"] <= 0: continue
            out.append(ChipSpec(
                id=f"slot_{circle}", kind="resource", label=f"Кр.{circle}",
                cur=s["current"], mx=s["max"],
                color="#2a4a6a", icon="📖", group="resources",
                tip=f"Слоты {circle} круга.",
                edit={"get": lambda ci=circle: c.spell_slots[ci]["current"],
                      "set": lambda v, ci=circle: c.spell_slots[ci].__setitem__("current", v),
                      "title": f"Слоты Кр.{circle}"},
            ))

    # Классовые ресурсы
    for idx, r in enumerate(c.class_resources):
        out.append(ChipSpec(
            id=_make_id("resource", r["name"], idx), kind="resource", label=r["name"],
            cur=r["current"], mx=r["max"],
            color="#4a4a2a", group="resources",
            tip=r["name"],
            edit={"get": lambda i=idx: c.class_resources[i]["current"],
                  "set": lambda v, i=idx: c.class_resources[i].__setitem__("current", v),
                  "title": r["name"]},
        ))

    return out


def _abilities(c):
    """Классовые/расовые абилки с uses."""
    out = []
    for idx, a in enumerate(c.char_class.get("abilities", [])):
        if not isinstance(a, dict) or not a.get("uses") or a.get("uses_max", 0) <= 0 or not a.get("show_on_panel", True): continue
        out.append(ChipSpec(
            id=_make_id("ability_class", a["name"], idx), kind="ability", label=a["name"][:18],
            cur=a.get("uses_current", 0), mx=a["uses_max"],
            color="#2a5a3a", group="abilities",
            tip=a.get("desc") or a["name"],
            edit={"get": lambda i=idx: c.char_class["abilities"][i].get("uses_current", 0),
                  "set": lambda v, i=idx: c.char_class["abilities"][i].__setitem__("uses_current", v),
                  "title": a["name"]},
            data={"idx": idx, "source": "class"},
        ))
    for idx, a in enumerate(c.race.get("abilities", [])):
        if not isinstance(a, dict) or not a.get("uses") or a.get("uses_max", 0) <= 0 or not a.get("show_on_panel", True): continue
        out.append(ChipSpec(
            id=_make_id("ability_race", a["name"], idx), kind="ability", label=a["name"][:18],
            cur=a.get("uses_current", 0), mx=a["uses_max"],
            color="#5a3a2a", group="abilities",
            tip=a.get("desc") or a["name"],
            edit={"get": lambda i=idx: c.race["abilities"][i].get("uses_current", 0),
                  "set": lambda v, i=idx: c.race["abilities"][i].__setitem__("uses_current", v),
                  "title": a["name"]},
            data={"idx": idx, "source": "race"},
        ))
    return out


def _items(c):
    """Предметы с uses (show_on_panel)."""
    out = []
    for item in list(c.items.values()):
        if not item.get("uses") or item.get("uses_max", 0) <= 0 or not item.get("show_on_panel", False): continue
        iid = item["id"]
        out.append(ChipSpec(
            id=f"item:{iid}", kind="item", label=item.get("name", "?")[:16],
            cur=item.get("uses_current", 0), mx=item.get("uses_max", 0),
            color="#3a4a3a", icon="📦", group="items",
            tip=(item.get("desc") or item.get("name", "?")) + f"\nзаряды {item.get('uses_current', 0)}/{item.get('uses_max', 0)}",
            edit={"get": lambda i=iid: c.items[i].get("uses_current", 0),
                  "set": lambda v, i=iid: c.items[i].__setitem__("uses_current", v),
                  "title": item.get("name", "?")},
            data={"iid": iid},
        ))
    return out


def _attacks(c):
    """Атаки на панели (show_on_panel)."""
    out = []
    for a_idx, a in enumerate(c.attacks):
        if not a.get("show_on_panel"): continue
        a_name = a.get("name", "?")[:18]
        bonus = c.attack_bonus(a)
        dmg_mod = c.attack_damage_bonus(a)
        ct, cm = c.attack_crit(a)
        dmg = a.get("damage_dice", "") or "—"
        dmg_txt = dmg + (f" ({dmg_mod:+d})" if dmg_mod else "")
        lucky_thr, lucky_parts = c.attack_lucky(a)
        tip_lines = [a_name, f"Атака: {bonus:+d}", f"Урон: {dmg_txt}", f"Крит: {ct}+ ×{cm}"]
        lucky_line = f"Счастливая: {lucky_thr}+"
        if lucky_parts: lucky_line += f" ({', '.join(lucky_parts)})"
        tip_lines.append(lucky_line)
        if a.get("ranged") or a.get("thrown"):
            rng = c.attack_range(a) if hasattr(c, "attack_range") else 0
            if rng > 0: tip_lines.append(f"{'Стрелковое' if a.get('ranged') else 'Метательное'}: {rng} фт")
        if a.get("proficiency"):
            w_obj = c.weapon_by_name(a["proficiency"])
            if w_obj:
                tip_lines.append(f"Владение: {a['proficiency']}")
                bon_names = [WEAPON_BONUS_CATALOG[entry.get("id")]["name"] for entry in w_obj.get("bonuses", []) if entry.get("id") in WEAPON_BONUS_CATALOG]
                if bon_names: tip_lines.append("Бонусы: " + ", ".join(bon_names))
        if a.get("master_ability"):
            bdef = WEAPON_BONUS_CATALOG.get(a.get("master_ability_id", ""))
            if bdef: tip_lines.append(f"Мастерство: {bdef['name']} [{a.get('uses_current', 0)}/{a.get('uses_max', 0)}]")
        if a.get("from_item"):
            it = c.items.get(a["from_item"])
            if it: tip_lines.append(f"Оружие: {it.get('name','?')}")
        if a.get("desc"): tip_lines.extend(["", a["desc"]])
        tip = "\n".join(tip_lines)

        has_uses = bool(a.get("uses") and a.get("uses_max", 0) > 0)
        color = "#4a3a5a" if (not has_uses or a.get("uses_current", 0) > 0) else "#3a3a3a"
        out.append(ChipSpec(
            id=_make_id("attack", a.get("name"), a_idx), kind="attack", label=a_name,
            cur=a.get("uses_current", 0) if has_uses else 0,
            mx=a.get("uses_max", 0) if has_uses else 0,
            color=color, icon="⚔", group="attacks", tip=tip,
            data={"idx": a_idx, "has_uses": has_uses},
        ))
    return out


def _buffs(c):
    """Ситуативные бафы (situational_bonuses, кроме from_item)."""
    out = []
    for b_idx, b in enumerate(c.situational_bonuses):
        if "from_item" in b: continue
        is_activation = "from_item_activation" in b
        is_permanent = bool(b.get("permanent", False))
        b_name = b.get("name", "?")[:16]
        b_cur = int(b.get("duration_current", 0) or 0)
        b_max = int(b.get("duration_rounds", 0) or 0)
        b_zero = (not is_permanent) and (b_cur <= 0)
        chip_bg = "#3a3a3a" if b_zero else "#5a3a6a"
        eff_parts = [f"{e.get('value', 0):+d} {e.get('target', 'all')}" for e in b.get("effects", [])]
        tip_lines = [b.get("name", "?")]
        if is_permanent: tip_lines.append("Длительность: ∞ (вечный)")
        elif b_max > 0: tip_lines.append(f"Длительность: {b_cur}/{b_max} р.")
        else: tip_lines.append("Длительность: без потолка")
        if eff_parts: tip_lines.append("Эффект: " + ", ".join(eff_parts))
        if b.get("charges_max", 0) > 0: tip_lines.append(f"Заряды: {b.get('charges_current', 0)}/{b['charges_max']}")
        if b.get("blocks"): tip_lines.append("⛔ Блокирует: " + ", ".join(b["blocks"]))
        if b.get("keep_at_zero"): tip_lines.append("Не удаляется автоматически при 0")
        if b.get("desc"): tip_lines.extend(["", b["desc"]])
        tip = "\n".join(tip_lines)
        out.append(ChipSpec(
            id=_make_id("buff", b.get("name"), b_idx), kind="buff", label=b_name,
            cur=b_cur, mx=b_max, color=chip_bg,
            icon="📦" if is_activation else "✨",
            group="buffs", tip=tip,
            data={"idx": b_idx, "is_activation": is_activation,
                  "is_permanent": is_permanent,
                  "charges_max": int(b.get("charges_max", 0) or 0),
                  "charges_cur": int(b.get("charges_current", 0) or 0),
                  "has_on_act": bool(b.get("on_activate_effects")),
                  "bid": b.get("from_item_activation")},
        ))
    return out


def _feats(c):
    """Активные черты (is_buff + show_on_panel, не стойки)."""
    out = []
    for f_idx, f in enumerate(c.feats):
        if f.get("is_stance"): continue
        if not f.get("is_buff", False): continue
        if not f.get("show_on_panel", True): continue
        out.append(ChipSpec(
            id=_make_id("feat", f.get("name"), f_idx), kind="feat", label=(f.get("display_name") or f.get("name", "?"))[:16],
            cur=0, mx=0, color="#5a4a2a", icon="⭐", group="feats",
            tip=f.get("desc", "") or f.get("name", "?"),
            data={"idx": f_idx},
        ))
    return out


def _comfort(c):
    """Комфорт (если есть current или max)."""
    cur, mx = c.comfort["current"], c.comfort["max"]
    if not (cur > 0 or mx > 0):
        return []
    color = "#8b0000" if cur > mx else "#2a3a4a"
    tip = "Трата 1 комфорта = +" + str((c.level + 1) * 5) + " тренировок."
    return [ChipSpec(
        id="comfort", kind="comfort", label="Комфорт",
        cur=cur, mx=mx, color=color, icon="😌", group="comfort", tip=tip,
        data={"level": c.level},
    )]


def _overload(c):
    """Перегрузка (если включена)."""
    if not bool(getattr(c, "overload_enabled", False)):
        return []
    val = int(getattr(c, "overload", 0) or 0)
    color = "#8b2e2e" if val > 0 else "#3a4a3a"
    tip = ("Магическая перегрузка.\nКаждый «🔁 Нулевая инициатива» −1.\n"
           "Пока > 0 — баланс не восстанавливается.")
    return [ChipSpec(
        id="overload", kind="overload", label=f"Перегрузка: {val}",
        cur=val, mx=0, color=color, icon="⛓", group="overload", tip=tip,
        data={"val": val},
    )]


def _quests(c):
    """Квесты двора на панели (show_on_panel)."""
    out = []
    for q_idx, q in enumerate(c.court_quests):
        if not q.get("show_on_panel"): continue
        tip = f"{q.get('name','?')}\nДвор: {q.get('court','?')}\n\n{q.get('desc', '')}"
        out.append(ChipSpec(
            id=_make_id("quest", q.get("name"), q_idx), kind="quest",
            label=q.get("name", "?")[:16], cur=0, mx=0,
            color="#4a4a6a", icon="📜", group="quests", tip=tip,
            data={"idx": q_idx},
        ))
    return out


def _spells(c):
    """Заклинания на панели (show_on_panel)."""
    out = []
    for sp_idx, sp in enumerate(c.spells):
        if not sp.get("show_on_panel"): continue
        can = c.spell_can_cast(sp)
        mana_cost = int(sp.get("mana_cost", 0) or 0)
        slot_circle = int(sp.get("slot_circle", sp.get("circle", 0)) or 0)
        cost_txt = f"{mana_cost} маны" if mana_cost > 0 else (f"слот Кр.{slot_circle}" if c.spell_slots_enabled else "бесплатно")
        color = "#5a3a6a" if can else "#3a3a3a"
        tip = (f"{sp.get('name', '?')}\nКруг {sp.get('circle', 0)}\n"
               f"Стоимость: {cost_txt}\nПерегрузка: {sp.get('overload', 0)}\n"
               f"Баланс: {sp.get('balance_cost', 0)}")
        if sp.get("desc"): tip += f"\n\n{sp['desc']}"
        out.append(ChipSpec(
            id=_make_id("spell", sp.get("name"), sp_idx), kind="spell",
            label=sp.get("name", "?")[:18],
            cur=0, mx=0, color=color, icon="📖", group="spells", tip=tip,
            data={"idx": sp_idx, "can_cast": can},
        ))
    return out


def _lenses(c):
    """Линзы (show_on_panel)."""
    out = []
    for ln_idx, ln in enumerate(c.lenses):
        if not ln.get("show_on_panel"): continue
        cur = int(ln.get("current", 0) or 0)
        mx = int(ln.get("max", 0) or 0)
        status = c.lens_status(ln)
        color = "#3a6a3a" if status == "closed" else ("#6a2a2a" if status == "failed" else "#4a4a6a")
        out.append(ChipSpec(
            id=_make_id("lens", ln.get("name"), ln_idx), kind="lens", label=ln.get("name", "?")[:14],
            cur=cur, mx=mx, color=color, icon="🔍", group="lenses",
            tip=ln.get("desc", "") or ln.get("name", "?"),
            data={"idx": ln_idx},
        ))
    return out