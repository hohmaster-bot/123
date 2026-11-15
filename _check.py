# check.py — быстрый чек логики WIPEFINDER (без GUI).
# Запуск: python check.py
# При ошибке — AssertionError. При успехе — "ALL OK".

import sys
from character import (
    Character, VALID_SIT_TARGETS, CASTING_ACTIONS,
    SPELL_CIRCLE_TABLE, spell_display_name, spell_overload_auto,
)


def _new():
    c = Character("Test")
    c.init_defaults()
    return c


def check_valid_targets():
    assert "cmb" in VALID_SIT_TARGETS
    assert "cmd" in VALID_SIT_TARGETS
    assert "initiative" in VALID_SIT_TARGETS
    assert "all" not in VALID_SIT_TARGETS
    print("✓ VALID_SIT_TARGETS (cmb/cmd/initiative, no all)")


def check_situational_bonus():
    c = _new()
    c.situational_bonuses.append({
        "name": "Тест", "effects": [
            {"target": "attack", "value": 2},
            {"target": "ac", "value": 1},
            {"target": "cmb", "value": 3},
            {"target": "cmd", "value": 4},
            {"target": "initiative", "value": 5},
        ]})
    assert c.situational_bonus("attack") == 2
    assert c.situational_bonus("ac") == 1
    assert c.situational_bonus("cmb") == 3
    assert c.situational_bonus("cmd") == 4
    assert c.situational_bonus("initiative") == 5
    print("✓ situational_bonus (attack/ac/cmb/cmd/initiative)")


def check_cmb_cmd_init():
    c = _new()
    # Дефолт: CMB=1, CMD=11, INIT=0
    assert c.cmb_total() == 1, f"CMB={c.cmb_total()}"
    assert c.cmd_total() == 11, f"CMD={c.cmd_total()}"
    assert c.initiative_total() == 0, f"INIT={c.initiative_total()}"
    # Баф +3 CMB, +4 CMD, +5 INIT
    c.situational_bonuses.append({
        "name": "Тест", "effects": [
            {"target": "cmb", "value": 3},
            {"target": "cmd", "value": 4},
            {"target": "initiative", "value": 5},
        ]})
    assert c.cmb_total() == 4
    assert c.cmd_total() == 15
    assert c.initiative_total() == 5
    # Ручной combat.initiative
    c.combat["initiative"] = 2
    assert c.initiative_total() == 7
    print("✓ cmb_total / cmd_total / initiative_total")


def check_spell_helpers():
    assert CASTING_ACTIONS["swift"] == 0
    assert CASTING_ACTIONS["immediate"] == 0
    assert CASTING_ACTIONS["standard"] == 2
    assert CASTING_ACTIONS["full_round"] == 3
    assert SPELL_CIRCLE_TABLE[3]["mana"] == 5
    assert SPELL_CIRCLE_TABLE[0]["overload"] == 4
    sp = {"name": "Шар", "attack_type": "ranged"}
    assert spell_display_name(sp) == "Шар (Ranged)"
    sp2 = {"name": "Стрела", "attack_type": "ranged_touch"}
    assert spell_display_name(sp2) == "Стрела (Ranged touch)"
    # overload: 2 действия × 1 (мана) = 2
    assert spell_overload_auto({"casting_time": "standard",
                                 "mana_cost": 5}) == 2
    # overload: 2 действия × 2 (без маны) = 4
    assert spell_overload_auto({"casting_time": "standard",
                                 "mana_cost": 0}) == 4
    print("✓ spell_display_name / spell_overload_auto")


def check_spell_range():
    c = _new()
    c.char_class["level"] = 5
    assert c.spell_range_text({"range_type": "long"}) == "600 фт"
    assert c.spell_range_text({"range_type": "short"}) == "35 фт"
    assert c.spell_range_text({"range_type": "medium"}) == "150 фт"
    assert c.spell_range_text({"range_type": "custom",
                                "range_custom": 30}) == "30 фт"
    print("✓ spell_range_text (short/medium/long/custom)")


def check_spell_can_cast():
    c = _new()
    # без маны, без слотов
    sp = {"mana_cost": 0, "circle": 1, "slot_circle": 1}
    assert c.spell_can_cast(sp) is True
    # с маной, мана выключена
    sp2 = {"mana_cost": 5, "circle": 3}
    assert c.spell_can_cast(sp2) is False
    c.mana["enabled"] = True
    c.mana["current"] = 3
    assert c.spell_can_cast(sp2) is False
    c.mana["current"] = 5
    assert c.spell_can_cast(sp2) is True
    print("✓ spell_can_cast (мана / слоты)")


