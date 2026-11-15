# SCHEMA.md — WIPEFINDER: человекочитаемое описание схемы персонажа

> Компаньон к `character.schema.json`. При расхождении **прав `character.schema.json`**.
> Версия схемы: 2. Поле в JSON: `_schema_version`.

## 1. Верхний уровень

| Поле | Тип | Обяз. | Комментарий |
|---|---|---|---|
| `_schema_version` | int | да | Версия схемы. Сейчас **2** (v15: `show_portrait` → `hide_portrait`). |
| `name` | str | да | Имя персонажа. |
| `class_display` | str | да | Отображаемое «Волшебник 4». |
| `hp`, `pain_threshold`, `balance`, `spirit`, `mana` | str `N/M` | нет | **LEGACY display-only.** Источник: см. §2. |
| `ac`, `parrying`, `bab` | int | нет | **LEGACY display-only.** |
| `save_fort`, `save_ref`, `save_will` | int | нет | **LEGACY display-only.** |
| `injury_points` | int | нет | Очки травм (ОТ). |
| `morale` | int | нет | Мораль. |
| `overload`, `overload_enabled` | int/bool | нет | Перегрузка. |
| `auto_balance_on_tick` | bool | нет | Авто-восстановление баланса на тике. |
| `xp`, `xp_threshold` | int | нет | Опыт. |
| `portrait`, `portrait_b64`, `background_image`, `background_b64`, `music_url` | str | нет | Медиа. |
| `situational_bonuses[]` | array | нет | Бафы с длительностью/зарядами. |
| `char_class` | object | нет | Класс. |
| `race` | object | нет | Раса. |
| `abilities{str..cha}` | object | да | Характеристики. |
| `ability_damage{str..cha}` | object | да | Урон/штраф по характеристикам. |
| `combat` | object | да | Боевые параметры. |
| `equipment` | object | нет | AC от брони/щита. |
| `natural_armor`, `ac_bonus`, `ac_misc` | int | нет | Доп. AC. |
| `cmb_mods[]`, `cmd_mods[]` | array | нет | Модификаторы CMB/CMD. |
| `items{}` | dict uuid→Item | да | Инвентарь. |
| `attacks[]` | array | да | Атаки. |
| `spells[]`, `spell_slots{}` | array/object | нет | Магия. |
| `proficiencies` | object | нет | Владения. |
| `training` | object | нет | Журнал покупок. |
| `skills[]`, `feats[]`, `quirks[]`, `languages[]` | array | нет | Развитие. |
| `drives{}`, `drive_principles[]` | object/array | нет | Драйвы. |
| `courts[]`, `court_quests[]` | array | нет | Дворы. |
| `downtime` | object | нет | Валюта/время. |
| `injuries[]` | array | нет | Травмы. |
| `reactions`, `reactions_invested` | int | нет | Реакции. |
| `base`, `base_invested` | object/int | нет | База. |
| `comfort`, `attention` | `{current,max}` | нет | Комфорт/внимание. |
| `_hp_max_cap` | int | нет | **Вычисляемое.** Потолок HP. |
| `_pain_threshold_data`, `_balance_data`, `_spirit_data` | `{current,max}` | нет | **Вычисляемые.** |
| `_mana_data` | object | нет | **Вычисляемое.** Мана. |
| `settings` | object | да | GUI-настройки. **Не данные персонажа.** |
| `notes` | str | нет | Заметки. |

## 2. Карта «legacy → источник правды»

| Legacy (строка/int в корне) | Источник правды |
|---|---|
| `hp` | `combat.hp_current` + `_hp_max_cap` |
| `pain_threshold` | `_pain_threshold_data.current/max` |
| `balance` | `_balance_data.current/max` |
| `spirit` | `_spirit_data.current/max` |
| `mana` | `_mana_data.current/max` |
| `ac` | `combat.ac` |
| `bab` | `combat.bab` |
| `parrying` | — (самостоятельное поле, не legacy; см. §6) |
| `save_fort/ref/will` | `combat.saves.fort/ref/will` |

