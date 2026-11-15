# LOG
ver: v18.6 (2026-11) | prev: v18.5
linked: TECH v18.6, schema v2, CONTRACT v1, GLOSSARY, PROJECT_MAP.
statuses: OPEN / DOING / DONE / BLOCKED / CANCELLED.

# TASKS (T-серия)
T1-T51: DONE (кроме T13, T15 OPEN, T37, T49, T51 CANCELLED).
T57, T58 DONE.
T-CAT, T-P2, T-UI, T-SPELL, B5 DONE (v14).

# (v18.6) T-CHIPS (DONE) — v1.0
**Архитектура чипов:**
- **`DND/chips.py`** — `ChipSpec` (единый формат), `collect_all(c)` (все чипы), `_*` (по источникам: `_resources`, `_abilities`, `_items`, `_attacks`, `_buffs`, `_feats`, `_lenses`, `_spells`, `_quests`, `_overload`, `_comfort`, `_stances`, `_buttons`, `_rest`), `_make_id(kind, name, idx)` + `_dedup(ids)`, `clean_order(c)`.
- **`DND/gui_chips.py`** — `CHIP_REGISTRY` + `render_chip(app, spec)`, `@register(kind)` для 12 типов (`resource`, `ability`, `item`, `attack`, `buff`, `feat`, `lens`, `spell`, `quest`, `overload`, `comfort`, `stance`). Drag&drop, отдых, flow-контейнер.
- **`gui.py`** — 8 методов → обёртки на `gui_chips` (`_rebuild_resources_panel`, `_init_flow_container`, `_add_chip`, `_reflow_chips`, `_maybe_remove_buff`, `_rebuild_rest_panel`, `_do_short_rest`, `_do_long_rest`). `_rebuild_resources_panel_body` удалён.

**Функционал v1.0:**
- **Все элементы** (ресурсы, абилки, предметы, атаки, бафы, черты, линзы, заклинания, квесты, перегрузка, комфорт, стойка) → `ChipSpec` → `render_chip`.
- **Кнопки (`_buttons`)** — базовые действия (урон, лечение, temp HP, баланс, инициатива, ОТ, боль, мораль, ситуация, обновить). `color_fn` (динамика: ОТ/боль/мораль), `label_fn` (актуальный текст). Светло-серые (`#5a5a5a`), зелёные/синие/красные по смыслу.
- **Отдых (`_rest`)** — короткий (`#4a7` зелёный) / длинный (`#855` красный). `btn:rest` (дубль) удалён.
- **Цвета (`chips_colors`)** — `settings.chips_colors: {id: "#hex"}`. В `edit_settings`: выпадающий список чипов + поле цвета + «Применить» / «Сбросить». Перекрывает `spec["color"]`.
- **Drag&drop:** призрак (полупрозрачный Toplevel) + линия-индикатор (`#4af`, 2px), `_find_target` (точное/ближайшее), `_preview_insert`, `_reorder`. Без мигания (`reflow_chips` не при drag). `settings.chips_order`.
- **Фильтр:** `settings.chips_visible_enabled` + `chips_visible`.
- **Правый клик** на ресурсах → `gui_dialogs.ask_int` (`bind_edit_number`).
- **Кнопки в настройках:** «👁 Спрятать/показать все», «🔄 Сбросить все чипы» (`edit_settings`).
- **`chips.clean_order(c)`** — при загрузке (4 места в `gui_file_ops`: `load_or_new`, `new_character`, `open_character`, `import_character`).
- **Ч / О / Б** — toggle (первый клик с фокусом, повторный — свернуть).

**Схема:**
- `settings.chips_visible_enabled` (bool, default false).
- `settings.chips_visible` (array, default []).
- `settings.chips_order` (array, default []).
- `settings.chips_colors` (object, default {}) — `{id: "#hex"}` (кастомные цвета).

**Проверки:** `_check.py` — 39 (без изменений).

# (v1.1) T-SPLIT-3.2 — Desktop overlay (PLANNED)
- **Решение:** `pywin32` + `WM_NCHITTEST` (не `-transparentcolor`, не PySide6).
- **Причины:** надёжнее `-transparentcolor` (не глючит, не искажает цвет); точечный контроль (клик сквозь фон, клик в чип); не требует переписывать GUI (в отличие от PySide6); родной механизм Windows.
- **Архитектура:**
  - **Окно 1 (фон):** fullscreen, `WS_EX_LAYERED | WS_EX_TRANSPARENT`, `LWA_ALPHA=0` — невидимо, клики сквозь.
  - **Окно 2 (чипы):** `Toplevel` без рамки, `topmost`, чипы через `place(x, y)`.
  - **`WM_NCHITTEST`:** `HTTRANSPARENT` (пусто) / `HTCLIENT` (чип).
  - **Позиции:** `settings.chips_positions: {id: [x, y]}`.
  - **Режим:** `settings.chips_drag_mode: bool` — false = только клики; true = drag.
  - **Трей:** меню/чарник скрыты, только чипы на экране.