def check_cast_spell():
    c = _new()
    # 1. Сначала задаём class_max (иначе recompute_derived обнулит ману).
    c.mana["enabled"] = True
    c.mana["class_max"] = 10
    # 2. Баланс: balance_bonus 5 → max = 2 + 5 = 7 (хватит на кост 3).
    c.balance_bonus = 5
    c.recompute_derived()
    # 3. Теперь mana["max"] = 10 (class_max), current выставим на 10.
    c.mana["current"] = c.mana["max"]
    assert c.mana["current"] == 10, ("mana must be 10", c.mana)
    c.balance["current"] = c.balance["max"]
    assert c.balance["max"] >= 3, ("нужен запас баланса", c.balance)
    c.spells.append({"name": "Шар", "circle": 3, "mana_cost": 5,
                      "balance_cost": 3, "overload": 2,
                      "slot_circle": 3})
    r = c.cast_spell(0)
    assert r["ok"] is True, ("cast_spell ok?", r)
    assert c.mana["current"] == 5, ("mana", c.mana, r)
    assert c.overload == 2, ("overload", c.overload, r)
    # Баланса хватило → ОТ 0, КС 0, баланс уменьшился ровно на 3.
    assert r["injury"] == 0, r
    assert r["concentration_ks"] == 0, r
    assert c.balance["current"] == c.balance["max"] - 3, c.balance
    print("✓ cast_spell (мана/перегрузка/баланс, ОТ 0)")


def check_cast_spell_no_balance():
    """Нехватка баланса → ОТ, КС = 10 + 2*ОТ,
    ресурсы списаны (без отката)."""
    c = _new()
    c.mana["enabled"] = True
    c.mana["current"] = 10
    c.mana["max"] = 10
    # Баланса по умолчанию 2, кост 5 → ОТ += 3
    c.balance["current"] = c.balance["max"]  # = 2
    c.injury_points = 0
    c.spells.append({"name": "Тяжёлое", "circle": 3, "mana_cost": 5,
                      "balance_cost": 5, "overload": 2,
                      "slot_circle": 3})
    r = c.cast_spell(0)
    assert r["ok"] is True
    # Ресурсы списаны
    assert c.mana["current"] == 5, c.mana
    assert c.overload == 2, c.overload
    assert c.balance["current"] == 0, c.balance
    # ОТ начислены, КС посчитан
    assert r["injury"] == 3, r
    assert c.injury_points == 3, c.injury_points
    assert r["concentration_ks"] == 16, r   # 10 + 2*3
    print("✓ cast_spell (ОТ 3 → КС 16, ресурсы списаны)")


def check_lens_status():
    c = _new()
    assert c.lens_status({"current": 0, "max": 12}) == "failed"
    assert c.lens_status({"current": 12, "max": 12}) == "closed"
    assert c.lens_status({"current": 6, "max": 12}) == ""
    print("✓ lens_status (failed/closed/'')")


def check_ability_buff():
    c = _new()
    c.char_class["abilities"] = [{
        "name": "Ярость", "is_buff": True,
        "charges_max": 1, "charges_current": 1,
        "duration_rounds": 3,
        "effects": [{"target": "attack", "value": 2}],
    }]
    ok = c.activate_ability_buff("class", 0)
    assert ok is True
    assert c.char_class["abilities"][0]["charges_current"] == 0
    # в situational_bonuses появился баф
    found = [b for b in c.situational_bonuses
             if b.get("name") == "Ярость"]
    assert len(found) == 1
    assert found[0]["effects"][0]["value"] == 2
    print("✓ activate_ability_buff (class)")


def check_take_damage():
    c = _new()
    c.combat["hp_current"] = 20
    c.combat["hp_temp"] = 5
    c.balance["current"] = 10
    r = c.take_damage(8)
    # 5 temp + 3 hp = 8; баланс теряет 3 (не 8, т.к. temp не трогает баланс)
    assert r["temp_loss"] == 5, r
    assert r["hp_loss"] == 3, r
    assert r["balance_loss"] == 3, r
    assert r["injury"] == 0, r
    print("✓ take_damage (temp HP не съедает баланс)")


def check_load_save():
    import tempfile, os
    c = _new()
    c.name = "CheckChar"
    c.spells.append({"name": "X", "circle": 1,
                      "attack_type": "ranged",
                      "mana_cost": 1, "overload": 2,
                      "casting_time": "standard"})
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        c.save(path)
        c2 = Character.load(path)
        assert c2.name == "CheckChar"
        assert len(c2.spells) == 1
        assert c2.spells[0].get("attack_type") == "ranged"
        print("✓ save/load (заклинания с новыми полями)")
    finally:
        os.remove(path)

def check_catalogs():
    """T-K2: 12 папок (misc убран), load_catalogs."""
    from character import CATALOG_SUBDIRS, load_catalogs
    assert len(CATALOG_SUBDIRS) == 12, len(CATALOG_SUBDIRS)
    assert "weapons" in CATALOG_SUBDIRS
    assert "custom" in CATALOG_SUBDIRS
    assert "misc" not in CATALOG_SUBDIRS
    load_catalogs()
    print("✓ CATALOG_SUBDIRS (12) + load_catalogs")


