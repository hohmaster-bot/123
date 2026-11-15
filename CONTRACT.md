# CONTRACT.md — WIPEFINDER: правила для чат-ботов

> Роль: единые правила поведения для любого бота (DeepSeek, Continue, ChatGPT и т.д.),
> чтобы ответы были предсказуемы и без расхождений. Читать **первым** после `TECH.md §0`.
> Порядок передачи боту: PROJECT_MAP.md → CONTRACT.md → PROMPT.md → character.schema.json → GLOSSARY.md → TECH.md → файл кода.

## §0. Физическая карта

Где что лежит — **`PROJECT_MAP.md §0`**. Читать **до** `Ctrl+F` по проекту.
Коротко: `Старт/` — документы (TECH, CONTRACT, PROMPT, schema, SCHEMA, GLOSSARY, LOG, PROJECT_MAP); `DND/` — код (модули по зонам); `catalogs/` — данные каталогов; `characters/` — сейвы; `config.json` — настройки приложения.
За что отвечает конкретный модуль — таблица `DND/` в `PROJECT_MAP.md §0`.

## §1. Источники правды (по убыванию приоритета)

0. **`PROJECT_MAP.md`** — карта «функция → файл» + **`§0` физическая карта** (где документы, код, данные). Читать **первым**, чтобы не искать `Ctrl+F` по всем файлам.
1. **`character.schema.json`** — типы, пути, enum'ы, обязательность. При любом конфликте прав он.
2. **`GLOSSARY.md`** — человеческие названия/переводы/сокращения/JSON-пути.
3. **`TECH.md`** — задачи, приоритеты, правила процесса.
4. **`LOG.md`** — статус задач (история).
5. **Пример персонажа** (Гэндальф) — эталон формата.

Если бот не нашёл поле в `character.schema.json` — **он не выдумывает**, а спрашивает или предлагает добавить в схему (см. §2).

## §2. Правила изменения схемы

- Новое поле: **сначала** `character.schema.json` (в нужный `$defs`/`properties`), **потом** `GLOSSARY.md` (§ с JSON-путём), **потом** код.
- Удаление/переименование: помечать в `GLOSSARY.md` как `[DEPRECATED]`, не удалять сразу из схемы (ломает старые сейвы). Удаление — только через миграцию и `_schema_version++`.
- **`charges_tick_mode`** (T34.1) — **DONE (v11)**. Поле есть в схеме: `situational_bonuses[].charges_tick_mode` и `AbilityDef.charges_tick_mode` (enum `none|decrement|increment`, default `none`). Тик зарядов — в `tick_initiative`, блок «1) Бафы».
- **`_schema_version` = 2 (v15)**: `settings.show_portrait` → `settings.hide_portrait` (инверсия смысла: `True` = скрыть портрет). Старые сейвы **не мигрируются** (бетки); новый персонаж получает `hide_portrait=False` (портрет виден). `gui_media.update_portrait_size` читает `not settings.get("hide_portrait", False)`.

## §3. Формат ответа бота

- **Точечные патчи**: «найди X → замени на Y». Без «вот весь файл», если не просят.
- Для больших файлов — только точечные замены (правило проекта).
- Если правка затрагивает схему — **сначала** предложи правку `character.schema.json`, дождись «ок», потом код.
- Никогда не выдавай «псевдокод с полями, которых нет в схеме».

## §4. Работа с JSON персонажа

