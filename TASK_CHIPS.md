# TASK_CHIPS.md — задачи по чипам (v1.0 DONE, v1.1 план)

> Читать после `PROJECT_MAP.md` → `CONTRACT.md`.
> Связано: `TECH.md §0.1` (F15 v18.6, F17 v1.0, F16 v1.1), `LOG.md` (блоки v18.6, v1.0, v1.1).

## 1. v1.0 — T-CHIPS + T-CHIPS-BUTTONS (DONE)

### 1.1 Архитектура

- **`DND/chips.py`** — `ChipSpec` (единый формат), `collect_all(c)` (14 источников), `_*` (`_resources`, `_abilities`, `_items`, `_attacks`, `_buffs`, `_feats`, `_buttons`, `_rest`, `_lenses`, `_spells`, `_quests`, `_overload`, `_comfort`, `_stances`), `_make_id(kind, name, idx)`, `_dedup(ids)`, `clean_order(c)`. Без tkinter.
- **`DND/gui_chips.py`** — `CHIP_REGISTRY` + `render_chip(app, spec)` + `@register(kind)` (13 типов: `resource`, `ability`, `item`, `attack`, `buff`, `feat`, `lens`, `spell`, `quest`, `overload`, `comfort`, `stance`, `button`). Drag&drop, flow-контейнер, `_render_button` (`color_fn` / `label_fn`).
- **`gui.py`** — 8 методов → делегируют в `gui_chips` (`_rebuild_resources_panel`, `_init_flow_container`, `_add_chip`, `_reflow_chips`, `_maybe_remove_buff`, `_do_short_rest`, `_do_long_rest`). `_rebuild_rest_panel` удалён.
- **`gui_file_ops.py`** — `chips.clean_order(c)` при загрузке (4 места: `load_or_new`, `new_character`, `open_character`, `import_character`).
- **`gui_combat.py`** — `build_combat_panel` → `pass` (кнопки в `chips._buttons`). `update_combat_status` — no-op.
- **`gui_rest.py`** — галочки `show_rest_short` / `show_rest_long` → `app._refresh()` (чипы отдыха).

### 1.2 id чипов

- `kind:name` — напр. `attack:Меч`, `buff:Окаменение`, `spell:Огненный шар`, `feat:Стойка волка`, `rest:short`, `rest:long`.
- `item:<uuid>` — предметы (uuid стабилен).
- Фиксированные — `hp`, `ac_full`, `ac_touch`, `ac_flat`, `ac_parry`, `bp`, `mana`, `spirit`, `balance`, `slot_<N>`, `resource:<name>`, `stance`.
- Кнопки — `btn:damage`, `btn:heal`, `btn:temp_hp`, `btn:lose_balance`, `btn:new_turn`, `btn:injury`, `btn:pain`, `btn:morale`, `btn:restore_balance`, `btn:situational`, `btn:refresh`.
- Дубли (`#1`, `#2`) — `_dedup` в `collect_all`.

### 1.3 Drag&drop (DONE)

- **За имя чипа** (лейбл) или **чёрную точку** (кнопки, 6×6 внизу справа). Кнопки `−` / `+` / `×` не ломаются.
- **Призрак** — полупрозрачный `Toplevel` (`-alpha 0.75`), летит за мышью.
- **Оригинал** — затемняется (`bg="#222"` + контур).
- **Линия-индикатор** — `#4af`, 2px, перед/после target.
- **`_preview_insert`** — пересчёт «дырки» (без `reflow_chips` — без мигания).
- **`_reorder`** — вставка, `chips_order` сохраняется, `_refresh`.
- **`_find_target`** — точное попадание (левее/правее центра) → ближайший.

### 1.4 Фильтр и порядок

- **`settings.chips_visible_enabled`** (bool, default false) — включён ли фильтр. `false` = все, `true` = только из `chips_visible`.
- **`settings.chips_visible`** (array, default []) — id чипов (при `enabled = true`; пусто = ничего).
- **`settings.chips_order`** (array, default []) — порядок (id). Отсутствующие — в конец.
- **Сортировка** в `rebuild_resources_panel`: `order_map = {sid: i}`, `sort(key=lambda s: order_map.get(s["id"], 10**9))`.

### 1.5 Цвета (DONE)

- **`settings.chips_colors`** (object, default {}) — `{id: '#hex'}`. Перекрывает `spec["color"]`.
- **`chips.collect_all`** — применяет `custom[s["id"]]`.
- **`gui_editors.edit_settings`** — блок «Цвета чипов» (выпадающий список + поле + «Применить» / «Сбросить»).
- **`gui_chips._render_button`** — `color_fn()` (динамика: ОТ / боль / мораль).

### 1.6 Кнопки (`_buttons`, `_rest`)

