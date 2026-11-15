# TECH
ver: v1.0 (2026-11) | prev: v18.6
main: WIPEFINDER = чарлист-справка D&D (Python + tkinter).
priority: PANEL > EDITOR > CATALOGS > SHOP.
read: PROJECT_MAP → CONTRACT → PROMPT → schema → GLOSSARY → TECH → code.

# 0. RULES
- encoding: VS Code only (Ctrl+A,C,V,S). no PowerShell for saving.
- patches: find X → replace Y. never rewrite whole file.
- numeric GUI fields: _safe() / _gi().
- new fields: schema → GLOSSARY → code.
- T-WINDOW: все новые окна — Toplevel(modal=False), transient(parent), topmost — галочка, не grab_set.
- Escape: все окна закрываются по Escape (через open_window).

# 0.1. ROADMAP (phases)
F1-F8: DONE (v10-v16). (баги починены, вынос gui.py)
F9 DONE (v17): **T-SPLIT-VIEW (этап 2)**. `withdraw` вместо `destroy`, `overrideredirect(False)`.
F10 DONE (v18): **T-STANCE, T-LOG, T-ALPHA, T-BONUS-TYPES**.
  - Стойки: `feats[].is_stance`, `display_name`, `stance_effects`, чип в панели ресурсов.
  - Черты: получили возможность давать постоянные эффекты `feats[].effects`.
  - AC: группировка по типам (dodge, armor, flat и т.д.), `bonus_type` в `Effect`.
F11 DONE (v18.3): **T-SPLIT-4** (Окна-спутники).
  - Окна редакторов привязаны к `menu_win` (справа от него).
  - Кнопки Ч/О/Б/Л в левой панели сплита.
  - Починены трей, тултипы, Escape.
F12 DONE (v18.4): **T-BONUS-TYPES-2**. `DND/modifiers.py` (барабаны: `BONUS_TYPES`, `AC_*_TYPES`, `apply_bonus_type`, `size_mod`/`size_mod_attack`), 4 вида AC, `ac_max_dex`, enum `bonus_type` (20), `Feat.effects`, inline → `$ref: Effect`.
F14 DONE (v18.5): **T-EFFECTS-UI + T-MAX-STATS + T-BLOCKS-EXPANDED**. `DND/gui_effects.py`, `EFFECTS_DEFAULTS`, `apply_effects_defaults`, `deny:*` (бонусы), `max_*` (потолки), `blocks` (действия/ресурсы).
F15 DONE (v18.6): **T-CHIPS**. `DND/chips.py` (`ChipSpec`, `collect_all`, `_*`, `_make_id`, `_dedup`, `clean_order`), `DND/gui_chips.py` (`CHIP_REGISTRY`, `render_chip`, `@register` 12 типов, drag&drop, отдых), `gui.py` делегирует. `settings.chips_visible_enabled` / `chips_visible` / `chips_order`. Кнопки в настройках, Ч/О/Б toggle.
F17 DONE (v1.0): **T-CHIPS-BUTTONS**. `chips._buttons` (базовые кнопки, `color_fn` / `label_fn`), `chips._rest` (короткий / длинный), `chips_colors` (кастомные цвета), `_render_button` (`color_fn`). `btn:rest` удалён.
F16 PLANNED (v1.1): **T-SPLIT-3.2 Desktop overlay** (`pywin32` + `WM_NCHITTEST`). `settings.chips_positions`, `chips_drag_mode`. `DND/gui_desktop.py`.

# 0.2. ONBOARDING
Перед задачей — `PROMPT.md` (5–10 вопросов по одному, с рекомендацией). Не спрашивать то, что в документации.

# 1. TASKS

## A (DONE): T1-T4.
## B panel: T8, T9, T9.1, T17, T18, T26 (DONE).
## C (DONE): T5-T7, T19.
## D catalogs: T10-T12 (DONE).
## E minor: T13 OPEN, T15 OPEN. T14, T16 DONE.
## F contract: T20-T25 (DONE).
## G logic: T27-T36, T38-T48, T50, T57, T58 (DONE).
  T37 CANCELLED, T49 CANCELLED, T51 CANCELLED.