**Правило для ботов:** читать legacy можно только для отображения; **писать** — только в источник правды. Legacy-строки GUI пересобирает из источника.

## 3. `items{}` — поля Item (канон как в инвентаре)

Ключевое:
- Ключ словаря = `item.id` = UUID. **Всегда.**
- `category`: `armor|shield|weapon|belt|body|chest|eyes|gloves|head|neck|ring|back|shoulders|legs|feet|companion|pet|modifier|tools_craft|tools_travel|components|holy_symbol|unload|consumable|misc` (25, `ITEM_CATEGORIES`).
- `location`: `equipped|unload|bag|base` (`LOCATIONS`).
- `slot`: `armor|belt|body|chest|eyes|gloves|head|neck|ring1|ring2|back|shoulders|legs|feet|weapon_main|weapon_off|shield|companion|pet|modifier|tools_craft|tools_travel|components|holy_symbol|unload|null` (25, `EQUIP_SLOTS`).
- `pack` (str): имя файла-источника (без `.json`). T-CAT: ставится `load_catalogs` для элементов из каталога.

### Канон оружия (зафиксировано по инвентарю)

| Поле Item | Смысл |
|---|---|
| `damage` | **КАНОН** урона оружия (`"6d6"`, `"d3+5"`). |
| `crit_threshold` | Порог крита (1..20). |
| `crit_mult` | Множитель крита (≥1). |
| `weapon_group` | Группа оружия. |
| `attack_bonus` | Бонус атаки от предмета. |
| `damage_bonus` | Бонус урона от предмета. |
| `finesse`, `two_handed` | Свойства. |
| `ranged`, `thrown` | Тип атаки. |
| `range_ft` | Дистанция (футы). |
| `required_level` | Требуемый уровень. |
| `uses/uses_max/uses_current`, `tick_mode`, `cooldown_*`, `tick_on_initiative` | Заряды/кулдауны. |

**LEGACY/резерв (не канон):** `damage_sml`, `damage_med`, `damage_type`, `hands`. В текущих сейвах пусто.

### Броня/щит

`armor_type` (`Light|Medium|Heavy|null`), `ac_bonus`, `ac_type` (`armor|shield|natural|deflection|misc`), `ac_max_dex` (лимит `dex_mod + dodge` для AC full/touch/parry; **не** для flat; берётся минимум из источников), `speed_penalty`, `skill_penalty`, `arcane_failure`, `mana_penalty`, `unprof_penalty`.

### Прочее по предмету

`hp`, `max_hp`, `hardness`, `passive_bonuses[]`, `activatable`, `activation_cost_spirit`, `activation_effects[]`, `activation_duration`, `activated`, `base_slots`, `gray`, `enchants[]`, `unload_bonus`, `order`, `price`, `weight`, `weight_type`, `qty`, `desc`, `icon_b64`.

## 4. `attacks[]` — поля Attack

- `name`, `use_bab`, `stat`, `extra_bonus`, `manual_bonus`.
- **Урон: канон — `damage_dice`** (напр. `"6d6"`). (У Item — `damage`, у Attack — `damage_dice`. Это **разные** поля.)
- `damage_stat`, `damage_mult`, `damage_stat_auto`, `finesse`, `two_handed`, `ranged`, `thrown`.
- `from_item`: UUID из `items{}` или `null`. **FK.** При отсутствии предмета — не падать, показывать «предмет удалён».
- `proficiency`, `master_ability`, `master_ability_id` ∈ `{"", "master_reroll", "master_no_attack_tag", "master_full_balance"}`.
- `show_on_panel`, `uses*`, `tick_mode`, `cooldown_*`, `tick_on_initiative`, `order`.
- `source` ∈ `{training, loot, race, class, quirk, manual}`.

## 5. `proficiencies.weapons[].bonuses[]` — слоты перков владения

