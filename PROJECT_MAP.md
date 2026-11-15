# MAP

## §0. Физическая карта (где что лежит)

> Правило: сначала смотри сюда, потом `Ctrl+F` по нужному файлу.
> Если не нашёл — `CONTRACT.md §6` (спросить, не догадываться).

### `Старт/` — документы проекта (читать в этом порядке)

| Файл | Что внутри |
|---|---|
| `TECH.md` | §0 RULES, §0.1 ROADMAP, §0.2 ONBOARDING, §1 TASKS, §2 DEFERRED, T-NEW (план) |
| `CONTRACT.md` | §1 источники правды, §2 правила схемы, §3 формат ответа бота, §4 работа с JSON, §5 кодировка, §6 неопределённость, §7 чек-лист |
| `PROMPT.md` | онбординг бота: 5–10 вопросов по одному, с рекомендацией |
| `character.schema.json` | **источник правды №1**: типы, enum'ы, обязательность, `_schema_version` |
| `SCHEMA.md` | человекочитаемое описание схемы (компаньон к `.schema.json`) |
| `GLOSSARY.md` | переводы/сокращения/JSON-пути, `[L]` legacy, `[C]` calc, `[E]` enum |
| `LOG.md` | история версий и статусы задач (OPEN/DOING/DONE/CANCELLED) |
| `PROJECT_MAP.md` | **этот файл**: физическая карта + карта «функция → файл» |

### `DND/` — код (Python + tkinter)