# (v15) T-SPLIT
- Вынос gui_app_config.py, gui_media.py, gui_file_ops.py, gui_buttons.py, gui_menu.py.
- T-ALT-TAB, T-TRAY, T-DRAG, T-COPY, T-PORTRAIT, T-CHECK DONE.

# (v16) T-SPLIT-VIEW (Этап 1)
- 3 окна (меню/чарник/чипы). `gui_split.py`.
- `app.get_dialog_parent()`, `gui_shared.create_dialog()`.
- T-OPT-EDITORS, T-OPT-DIALOGS, T-TRAY, T-EXIT DONE.

# (v17) T-SPLIT-VIEW (Этап 2) — DONE
- **Проблема:** `overrideredirect(True)` + `withdraw` → `deiconify` не работает на Windows (окно «мигает» и не выходит наверх). Ошибка `bad window path name` при перерисовке.
- **Решение:**
  1. `overrideredirect(False)` + `attributes("-toolwindow", True)` для всех окон сплита.
  2. **Делегирование:** `gui.py` вызывает `app._split.show_editor()` и `app._split.show_main()`, если сплит активен.
  3. **Никаких `destroy()`** — только `withdraw()`.
  4. `SplitView` имеет свой `_show_editor_split`, который рисует в `self.app.view_edit`.
- **Итог:** кнопки меню работают, `TclError` исчез.

# (v18.3) UI/UX & BUGFIX (DONE)
- **T-TRAY-FIX:** Полностью починена работа с треем. Клик по иконке трея («Меню», «Чарник», «Быстрый доступ») теперь открывает окна с первого раза. Убрана лишняя логика проверки видимости, которая блокировала показ.
- **T-SPLIT-BUTTONS:** Починены кнопки навигации в сплите (левая панель). Теперь они работают с первого клика. Добавлена кнопка «О» (открыть последнее окно редактора). Кнопка «Ч» всегда возвращает в главный вид (статы).
- **T-TOOLTIPS:** Добавлены тултипы для эффектов в редакторе черт, абилок расы/класса. Тултипы в чарнике теперь тоже показывают списки эффектов (например, `+4 инициатива`), а не только описание.
- **T-INITIATIVE-BREAKDOWN:** Инициатива в чарнике теперь показывает источники (как спасброски и скорость). В скобках перечисляются: ЛОВ, черты, стойки и бафы. Для стоек и черт берется `display_name` (короткое имя).
- **T-ESCAPE-CLOSE:** Все окна (редакторы, чипы, диалоги ввода, результаты) теперь закрываются по нажатию `Escape`.

# (v18.6) — T-CHIPS — DONE
- **`DND/chips.py`** — `ChipSpec(id, kind, label, cur, mx, color, tip, icon, group, widgets, edit, data)`, `collect_all(c)`, `_*` (14 источников: `_resources`, `_abilities`, `_items`, `_attacks`, `_buffs`, `_feats`, `_buttons`, `_rest`, `_quests`, `_spells`, `_overload`, `_comfort`, `_lenses`, `_stances`), `_make_id(kind, name, idx)`, `_dedup(ids)`, `clean_order(c)`.
- **`DND/gui_chips.py`** — `CHIP_REGISTRY`, `render_chip(app, spec)`, `@register(kind)` (13 типов: `resource`, `ability`, `item`, `attack`, `buff`, `feat`, `lens`, `spell`, `quest`, `overload`, `comfort`, `stance`, `button`), `rebuild_resources_panel` (фильтр + сортировка), drag&drop (призрак + линия, `_drag_start` / `_drag_move` / `_drag_end` / `_preview_insert` / `_reorder`), отдых, flow-контейнер, `_render_button` (`color_fn` / `label_fn`).
- **`gui.py`** — 8 методов → обёртки на `gui_chips`; `_rebuild_resources_panel_body` удалён; `_rebuild_rest_panel` удалён; `update_combat_status` (no-op).
- **`gui_file_ops.py`** — `chips.clean_order(c)` в 4 местах (`load_or_new`, `new_character`, `open_character`, `import_character`).
- **`gui_editors.py`** — `edit_settings`: блок «Чипы» (галочка `chips_visible_enabled`, кнопки «👁 Спрятать/показать все», «🔄 Сбросить все чипы»), блок «Цвета чипов» (выпадающий список + поле + «Применить» / «Сбросить»).
- **`gui_split.py`** — Ч / О / Б — toggle (первый клик с фокусом, повторный — свернуть). `_build_rest` удалён.
- **`gui_combat.py`** — `build_combat_panel` → `pass` (кнопки в `chips._buttons`).
- **`gui_rest.py`** — галочки `show_rest_short` / `show_rest_long` → `app._refresh()` (чипы отдыха).
- **Схема:** `settings.chips_visible_enabled`, `chips_visible`, `chips_order`, `chips_colors`.
- **Проверки:** `_check.py` — 39 (без изменений).

