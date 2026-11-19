# Пакет 9: отчёт

Ветка `Rework`. Коммиты: `40c6d70` (данные доспехов и щитов), `9fefd71` (код и тесты), `899da84` (правила и
документы), плюс коммит с этим отчётом. Код только ASCII, модули меньше 500 строк (самый большой `derived_view.py`, 431).

## Что запускалось
- Все 33 набора тестов (`core/` 16, `model/` 16 с новым `test_pkg9.py`, `storage/` 1), `test_module_size.py`,
  `test_ascii_code.py`: **все прошли**.
- Старые тесты легаси `test_rules_baseline.py`: 105 примеров, 69 прошли / 17 не прошли / 19 не сделаны. Так же, как
  раньше (известные провалы старого кода в BASELINE_REPORT.md).
- Проверка «сломай код»: 69 нарочных поломок в настоящих файлах, после каждой запускался `test_pkg9.py`, файл
  возвращался как был. Каждый из 64 новых тестов упал хотя бы от одной поломки (таблица ниже). После проверки весь
  набор снова прошёл.
  Две поломки сначала НЕ поймались, я это исправил:
  - «касательный бонус при HP 0»: проверка в коде повторялась (надетая вещь с HP 0 и так считается снятой). Поломку
    сделал честной: убрал обе проверки сразу, тест упал.
  - «у шанса провала нет пола 0»: показ скрывал ошибку. Добавил в тест проверку самого числа (`failure_pct_raw`).

## Что изменилось

### A. Дух (Q33 закрыт)
Код уже считал как сказал владелец: сначала `max(0, 5 + 5 * мод. Хар)`, потом бонусы, итог не ниже 0.
Тесты: Хар -2 и +3 -> 3; -2 и -1 -> 0; +2 и +3 -> 18.

### B. Доспех и щит без владения (Q34 закрыт)
- У доспеха теперь есть категория `armor_type` (light / medium / heavy, нужен ранг 1 / 2 / 3).
- Без нужного ранга штраф навыков вещи (после мастерской работы, x2 у сломанной) идёт и на КАЖДУЮ атаку.
- Щиты так же: light / heavy / tower нужен ранг 1 / 2 / 3. Щит в сумке штрафа не даёт.

### C. Максимум баланса в бою (Q35 закрыт)
- `start_combat` запоминает максимум баланса (`balance_cap_start`). В бою он меняется только от ударов (-1 за удар).
  Трата БП, снятие доспеха, изменение Тел и бонусов его не меняют. `end_combat` считает заново и снимок стирает.
- Восстановление баланса считается по текущему Тел, как и раньше.
- Новая команда `spend_balance(n)`: это оплата, максимум не падает. Больше, чем есть, заплатить нельзя.
- Новая команда `pay_hp_cost(amount)`: платит из текущего баланса, HP не трогает. Излишек даёт ОТ и +1 боль, как
  «урон по балансу». Максимум не падает.

### D. Мастерская работа (Q39, Q40 закрыты)
- Оружие: +1 к атаке, но выключается, пока активно зачарование +1 и выше. Это видно в `item_view`:
  `masterwork_active = False`, причина `enchant_active`. Включённая вкладка без зачарования (огонь d6) её не выключает.
- Доспех/щит: штраф навыков всегда на 1 меньше, зачарование не мешает. У сломанного сначала -1, потом x2.
- Из правил убран старый способ «+1 во вкладке "не активирован"»: теперь только флаг.

### E. Метка условия (Q36 закрыт)
Поле `condition_tag` (none / combat_only / out_of_combat_only) у предметов, статусов и черт. Оно только для показа
и не меняет ни одного числа. Видно в `item_view` и `condition_tags(ch)`. Команда `set_condition_tag`.

### F. Основная запись и порядок чисел предмета (Q38 закрыт)
- У записи атаки есть вид `kind`: «main» (обычная атака оружием) или «maneuver» (приём на основе записи `base_record`).
  Первая запись предмета становится основной, следующие становятся приёмами на ней.
- Вторую основную запись добавить нельзя. Приём с другой группой добавить нельзя. Основную запись, на которой
  стоят приёмы, удалить нельзя, пока не удалены приёмы.
- Приём берёт группу и характеристику атаки у основной записи. Свои модификаторы появятся в пакете 11.
- На HP и прочность предмета влияет только основная запись.
- Порядок: база -> зачарование (если активировано) -> мастерство. Проценты складываются:
  прочность = (база + 2N) * (100 + %) / 100, вниз. +30% и +70% вместе дают x2.

### G. Зарубки
Новая команда `hit_item(iid, damage)`. Зарубки = урон // итоговая прочность, 1 зарубка = 1 HP предмета.
Флаг `durable`: по умолчанию «да» у доспехов и щитов. Такая вещь теряет не больше 1 HP за атаку. Прочность 0 —
мягкий отказ («используйте damage_item»). `damage_item` по-прежнему просто меняет HP.