| Файл | Зона ответственности |
|---|---|
| `character.py` | ядро: `Character`, `load/save`, `tick_initiative`, `situational_bonus`, `_ac_situational_by_type`, `initiative_breakdown`, `cast_spell`, `cmb_total`/`cmd_total`/`initiative_total`, `load_catalogs`, `ensure_dirs`, `activate_feat_buff`, `activate_injury_buff`, константы. Импортирует `modifiers.py` + `apply_effects_defaults`. |
| `gui_effects.py` (v18.5) | **Единый UI эффектов** (T-EFFECTS-UI). `render_effects_list`, `apply_effects_list`, `render_temporal_fields`, `apply_temporal_fields`. Вызывается из `gui_editors.py` / `gui_combat.py`. |
| `modifiers.py` (v18.4) | **Единственный источник правды для барабанов бонусов.** `BONUS_TYPES` (20), `BONUS_TYPES_FLAT`, `BONUS_TYPES_ROLL` (15), `BONUS_TYPES_CMD`, `AC_TOUCH_TYPES`, `AC_FLAT_TYPES`, `AC_PARRY_TYPES`, `AC_FULL_TYPES`, `apply_bonus_type(bonuses, allowed)`, `size_mod(size)`, `size_mod_attack(size)`. Без GUI, без окон. |
| `chips.py` (v1.0) | **Дескрипторы чипов (ChipSpec).** Без tkinter. `ChipSpec(id, kind, label, cur, mx, color, tip, icon, group, widgets, edit, data)`, `collect_all(c)`, `_*` (14 источников: `_resources`, `_abilities`, `_items`, `_attacks`, `_buffs`, `_feats`, `_buttons`, `_rest`, `_quests`, `_spells`, `_overload`, `_comfort`, `_lenses`, `_stances`), `_make_id(kind, name, idx)`, `_dedup(ids)`, `clean_order(c)`. |
| `purchases.py` | покупки/тренировки (`buy_*`, `_pay`, `_refund`) |
| `gui.py` | `App`, `_build_layout`, `_refresh`, `_draw_canvas`, `_show_main`/`_show_editor` (**делегируют сплиту**), drag-за-шапку, `_do_level_up`, `_on_tray_window` (трей). Чипы — **делегируют** в `gui_chips`. |
| `gui_chips.py` (v1.0) | **Чипы + панель ресурсов** (T-SPLIT-3.2). `CHIP_REGISTRY`, `render_chip(app, spec)`, `@register(kind)` (13 типов: `resource`, `ability`, `item`, `attack`, `buff`, `feat`, `lens`, `spell`, `quest`, `overload`, `comfort`, `stance`, `button`), `rebuild_resources_panel` (фильтр + сортировка), drag&drop (призрак + линия: `_drag_start` / `_drag_move` / `_drag_end` / `_preview_insert` / `_reorder` / `_find_target` / `_make_ghost` / `_move_ghost` / `_destroy_ghost`), flow-контейнер (`init_flow_container`, `add_chip`, `reflow_chips`), `maybe_remove_buff`, `bind_edit_number`, `_lens_step`, `_render_button` (`color_fn` / `label_fn`). |
| `gui_split.py` | 3-панельный режим (`SplitView`): `menu_win`, `center_win`, `chips_win`. `_build_side_tabs` (кнопки Ч/О/Б). `show_char_sheet` / `show_last_editor` / `_toggle_chips` (**toggle**, первый клик с фокусом). `set_active_window(win)`. `_apply_pin`. **Все окна `overrideredirect(False)` + `withdraw()`.** |
| `gui_desktop.py` (v1.1, план) | **Desktop overlay** (`pywin32` + `WM_NCHITTEST`). `DesktopView`: фон (fullscreen, `WS_EX_LAYERED | WS_EX_TRANSPARENT`, `LWA_ALPHA=0`) + чипы (Toplevel без рамки, `topmost`, `place(x, y)`). `HTTRANSPARENT` / `HTCLIENT`. `settings.chips_positions`, `chips_drag_mode`. |
| `gui_tray.py` (v18, план) | Трей: `_make_tray_icon` / `_start_tray` / `_stop_tray` / `_tray_mode`. |
| `gui_canvas.py` (v18, план) | Отрисовка чарника + тултипы: `_draw_canvas`, `_show_canvas_tip`, `_hide_canvas_tip`. |
| `gui_dialogs.py` (v18) | Свои диалоги «от мышки»: `ask_int`, `show_text`, `ask_yes_no`. Вместо `simpledialog` / `messagebox` в чипах. |
| `gui_actions.py` (v18, план) | Реестр чипов: `CHIP_SPEC`, `CHIP_GENERATORS`, `run_chip(app, key)`. (Заменён на `chips.py` + `gui_chips.py` в v18.6.) |
| `gui_app_config.py` | `config.json` (`load_app_config`, `save_app_config`, `get/set_last_character`, `CONFIG_FILE`) |
| `gui_buttons.py` | кнопки левого меню (`buttons_list`, `rebuild_side_buttons`, `DEFAULT_VISIBLE_BUTTONS`, `FORCED_VISIBLE_BUTTONS`, `CENTER_BUTTONS`) |
| `gui_menu.py` | меню-бар (`MENU_SPEC` — данные, `build_menu(app, spec=None)`, `save_menu_spec`, `reset_menu_spec`) |
| `gui_media.py` | портрет/фон (`load_portrait`, `load_background`, `update_portrait_size`, `expand_portrait`, `force_taskbar_alt_tab`) |
| `gui_file_ops.py` | файловые операции (`load_or_new`, `new_character`, `save`, `import/export`, `copy_sheet`, `on_close`, `_ask_exit_custom`). Вызывает `chips.clean_order(c)` в 4 местах. |
| `gui_combat.py` | боевая панель, `action_new_turn`, `action_situational`, `_edit_buff_dialog` |
| `gui_editors.py` | редакторы (раса, класс, атаки, спасброски, настройки (**блок «Чипы»**), черты и стойки, CMB/CMD). `_feat_dialog` (вкл. `display_name` и `bonus_type`). |
| `gui_skills.py`, `gui_spells.py`, `gui_training.py` | редакторы навыков / заклинаний / тренировок |
| `gui_shop.py`, `gui_catalogs.py` | магазин/каталог, управление каталогами |
| `gui_inventory.py`, `gui_rest.py` | инвентарь, отдых |
| `gui_templates.py`, `gui_wiki.py`, `gui_stub.py` | шаблоны, вики, драйвы/дворы/линзы |
| `gui_windows.py` | **ЕДИНСТВЕННАЯ ФАБРИКА ОКОН**. `open_window(app, title, w, h, mode)`. Читает настройки `window_open_mode` / `pin_editor_to_menu`. Все окна закрываются по `Escape`. |
| `gui_shared.py` | Утилиты (без окон): `ToolTip`, `make_scrollable`, `_load_image*`, `bind_*`. |
| `gui_alphabet.py` | единый словарь отображения (`TARGET_NAMES`, `CATEGORY_NAMES`, `BONUS_TYPE_NAMES`), `assert` с ядром |
| `gui_registry.py`, `gui_editors_window.py` | реестр редакторов, окно «Редакторы» |
| `pdf_export.py` | экспорт PDF |
| `_check.py` | быстрый чек логики (без GUI) + проверки GUI-модулей (39 проверок) |
| `_debug.py` | виртуальный тест сплита |