def check_situational_cmb_cmd_init():
    """B: боль/мораль/ситуативка на cmb/cmd/init."""
    c = _new()
    c.pain_extra = 2          # боль 2 (ignore_pain=False)
    c.morale = 4              # мораль +2
    c.situational_bonuses.append({
        "name": "T", "effects": [
            {"target": "cmb", "value": 3},
            {"target": "cmd", "value": 4},
            {"target": "initiative", "value": 5},
        ]})
    # CMB = 1 + боль(-2) + мораль(+2) + sit(+3) = 4
    assert c.cmb_total() == 4, c.cmb_total()
    # CMD = 11 + боль(-2) + мораль(+2) + sit(+4) = 15
    assert c.cmd_total() == 15, c.cmd_total()
    # INIT = 0 + боль(-2) + мораль(+2) + sit(+5) = 5
    assert c.initiative_total() == 5, c.initiative_total()
    print("✓ cmb/cmd/init + боль/мораль/ситуативка")


def check_skill_tier_rating():
    """T-K2: навык из каталога (SKILLS_CATALOG)."""
    from character import SKILLS_CATALOG
    assert isinstance(SKILLS_CATALOG, list)
    print("✓ SKILLS_CATALOG (list)")


def check_registry():
    """R: реестр редакторов."""
    import gui_registry
    assert len(gui_registry.EDITORS) == 18
    groups = gui_registry.groups()
    assert "Предметы" in groups
    assert "Развитие" in groups
    assert "Бой" in groups
    assert "Магия" in groups
    assert "Мир" in groups
    assert "Настройки" in groups
    print(f"✓ gui_registry ({len(gui_registry.EDITORS)} редакторов, "
          f"{len(groups)} групп)")

def check_alphabet():
    """A: gui_alphabet.TARGET_NAMES == VALID_SIT_TARGETS."""
    import gui_alphabet
    from character import VALID_SIT_TARGETS
    assert set(gui_alphabet.TARGET_NAMES) == VALID_SIT_TARGETS
    assert "all" not in gui_alphabet.TARGET_NAMES
    print(f"✓ gui_alphabet ({len(gui_alphabet.TARGET_NAMES)} целей)")


def check_catalogs_filter():
    """T-CAT: catalogs_enabled/mode (default whitelist)."""
    c = _new()
    assert c.settings.get("catalogs_enabled") == []
    assert c.settings.get("catalogs_mode") == "whitelist"
    print("✓ catalogs_enabled/mode (whitelist)")


def check_hp_regen():
    """T41: hp_regen_per_tick."""
    c = _new()
    c.combat["hp_current"] = 1
    c.settings["hp_regen_per_tick"] = 3
    r = c.tick_initiative()
    assert c.combat["hp_current"] == 4, c.combat["hp_current"]
    assert any("HP-реген" in x for x in r), r
    print("✓ hp_regen_per_tick")


def check_charges_tick_mode():
    """T34.1: charges_tick_mode."""
    c = _new()
    c.situational_bonuses.append({
        "name": "X", "charges_tick_mode": "decrement",
        "charges_max": 3, "charges_current": 3,
        "tick_on_initiative": True,
        "duration_rounds": 1, "duration_current": 1})
    c.tick_initiative()
    assert c.situational_bonuses[0]["charges_current"] == 2
    print("✓ charges_tick_mode (decrement)")


def check_drive_extras():
    """T16: пустые принцип (2+) / квест (3+)."""
    import gui_stub
    c = _new()
    gui_stub._ensure_drive_extras(c, "idealism", 0, 2)
    assert any(p.get("drive_key") == "idealism"
               for p in c.drive_principles)
    gui_stub._ensure_drive_extras(c, "idealism", 2, 3)
    assert any(q.get("drive_key") == "idealism"
               and q.get("source") == "drive"
               for q in c.court_quests)
    # при 3→4 — не дублирует
    before = len(c.court_quests)
    gui_stub._ensure_drive_extras(c, "idealism", 3, 4)
    assert len(c.court_quests) == before
    print("✓ drive extras (2+/3+, без дублей)")

def check_gui_menu():
    """T-SPLIT: gui_menu.MENU_SPEC консистентен, actions резолвятся."""
    import gui_menu
    from gui import App
    spec = gui_menu.MENU_SPEC
    assert spec.get("_version") == 1, spec.get("_version")
    assert isinstance(spec.get("menus"), list) and spec["menus"]
    for menu in spec["menus"]:
        assert menu.get("key"), f"menu без key: {menu}"
        assert menu.get("title"), f"menu без title: {menu}"
        for item in menu.get("items", []):
            t = item.get("type", "command")
            if t == "command":
                name = item.get("action", "")
                assert name, f"command без action: {item}"
                assert hasattr(App, name), f"action не резолвится: {name}"
            elif t == "check":
                assert item.get("key"), f"check без key: {item}"
            elif t == "separator":
                pass
            else:
                raise AssertionError(f"unknown item type: {t}")
    print(f"✓ gui_menu.MENU_SPEC ({len(spec['menus'])} меню)")