### H. Касательный бонус брони
Поле `touch_bonus` идёт только в касательный КД, как слой брони. Баланс не даёт, другие КД не меняет. Работает
только надетая броня: при HP 0 бонуса нет, у сломанной он делится пополам вниз.

### I. Штрафы магии от брони
- Поля `spell_penalty_mana` и `spell_failure_pct`. Числа надетого и щитов в руке складываются, потом их меняют
  эффекты с целями `spell_penalty_mana` / `spell_failure_pct`. Пол 0, шанс не выше 100. Всё видно в новом
  `wp/model/spell_view.py` (`view(ch)`).
- Маг: доплата идёт к каждому заклинанию 1+ круга. Параметр `penalty_balance` у `cast_spell` говорит, сколько
  доплатить балансом, остальное платится маной. Если задан `mana_level`, цена одного заклинания не выше его, и
  команда пишет, что цену урезали.
- Провал: у кастеров со слотами шанс есть всегда, у магов только если он больше 0. Программа кубики не бросает:
  команда `resolve_spell_failure(failed)`. Режим `cancel` значит «не сработало». Режим `zero_balance` значит
  «сработало, баланс в 0». Божественные кастеры по умолчанию `zero_balance`.

### K. Данные доспехов и щитов
`wp/catalog/data/armor_set_1.json` (8 строк) и `armor_set_2.json` (15 строк), загрузчик `wp/catalog/armor_catalog.py`.
Это просто наборы данных на выбор (`load_sets()` читает любой `armor_set_*.json`). `make_item` делает из строки предмет.
Имена пока английские, id сделаны из имён по правилам транслитерации.

### J, L
Вес и расходники не трогал. Пакеты 10 и 11 записаны в ROADMAP.

## Правила, которые обновлены (английский текст)
resources.md (дух, снимок максимума баланса, spend_balance, pay_hp_cost), training.md (штраф без владения), buffs.md
(метка условия), gear.md (касательный бонус, штрафы магии, мастерская работа, порядок чисел, зарубки, основная
запись), weapons.md (проценты складываются), combat.md (виды записей), defense.md (касательный КД), classes_magic.md
(ссылка на штрафы), catalog.md (наборы доспехов). Плюс OPEN_QUESTIONS, ROADMAP, CLAUDE.md (новый тест), MODEL_REPORT.

## OPEN_QUESTIONS
- Закрыты: Q33, Q34, Q35, Q36, Q38, Q39, Q40 (ответы перенесены в RULES).
- **Q37 остался открытым**: в пакете 9 на него ответа нет (показывать ли серыми записи оружия не в руках).
- Новые вопросы (ни в задании, ни в RULES этого нет, поэтому не выбирал молча):
  - **Q41.** `pay_hp_cost`: в задании «+1 ОТ», а у «урона по балансу» ОТ = весь излишек. Сделал как у «урона по
    балансу» (стоимость 9 при балансе 7 -> ОТ +2).
  - **Q42.** Доспех или щит без категории считается лёгким (ранг 1).
  - **Q43.** `spend_balance` больше, чем есть: отказ.
  - **Q44.** Основную запись с приёмами удалить нельзя, пока есть приёмы.
  - **Q45.** Приём берёт группу и характеристику у основной записи; хват свой.
  - **Q46.** Зачарование касательный бонус НЕ повышает.
  - **Q47.** Эффект снижения штрафа магии пишется как обычное число (-2 = на 2 меньше).
  - **Q48.** Доплата мага делится только в части штрафа; сама цена заклинания по-прежнему «мана = баланс».
    По умолчанию вся доплата идёт маной.
  - **Q49.** «Уровень маны» (потолок цены) в правилах не описан. Сделал поле `mana_level`, которое вводят руками
    (0 = без потолка). Сначала урезается штраф, потом сама цена.
  - **Q50.** На заговоры (0 круг) штраф маны не идёт.
  - **Q51.** Что тратится при провале в режиме `cancel`: в правилах не сказано. Сейчас ничего не возвращается.
  - **Q52.** Кастер со слотами при шансе 0: «шанс есть», но он 0.
  - **Q53.** Данные набора 1: «-1 / -4 / -8» в колонке «маг.» записаны как доплата 1 / 4 / 8. Вес «(1)» = 10 L.
    «Класс доступа» и «+» набора 2 хранятся только как данные.
  - **Q54.** Снимок максимума баланса хранится в персонаже, пока идёт бой. Иначе правило «с начала боя» не выполнить.

## Что ещё я решил сам (тоже в вопросах выше)
Всё, что не было в задании и в RULES, перечислено в Q41–Q54. Других молчаливых решений нет. Только мелочи кода:
у `hit_item` отказ на уничтоженном предмете и на отрицательном уроне, как у `damage_item`.

## Что осталось открытым
- Вопросы Q37, Q41–Q54.
- Свои модификаторы приёмов (пакет 11).
- Старые файлы сохранения открываются (поля только добавлены, ничего не убрано).