### `catalogs/` — данные (12 папок, `CATALOG_SUBDIRS`)
`weapons`, `armor`, `shields`, `weapon_items`, `feats`, `templates`, `skills`, `race_abilities`, `class_abilities`, `spells`, `buffs`, `custom`.

### `characters/` — сейвы персонажей
`<Имя>.json`. Бот **не трогает** эти файлы (`CONTRACT.md §4`).

### `config.json` — настройки приложения
`last_character`, `view_options`. Читает/пишет `gui_app_config.py`.

---

## Карта «функция → файл»

character.py: Character,load,save,to_dict,tick_initiative,_eval_effect_value,_apply_effect_values,activate_buff,trigger_buff,take_damage,situational_bonus,_ac_situational_by_type,ac_full,ac_touch,ac_flat,ac_parry,save_total,save_breakdown,skill_bonus,attack_bonus,attack_damage_bonus,attack_crit,attack_lucky,attack_range,long_rest,short_rest,recompute_derived,load_catalogs,ensure_dirs,cmb_total,cmd_total,initiative_total,initiative_breakdown,activate_ability_buff,spell_range_text,spell_can_cast,cast_spell,spell_display_name,spell_overload_auto,lens_status,stances,set_active_stance,stance_effects,stance_blocks,feats_for_ui,log_action,revert_action
modifiers.py (v18.4): BONUS_TYPES,BONUS_TYPES_FLAT,BONUS_TYPES_ROLL,BONUS_TYPES_CMD,AC_TOUCH_TYPES,AC_FLAT_TYPES,AC_PARRY_TYPES,AC_FULL_TYPES,apply_bonus_type,size_mod,size_mod_attack,EFFECTS_DEFAULTS,apply_effects_defaults
chips.py (v1.0): ChipSpec,collect_all,_resources,_abilities,_items,_attacks,_buffs,_feats,_buttons,_rest,_lenses,_spells,_quests,_overload,_comfort,_stances,_make_id,_dedup,clean_order
gui_effects.py (v18.5): render_effects_list,apply_effects_list,render_temporal_fields,apply_temporal_fields
gui_chips.py (v1.0): maybe_remove_buff,init_flow_container,add_chip,reflow_chips,_lens_step,_drag_bind,_find_src,_drag_start,_drag_move,_drag_end,_make_ghost,_move_ghost,_destroy_ghost,_hide_indicator,_preview_insert,_find_target,_reorder,bind_edit_number,CHIP_REGISTRY,register,render_chip,_render_resource,_render_ability,_render_item,_render_attack,_render_buff,_render_feat,_render_lens,_render_spell,_render_quest,_render_overload,_render_comfort,_render_stance,_render_button,rebuild_resources_panel
purchases.py: buy_ability_up,remove_ability_up,ability_up_cost,_pay,_refund,add_training_points
gui.py: App,_build_layout,_refresh,_hard_refresh,_do_level_up,_show_main,_show_editor,_draw_canvas,_on_canvas_resize,_on_left_resize,_start_move,_do_move,_rebuild_menu,_open_editors_window,_open_inventory,_open_catalogs,_edit_templates,_edit_wiki,_rest_dialog,_set_music,_play_music,_toggle_view_opt,_show_canvas_tip,_hide_canvas_tip,_on_tray_window + обёртки: _rebuild_resources_panel,_init_flow_container,_add_chip,_reflow_chips,_maybe_remove_buff,_do_short_rest,_do_long_rest
gui_split.py: SplitView,_build_menu,_build_center,_build_chips,_build_side_tabs (кнопки Ч/О/Б),_run_button,_show_win,_show_editor_split,show_editor,show_main,_toggle_center,_toggle_chips,_show_char_sheet,_show_last_editor,_open_center,_open_chips,_on_center_close,_on_chips_close,_on_menu_close,_apply_pin,set_active_window,build
gui_menu.py: MENU_SPEC,build_menu,save_menu_spec,reset_menu_spec,_resolve_spec,_build_one_menu
gui_buttons.py: DEFAULT_VISIBLE_BUTTONS,FORCED_VISIBLE_BUTTONS,CENTER_BUTTONS,buttons_list,is_visible,rebuild_side_buttons
gui_media.py: load_portrait,load_background,update_portrait_size,expand_portrait,force_taskbar_alt_tab
gui_file_ops.py: load_or_new,new_character,rename_character,open_characters_folder,open_character,save,import_character,export_character,export_pdf,copy_sheet,on_close,_ask_exit_custom
gui_app_config.py: CONFIG_FILE,load_app_config,save_app_config,get_last_character,set_last_character
gui_combat.py: build_combat_panel,action_new_turn,action_situational,_edit_buff_dialog,_describe_effects
gui_training.py: edit_training,_fill_training,_ability_decrease,_pick_source_dialog,_gi_int
gui_editors.py: edit_class,edit_race,edit_attacks,edit_saves,edit_settings (вкл. блок «Чипы»),edit_feats,_feat_dialog (вкл. display_name и bonus_type),_feat_from_catalog,_render_ability_buff_fields,_apply_ability_buff_fields,_class_abil_from_catalog,_race_abil_from_catalog,_ab_edit,_race_abil_edit,_ab_delete
gui_skills.py: edit_skills
gui_spells.py: edit_spells
gui_shop.py: open_shop,_catalog_packs,_catalog_categories,_catalog_items_for_shop,_shop_catalog_row,_buy_from_catalog,_open_catalogs_manager,_import_catalog_from_file,_import_catalog_from_url,_export_catalog_file,_pick_catalog_folder,_reload_catalog,_shop_item_row,_shop_item_dialog,_buy,_delete_shop_item,_import_csv,_export_json,_reload,open_catalogs,_new_catalog,_edit_catalog_file,_delete_catalog_file,_take_from_catalog,_import_catalog_url
gui_catalogs.py: open_catalogs_manager,_render_file_row,_render_file_items,_range_select,_bulk_set_items,_import_from_file,_import_from_url,_new_empty,_edit_json,_pick_folder_dialog,_file_enabled,_item_hidden,_set_file_enabled,_set_item_hidden,_count_items,_load_items,_unique_name,_catalog_path
gui_templates.py: edit_templates
gui_wiki.py: edit_wiki
gui_stub.py: edit_drives,edit_courts,edit_lenses
gui_rest.py: rest_dialog
gui_shared.py: ToolTip,make_scrollable,_load_image,_load_image_from_data,bind_canvas_wheel,bind_context_menu,bind_clipboard_all
gui_dialogs.py: ask_int,show_text,ask_yes_no
pdf_export.py: export_pdf
gui_alphabet.py: TARGET_NAMES,CATEGORY_NAMES,BONUS_TYPE_NAMES (единый словарь, assert с VALID_SIT_TARGETS)
gui_registry.py: EDITORS, groups, by_group, get (реестр редакторов)
gui_editors_window.py: open_editors_window, _build_editor_tab, _run_editor
_check.py: main, check_* (39 проверок)
_debug.py: test_split