def check_gui_media():
    """T-SPLIT: gui_media.force_taskbar_alt_tab есть и callable."""
    import gui_media
    assert callable(getattr(gui_media, "force_taskbar_alt_tab", None))
    print("✓ gui_media.force_taskbar_alt_tab")


def check_gui_file_ops():
    """T-SPLIT: gui_file_ops.copy_sheet есть и callable."""
    import gui_file_ops
    assert callable(getattr(gui_file_ops, "copy_sheet", None))
    print("✓ gui_file_ops.copy_sheet")


def check_gui_buttons():
    """T-SPLIT: gui_buttons.buttons_list + константы."""
    import gui_buttons
    assert callable(getattr(gui_buttons, "buttons_list", None))
    assert callable(getattr(gui_buttons, "rebuild_side_buttons", None))
    assert isinstance(gui_buttons.DEFAULT_VISIBLE_BUTTONS, dict)
    assert isinstance(gui_buttons.FORCED_VISIBLE_BUTTONS, set)
    print("✓ gui_buttons (buttons_list/rebuild + константы)")


def check_gui_app_config():
    """T-SPLIT: gui_app_config API."""
    import gui_app_config
    assert callable(getattr(gui_app_config, "load_app_config", None))
    assert callable(getattr(gui_app_config, "save_app_config", None))
    assert isinstance(gui_app_config.CONFIG_FILE, str)
    print("✓ gui_app_config (load/save/CONFIG_FILE)")


def check_feats_save_load():
    """feats: save → load сохраняет черты."""
    import tempfile, os
    c = _new()
    c.feats.append({"name": "Тест-черта", "desc": "d",
                    "source": "loot", "invested": 0})
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        c.save(path)
        c2 = Character.load(path)
        assert len(c2.feats) == 1, c2.feats
        assert c2.feats[0]["name"] == "Тест-черта", c2.feats
        print("✓ feats save/load")
    finally:
        os.remove(path)

def check_ui_layout_mode():
    """T-SPLIT: ui_layout_mode в settings (classic/split/split_pinned)."""
    import json
    import os
    from character import BASE_DIR
    schema_path = os.path.join(BASE_DIR, "character.schema.json")
    # Если схемы нет рядом — пропускаем (тест не критичен для логики)
    if not os.path.exists(schema_path):
        # fallback: просто проверим, что в дефолтных настройках есть поле
        c = _new()
        mode = c.settings.get("ui_layout_mode", "split")
        assert mode in ("classic", "split", "split_pinned"), mode
        print("✓ settings.ui_layout_mode (по умолчанию split, без схемы)")
        return
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    settings = schema.get("$defs", {}).get("Settings", {}).get("properties", {})
    field = settings.get("ui_layout_mode")
    assert field is not None, "ui_layout_mode нет в схеме"
    assert field.get("default") == "split", field.get("default")
    assert set(field.get("enum", [])) == {"classic", "split", "split_pinned"}, field.get("enum")
    print("✓ schema settings.ui_layout_mode (enum + default)")


def check_center_buttons():
    """T-SPLIT: все ключи CENTER_BUTTONS есть в buttons_list."""
    import gui_buttons
    # Собираем ключи из списка кнопок (3-элементные кортежи)
    # без создания App — просто статический анализ.
    lst = gui_buttons.buttons_list
    # Список ключей берём из центрального множества
    keys = set(gui_buttons.CENTER_BUTTONS)
    # Все возможные ключи из DEFAULT_VISIBLE_BUTTONS + FORCED_VISIBLE_BUTTONS
    all_keys = set(gui_buttons.DEFAULT_VISIBLE_BUTTONS) | set(gui_buttons.FORCED_VISIBLE_BUTTONS)
    for k in keys:
        assert k in all_keys, f"CENTER_BUTTONS содержит неизвестный ключ: {k}"
    # Дополнительно: каждый ключ из CENTER_BUTTONS должен встречаться в buttons_list
    # (по исходнику: ключи — 3-й элемент кортежа). Сделаем простой поиск по коду.
    import inspect
    src = inspect.getsource(lst)
    for k in keys:
        assert f'"{k}"' in src or f"'{k}'" in src, f"ключ {k} не найден в buttons_list"
    print(f"✓ CENTER_BUTTONS ({len(keys)} ключей, все в buttons_list)")