Формат: `{ "slot": int, "id": str }`. `slot` — индекс слота, `id` — идентификатор перка (напр. `spec_parry_1`, `spec_hardness_30`). **Пока тестим** — включено в схему; боты **не пересчитывают** из них бонусы, пока подсистема не описана (см. CONTRACT.md §4). **Реестр допустимых `id` — T24 DONE (v12):** `WEAPON_BONUS_CATALOG` в `character.py` (ключи `spec_*`/`expert_*`/`master_*`). Валидация — в `purchases.set_weapon_bonuses`.

## 5.1. `injuries[]` — поля Injury (T46)

`name`, `severity` ∈ `{light|medium|heavy|custom}`, `heal_rating` (int ≥ 0), `desc`, `uses`, `uses_max`, `uses_current`, `tick_on_initiative`, **`active` (bool, T46)** — включён ли эффект, **`effects[]` (T46)** — постоянные бафы/дебафы травмы.

**Правило (T46):** травма с `active == True` в «Ситуативно» рендерится как постоянный баф (галочка вкл/выкл), эффекты `effects[]` применяются в `situational_bonus(...)`. Тик `tick_on_initiative` — отдельно (в `tick_initiative`, блок «4) Травмы»).

## 5.2. `char_class.abilities[]` / `race.abilities[]` — поля AbilityDef (T48)

Базовые: `name`, `desc`, `uses`, `uses_current`, `uses_max`, `show_on_panel`, `tick_mode`, `cooldown_rounds`, `cooldown_current`, `tick_on_initiative`.

**Для бафов (T48):** `is_buff` (bool), `duration_rounds`, `duration_current`, `charges_max`, `charges_current`, `effects[]`, `on_activate_effects[]`. Если `is_buff == True` — способность шаблон `situational_bonuses` (видна в «Ситуативно» как кнопка `+ <Название>`).

## 5.3. `Feat` — поля (T-STANCE / T-FEAT-EFFECTS)

`name`, `desc`, `source`, `invested`, `link`, **`display_name`** (короткое имя для чипа), **`is_stance`** (bool), **`stance_effects[]`** (эффекты стойки, `$ref: Effect`), **`stance_blocks[]`** (что блокирует), **`effects[]`** (постоянные эффекты обычной черты, `$ref: Effect`).

## 5.4. `Effect` — поля (T-BONUS-TYPES-2 v18.4)

`target`, `value` (**number | string**, формула: `lvl`, `2*lvl`, `lvl+3`, `d4+1`, `2d6`, `str_mod`…`cha_mod`, `+ - * / ()`), **`bonus_type`** (enum из 20: `flat`, `alchemical`, `armor`, `circumstance`, `competence`, `deflection`, `dodge`, `enhancement`, `inherent`, `insight`, `luck`, `morale`, `natural`, `profane`, `racial`, `resistance`, `sacred`, `shield`, `size`, `trait`), `skill_name` (для `target='skill'`), `resource_name` (для `target='restore_resource'`).

**Все inline-эффекты** (`situational_bonuses[].effects`, `AbilityDef.effects`/`on_activate_effects`, `Injury.effects`, `Feat.effects`/`stance_effects`) — `$ref: "#/$defs/Effect"`. Один источник правды.

## 5.5. `settings` — поля (v15)