- **Риски:** topmost перекрывает диалоги (временно `topmost=False`); много Toplevel — тормоза (решение: один оверлей + `place`).

# (v18.5) T-EFFECTS-UI + T-MAX-STATS + T-BLOCKS-EXPANDED (DONE)
- **`T-MAX-STATS`** — `max_hp` / `max_mana` / `max_balance` / `max_spirit` / `max_resource` / `max_pain_threshold` в `VALID_SIT_TARGETS`, `TARGET_NAMES`, `character.py`.
- **`T-BLOCKS-EXPANDED`** — `blocks[]` — список имён блокируемых функций (реестр `BLOCKABLE`); `is_blocked(name)`; список в `gui_effects`.
- **`DND/gui_effects.py`** — единый UI эффектов: ...
- **`modifiers.py`** — `EFFECTS_DEFAULTS` (19 полей) + `apply_effects_defaults` (единый шаблон для feats/injuries/abilities).
- **`character.py`** — `activate_feat_buff` / `activate_injury_buff`; `load()` — один цикл `apply_effects_defaults`.
- **`gui_editors.py`** — `_feat_dialog` / `_ab_edit` / `_race_abil_edit` → `gui_effects`. `Feat.effects` / `Feat.blocks` (вместо `stance_effects` / `stance_blocks`).
- **`gui_combat.py`** — `_edit_buff_dialog` → `gui_effects`. `action_situational` — `injuries[].enabled` (вместо `active`). «Черты-бафы» / «Травмы-бафы» (активация).
- **`gui.py`** — тултипы через `gui_effects` (русский `bonus_type`).
- **`_check.py`** — +2 (`check_effects_ui`, `check_effects_ui_expanded`). Всего **39**.

# (v18.4) T-BONUS-TYPES-2 (DONE)
- **`DND/modifiers.py`** — единственный источник правды для барабанов. `BONUS_TYPES` (20), `BONUS_TYPES_ROLL` (15), `BONUS_TYPES_CMD`, `AC_TOUCH_TYPES`/`AC_FLAT_TYPES`/`AC_PARRY_TYPES`/`AC_FULL_TYPES`, `apply_bonus_type`, `size_mod`/`size_mod_attack`.
- **4 вида AC:** full / touch / flat / parry. `ac_max_dex` (минимум из источников) ограничивает `dex_mod + dodge`.
- **Правило «бонус vs штраф одного типа»:** побеждает больший по модулю, равны → 0. `flat`/`dodge` — складываются.
- **`bonus_type` enum 20** в `$defs.Effect`. Inline-эффекты → `$ref: Effect` (один источник правды).
- **`Feat.effects`** — в схеме (T-FEAT-EFFECTS, было в коде с v18.2).
- **`size_mod`**: Medium=0, Small=−1 (CMB/CMD) / +1 (атака), Large=+1 (CMB/CMD) / −1 (атака).
- **`speed_mult`** — `[DEPRECATED]`, код не применяет.
- **`gui_alphabet.BONUS_TYPE_NAMES`** (20) + `assert` с `modifiers.BONUS_TYPES`.
- **`gui_editors._feat_dialog`** — `OptionMenu` типов через `*BONUS_TYPE_NAMES.keys()` (20). Тултип эффектов — русские подписи.
- **`_check.py`**: +1 проверка (`check_bonus_types`, 13 подпроверок). Всего **37**.

# (v18.3) UI/UX & BUGFIX (DONE)
- **T-ESCAPE-CLOSE:** Все окна (редакторы, чипы, диалоги ввода, результаты) теперь закрываются по нажатию `Escape`. Для окон сплита (Меню, Чарник) `Escape` скрывает их (уводит в трей/сворачивает).
- **T-TRAY-FIX:** Полностью починена работа с треем. Клик по иконке трея («Меню», «Чарник», «Быстрый доступ») теперь открывает окна с первого раза. Убрана лишняя логика проверки видимости, которая блокировала показ.
- **T-SPLIT-BUTTONS:** Починены кнопки навигации в сплите (левая панель). Теперь они работают с первого клика. Добавлена кнопка «О» (открыть последнее окно редактора). Кнопка «Ч» всегда возвращает в главный вид (статы).
- **T-TOOLTIPS:** Добавлены тултипы для эффектов в редакторе черт, абилок расы/класса. Тултипы в чарнике теперь тоже показывают списки эффектов (например, `+4 инициатива`), а не только описание.
- **T-INITIATIVE-BREAKDOWN:** Инициатива в чарнике теперь показывает источники (как спасброски и скорость). В скобках перечисляются: ЛОВ, черты, стойки и бафы. Для стоек и черт берется `display_name` (короткое имя).