- **Числовые поля в GUI** — только через `_safe()` / `_gi()`. Пустое поле → прежнее значение (не 0), если иное не указано в задаче.
- **Legacy-строки** (`hp`, `pain_threshold`, `balance`, `spirit`, `mana`, `ac`, `bab`, `parrying`, `save_*`) — **display-only**. Писать только в источник правды (см. `GLOSSARY.md §2`).
- **Ключи с `_`** (`_hp_max_cap`, `_pain_threshold_data`, `_balance_data`, `_spirit_data`, `_mana_data`, `_schema_version`) — **не редактируются вручную**, только через GUI/код. Бот их не пишет.
- **`settings`** — GUI-конфиг, **не данные персонажа**. Ботам-механикам — не трогать.
- **`training.purchases[]`** — **append-only**. Состояние **не пересчитывать** из purchases; это история. Текущее состояние — в `abilities`, `skills`, `feats` и т.д.
- **`items{uuid}`** — ключ обязан совпадать с `item.id`. При добавлении предмета — генерировать UUID и класть в оба места.
- **`attacks[].from_item`** — FK на `items{}`. Если предмета нет — **не падать**, показать «предмет удалён» и оставить атаку как ручную.
- **`proficiencies.weapons[].bonuses[]`** — **T24 DONE (v12)**: реестр `id` = `WEAPON_BONUS_CATALOG` в `character.py` (ключи `spec_*`/`expert_*`/`master_*`); валидация — в `purchases.set_weapon_bonuses`. Бот **не пересчитывает** из них бонусы (подсистема не описана).
- **Урон**: канон для оружия — **`Item.damage`** (как в инвентаре). Для атаки — **`Attack.damage_dice`**. Не путать. `damage_sml/med/type/hands` — legacy/резерв, не канон.
- **Эффекты (`target`)**: **`all` запрещён**. Всегда указывать конкретную цель (`attack`, `damage`, `skill`, `lucky`, `speed` и т.д.). Если `target == "skill"` — обязательно заполнять `skill_name` (имя из `character.skills`).
- **Счастливая атака (`lucky_threshold`)**: база — 20. Бонусы к порогу (пассивки/активки предметов, зачарования, абилки) идут через `situational_bonuses` с `target == "lucky"`. Метод `attack_lucky` **не должен** читать `item.passive_bonuses` напрямую (они уже в `situational_bonuses` через `_sync_item_bonuses`) — иначе двойной счёт.
- **Бафы (`situational_bonuses[]`)**: `permanent == true` → `duration_current` не тикает, `+`/`−` не рендерятся, `×` рендерится всегда. `keep_at_zero == true` → чип НЕ удаляется автоматически на след. тике при `duration_current == 0`. `settings.buff_delete_on_zero` / `settings.confirm_chip_delete` — GUI-конфиг, боты не пишут.
- **Заряды бафов**: тикают **только** если задан `charges_tick_mode` (T34.1). По умолчанию `charges_current` **не тикает**. Тратятся кнопкой `[⟳]` (`Character.activate_buff` / `trigger_buff`), восстанавливаются на `long_rest()` до `charges_max`.
- **Разовые эффекты**: `on_activate_effects[]` применяются **один раз** при `[⟳]`/`trigger_buff` через `_apply_effect_values`. Постоянные (`effects[]`) — каждый тик.
- **Порядок `tick_initiative`**: (1) тик длительностей; (2) кулдауны; (3) тик зарядов (если включён); (4) травмы; (5) перегрузка; (6) баланс (может превысить `max`); (7) `self_damage_per_tick` через `take_damage`, затем обрезка баланса до `max`; (8) `restore_*`. `permanent == True` не блокирует применение `restore_*` и `self_damage_per_tick` — они работают каждый тик.
- **Формулы в `value`**: число **или** строка (`2*lvl`, `d4+1`, `con_mod`, `2d6`, `lvl+N`). Парсер — `Character._eval_effect_value`. Ошибка формулы → `0` без исключения. Редактор (`gui_combat._edit_buff_dialog`) показывает `value` как `Entry`, не `Spinbox`.
- **Травмы (`injuries[]`)**: это **отдельная подсистема**, не бафы. У травмы есть `effects[]` (постоянные, T46) и `active` (bool). В «Ситуативно» травма с `active == True` показывается как **постоянный баф/дебаф** (галочка вкл/выкл). Тик `injuries[]` — отдельный (см. `tick_initiative`, блок «4) Травмы»), **не** через `situational_bonuses`.
- **Классовые/расовые бафы (T48)**: `char_class.abilities[]`/`race.abilities[]` с `is_buff == True` — шаблоны для «Ситуативно». Поля: `duration_*`, `charges_*`, `effects[]`, `on_activate_effects[]` — как у `situational_bonuses`. Кнопка `+ <Название>` в «Ситуативно» активирует (тратит заряд, сбрасывает длительность, применяет `on_activate_effects[]`).
- **`catalogs_enabled` / `catalogs_items_disabled` / `catalogs_mode`** (T-CAT): GUI-конфиг (в `settings`). Боты **не пишут**. `catalogs_enabled` — **файлы** `<папка>/<файл>.json` или `<папка>` (вся папка, старое). `catalogs_items_disabled` — скрытые элементы `<папка>/<файл>#<имя>`. `catalogs_mode` — `whitelist` (default, только перечисленные включены) / `blacklist` (все, кроме). Загрузка — `character.load_catalogs`, фильтр `_allowed(sub, fname)` + `_item_allowed`. UI — `gui_catalogs.open_catalogs_manager` (⚙ Управление каталогами).
- **Счётчики мастерских абилок и паррирования (`master_*`, `parry_ranged_*`)**: это ресурсы персонажа. Восстанавливаются на отдыхе / нулевой инициативе. Бот не пересчитывает их из оружия при каждом запросе — только при экипировке.
- **T34.1** (`charges_tick_mode`) — **DONE (v11)**. Заряды тикают в `tick_initiative` (блок «1) Бафы»): `decrement` → −1, `increment` → +1, `none` → не тикают. По умолчанию `none`.
- **T-CAT** (`catalogs_enabled`, `catalogs_items_disabled`, `catalogs_mode`) — **GUI-конфиг**. Боты **не пишут**; читают, если нужен список включённых/скрытых каталогов. `CATALOG_SUBDIRS` = 12 (без `misc`). `custom.json` в каждой папке — «своё», создаётся `ensure_dirs`.
- **`cast_spell`** — ресурсы (мана/слот/перегрузка/баланс) списываются **всегда**. Если `balance` не хватает — **разница уходит в ОТ**. `concentration_ks = 10 + 2 × ОТ_от_каста` (0, если ОТ=0). `gui._rebuild_resources_panel._cast` при `ks > 0` показывает `showinfo` «Концентрация КС X». **Отката нет.**
- **T46** (`injuries[].effects[]`, `injuries[].active`) — **постоянные** эффекты травмы + галочка вкл/выкл. Тик — **отдельно** (не через `situational_bonuses`).
- **T48** (`char_class.abilities[].is_buff`) — **шаблон бафа** (поля `duration_*`, `charges_*`, `effects[]`, `on_activate_effects[]`). Кнопка `+ Название` в «Ситуативно».
- **T50** (`settings.hide_hints`) — **скрыть примечания** в редакторах (подсказки под полями), **НЕ** тултипы (`ToolTip`).
- **`gui_alphabet.py`** — **единый словарь отображения** «ключ → русская подпись» для **всех** GUI-файлов (`gui_combat.py`, `gui.py`, `gui_inventory.py`, `gui_rest.py`, `gui_shop.py`, `pdf_export.py`). **Два словаря:** `TARGET_NAMES` (цели бафов) + `CATEGORY_NAMES` (категории предметов, T-P2). **Только для отображения**, на расчёты не влияет. **Правило:** `set(TARGET_NAMES) == character.VALID_SIT_TARGETS`, `set(CATEGORY_NAMES) == set(character.ITEM_CATEGORIES)` (проверяется `assert` при импорте). **`all` запрещён** — в словаре его нет. Новые `target` добавляются **сначала** в `character.VALID_SIT_TARGETS`, **потом** в `gui_alphabet.TARGET_NAMES`. **`cmd`/`cmb`/`initiative` — DONE (v11):** есть в `VALID_SIT_TARGETS`, `TARGET_NAMES`, `cmb_total()`/`cmd_total()`/`initiative_total()`.
- **CMB / CMD / Инициатива (v11)**: `cmb_total()` = `ББА + СИЛ + размер + cmb_mods + боль + мораль + situational_bonus("cmb")`. `cmd_total()` = `10 + ББА + СИЛ + ЛОВ + размер + cmd_mods + боль + мораль + situational_bonus("cmd")`. `initiative_total()` = `ЛОВ + situational_bonus("initiative") + боль + мораль + combat.initiative`. Боль/мораль **работают** на CMB/CMD/Init (как на атаки/спасброски). **Не работают** на крит и lucky.
- **`gui_registry.py`** — реестр редакторов `(key, title, group, callable(app))` — **4-элементные** кортежи. P2-3 (5-й элемент `paid`) **ОТМЕНЁН**. Две вкладки «Редакторы» = **режим** (`paid=False` → `app.force_free=True`; `paid=True` → `False`). `gui_editors_window._build_editor_tab` красит кнопки по `paid` вкладки, **не** по редактору.
- **`gui_shop.open_shop`** — «📦 Каталог». Combobox «Категория» + «Источник 1/2» + «Поиск». Секции «📚 Из каталогов» + «🛒 Мой магазин». Кнопка «⚙ Управление каталогами» → `gui_catalogs.open_catalogs_manager`. «💰 Купить» → `_buy_from_catalog` (копия в `c.items`, деньги списываются).
- **T-WINDOW (все новые окна)** — `Toplevel` с **`modal=False`**, **`transient(parent)`**, `center_window(..., modal=False)`. **Не** `grab_set`. **`topmost`** — галочка (`wm_attributes("-topmost", bool)`), по умолчанию False. `focus_force` — только при открытии. **Не** блокировать главное окно. `wait_window` — только для подтверждений (`askyesno`), не для редакторов.
- **`settings.visible_buttons`** — GUI-конфиг. Читается в `gui_buttons.is_visible(app, key)` (после T-SPLIT; раньше был `gui.py._is_visible`). `DEFAULT_VISIBLE_BUTTONS`/`FORCED_VISIBLE_BUTTONS` — в `gui_buttons.py`. Бот **не пишет**.
- **T-SPLIT-VIEW (v17):** `gui.py` делегирует вызовы сплиту, если `app._split` активен. Бот **не пишет** в `gui.py` методы `_show_editor` / `_show_main` без проверки `hasattr(self, "_split")`. В сплите окна не уничтожаются (`destroy`), только скрываются (`withdraw`). Это критично для стабильности на Windows.
- **T-STANCE (v18, стойки):** стойка — это **черта** `feats[]` с `is_stance == true`. В `edit_feats` такие черты **не показываются** (только в блоке «Стойка» в «Ситуативно»). Поля: `stance_effects[]` (как `situational_bonuses.effects`, `Effect`), `stance_blocks[]`. Активная — `active_stance` (имя из `feats[].name` с `is_stance=true`) или `null` = «Обычная» (заглушка). Одна активная одновременно. **Не тикает**, меняется сколько угодно. `settings.stance_chips` — имена в быстром доступе; «× Удалить» в чипе убирает из `stance_chips`, **не** из `feats[]`. Тултип «1 раз до начала след. хода» — правило для игрока, **не код**.
- **T-LOG (v18, журнал трат):** `action_log[]` — append-only, `maxItems 20`, **только расход** (получение не пишется). Поля: `ts`, `kind` ∈ `hp|balance|spirit|mana|slot|charge|ability|stat|training|spell|item|buff|initiative_tick|other`, `summary`, `before`/`after` (снимки), `rev` (по умолчанию `true`). Реверс = применить `before` обратно (простой откат, без умных пересчётов). `initiative_tick` — реверс откатывает раунды/бафы/реген на 1. **Не путать** с `training.purchases` (это история покупок, не лог трат).
- **T-RACE (v18, расовые способности):** `AbilityDef.source` ∈ `training|loot|race|class|quirk`, `AbilityDef.invested` (0 = бесплатная). `source == "race"/"class"` → подпись `[Раса]`/`[Класс]`; `invested > 0` → `[Тренировка, N]` (как `Feat.source`/`invested` в чертах). Покупка — `purchases.buy_race_ability` / `_refund`. `race.abilities[]` и `char_class.abilities[]` — **общий** `AbilityDef`.
- **T-ALPHA (v18, прозрачность):** `settings.alpha_menu` / `alpha_center` / `alpha_chips` / `alpha_log` / `alpha_chip_buttons` — **10..90** (не 0, не 100). Clamp в GUI через `_safe`/`_gi` (`>=100 → 90`, `<10 → 10`). Боты **не пишут** (GUI-конфиг, как остальной `settings`).