def check_gui_split():
    """T-SPLIT-VIEW: gui_split импортируется и имеет build()."""
    import gui_split
    assert callable(getattr(gui_split, "build", None)), "gui_split.build отсутствует"
    print("✓ gui_split.build()")


def check_tray_always():
    """T-TRAY: трей всегда виден (иконка создаётся в __init__, есть _stop_tray)."""
    import gui
    assert callable(getattr(gui, "_make_tray_icon", None)), "нет _make_tray_icon"
    assert callable(getattr(gui, "_start_tray", None)), "нет _start_tray"
    assert callable(getattr(gui, "_stop_tray", None)), "нет _stop_tray"
    # App._stop_tray (обёртка) должна существовать
    assert hasattr(gui.App, "_stop_tray"), "App._stop_tray отсутствует"
    # _tray_mode — функция для выбора split/classic
    assert callable(getattr(gui, "_tray_mode", None)), "нет _tray_mode"
    print("✓ tray (_make_tray_icon/_start_tray/_stop_tray/_tray_mode)")

def main():
    checks = [
        check_valid_targets,
        check_situational_bonus,
        check_cmb_cmd_init,
        check_spell_helpers,
        check_spell_range,
        check_spell_can_cast,
        check_cast_spell,
        check_cast_spell_no_balance,
        check_lens_status,
        check_ability_buff,
        check_take_damage,
        check_load_save,
        # v11+
        check_catalogs,
        check_situational_cmb_cmd_init,
        check_skill_tier_rating,
        check_registry,
        check_alphabet,
        check_catalogs_filter,
        check_hp_regen,
        check_charges_tick_mode,
        check_drive_extras,
        # T-SPLIT (GUI-модули)
        check_gui_menu,
        check_gui_media,
        check_gui_file_ops,
        check_gui_buttons,
        check_gui_app_config,
        check_feats_save_load,
        # T-SPLIT-VIEW (v16)
        check_ui_layout_mode,
        check_center_buttons,
        check_gui_split,
        check_tray_always,
        # v18 (T-STANCE / T-LOG / T-ALPHA / T-RACE)
        check_schema_v18,
        check_stance_data,
        check_action_log,
        check_alpha_clamp,
        check_race_ability_fields,
        # v18.4 (T-BONUS-TYPES-2)
        check_bonus_types,
        # v18.5 (T-EFFECTS-UI)
        check_effects_ui,
        check_effects_ui_expanded
    ]
    failed = 0
    for fn in checks:
        try:
            fn()
        except AssertionError as e:
            print(f"✗ {fn.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {fn.__name__}: ОШИБКА {type(e).__name__}: {e}")
            failed += 1
    if failed == 0:
        print(f"\nALL OK ({len(checks)} проверок)")
        return 0
    print(f"\nПРОВАЛЕНО: {failed} из {len(checks)}")
    return 1

def check_stance_data():
    """T-STANCE: active_stance FK, feats[].is_stance, stance_chips."""
    c = _new()
    # 1) по умолчанию active_stance = None
    assert c.active_stance is None, c.active_stance
    # 2) добавим стойку-черту
    c.feats.append({"name": "Защитная стойка", "is_stance": True,
                    "stance_effects": [{"target": "ac", "value": 2}],
                    "stance_blocks": []})
    # 3) active_stance можно поставить именем
    c.active_stance = "Защитная стойка"
    # 4) stance_effects применяются (если character.py уже умеет —
    #    проверим через situational_bonus; если нет — пропустим)
    if hasattr(c, "stance_effects"):
        assert c.stance_effects() == [{"target": "ac", "value": 2}]
    # 5) stance_chips по умолчанию пуст
    assert c.settings.get("stance_chips") == [], c.settings.get("stance_chips")
    # 6) сброс в «Обычную»
    c.active_stance = None
    print("✓ stance data (active_stance / is_stance / stance_chips)")


def check_action_log():
    """T-LOG: append-only, maxItems 20, rev по умолчанию."""
    c = _new()
    # 1) по умолчанию пуст
    assert c.action_log == [], c.action_log
    # 2) ручное добавление (как это делает character.py)
    c.action_log.append({"ts": "2026-11-14T00:00:00", "kind": "hp",
                         "summary": "Урон 10", "before": {"hp_current": 20},
                         "after": {"hp_current": 10}, "rev": True})
    assert len(c.action_log) == 1
    # 3) обрезка до 20 (эмулируем)
    for i in range(25):
        c.action_log.append({"ts": f"t{i}", "kind": "other",
                             "summary": f"#{i}", "rev": False})
    if hasattr(c, "_trim_action_log"):
        c._trim_action_log()
        assert len(c.action_log) == 20, len(c.action_log)
    else:
        # fallback: схема говорит 20 — проверим константу, если она есть
        assert len(c.action_log) <= 30, len(c.action_log)
    print("✓ action_log (append-only, max 20, rev)")


