# GLOSSARY
rule: schema > glossary. legacy=[L] calc=[C] enum=[E].
schema: _schema_version = 2 (v15: show_portrait → hide_portrait).
format: `path: meaning | files`.
search: PROJECT_MAP.md §FIELDS for path→function.

# ABILITIES
abilities.str/dex/con/int/wis/cha: stats | character.py, gui_*.
ability_damage.str..cha: урон по стату | gui_combat.py.

# COMBAT
combat.hp_current: HP | character.py, gui_rest, gui_combat, gui.
_hp_max_cap[C]: max HP. combat.hp_temp: temp HP.
combat.ac: AC. parrying: отдельно (≠ combat.cmd).
combat.bab / cmb / cmd / speed / size.
cmb_total(): ББА + СИЛ + размер + cmb_mods + боль + мораль + sit("cmb").
cmd_total(): 10 + ББА + СИЛ + ЛОВ + размер + cmd_mods + боль + мораль + sit("cmd").
initiative_total(): ЛОВ + sit("initiative") + боль + мораль + combat.initiative.
_pain_threshold_data[C]: БП. pain_level[C]. pain_max.
morale. _balance_data[C]. _spirit_data[C]. _mana_data[C].
reactions. overload / overload_enabled. auto_balance_on_tick.
combat.saves.fort/ref/will.
[L] hp, ac, bab, save_* : display-only.
parry_ranged_* / master_reroll_* / master_no_attack_tag_* / master_full_balance_*.

# INVENTORY
items{}.category: armor/shield/weapon/... (25, см. ENUMS) | gui_inventory, gui_shop.
items{}.weight,weight_type,qty,location,slot,base_slots,unload_bonus,icon_b64,desc,price,order | gui_inventory.
items{}.pack: имя файла-источника (без .json). T-CAT: ставится load_catalogs.

# WEAPON/ATTACK (canon)
items{}.damage: canon damage. items{}.crit_threshold,crit_mult,weapon_group,attack_bonus,damage_bonus,finesse,two_handed,ranged,thrown,range_ft,required_level,lucky_threshold.
attacks[].damage_dice: canon (≠ item.damage). attacks[].crit_threshold,crit_mult,proficiency,from_item,is_maneuver,master_ability,master_ability_id,show_on_panel,damage_stat,damage_mult,damage_stat_auto,use_bab,extra_bonus,manual_bonus,order,lucky_threshold.
[L] items{}.damage_sml/med/type/hands.

# ARMOR & AC TYPES (T-BONUS-TYPES-2 v18.4)
items{}.armor_type,ac_bonus,ac_type,ac_max_dex,skill_penalty,speed_penalty,unprof_penalty,arcane_failure,mana_penalty.
equipment.armor_ac,shield_ac,add_shield_ac_to_balance. natural_armor,ac_bonus,ac_misc. cmb_mods,cmd_mods.
bonus_type[E]: flat, alchemical, armor, circumstance, competence, deflection, dodge, enhancement, inherent, insight, luck, morale, natural, profane, racial, resistance, sacred, shield, size, trait.
- flat / '' : складывается всегда.
- dodge: складывается с другими dodge и с dex_mod; ограничен ac_max_dex.
- остальные: побеждает больший по модулю (см. apply_bonus_type).
- dex_mod = бонус уклонения. dex_mod + dodge ≤ ac_max_dex (минимум из источников: броня/щит/перегруз).
AC full   = 10 + dex_mod(≤ac_max_dex) + equipment.armor_ac + equipment.shield_ac + natural_armor + ac_bonus + ac_misc + барабан(все 20).
AC touch  = 10 + dex_mod(≤ac_max_dex) + барабан(AC_TOUCH_TYPES). Игнор: natural, parrying, armor, shield.
AC flat   = 10 + барабан(BONUS_TYPES − {dodge}). Без dex_mod.
AC parry  = 10 + dex_mod(≤ac_max_dex) + parrying + equipment.shield_ac + natural_armor + ac_bonus + ac_misc + барабан(BONUS_TYPES − {armor}). armor из Effect — игнор.
AC_TOUCH_TYPES: flat, deflection, dodge, insight, morale, competence, luck, circumstance.
AC_FLAT_TYPES = BONUS_TYPES − {dodge}.
AC_PARRY_TYPES = BONUS_TYPES − {armor}.