# CONST
gui.py: SIT_TARGET_NAMES,DEFAULT_VIEW_OPTIONS
chips.py (v18.6): ChipSpec
gui_chips.py (v18.6): CHIP_REGISTRY
gui_menu.py: MENU_SPEC
gui_buttons.py: DEFAULT_VISIBLE_BUTTONS,FORCED_VISIBLE_BUTTONS,CENTER_BUTTONS
character.py: VALID_SIT_TARGETS,WEAPON_BONUS_CATALOG,WEAPON_BONUS_SLOTS,ARMOR_LEVELS,SHIELD_LEVELS,SOURCE_NAMES,SOURCE_ICONS,PAIN_MAX,PAIN_HP_STEP,BAB_MAP,CASTING_ACTIONS,SPELL_CIRCLE_TABLE,SPELL_ATTACK_SUFFIX,SPELL_AOE_NAMES,CATALOG_SUBDIRS,AC_TYPES_NON_STACK,AC_TOUCH_TYPES
modifiers.py (v18.4): BONUS_TYPES,BONUS_TYPES_FLAT,BONUS_TYPES_ROLL,BONUS_TYPES_CMD,AC_TOUCH_TYPES,AC_FLAT_TYPES,AC_PARRY_TYPES,AC_FULL_TYPES,EFFECTS_DEFAULTS
gui_windows.py: DEFAULT_MODE