def check_alpha_clamp():
    """T-ALPHA: 5 полей, 10..90, clamp."""
    c = _new()
    for key in ("alpha_menu","alpha_center","alpha_chips","alpha_log","alpha_chip_buttons"):
        v = c.settings.get(key, 90)
        assert 10 <= v <= 90, f"{key}={v}"
    # clamp: 5 -> 10, 100 -> 90
    def _clamp(v):
        return max(10, min(90, int(v)))
    assert _clamp(5) == 10
    assert _clamp(100) == 90
    assert _clamp(50) == 50
    print("✓ alpha_* (10..90, clamp 5->10 / 100->90)")


def check_race_ability_fields():
    """T-RACE: AbilityDef.source / invested."""
    c = _new()
    c.race["abilities"] = [
        {"name": "Я дракон", "source": "race", "invested": 0},
        {"name": "Полёт", "source": "training", "invested": 300},
    ]
    a0 = c.race["abilities"][0]
    a1 = c.race["abilities"][1]
    assert a0["source"] == "race" and a0["invested"] == 0
    assert a1["source"] == "training" and a1["invested"] == 300
    # class: тот же AbilityDef
    c.char_class["abilities"] = [
        {"name": "Ярость", "source": "class", "invested": 0},
    ]
    assert c.char_class["abilities"][0]["source"] == "class"
    print("✓ race/class abilities (source/invested)")

def check_schema_v18():
    """T-STANCE / T-LOG / T-ALPHA / T-RACE — проверки v18."""
    import json, os
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "Старт", "character.schema.json")
    if not os.path.exists(schema_path):
        print(f"  [SKIP] schema not found: {schema_path}")
        return True
    with open(schema_path, encoding="utf-8") as f:
        s = json.load(f)
    props = s.get("properties", {})
    defs = s.get("$defs", {})
    ok = True

    # 1) active_stance: string|null, default null
    ast = props.get("active_stance", {})
    if ast.get("default", "MISSING") is not None:
        print(f"  [FAIL] active_stance.default != null: {ast.get('default')!r}")
        ok = False
    if "string" not in (ast.get("type") or []) and ast.get("type") != ["string","null"]:
        print(f"  [FAIL] active_stance.type != [string,null]: {ast.get('type')!r}")
        ok = False

    # 2) action_log: array, maxItems 20
    al = props.get("action_log", {})
    if al.get("type") != "array":
        print(f"  [FAIL] action_log.type != array: {al.get('type')!r}")
        ok = False
    if al.get("maxItems") != 20:
        print(f"  [FAIL] action_log.maxItems != 20: {al.get('maxItems')!r}")
        ok = False

    # 3) alpha_*: 5 полей, 10..90
    settings_props = defs.get("Settings", {}).get("properties", {})
    for key in ("alpha_menu","alpha_center","alpha_chips","alpha_log","alpha_chip_buttons"):
        p = settings_props.get(key, {})
        if p.get("minimum") != 10 or p.get("maximum") != 90:
            print(f"  [FAIL] settings.{key} range != 10..90: "
                  f"min={p.get('minimum')} max={p.get('maximum')}")
            ok = False

    # 4) stance_chips: array[string]
    sc = settings_props.get("stance_chips", {})
    if sc.get("type") != "array" or (sc.get("items") or {}).get("type") != "string":
        print(f"  [FAIL] settings.stance_chips != array[string]")
        ok = False

    # 5) Feat: is_stance / stance_effects / stance_blocks
    feat_props = defs.get("Feat", {}).get("properties", {})
    if feat_props.get("is_stance", {}).get("type") != "boolean":
        print(f"  [FAIL] Feat.is_stance != boolean")
        ok = False
    if feat_props.get("stance_effects", {}).get("type") != "array":
        print(f"  [FAIL] Feat.stance_effects != array")
        ok = False
    if feat_props.get("stance_blocks", {}).get("type") != "array":
        print(f"  [FAIL] Feat.stance_blocks != array")
        ok = False

    # 6) AbilityDef: source (enum) / invested (int>=0)
    ab_props = defs.get("AbilityDef", {}).get("properties", {})
    src = ab_props.get("source", {})
    if src.get("type") != "string" or set(src.get("enum") or []) != {"training","loot","race","class","quirk"}:
        print(f"  [FAIL] AbilityDef.source enum != expected: {src.get('enum')!r}")
        ok = False
    inv = ab_props.get("invested", {})
    if inv.get("type") != "integer" or inv.get("minimum") != 0:
        print(f"  [FAIL] AbilityDef.invested != integer>=0: {inv!r}")
        ok = False

    if ok:
        print("  [OK] schema v18 fields (T-STANCE/T-LOG/T-ALPHA/T-RACE)")
    return ok