## Проверка «сломай код»: тест -> что сломал -> упал ли
| test | what I broke | failed |
|---|---|---|
| a-spirit | spirit floor before bonuses removed; spirit final floor removed | yes |
| b-armor-light | no non-proficient penalty; light armor needs rank 0 | yes |
| b-armor-medium | no non-proficient penalty; medium armor needs rank 1 | yes |
| b-armor-heavy | no non-proficient penalty; heavy armor needs rank 2 | yes |
| b-shield-light | no non-proficient penalty; light shield needs rank 0; held shields left out | yes |
| b-shield-heavy | no non-proficient penalty; heavy shield needs rank 1; held shields left out | yes |
| b-shield-tower | no non-proficient penalty; tower shield needs rank 2; held shields left out | yes |
| b-mwk-broken | no non-proficient penalty; raw penalty, no masterwork/broken; armor masterwork relief removed; broken x2 before masterwork | yes |
| b-every-attack | no non-proficient penalty; light armor needs rank 0; penalty only on unarmed | yes |
| b-bag-shield | bag shields counted | yes |
| c-snapshot | start_combat stores no snapshot | yes |
| c-spend-bp | cap snapshot ignored (live); start_combat stores no snapshot | yes |
| c-armor-off | cap snapshot ignored (live); start_combat stores no snapshot | yes |
| c-bonus-con | cap snapshot ignored (live); start_combat stores no snapshot | yes |
| c-regen-live | regen from max Con (not live) | yes |
| c-hit | hit does not lower cap | yes |
| c-end | end_combat keeps snapshot | yes |
| c-spend-balance | spend_balance lowers cap | yes |
| c-spend-balance-short | spend_balance no check | yes |
| c-pay-hp | pay_hp_cost lowers cap; pay_hp_cost as real damage; pay_hp_cost one more | yes |
| c-pay-hp-small | pay_hp_cost one more | yes |
| d-mwk-plain | masterwork +0 to attack | yes |
| d-mwk-enchant-off | masterwork off by enchant level; masterwork +0 to attack | yes |
| d-mwk-enchant-on | masterwork ignores active enchant | yes |
| d-mwk-ability-only | masterwork off by any activation; masterwork +0 to attack | yes |
| d-mwk-not-flag | no not_masterwork reason | yes |
| d-mwk-armor-enchant | armor masterwork relief removed | yes |
| d-mwk-armor-broken | armor masterwork relief removed; broken x2 before masterwork | yes |
| e-tag-no-effect | tag switches a status off; tag switches an item off | yes |
| e-tag-view | tag not in view | yes |
| e-tag-bad | tag not validated | yes |
| f-kinds | every record main | yes |
| f-second-main | second main allowed | yes |
| f-remove-main | main removable under maneuvers | yes |
| f-main-picks-only | item picks from primary record (old) | yes |
| f-order-30 | hardness: mastery before enchant; item HP ignores enchant | yes |
| f-order-both | hardness: mastery before enchant; hardness: picks multiply; item HP ignores enchant | yes |
| f-order-off | hardness: picks multiply | yes |
| f-maneuver-view | maneuver not resolved | yes |
| g-hardness-5 | notches rounded up | yes |
| g-durable | durable cap removed; armor not durable by default | yes |
| g-hp-after | hit_item applies raw damage | yes |
| g-enchanted | notches from base hardness; notches rounded up | yes |
| g-no-hardness | hardness 0 not refused | yes |
| g-broken | hit_item applies raw damage | yes |
| h-touch | touch bonus not used; touch adds balance | yes |
| h-touch-broken | touch bonus not used; broken touch not halved; touch adds balance | yes |
| h-touch-hp0 | touch at HP 0 (both checks) | yes |
| h-touch-not-worn | touch from items not worn | yes |
| i-sum | spell: shields left out; spell: +1 mana always | yes |
| i-bag-shield | spell: bag shields counted; spell: +1 mana always | yes |
| i-reduction | spell: shields left out; spell: reductions ignored; spell: no floor on failure; spell: +1 mana always | yes |
| i-cap-100 | spell: shields left out; spell: no cap 100 | yes |
| i-cast-mana | spell: +1 mana always; cast: extra not added | yes |
| i-cast-mix | spell: +1 mana always; cast: extra not added; cast: split ignored | yes |
| i-cast-cap | cast: extra not added; cast: no mana level cap | yes |
| i-cast-no-armor | spell: +1 mana always | yes |
| i-failure-applies | failure: mage always applies | yes |
| i-modes | failure: divine default cancel | yes |
| i-resolve | failure: divine default cancel; failure: zero_balance keeps balance; failure: cancel still cast | yes |
| k-sets | catalog: first row lost | yes |
| k-set1-spot | catalog: first row lost; catalog: touch read from ac | yes |
| k-set2-spot | catalog: max dex lost | yes |
| k-make-item | catalog: penalty sign kept positive | yes |