# BONUS TYPES / MODIFIERS (T-BONUS-TYPES-2 v18.4)
DND/modifiers.py — единственный источник правды для барабанов. character.py импортирует.
BONUS_TYPES: 20 значений (см. ARMOR & AC TYPES bonus_type[E]).
BONUS_TYPES_FLAT = {flat, ""}.
BONUS_TYPES_ROLL = BONUS_TYPES − {armor, deflection, dodge, natural, shield} (15).
  Применяется к: атака, урон, спасброски, инициатива, навыки, CMB.
BONUS_TYPES_CMD = BONUS_TYPES − {armor, shield, natural, resistance}. Логика — T-BONUS-CMD.
apply_bonus_type(bonuses): flat → сумма; остальные → побеждает больший по модулю:
  bonus_max = max(+), penalty_max = max(|−|);
  bonus_max > penalty_max → +bonus_max; penalty_max > bonus_max → −penalty_max; равны → 0.
  Неизвестный тип → flat.
size_mod: size_index − Medium_index. CMB/CMD: +size_mod. Атаки: −size_mod.
speed_mult [DEPRECATED]: код не применяет. T-REMOVE-SPEED-MULT.
random: Mersenne Twister (random из stdlib), для d20 достаточно.

# MAGIC
_mana_data.class_max,bonus_sources[]. spell_slots{}. spell_slots_enabled.
class_resources[]. char_class.abilities[]. race.abilities[]. spells[].
spells[].circle,mastery,mastery_level,invested.
cast_spell()[C]: +concentration_ks (10 + 2×ОТ от каста). T-CAT.
items{}.uses/uses_max/uses_current. attacks[].uses*.
tick_mode[E none/restore/spend/initiative]. cooldown_rounds/current. tick_on_initiative.

# BUFFS
situational_bonuses[]: effects. duration_rounds/current. charges_max/current. charges_tick_mode (none/decrement/increment). blocks.
effects[].target/value/bonus_type. from_item. from_item_activation.
permanent: не тикает, ∞, без +/−.
keep_at_zero: не удалять при 0.
on_activate_effects[]: разово при ⟳.
on_activate_effects[].resource_name: для restore_resource.
settings.buff_delete_on_zero: удалять на след тике при 0.
settings.confirm_chip_delete: спросить перед ×.
chip: `[−] ИМЯ [N] [+] [⟳] ⚡N/M [−][+] [×]`. permanent → `∞` без +/−.
input: `N` (=max) или `current/max`. check current ≤ max if max>0.

# FEATS & STANCES (v18)
feats[].is_stance: черта = стойка. Стойки отображаются в редакторе черт с тегом [Стойка]. В чипе ситуативно — отдельный блок.
feats[].display_name: короткое имя для чипа/кнопки (особенно у стоек). Если пусто — берётся name.
feats[].stance_effects: эффекты стойки (как situational_bonuses.effects). Учитываются только когда стойка активна.
feats[].stance_blocks: что блокирует активная стойка.
feats[].effects: постоянные эффекты обычной черты (не стойки). Работают всегда, пока черта есть в списке (как у предметов).
active_stance: имя активной стойки (FK на feats[].name, is_stance=true) или null = «Обычная».
  - «Обычная» = null (заглушка, ничего не делает).
  - Меняется сколько угодно раз, НЕ тикает. Одна активная одновременно.
settings.stance_chips: имена стоек в быстром доступе. Пусто = все is_stance.