# (v18.2) BUGFIX & GUI (DONE)
- **T-WINDOW-FIX-DEICONIFY:** Исправлен баг, когда диалоги (например, «Выход») мигали и исчезали. В `gui_windows.open_window` добавлен принудительный `deiconify()`.
- **T-FILEOPS-DIALOGS:** Заменены `tk.Toplevel(app.root)` и `parent=app.root` на `get_dialog_parent()` / `open_window` в `gui_file_ops.py`. Диалоги (Выход, Импорт, Экспорт) больше не улетают в левый угол.
- **T-STANCE-CORE-V2:** Доработана логика стоек.
  - Чип стойки в панели ресурсов теперь выглядит как `[Стойка ▼] [On/Off]`.
  - В редакторе черт стойки отображаются в общем списке с тегом `[Стойка]`.
  - В схему добавлено поле `display_name` (короткое имя для чипа).
- **T-FEAT-EFFECTS:** Обычные черты теперь могут давать постоянные эффекты (`feats[].effects`), как предметы. В редакторе черт появился блок эффектов.
- **T-BONUS-TYPES:** В схему `Effect` добавлено поле `bonus_type` (flat, dodge, armor и т.д.).
  - `character.py`: добавлен метод `_ac_situational_by_type`, который группирует бонусы AC и берет максимум из одинаковых типов (кроме flat).
  - `gui_editors.py`: в редакторы стоек и черт добавлена третья колонка «Тип» (выпадающий список).

# (v18.1) T-SPLIT-4 (Окна-спутники) — DONE
- **Причина:** `winfo_pointerx` у невидимого Toplevel даёт 0 (в левый угол), даже с `update_idletasks` и `_default_root`.
- **Решение:** отказаться от `at_pointer`. Все окна (редакторы, чипы) открываются как `Toplevel`, привязанный к `menu_win` (справа от него). Двигаются вместе с меню.
- **Закрытие:** новое окно закрывает (или скрывает) предыдущее. Настройка `settings.close_prev_window` (default True).
- **Стойки:** отдельная кнопка «＋ Добавить стойку» в «Чертах» (через `_feat_dialog(is_stance=True)`).
- **Отменено:** T-CHIPS-POINTER (at_pointer).

# (v18) T-SPLIT-3 + T-CHIPS (начало) — OPEN
**DONE (v18):**
- **T-ICON** — `WP.png` → трей (`gui.py._make_tray_icon`).
- **T-SCHEMA-V18** — схема v18: `is_stance`, `stance_effects`, `stance_blocks`, `active_stance`, `action_log[]` (20), `AbilityDef.source`/`invested`, `settings.alpha_*` (10..90), `settings.stance_chips`.
- **T-STANCE-CORE** — `character.py`: `feats_for_ui`, `stances`, `stance_effects`, `stance_blocks`, `set_active_stance`, `log_action`, `revert_action`. `situational_bonus` / `is_blocked` учитывают `active_stance`.
- **T-FEAT-STANCE-UI** — `gui_editors.edit_feats` (фильтр `is_stance`), `_feat_dialog` (галочка «Это стойка»).
- **T-WINDOW-FIX** — `gui_shared.center_window(..., modal=False)` (без `grab_set` — висел в сплите), `_visible_root(parent)`, `at_pointer=True` (окно рядом с мышкой + clamp). `create_dialog` → `center_window(at_pointer=True)`.

**OPEN (v18, не начато):**
- **T-SPLIT-3.1** — `gui_tray.py` (tray + `pystray`; отдельный файл — легитимно, tray-поток).
- **T-SPLIT-3.2** — `gui_chips.py` (чипы + панель ресурсов + отдых) — **частично DONE в v18.6** (см. выше), desktop overlay — v1.1.
- **T-SPLIT-3.3** — `gui_canvas.py` (отрисовка чарника + тултипы).

**PLAN (v18):**
- **T-SPLIT-3.4** — `gui_levelup.py` (отложено, ~30 строк).
- **GUI-EFFECTS-REFACTOR** — вынос UI списков эффектов в `gui_effects.py`.