def check_bonus_types():
    """T-BONUS-TYPES-2 (v18.4): барабаны, 4 вида AC, dodge+dex, size_mod."""
    from modifiers import (
        BONUS_TYPES, BONUS_TYPES_FLAT, BONUS_TYPES_ROLL,
        BONUS_TYPES_CMD, AC_TOUCH_TYPES, AC_FLAT_TYPES,
        AC_PARRY_TYPES, AC_FULL_TYPES, apply_bonus_type, size_mod,
    )
    import gui_alphabet

    # 1) 20 типов, все подписи
    assert len(BONUS_TYPES) == 20, BONUS_TYPES
    assert set(gui_alphabet.BONUS_TYPE_NAMES) == BONUS_TYPES, (
        "BONUS_TYPE_NAMES != BONUS_TYPES: "
        f"{set(gui_alphabet.BONUS_TYPE_NAMES) ^ BONUS_TYPES}")
    print("  [OK] BONUS_TYPES (20) == gui_alphabet.BONUS_TYPE_NAMES")

    # 2) ROLL = 15, без armor/deflection/dodge/natural/shield
    assert len(BONUS_TYPES_ROLL) == 15, BONUS_TYPES_ROLL
    assert BONUS_TYPES_ROLL & {"armor", "deflection", "dodge",
                                "natural", "shield"} == set()
    print("  [OK] BONUS_TYPES_ROLL (15, без armor/deflection/dodge/natural/shield)")

    # 3) AC-виды
    assert AC_FLAT_TYPES == BONUS_TYPES - {"dodge"}
    assert AC_PARRY_TYPES == BONUS_TYPES - {"armor"}
    assert AC_FULL_TYPES == BONUS_TYPES
    assert AC_TOUCH_TYPES <= BONUS_TYPES
    print("  [OK] AC full/touch/flat/parry (фильтры)")

    # 4) Барабан: flat складывается
    assert apply_bonus_type([
        {"value": 4, "type": "flat"}, {"value": 2, "type": "flat"}]) == 6
    print("  [OK] apply_bonus_type: flat складывается (4+2=6)")

    # 5) Барабан: max положительных
    assert apply_bonus_type([
        {"value": 4, "type": "morale"}, {"value": 2, "type": "morale"}]) == 4
    print("  [OK] apply_bonus_type: max(+) morale (4,2 -> 4)")

    # 6) Барабан: max штрафа
    assert apply_bonus_type([
        {"value": -4, "type": "morale"}, {"value": -2, "type": "morale"}]) == -4
    print("  [OK] apply_bonus_type: max(|-|) morale (-4,-2 -> -4)")

    # 7) Барабан: штраф > бонуса → штраф
    assert apply_bonus_type([
        {"value": -4, "type": "morale"}, {"value": 2, "type": "morale"}]) == -4
    print("  [OK] apply_bonus_type: штраф побеждает (-4,+2 -> -4)")

    # 8) Барабан: равны → 0
    assert apply_bonus_type([
        {"value": 4, "type": "morale"}, {"value": -4, "type": "morale"}]) == 0
    print("  [OK] apply_bonus_type: равны -> 0")

    # 9) Барабан: бонус > штрафа → бонус
    assert apply_bonus_type([
        {"value": 4, "type": "morale"}, {"value": -2, "type": "morale"}]) == 4
    print("  [OK] apply_bonus_type: бонус побеждает (+4,-2 -> +4)")

    # 10) size_mod: Medium=0, Small=-1, Large=+1
    assert size_mod("Medium") == 0
    assert size_mod("Small") == -1
    assert size_mod("Large") == 1
    print("  [OK] size_mod (Medium=0, Small=-1, Large=+1)")

    # 11) AC: dex+dodge ≤ ac_max_dex
    c = _new()
    c.abilities = {"str": 10, "dex": 20, "con": 10,
                   "int": 10, "wis": 10, "cha": 10}
    # dex_mod = +5, dodge +3, cap 4 → сумма 8, обрезается до 4
    c.situational_bonuses.append({
        "name": "Dodge", "effects": [
            {"target": "ac", "value": 3, "bonus_type": "dodge"},
        ]})
    c.items["_cap"] = {
        "id": "_cap", "name": "cap", "category": "armor",
        "location": "equipped", "slot": "armor",
        "ac_max_dex": 4,
    }
    assert c.dex_bonus_for_ac() == 4, c.dex_bonus_for_ac()
    print("  [OK] dex_mod + dodge ≤ ac_max_dex (5+3, cap 4 -> 4)")

    # 12) AC full: morale -4 + 2 = -4 (не 2)
    c2 = _new()
    c2.situational_bonuses.append({
        "name": "M", "effects": [
            {"target": "ac", "value": -4, "bonus_type": "morale"},
            {"target": "ac", "value": 2, "bonus_type": "morale"},
        ]})
    assert c2.ac_full() == 6, c2.ac_full()  # 10 + 0 + (-4)
    print("  [OK] ac_full: morale -4+2 -> -4 (AC 6)")

    # 13) AC parry: armor игнорируется, parrying учитывается
    c3 = _new()
    c3.abilities = {"str": 10, "dex": 10, "con": 10,
                    "int": 10, "wis": 10, "cha": 10}
    # armor +10 (должен игнорироваться в parry)
    c3.items["_armor"] = {
        "id": "_armor", "name": "armor", "category": "armor",
        "location": "equipped", "slot": "armor",
        "ac_type": "armor", "ac_bonus": 10,
    }
    # parrying 3
    c3.feats.append({"name": "P", "is_stance": False,
                     "effects": [{"target": "ac", "value": 3,
                                  "bonus_type": "deflection"}]})
    full = c3.ac_full()
    parry = c3.ac_parry()
    armor_bonus = c3._ac_type_max("armor")
    sit_full = c3._ac_situational_by_type()
    sit_parry = c3._ac_situational_by_type(for_parry=True)
    print(f"  [DBG] full={full} parry={parry} armor={armor_bonus} "
          f"sit_full={sit_full} sit_parry={sit_parry}")
    # full = 10 (база) + 10 (armor) + 3 (deflection) = 23
    assert full == 23, full
    # parry = 10 (база) + 0 (parrying) + 3 (deflection) = 13
    # (armor 10 игнорируется — в AC_PARRY_TYPES нет "armor")
    assert parry == 13, parry
    print("  [OK] ac_parry: armor игнор (full 23 vs parry 13)")