# T-LOG (v18)
action_log[]: журнал ТРАТ (append-only, maxItems 20). Получение НЕ логируется.
  - kind ∈ hp/balance/spirit/mana/slot/charge/ability/stat/training/spell/item/buff/initiative_tick/other.
  - before/after: снимки затронутых полей (для реверса).
  - rev: true = можно откатить (реверс применяет before обратно).
  - initiative_tick: реверс откатывает раунды/бафы/реген на 1 (снимок before всех затронутых).
  - Реверс каста: возвращает мана/слот/баланс/ОТ/перегрузку/концентрацию.

# T-ALPHA (v18)
settings.alpha_menu / alpha_center / alpha_chips / alpha_log / alpha_chip_buttons: 10..90 (не 0, не 100).
  - alpha_menu = окно меню; alpha_center = чарник; alpha_chips = быстрый доступ; alpha_log = лог; alpha_chip_buttons = сами чипы.
  - Clamp в GUI через _safe/_gi (>=100 → 90, <10 → 10).

# T-RACE (v18)
AbilityDef.source: training/loot/race/class/quirk. 'race'/'class' = бесплатная, 'training' = куплена.
AbilityDef.invested: сколько тренировок вложено (0 = бесплатная). >0 → UI «куплено (N)».
  - Подпись в _refresh: [Раса] / [Тренировка, N] — как у черт (Feat.source/invested).
  - Покупка: purchases.buy_race_ability / _refund.

# T46/T48 (DONE v11)
injuries[].active: включён (галочка в «Ситуативно»).
injuries[].effects[]: постоянные (применяются в situational_bonus).
char_class.abilities[].is_buff: это класс-баф (виден в «Ситуативно», кнопка «+ активировать»).
race.abilities[].is_buff: то же для расы.

# OTHER
drives{}/drive_principles[]. quirks[]. seeds[]. courts[]/court_quests[].
injuries[]. injury_points. heal_rating. comfort/attention. training.purchases (append-only). downtime.
languages[]/templates[]/wiki_links[]/lenses[]. settings (GUI).
active_stance, action_log[] (v18; T-STANCE, T-LOG).
race.abilities[].
custom.json: <папка>/custom.json — «своё», создаётся ensure_dirs. T-CAT.

# ABBREV
БП=_pain_threshold_data. ОТ=injury_points. РЛ=heal_rating.
ББА=combat.bab. CMB/CMD=combat.cmb/cmd. AC=combat.ac. HP=combat.hp_current.
XP=xp. FK=items{uuid}. GM=game master.

# TARGETS [E] (no `all`)
str,dex,con,int,wis,cha,will,attack,damage,ac,ref,fort,cmd,cmb,initiative,speed,skill,lucky,hp_temp,restore_hp,restore_mana,restore_spirit,restore_balance,restore_resource,self_damage_per_tick.
speed_mult [DEPRECATED]: не применяется, оставлен в VALID_SIT_TARGETS для старых сейвов.
skill → skill_name. restore_resource → resource_name.
cmd/cmb/initiative — DONE (v11): в VALID_SIT_TARGETS, TARGET_NAMES, cmb_total/cmd_total/initiative_total.
**ВАЖНО:** target="lucky" (счастливая атака) — это НЕ тип бонуса "luck". Счастливая атака — особый шанс на крит (уменьшает порог d20).