# (v18.5) — T-EFFECTS-UI + T-MAX-STATS + T-BLOCKS-EXPANDED (DONE)
- **`DND/gui_effects.py`** — единый UI (список эффектов + временные поля).
- **`modifiers.py`** — `EFFECTS_DEFAULTS` + `apply_effects_defaults`.
- **`character.py`** — `activate_feat_buff` / `activate_injury_buff`.
- **`gui_editors.py`** / **`gui_combat.py`** — через `gui_effects`.
- **`gui.py`** — тултипы (русский `bonus_type`).
- **`T-MAX-STATS`** — `max_hp` / `max_mana` / `max_balance` / `max_spirit` / `max_resource` / `max_pain_threshold` в `VALID_SIT_TARGETS`, `TARGET_NAMES`, `character.py`.
- **`T-BLOCKS-EXPANDED`** — `blocks[]` — список имён блокируемых функций (реестр `BLOCKABLE`); `is_blocked(name)`.

# (v18.4) — T-BONUS-TYPES-2 (DONE)
- **`DND/modifiers.py`** — единственный источник правды для барабанов. `BONUS_TYPES` (20), `BONUS_TYPES_FLAT`, `BONUS_TYPES_ROLL` (15), `BONUS_TYPES_CMD`, `AC_TOUCH_TYPES`/`AC_FLAT_TYPES`/`AC_PARRY_TYPES`/`AC_FULL_TYPES`, `apply_bonus_type(bonuses, allowed)`, `size_mod`, `size_mod_attack`.
- **4 вида AC:** full / touch / flat / parry. `ac_max_dex` (минимум из источников) ограничивает `dex_mod + dodge`.
- **`bonus_type` enum 20** в `$defs.Effect`. Inline-эффекты → `$ref: Effect` (5 мест).
- **`Feat.effects`** — в схеме (T-FEAT-EFFECTS, было в коде с v18.2).
- **`speed_mult`** — `[DEPRECATED]`, код не применяет.
- **Правило «бонус vs штраф одного типа»:** побеждает больший по модулю, равны → 0.

# (v18) — T-STANCE & T-BONUS-TYPES (DONE)
- **T-STANCE:** стойки теперь отображаются в общем списке черт с тегом `[Стойка]`. Создаются через кнопку «🗡 Добавить стойку». Имеют `display_name`, чип `[Стойка ▼] [On/Off]` в панели ресурсов.
- **T-FEAT-EFFECTS:** обычные черты получили блок `feats[].effects` (постоянные бонусы, как у предметов).
- **T-BONUS-TYPES:** В `Effect` добавлено поле `bonus_type` (flat, dodge, armor и т.д.). В `character.py` добавлен метод `_ac_situational_by_type`, который группирует бонусы AC и берет максимум из одинаковых типов. Без типа (flat) — складывается всегда.
- **Важно:** Счастливая атака (`target="lucky"`) не связана с типом бонуса `luck`.

# T-NEW (план)

## Срочные (v1.0)
- **T-CHIPS-BUTTONS:** **DONE (v1.0)**. `chips._buttons` (базовые кнопки, `color_fn` / `label_fn`), `chips._rest` (короткий / длинный), `chips_colors` (кастомные цвета), `_render_button` (`color_fn`). `btn:rest` удалён.
- **T-CATALOG-UI:** Доработать UI управления каталогами. Добавить возможность создавать/редактировать не только предметы, но и черты, стойки, заклинания, расовые/классовые абилки, бафы.