# (v17) T-SPLIT-VIEW (Этап 2) — DONE
**T-SPLIT-OVERIDEREDIRECT (DONE):**
- **Решение:** `overrideredirect(False)` + делегирование.
- `gui.py` → `app._split.show_editor()` / `show_main()`.
- `destroy()` заменен на `withdraw()`.
- **Результат:** кнопки меню работают, чарник открывается, `TclError` исчез.

**T-SHOP-REST (OPEN):**
- «Каталог» и «Восстановление» открываются как отдельные окна (патч `get_dialog_parent`).
- **TODO:** переделать в `show_editor` (внутри чарника).

# TODO / NEXT (обновлено v18.6)
- **T-CHIPS-BUTTONS (v1.0):** DONE. `_buttons` + `_rest` + `chips_colors`.
- **T-SPLIT-3.2 (v1.1):** Desktop overlay — `pywin32` + `WM_NCHITTEST` (см. блок v1.1).
- **T-REMOVE-SPEED-MULT** — выпилить `speed_mult` из `VALID_SIT_TARGETS` / `TARGET_NAMES` / схемы.
- **T-BONUS-CMD** — `_cmd_situational_by_type` + `BONUS_TYPES_CMD` (полная формула CMD).
- **T-CMD-REWORK** — убрать боль/мораль из `cmd_total`.
- **T-DAMAGE-TYPES** — типы урона + сопротивления/уязвимости.
- **T-SPLIT-3.1** `gui_tray.py` (tray + pystray).
- **T-SPLIT-3.3** `gui_canvas.py` (отрисовка чарника + тултипы).
- **T-SHOP-REST** — после `gui_chips`.
- **T-EXIT-BTN** — кнопка «Выход» в `gui_buttons.py`.
- **T-OPT-DIALOGS-REFACTOR** — `create_dialog` во всех `gui_*.py`.
- UI-редактор меню (`MENU_SPEC`).
- Прозрачность (`settings.alpha_*` — уже в схеме v18, нужен UI-ползунок).
- Чипы на экране (`settings.chips_on_tray`).

# VTT (Ф6-Ф7) — CANCELLED.

# HISTORY (сжато)
v13-v14 (2026-11): баги починены, каталоги, чипы, схемы v2.
v15 (2026-11): T-SPLIT, T-ALT-TAB, T-TRAY, T-DRAG, T-COPY, T-PORTRAIT, T-CHECK.
v16 (2026-11): T-SPLIT-VIEW (Этап 1), 3 окна, `create_dialog`.
v17 (2026-11): **T-SPLIT-VIEW (Этап 2) DONE.** Делегирование, `withdraw`, `overrideredirect(False)`. `TclError` исчез.
v18 (2026-11): **T-STANCE, T-FEAT-EFFECTS, T-BONUS-TYPES.** Починены диалоги (Выход). Чип стоек. Добавлен `bonus_type`.
v18.3 (2026-11): **T-TRAY-FIX, T-SPLIT-BUTTONS, T-TOOLTIPS, T-ESCAPE-CLOSE.** Инициатива с источниками.
v18.4 (2026-11): **T-BONUS-TYPES-2.** `DND/modifiers.py`, 4 вида AC, enum `bonus_type` (20), `Feat.effects`, inline → `$ref`, `size_mod`, `speed_mult [DEPRECATED]`.
v18.5 (2026-11): **T-EFFECTS-UI, T-MAX-STATS, T-BLOCKS-EXPANDED.** gui_effects.py, EFFECTS_DEFAULTS, max_* (потолки), blocks (do/deny/res).
v18.6 (2026-11): **T-CHIPS (v1.0).** `chips.py` + `gui_chips.py`, `ChipSpec`, `collect_all`, `CHIP_REGISTRY`, drag&drop (призрак + линия), `chips_visible_enabled` / `chips_visible` / `chips_order`, `clean_order`, кнопки в настройках, Ч/О/Б toggle.
v1.0 (2026-11): **T-CHIPS-BUTTONS.** `_buttons` (базовые кнопки, `color_fn` / `label_fn`), `_rest` (короткий / длинный), `chips_colors` (кастомные цвета), `_render_button` (`color_fn`), `btn:rest` удалён.
v1.1 (план, 2026-11): **T-SPLIT-3.2 Desktop overlay.** `pywin32` + `WM_NCHITTEST`, `chips_positions`, `chips_drag_mode`.

# BLOCKED
- **Нет.** T-SPLIT-OVERIDEREDIRECT решён.