# ENUMS
tick_mode: none/restore/spend/initiative.
charges_tick_mode[T34.1]: none/decrement/increment.
source: training/loot/race/class/quirk/manual.
master_ability_id: ""/master_reroll/master_no_attack_tag/master_full_balance (T24 DONE: реестр = WEAPON_BONUS_CATALOG, ключи master_*).
bonuses[].id: T24 DONE (v12): реестр = WEAPON_BONUS_CATALOG (character.py). Валидация в purchases.set_weapon_bonuses.
category: armor/shield/weapon/belt/body/chest/eyes/gloves/head/neck/ring/back/shoulders/legs/feet/companion/pet/modifier/tools_craft/tools_travel/components/holy_symbol/unload/consumable/misc.
location: equipped/unload/bag/base.
slot: armor/belt/body/chest/eyes/gloves/head/neck/ring1/ring2/back/shoulders/legs/feet/weapon_main/weapon_off/shield/companion/pet/modifier/tools_craft/tools_travel/components/holy_symbol/unload/null.
skill.tier: normal/advanced/specialized.
size: Fine..Colossal. severity: light/medium/heavy/custom.
bab_type: poor/medium/good. good_saves: fort/ref/will.
catalogs_enabled[]: <папка>/<файл>.json | <папка> (старое: вся папка).
catalogs_items_disabled[]: '<папка>/<файл>#<имя>' — скрытые элементы.
catalogs_mode: whitelist/blacklist (default whitelist).
bonus_type: flat/alchemical/armor/circumstance/competence/deflection/dodge/enhancement/inherent/insight/luck/morale/natural/profane/racial/resistance/sacred/shield/size/trait.

# SETTINGS (GUI, не механика)
buff_delete_on_zero, confirm_chip_delete (T9).
catalogs_enabled, catalogs_items_disabled, catalogs_mode (T-CAT).
hide_hints (T50; примечания, НЕ тултипы).
hp_regen_per_tick (T41; HP-реген за тик, 0 = выкл).
hide_portrait (v15; True = скрыть портрет в главном окне; было show_portrait, инверсия).
visible_buttons (gui_buttons.is_visible; после T-SPLIT, было gui.py._is_visible).
ui_layout_mode (v16; classic/split/split_pinned, default split).
minimize_to_tray_on_close (v16; сворачивать меню+чарник в трей при закрытии, default True).
stance_chips (v18; имена стоек в быстром доступе; пусто = все is_stance).
chips_visible_enabled / chips_visible / chips_order (v1.0; T-CHIPS: фильтр, список id, порядок; id из chips.collect_all).
chips_colors (v1.0; T-CHIPS: {id: '#hex'} — кастомные цвета, перекрывают spec['color']).
chips_positions (v1.1, план; T-SPLIT-3.2: {id: [x, y]} — позиции чипов на десктопе).
chips_drag_mode (v1.1, план; T-SPLIT-3.2: false = только клики, true = drag).
alpha_menu / alpha_center / alpha_chips / alpha_log / alpha_chip_buttons (v18; 10..90).
T-WINDOW-FIX (v18): `center_window(..., modal=False)` — без `grab_set` (иначе висит в сплите); `at_pointer=True` — рядом с мышкой; `_visible_root` — видимый родитель.

# DEPRECATED (v18.4)
speed_mult — [DEPRECATED], код не применяет. Используй speed (сумма) или отдельную задачу T-REMOVE-SPEED-MULT.
armor / shield в Effect.bonus_type для AC — не складываются с equipment.armor_ac / shield_ac (см. AC full в ARMOR & AC TYPES).

# T-EFFECTS-UI (v18.5)
EFFECTS_DEFAULTS (modifiers.py): единый шаблон для Feat/Injury/AbilityDef. 19 полей: effects, on_activate_effects, duration_*, charges_*, cooldown_*, tick_mode, tick_on_initiative, permanent, keep_at_zero, is_buff, show_on_panel, allow_toggle, enabled, blocks, is_stance.
apply_effects_defaults(obj): setdefault для всех полей шаблона.
activate_feat_buff(feat_idx): копирует feats[feat_idx] → situational_bonuses. Тратит charges. Применяет on_activate_effects.
activate_injury_buff(injury_idx): то же для injuries.
gui_effects.py: render_effects_list / apply_effects_list / render_temporal_fields / apply_temporal_fields.
injuries[].enabled: вместо injuries[].active (T-EFFECTS-UI). active — удалён.
max_*: max_hp / max_mana / max_balance / max_spirit / max_resource / max_pain_threshold — потолки (T-MAX-STATS).
blocks[]: список имён блокируемых функций (одна механика is_blocked). Валидные имена — реестр BLOCKABLE в character.py. T-BLOCKS-EXPANDED.