| Поле | Тип | Комментарий |
|---|---|---|
| `hide_portrait` | bool | **v15**: `True` = скрыть портрет в главном окне. Было `show_portrait` (инверсия смысла). |
| `visible_buttons` | object | GUI-конфиг видимости кнопок левого меню. |
| `hide_hints` | bool | T50: скрыть примечания в редакторах. |
| `hp_regen_per_tick` | int | T41: HP-реген за тик, `0` = выкл. |
| `buff_delete_on_zero` | bool | Удалять чип бафа на след. тике при `duration_current == 0`. |
| `confirm_chip_delete` | bool | Спрашивать перед удалением чипа бафа. |
| `catalogs_enabled` | array | T-CAT: список включённых каталогов. |
| `catalogs_items_disabled` | array | T-CAT: скрытые элементы. |
| `catalogs_mode` | enum | T-CAT: `whitelist` / `blacklist`. |
| `menu_spec` | object | Сохранённый спек меню. |
| `ui_layout_mode` | enum | **v16**: `classic` / `split` / `split_pinned`. Default `split`. |
| `window_open_mode` | enum | **v17**: `pointer` / `menu` / `center`. Default `menu`. |
| `pin_editor_to_menu` | bool | Привязывать окна к меню (магнит). |
| `close_prev_window` | bool | T-SPLIT-4: закрывать предыдущее окно. |
| `stance_chips` | array | T-STANCE: имена стоек в быстром доступе. |
| `chips_visible_enabled` | bool | T-CHIPS: включён ли фильтр. `false` = все, `true` = только из `chips_visible`. |
| `chips_visible` | array | T-CHIPS: id чипов, которые показывать (при `enabled = true`; пусто = ничего). |
| `chips_order` | array | T-CHIPS: порядок чипов (id). Drag&drop пишет сюда. |
| `alpha_menu` / `alpha_center` / `alpha_chips` / `alpha_log` / `alpha_chip_buttons` | int | T-ALPHA: 10..90. |

> `settings` — GUI-конфиг, **не данные персонажа**. Ботам-механикам не трогать.

## 5.6. Барабаны бонусов (T-BONUS-TYPES-2 v18.4)

`DND/modifiers.py` — единственный источник правды. `character.py` импортирует.

- `BONUS_TYPES` (20), `BONUS_TYPES_FLAT` (`flat`, `""`), `BONUS_TYPES_ROLL` (15, без `armor/deflection/dodge/natural/shield`), `BONUS_TYPES_CMD`.
- `apply_bonus_type(bonuses)`:
  - `flat`/`""` → сумма;
  - остальные → побеждает больший по модулю (`bonus_max` vs `penalty_max`), равны → 0;
  - неизвестный тип → `flat`.
- `size_mod = size_index − Medium_index`. CMB/CMD: `+size_mod`. Атаки: `−size_mod`.
- `dodge` и `dex_mod` — складываются, ограничены `ac_max_dex` (минимум из источников: броня/щит/перегруз).
- `speed_mult` — `[DEPRECATED]`, не применяется (`T-REMOVE-SPEED-MULT`).
- `random` — Mersenne Twister (stdlib), для d20 достаточно.

## 5.7. Четыре вида AC (T-BONUS-TYPES-2 v18.4)

| Вид | Формула |
|---|---|
| **AC full** | 10 + dex_mod(≤ac_max_dex) + equipment.armor_ac + equipment.shield_ac + natural_armor + ac_bonus + ac_misc + барабан(20) |
| **AC touch** | 10 + dex_mod(≤ac_max_dex) + барабан(`AC_TOUCH_TYPES`). Игнор: natural, parrying, armor, shield |
| **AC flat** | 10 + барабан(`BONUS_TYPES − {dodge}`). Без dex_mod |
| **AC parry** | 10 + dex_mod(≤ac_max_dex) + parrying + equipment.shield_ac + natural_armor + ac_bonus + ac_misc + барабан(`BONUS_TYPES − {armor}`). armor из Effect — игнор |

**`AC_TOUCH_TYPES`** = `flat, deflection, dodge, insight, morale, competence, luck, circumstance`.
**`AC_FLAT_TYPES`** = `BONUS_TYPES − {dodge}`.
**`AC_PARRY_TYPES`** = `BONUS_TYPES − {armor}`.

## 5.8. Единый шаблон эффектов (T-EFFECTS-UI v18.5)

`DND/modifiers.py` — `EFFECTS_DEFAULTS` (19 полей): `effects`, `on_activate_effects`, `duration_rounds`, `duration_current`, `charges_max`, `charges_current`, `charges_tick_mode`, `cooldown_rounds`, `cooldown_current`, `tick_mode`, `tick_on_initiative`, `permanent`, `keep_at_zero`, `is_buff`, `show_on_panel`, `allow_toggle`, `enabled`, `blocks`, `is_stance`.

`apply_effects_defaults(obj)` — `setdefault` для **всех** полей (для `Feat` / `Injury` / `AbilityDef`).