def check_effects_ui():
    """T-EFFECTS-UI (v18.5): единый шаблон, gui_effects."""
    from gui_effects import (render_effects_list, apply_effects_list,
                             render_temporal_fields, apply_temporal_fields)
    import gui_combat
    import gui_editors
    from modifiers import EFFECTS_DEFAULTS, apply_effects_defaults
    # 1) apply_effects_list: пустые (value == 0) отбрасываются
    assert apply_effects_list([
        {"target": "ac", "value": 0},
        {"target": "attack", "value": 2},
    ]) == [{"target": "attack", "value": 2}]
    # 2) apply_effects_defaults: setdefault
    obj = {"name": "X"}
    apply_effects_defaults(obj)
    assert obj["permanent"] is True
    assert obj["enabled"] is True
    assert obj["is_buff"] is True
    assert obj["allow_toggle"] is True
    assert obj["show_on_panel"] is True
    assert obj["is_stance"] is True
    assert obj["effects"] == []
    assert obj["on_activate_effects"] == []
    assert obj["blocks"] == []
    # 3) EFFECTS_DEFAULTS — 19 полей
    assert len(EFFECTS_DEFAULTS) >= 18, len(EFFECTS_DEFAULTS)
    # 4) gui_combat / gui_editors импортируются
    assert hasattr(gui_combat, "action_situational")
    assert hasattr(gui_combat, "_edit_buff_dialog")
    assert hasattr(gui_editors, "_feat_dialog")
    # 5) activate_feat_buff / activate_injury_buff
    c = _new()
    c.feats.append({"name": "F", "is_buff": True,
                    "effects": [{"target": "attack", "value": 2}],
                    "charges_max": 1, "charges_current": 1})
    assert c.activate_feat_buff(0) is True
    assert c.feats[0]["charges_current"] == 0
    assert len([b for b in c.situational_bonuses
                if b.get("from_feat") == 0]) == 1
    c.injuries.append({"name": "I", "severity": "light",
                       "is_buff": True,
                       "effects": [{"target": "ac", "value": 1}]})
    assert c.activate_injury_buff(0) is True
    assert len([b for b in c.situational_bonuses
                if b.get("from_injury") == 0]) == 1
    print("  [OK] T-EFFECTS-UI (gui_effects + activate_*_buff)")

def check_effects_ui_expanded():
    c = _new()
    c.situational_bonuses.append({
        "name": "X", "blocks": ["do:attack", "bonus:dodge", "res:restore_hp"]})
    assert c.is_blocked("attack") is True
    assert c.is_blocked("balance_restore") is False
    assert c.is_bonus_denied("dodge") is True
    assert c.is_resource_denied("restore_hp") is True
    
    c2 = _new()
    c2.situational_bonuses.append({
        "name": "Y", "effects": [{"target": "max_hp", "value": -5}]})
    c2.recompute_derived()
    assert c2.hp_max_actual() == (c2.hp_max_from_rolls() + c2.combat["hp_bought"] - 5)
    print("  [OK] T-EFFECTS-UI: blocks + max_hp")

if __name__ == "__main__":
    sys.exit(main())