# FIELDS
situational_bonuses: character.py(tick_initiative,situational_bonus,activate_buff,trigger_buff,_sync_item_bonuses)
situational_bonuses.permanent: character.py(tick_initiative)
situational_bonuses.keep_at_zero: character.py(tick_initiative)
situational_bonuses.on_activate_effects: character.py(activate_buff,trigger_buff)
situational_bonuses.charges_*: character.py(activate_buff,trigger_buff,long_rest)
effects[].bonus_type: modifiers.py(apply_bonus_type), character.py(_ac_situational_by_type,initiative_breakdown), gui_effects.py(render_effects_list), gui_editors.py(_feat_dialog) (T-BONUS-TYPES-2, v18.4)
feats[].effects: character.py(situational_bonus,initiative_breakdown), gui_effects.py(render_effects_list) (T-FEAT-EFFECTS, v18.2) — в схеме с v18.4
feats[].enabled / is_buff / show_on_panel / allow_toggle: T-EFFECTS-UI (v18.5, gui_effects.py)
injuries[].enabled: T-EFFECTS-UI (v18.5, gui_combat.py action_situational)
max_hp / max_mana / max_balance / max_spirit / max_resource / max_pain_threshold: T-MAX-STATS (v18.5, character.py)
blocks[] (имена функций, реестр BLOCKABLE): T-BLOCKS-EXPANDED (v18.5, character.py, gui_effects.py)
settings.buff_delete_on_zero: character.py(tick_initiative)
settings.confirm_chip_delete: gui_chips.py(maybe_remove_buff)
settings.hide_portrait: gui_media.py(update_portrait_size), gui_editors.py(edit_settings)
settings.hide_hints: T50 (gui_shared.hint)
settings.catalogs_enabled,catalogs_items_disabled,catalogs_mode: T-CAT (character.load_catalogs)
settings.alpha_menu, alpha_center, alpha_chips, alpha_log, alpha_chip_buttons: T-ALPHA (v18, 10..90)
settings.stance_chips: T-STANCE (v18, имена стоек в быстром доступе)
settings.chips_visible_enabled / chips_visible / chips_order: T-CHIPS (v1.0, chips.collect_all, gui_chips, gui_editors.edit_settings)
settings.chips_colors: T-CHIPS (v1.0, chips.collect_all, gui_editors.edit_settings)
settings.chips_positions / chips_drag_mode: T-SPLIT-3.2 (v1.1, gui_desktop.py, план)
settings.close_prev_window: T-SPLIT-4 (v18.1, закрывать предыдущее окно при открытии нового, default True)
active_stance: T-STANCE (v18, character.set_active_stance / situational_bonus)
action_log[]: T-LOG (v18, character.log_action / revert_action, maxItems 20)
feats[].is_stance, stance_effects, stance_blocks, display_name: T-STANCE (v18)
feats[].effects: T-FEAT-EFFECTS (v18, постоянные эффекты черт, character.situational_bonus, initiative_breakdown)
AbilityDef.source, invested: T-RACE (v18)
settings.hp_regen_per_tick: T41 (character.tick_initiative)
settings.visible_buttons: gui_buttons.py(is_visible), gui.py(_rebuild_side_buttons)
settings.menu_spec: gui_menu.py(_resolve_spec,save_menu_spec,reset_menu_spec)
settings.ui_layout_mode: gui_split.py(SplitView.__init__), gui.py(_build_layout)
items{}.pack: T-CAT (character.load_catalogs)
cast_spell().concentration_ks: T-CAT (character.cast_spell, gui_chips._render_spell._cast)
injuries: character.py(tick_initiative,long_rest)
injuries.active,effects: T46
char_class.abilities: character.py(use_ability,restore_ability,start_session)
char_class.abilities.is_buff: T48 (character.activate_ability_buff, gui_combat.action_situational)
race.abilities.is_buff: T48 (character.activate_ability_buff, gui_combat.action_situational)
spells[].attack_type/range_type/is_aoe/casting_time/mana_cost/overload/slot_circle: T-C (character.spell_*, gui_spells._spell_dialog, gui_chips._render_spell)
lenses[].current/max/show_on_panel: T-L (character.lens_status, gui_stub.edit_lenses, gui_chips._render_lens, gui_chips._lens_step)
items: character.py(add_item,move_item,_sync_item_bonuses,_item_bonus)
attacks: character.py(attack_bonus,attack_damage_bonus,attack_crit,attack_lucky)
training.available: purchases.py(_pay,_refund)
training.purchases: purchases.py(_pay)
xp,xp_threshold,level,hp_rolls: gui.py(_do_level_up)