# T-CHIPS (v1.0)
chips.py: ChipSpec,collect_all,_resources,_abilities,_items,_attacks,_buffs,_feats,_buttons,_rest,_lenses,_spells,_quests,_overload,_comfort,_stances,_make_id,_dedup,clean_order.
  - ChipSpec: id,kind,label,cur,max,color,tip,icon,group,widgets,edit,data.
  - collect_all(c): все доступные чипы (14 источников).
  - id: kind:name (напр. attack:Меч, buff:Окаменение, spell:Огненный шар, rest:short, rest:long), item:<uuid>, фикс. (hp, ac_full, bp, mana, spirit, balance, slot_<N>, stance, btn:*), фикс. кнопки (btn:damage, btn:heal, btn:temp_hp, btn:lose_balance, btn:new_turn, btn:injury, btn:pain, btn:morale, btn:restore_balance, btn:situational, btn:refresh). Дубли — #1, #2 (_dedup).
  - _buttons: базовые кнопки (color_fn / label_fn). _rest: короткий / длинный.
  - clean_order(c): убрать из settings.chips_order id, которых больше нет (при загрузке).
gui_chips.py: CHIP_REGISTRY,render_chip,register (13 типов: resource,ability,item,attack,buff,feat,lens,spell,quest,overload,comfort,stance,button),rebuild_resources_panel (фильтр+сортировка),drag&drop (призрак+линия),flow-контейнер,maybe_remove_buff,bind_edit_number,_lens_step,_render_button (color_fn / label_fn).
  - drag&drop: за имя чипа (или чёрную точку). Призрак (Toplevel,-alpha 0.75) + линия-индикатор (#4af,2px). _preview_insert + _reorder. reflow_chips НЕ при drag (без мигания).
  - правый клик: на ресурсах → gui_dialogs.ask_int (bind_edit_number).
  - настройки (edit_settings): «Спрятать/показать все» (chips_visible_enabled toggle), «Сбросить все чипы» (chips_order=[], chips_visible=[], chips_visible_enabled=false), «Цвета чипов» (chips_colors).
gui_desktop.py (v1.1, план): DesktopView (pywin32 + WM_NCHITTEST). Фон (fullscreen, WS_EX_LAYERED|WS_EX_TRANSPARENT, LWA_ALPHA=0) + чипы (Toplevel без рамки, topmost, place(x,y)). HTTRANSPARENT/HTCLIENT. settings.chips_positions, chips_drag_mode.

# T-SPLIT-VIEW (v17) / T-SPLIT-3 (v18)
- `gui_tray.py` (план, T-SPLIT-3.1) — трей (`pystray` в отдельном файле). **Не создан.**
- `gui_chips.py` (v1.0, T-SPLIT-3.2) — чипы + панель ресурсов (отдых — в `chips._rest`). **Создан.**
- `gui_canvas.py` (план, T-SPLIT-3.3) — отрисовка чарника + тултипы. **Не создан.**
- `gui_dialogs.py` (v18) — `ask_int` / `show_text` / `ask_yes_no` (свои диалоги, «от мышки»). Существует.
- `gui_actions.py` (v18, план) — заменён на `chips.py` + `gui_chips.py` (v18.6).
- `gui_split.py` — 3 окна: `menu_win`, `center_win`, `chips_win`.
- `overrideredirect(False)` + `attributes("-toolwindow", True)` — все окна.
- `show_editor(title, build_fn)` — метод сплита, рисует редактор в `view_edit`.
- `show_main()` — возврат в главный вид.
- `_run_button(key, cmd)` — для кнопок меню: `CENTER_BUTTONS` → чарник, остальные → отдельные окна.
- `withdraw()` — скрытие, `deiconify()` — показ. `destroy()` запрещён.
- Ч / О / Б — toggle (первый клик с фокусом, повторный — свернуть). `_show_char_sheet` / `_show_last_editor` / `_toggle_chips`.