- **`chips._buttons`** — базовые действия (урон, лечение, temp HP, баланс, инициатива, ОТ, боль, мораль, ситуация, обновить). `color_fn` (динамика), `label_fn` (актуальный текст). Светло-серые (`#5a5a5a`), зелёные / синие / красные по смыслу.
- **`chips._rest`** — короткий (`#4a7` зелёный) / длинный (`#855` красный). `btn:rest` (дубль) удалён.
- **`@register("button")`** — рендер кнопки. `command` (строка) → ленивый импорт `gui_combat` / `gui_rest` / `app`.

### 1.7 Правый клик (частично DONE)

- **Ресурсы** — правый клик → `gui_dialogs.ask_int` (`bind_edit_number`). ✅
- **Атаки / Бафы / Предметы** — правый клик → редактор объекта. ❌ (план: T-CHIPS-BUTTONS-2)

### 1.8 Кнопки в настройках (`edit_settings`)

- **«👁 Спрятать/показать все»** — toggle: `chips_visible_enabled` + `chips_visible = []`.
- **«🔄 Сбросить все чипы»** — `chips_order = []`, `chips_visible = []`, `chips_visible_enabled = false`.
- **«Цвета чипов»** — выпадающий список + поле `#hex` + «Применить» / «Сбросить».

### 1.9 Ч / О / Б — toggle (DONE)

- **Ч** (`_show_char_sheet`), **О** (`_show_last_editor`), **Б** (`_toggle_chips`) — toggle: первый клик с фокусом (`_show_win`), повторный — свернуть (`_on_center_close` / `_on_chips_close`).

### 1.10 Чистка

- **`chips.clean_order(c)`** — при загрузке (4 места в `gui_file_ops.py`).

---

## 2. v1.1 — T-SPLIT-3.2 Desktop overlay (PLAN)

**Цель:** чипы «висят» над всеми программами (Roll20, браузер), клики по чипам работают, клики мимо — проходят в другие окна. Программа в трее.

### 2.1 Решение: `pywin32` + `WM_NCHITTEST`

**Причины:**
- Надёжнее `-transparentcolor` (не глючит, не искажает цвет).
- Точечный контроль: клик сквозь фон, клик в чип.
- Не требует переписывать GUI (в отличие от PySide6).
- Родной механизм Windows.

**Архитектура:**
- **Окно 1 (фон):** fullscreen, `WS_EX_LAYERED | WS_EX_TRANSPARENT`, `LWA_ALPHA=0` — невидимо, клики сквозь.
- **Окно 2 (чипы):** `Toplevel` без рамки, `topmost`, чипы через `place(x, y)`.
- **`WM_NCHITTEST`:** `HTTRANSPARENT` (пусто) / `HTCLIENT` (чип).
- **Позиции:** `settings.chips_positions: {id: [x, y]}`.
- **Режим:** `settings.chips_drag_mode: bool` — false = только клики; true = drag.
- **Трей:** меню/чарник скрыты, только чипы на экране.

### 2.2 Файлы

- **`DND/gui_desktop.py`** — новый (`DesktopView`).
- **`gui.py`** — `_build_layout` → `DesktopView`, если `settings.ui_layout_mode = "desktop"`.
- **`gui_split.py`** — трей, скрытие меню/чарника.
- **`character.schema.json`** — `settings.chips_positions`, `chips_drag_mode`.

### 2.3 Настройка

- **«Режим перемещения чипов»** (`chips_drag_mode`) — галочка в настройках. Без неё чипы **только кликаются**, drag выключен.

### 2.4 Риски

- **Topmost** перекрывает диалоги (временно `topmost=False`).
- **Много Toplevel** — тормоза (решение: один оверлей + `place`).
- **`-transparentcolor`** — Windows-only (у нас Windows, ок).

---

## 3. v1.1+ — Стиль / прозрачность (PLAN)

- Единый стиль чипов.
- Прозрачность (`settings.alpha_chip_buttons` — уже в схеме, нужен UI-ползунок).
- Тёмная / светлая тема — нет (пока).

---

## 4. Разделители групп (опционально, PLAN)

- Метки «Ресурсы», «Бафы», «Атаки», «Стойка» — перед группами чипов.
- Реализация: `_group_label(text)` в `rebuild_resources_panel`.
- Метки не перетаскиваются (только чипы).

---

## 5. Сортировка бафов — НЕ нужна

Бафы стоят там, где их поставили. Порядок — через drag.

---

## Как использовать этот файл

- Новый бот читает `TASK_CHIPS.md` → понимает, что **v1.0 DONE** (чипы + кнопки + цвета), **v1.1 (Desktop overlay)** — следующая.
- Начать с **v1.1** (`gui_desktop.py`, `pywin32` + `WM_NCHITTEST`).