# CATALOGS (12 папок, CATALOG_SUBDIRS)
catalogs/weapons: {groups} — оружейные группы
catalogs/armor: {items} — броня
catalogs/shields: {items} — щиты
catalogs/weapon_items: {items} — предметы-оружие
catalogs/feats: {items} — черты (в т.ч. стойки)
catalogs/templates: {items} — шаблоны
catalogs/skills: {items} — навыки
catalogs/race_abilities: {items} — абилки расы
catalogs/class_abilities: {items} — абилки класса
catalogs/spells: {items} — заклинания
catalogs/buffs: {items} — травмы/бафы
catalogs/custom: {items} — юзер/кастом

# SEARCH
1. MAP→2. Ctrl+F в указанном файле→3. спросить(CONTRACT §6)

# TROUBLESHOOTING
- **Окна сплита не появляются:** см. `TECH.md` (v17, делегирование).
- **`TclError: bad window path name`:** см. `TECH.md` (v17, `withdraw` вместо `destroy`).
- **Окна открываются не там:** см. `gui_windows.py` и настройки `window_open_mode` / `pin_editor_to_menu`.
- **Запрещено** создавать `tk.Toplevel()` вне `gui_windows.py`, `gui_split.py` и `gui_desktop.py` (план).
- **Бонусы не складываются / AC неверный:** см. `DND/modifiers.py` (`apply_bonus_type`). Все расчёты — там, `character.py` только вызывает. Не дублировать логику в `character.py`.
- **Чипы не двигаются / не сохраняются:** см. `gui_chips.py` (`_drag_start` / `_preview_insert` / `_reorder`), `chips.clean_order`, `settings.chips_order`.

# WINDOWS (все Toplevel окна приложения)
# ПРАВИЛО: создаются ТОЛЬКО через gui_windows.py (кроме gui_split.py, gui_desktop.py — план).

gui_windows.py: open_window (универсальная фабрика).
gui_split.py: menu_win, center_win, chips_win, log_win (план).
gui_desktop.py (план, v1.1): overlay (фон, fullscreen, click-through), chips_overlay (чипы, topmost, place).
gui_chips.py: призрак drag (_make_ghost) — Toplevel без рамки.
gui_combat.py: _ask_number, action_pain_dialog, action_morale, action_situational, _edit_buff_dialog.
gui_rest.py: rest_dialog.
gui_editors.py: edit_race, edit_class, edit_attacks, edit_saves, edit_settings, edit_feats, _feat_dialog, _attack_dialog, _ab_edit, _race_abil_edit, _quirk_dialog.
gui_inventory.py: open_inventory.
gui_shop.py: open_shop, _shop_item_dialog.
gui_skills.py: edit_skills.
gui_spells.py: edit_spells.
gui_training.py: edit_training.
gui_templates.py: edit_templates.
gui_wiki.py: edit_wiki.
gui_stub.py: edit_drives, edit_courts, edit_lenses.
gui_editors_window.py: open_editors_window.
gui_file_ops.py: _ask_exit_custom.