## v1.1 (desktop overlay)
- **T-SPLIT-3.2:** Desktop overlay (`pywin32` + `WM_NCHITTEST`). `DND/gui_desktop.py` (`DesktopView`), `settings.chips_positions` (`{id: [x, y]}`), `settings.chips_drag_mode` (bool). Один прозрачный Toplevel (фон) + один Toplevel с чипами (`place`). `HTTRANSPARENT` / `HTCLIENT`. Трей.

## Отложено (механика)
- **T-REMOVE-SPEED-MULT:** Выпилить `speed_mult` из `VALID_SIT_TARGETS`, `TARGET_NAMES`, схемы. Заменить на `speed` (сумма).
- **T-BONUS-CMD:** `_cmd_situational_by_type` + полная формула CMD (без armor/shield/natural/resistance, без боли/морали).
- **T-CMD-REWORK:** Убрать боль/мораль из `cmd_total` (по PF1). Оставить в `cmb_total`.
- **T-DAMAGE-TYPES:** Типы урона (fire, cold, slashing…) + сопротивления/уязвимости.

## Рефакторинг и чистота
- **T-OPT-DIALOGS-REFACTOR:** Заменить оставшиеся `tk.Toplevel` / `simpledialog` / `messagebox` на `open_window` и `gui_dialogs`.
- **T-SPLIT-3:** Продолжить резку `gui.py`:
  - 3.1 `gui_tray.py` (трей) — OPEN
  - 3.2 `gui_chips.py` — DONE (v18.6, кроме desktop)
  - 3.3 `gui_canvas.py` (отрисовка чарника) — OPEN
- **T-SPLIT-3.4:** Вынести `_do_level_up` в `gui_levelup.py`.
- **GUI-EFFECTS-REFACTOR:** DONE (v18.5).

## Каталоги и данные
- **Каталог ситуативных бафов:** Сделать список шаблонов бафов, которые можно включать одной кнопкой.
- **Каталог базовых стоек:** Добавить `base_stances.json` в `catalogs/feats/`.

## Механика (новые фичи)
- **T-ACTIONS:** Система Действий/Реакций (сейчас `actions=3` в базе, атаки=1, заклинания=2).
- **Enter везде:** Нажатие Enter в полях ввода (опыт, комфорт, статы, ресурсы) должно применять значение.
- **Раса в цене стата:** Галочка «стат кост» при покупке расовых абилок за тренировки.
- **Прозрачность:** Ползунки `settings.alpha_*` (сейчас есть в схеме, но нет UI).
- **Лог действий:** Визуализация `action_log` и кнопка реверса (отката) последнего действия.

## Оптимизация кода (общая идея, план)
> Цель: меньше повторяющегося кода, единые точки изменения, проще добавлять новое.
> Начинать с малого (1–2 шаблона), не «переписать всё».

### Идея 1. Универсальность галочек (плоские / групповые)
- `_on_flag(key, var, after)` — плоский bool → settings[key] = var.get(); after().
- `_on_group(dict_vars, settings_key, after)` — группа галочек → список/словарь.
- Список `_FLAGS = [(key, var, after), ...]` — источник правды.

### Идея 2. Универсальность числовых полей (`_on_number`)
- `Entry` + int → settings/combat. Применять на `<Return>`/`<FocusOut>`, не на каждый символ.
- Сократить try/except до одной функции.

### Идея 3. Универсальность кнопок категорий/списков
- Один `_button_row(parent, items, on_click, ...)` вместо ручных `tk.Button` в каждом редакторе.
- Где: `gui_shop`, `gui_catalogs`, `gui_inventory`, `gui_training`.

### Идея 4. Поиск других повторов (сделать до реализации)
- `Select-String` по проекту на повторяющиеся паттерны:
  - `try: int(...) except` (числа);
  - `tk.Button(... command=lambda` (кнопки);
  - `BooleanVar(` + `settings[` рядом (галочки);
  - `for ... in ...: ... .get()` (группы).