## §5. Кодировка и файлы

- Кодировка — только через VS Code (Ctrl+A → Ctrl+C → Ctrl+V → Ctrl+S). **Никакого PowerShell** для сохранения/изменения кодировки.
- Большие файлы — точечные замены.
- Не дублировать функции, не выдумывать переменные.

## §6. Что делать при неопределённости

- Если поле/поведение не описано в `character.schema.json` и `GLOSSARY.md` — **спросить**, не догадываться.
- **Перед задачей** — **прочитать** `PROMPT.md`. **Задать 5–10 вопросов** (по одному). **Не** **начинать** **патч** **без** **«ок»**.
- Если задача противоречит `TECH.md §0` (приоритеты) — указать на противоречие.
- Если видишь расхождение между `character.schema.json` и `GLOSSARY.md` — сообщить, не «чинить» молча.
- Формат ввода длительности (`N` vs `current/max`) — правило **парсинга в GUI**, не в схеме. Бот в схеме не пишет `current/max` как строку.

## §7. Чек-лист перед ответом

1. Поле есть в `character.schema.json`? (если нет — §2)
2. Путь в JSON указан полностью?
3. Legacy/CALC учтены?
4. `training.purchases` не трогаем?
5. `settings` не трогаем?
6. Формат — точечный патч?
7. Если меняем схему — обновлены ли `character.schema.json` + `GLOSSARY.md`?