**UI:** `DND/gui_effects.py` — `render_effects_list`, `apply_effects_list`, `render_temporal_fields`, `apply_temporal_fields`.

**Активация:** `Character.activate_feat_buff(feat_idx)` / `activate_injury_buff(injury_idx)` — копируют объект в `situational_bonuses`.

**Цели (`max_*`):** `max_hp`, `max_mana`, `max_balance`, `max_spirit`, `max_resource`, `max_pain_threshold` — влияют на потолки (T-MAX-STATS).

**`blocks[]`:** список имён блокируемых функций (T-BLOCKS-EXPANDED). Одна механика `is_blocked(name)`. Валидные имена — реестр `BLOCKABLE` в `character.py` (напр. `ac`, `attack`, `restore_hp`, `balance_restore`). `_check.py` проверяет, что каждое имя ∈ `BLOCKABLE`.

## 5.9. Чипы (T-CHIPS v18.6, v1.0)

**Архитектура:** `DND/chips.py` (дескрипторы) + `DND/gui_chips.py` (рендер). Без tkinter в `chips.py`.

**`ChipSpec`** (единый формат): `id`, `kind`, `label`, `cur`, `max`, `color`, `tip`, `icon`, `group`, `widgets`, `edit`, `data`.

**`chips.collect_all(c)`** — все доступные чипы (12 источников): `_resources`, `_abilities`, `_items`, `_attacks`, `_buffs`, `_feats`, `_lenses`, `_spells`, `_quests`, `_overload`, `_comfort`, `_stances`.

**`id`** — стабильный ключ: `kind:name` (напр. `attack:Меч`, `buff:Окаменение`, `spell:Огненный шар`), `item:<uuid>`, фиксированные (`hp`, `ac_full`, `bp`, `mana`, `spirit`, `balance`, `slot_<N>`, `stance`). Дубли — `#1`, `#2` (`_dedup`).

**`gui_chips.py`:** `CHIP_REGISTRY` + `render_chip(app, spec)` + `@register(kind)` (12 типов: `resource`, `ability`, `item`, `attack`, `buff`, `feat`, `lens`, `spell`, `quest`, `overload`, `comfort`, `stance`).

**Панель:** `rebuild_resources_panel` → `chips.collect_all` → фильтр (`chips_visible_enabled` / `chips_visible`) → сортировка (`chips_order`) → `render_chip`.

**Drag&drop:** за имя чипа. Призрак (`Toplevel`, `-alpha 0.75`) + линия-индикатор (`#4af`, 2px). `_preview_insert` + `_reorder`. `chips_order` сохраняется. `reflow_chips` **не** при drag (без мигания).

**Правый клик:** на ресурсах → `gui_dialogs.ask_int` (`bind_edit_number`).

**Кнопки в настройках (`edit_settings`):** «👁 Спрятать/показать все» (`chips_visible_enabled` toggle), «🔄 Сбросить все чипы» (`chips_order = []`, `chips_visible = []`, `chips_visible_enabled = false`).

**Чистка:** `chips.clean_order(c)` при загрузке (4 места в `gui_file_ops.py`).

**План v1.1 (T-SPLIT-3.2):** `gui_desktop.py` (`pywin32` + `WM_NCHITTEST`), `chips_positions`, `chips_drag_mode`.

## 6. Открытые вопросы (TBD)

1. ~~`parrying` — это `combat.cmd` или отдельное поле?~~ **Решено (T25):** отдельное поле. `parrying` ≠ `combat.cmd`.
2. `master_ability_id` — реестр из 3 значений.
3. ~~`bonuses[].id` — реестр не заведён.~~ **Решено (T24, v12):** `WEAPON_BONUS_CATALOG`.
4. `char_class.abilities[]`, `race.abilities[]` — структура `AbilityDef`.
5. `spell_slots` — пока свободный словарь `{круг: кол-во}`.
6. ~~`bonus_type` — enum~~ **Закрыто (T-BONUS-TYPES-2, v18.4):** 20 значений, `DND/modifiers.py`.