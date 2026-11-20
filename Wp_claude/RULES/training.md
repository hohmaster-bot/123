# Training, modes, purchases [OWNER]

Old beta had no real edit or training mode: just an "add X" button. The new app has three modes.

## Modes
- Play: normal use.
- Training: spend training points to buy things (feats, race/class abilities, skills, etc.). Needs resources.
- Edit: change anything with NO resources, up to HARD caps (e.g. HP not above level * max hit die value). Counts as fixing mistakes.
  New abilities/spells added in edit mode are treated as obtained at creation or similar.
- Each ability/feat/item stores its SOURCE (race, class, training, loot, quirk, template...) and separately the COST paid
  (editable, e.g. to change what a feat cost).
- Rule: only source = training spends training points. Other sources (race, class, loot, quirk) never spend them
  (old code wrongly spends for any source). Race and class abilities and feats can ALSO be bought with training.
- Price is editable on any purchase except feats (feat price is entered by its author, default 200 [beta behavior]).
- Feat "Finesse training" (finesse_training): 200 [OWNER confirmed].
- Feats with effects [OWNER, package 11 D; closes Q68]: a feat has an effects list with the same structure as statuses
  (buffs.md), permanent while the feat is owned: bonuses to parameters, skills, attacks, damage, speed, any part of the
  sheet; values may be a stat modifier (buffs.md "Value from a stat modifier"). Removing the feat removes its effects
  (command remove_feat; no training refund: the rules give none). A feat may hold granted_maneuvers (a list of
  maneuver ids, used from package 12). Feats have NO toggle modes: "power attack" is a maneuver (package 12) and
  stances already exist. Catalog feats carry their effects and granted_maneuvers to the sheet.
  Tests: feat +1 attack / +2 damage reach the attack view; +Str to Intimidation; +10 ft speed; remove -> gone.

## Ability score cost
- Score used for pricing = base + RACE bonus. Item and quirk bonuses do NOT raise the price; injuries usually do not lower it.
- Cost of +1 = 150 * max(1, new modifier).
- Example: base 13 + race 2 = 15. 15->16 = 150*3 = 450; 16->17 = 450; 17->18 = 150*4 = 600.
  If a race bonus is lost narratively, the price follows the new score.

## Comfort for training [OWNER]
- 1 comfort = 5 + 5 * level training (10, 15, 20 at levels 1, 2, 3). Item and class bonuses change it.

## Armor / shield grades [OWNER confirmed, package 4]
- Shield: 100 per grade: none -> light -> heavy -> tower.
- Armor: 250 per grade: none -> light -> medium -> heavy.
- Owner text (verbatim):
  "Парирование растет на каждом нечетном уровне на 1."
  "Владение новой категорией доспехов - 250 очков
  Не владеет, 0 парирование -> Легкие, 2 парирование -> Средние, 4 парирование -> Тяжелые, 6 парирование. Парирование растет на 1 каждый нечетный уровень."
  "Владение новой категорией щитов - 100 очков. Тяжелые и ростовые щиты добавляют свой бонус щита к балансу персонажа.
  Легкие -> Тяжелые, рост баланса -> Ростовые, рост баланса, +2 парирование"
- Code reading: parry = armor proficiency parry (0/2/4/6) + 1 per odd level + weapon mastery parry picks.
  [OWNER, Q27] Level 1 does NOT count: growth starts at level 3 (level 1 -> +0, 3 -> +1, 5 -> +2, 7 -> +3).
  Tests: none at level 1 -> parry 0; heavy at level 5 -> 6 + 2 = 8.
- [OWNER, package 5] Parry comes from PROFICIENCY (armor categories 0/2/4/6, the "tower shields" grade +2), not from an
  item in the hand. Tests: level 1, heavy armor + tower shields grade -> 8; level 3 -> 9; without shield proficiency -> 6.
- Shields [OWNER, Q28]: the shield bonus (layer "shield") comes from the shield held in a hand. A shield card has a type:
  light / heavy / tower. Heavy and tower shields ALSO add their shield bonus to the balance max while in a hand
  (in the bag: no). Tests: heavy shield +2 in hand -> balance max +2; in the bag -> +0; light shield -> +0.
- Shield proficiency ranks [OWNER, package 8 D1] (buy_shield_grade, 100 per rank):
  rank 0 (none) = cannot use shields; rank 1 (light) = light shields without penalty; rank 2 (heavy) = heavy shields
  without penalty AND a heavy shield in hand adds its shield bonus to the balance max; rank 3 (tower) = tower shields
  without penalty AND a tower shield in hand adds its shield bonus to the balance max AND parry +2 (from the grade,
  counted once). Light shields never add balance. Below the shield's rank: no balance bonus. Tests: every rank x
  light / heavy / tower.
- Non-proficient armor / shield [OWNER, package 9, closes Q34]: wearing armor or holding a shield with a proficiency
  rank below its type (armor: light 1, medium 2, heavy 3; shield: light 1, heavy 2, tower 3) applies its Str/Dex skill
  penalty (after the masterwork reduction, doubled if broken) ALSO to every attack roll while worn / held. Proficient:
  no attack penalty. An item without a category counts as light [accepted, Q42]. Tests: every rank x type for
  armor (-2) and shields (-3); masterwork -3 -> -2, broken -> -4; the weapon attack gets it too; a shield in the bag
  gives none.

## Languages [OWNER confirmed]
- First native language free. Further native languages: buy with training or get narratively.
- CHEAP native purchase only while (number of native languages) < Int MODIFIER; otherwise the EXPENSIVE option.
  Int +2: 1 free + 1 cheap = 2 native. Int +3: 1 free + 2 cheap = 3 native. Int +1 or less: only the expensive option.
- Prices [OWNER confirmed, package 4]: cheap 50, expensive 100.
- Non-native language (verbatim): "Выучить язык - 30*число проектов от ближайшего родного."
  Test: 1 project -> 30, 3 projects -> 90. The number of projects is entered at the purchase (no language map yet).
- Native (verbatim): "Сделать язык родным - 50 (если родных меньше Инт). Сверх этого числа - 100." ("Инт" = Int
  MODIFIER, owner confirmed earlier.) Making an already known language native: rule only, no command yet.
- Old code compared with the Int SCORE (not the modifier): bug.
- Tests: Int mod 2, natives 1 -> next native 50; natives 2 -> 100. Int mod 3, natives 2 -> 50; natives 3 -> 100. Int mod 1, natives 1 -> 100.

## Other purchases [OWNER, package 4, verbatim; commands since package 15, see below]
- "Каждый уважающий себя приключенец старается держать себя в форме, оттачивать свое владение оружием, изучать
  подходящие заклинания и подобное. Для этого раз он может обменивать комфорт очки тренировок по курсу (ЛВЛ+1)*5."
  ((level+1)*5 = 5 + 5*level, same as "Comfort for training" above.)
- "Новый прием боя - 250 очков (Вы разрабатываете прием для оружия, которым владеете. Прием на 0-3 уровней сложнее,
  чем выбранный прием в ветке данного оружия. Вы можете выбирать в качестве стартового приема стандартные, вроде
  "базовая атака", "захват", "двойная атака". Минимальный уровень равен требуемому уровню владения оружием. Суть приема
  определяет мастер, и обычно она связана с прошлым приемом в "ветке")."
- "Новая черта или изменение классовых способностей - 200+ очков, по договоренности с ДМом. Вы можете придумывать
  бонусы самостоятельно."
- "Квалификация с предметом - 50*N, где N - указанное в предмете число (требуется для специфических предметов, чтобы
  раскрыть их более потенциал)."
- "Получить +1 реакцию - 200*новое число реакций." Test: 1 reaction -> 2nd costs 400.
- [OWNER, package 8] Command buy_hp: +1 hit-die HP for 50, up to die * level (progression.md "Max HP").
- "Увеличение макс хитов на 1 - 50 очков. Увеличивать макс хиты можно до капа, который можно было получить естественным
  образом (классовый КХП*уровень + ВЫН*уровень)." (КХП = class hit die, ВЫН = Con modifier.)
- "Новое заклинание - 20 + 10*круг^2. Классы с книгой или возможностью изучить заклинание от учителя или из свитка
  получают скидку в 2 раза." Test: circle 2 -> 60, with a book 30.
- "Повысить курс трансформация внимания на 1 - 200 (имеется в виду трансформация внимания в ОВ и пр., складывается с
  бонусом от характеристики)."

## Base points [OWNER, Q22]
- One base point costs 100 training. Max base points = 10 * level (start 5).

## Seeds, quirks, stories
- Seed ("new seed" (1), price 200): adds a seed entry to the Quirks tab (a separate tab, plain list).
- Sprout seed: narratively obtain a quirk. Price (verbatim): "Получить зерно - 200." "Прорастить зерно - 200."
- Stories are NOT listed separately in the sheet; a story is part of a quirk. Quirk fields: Seedling, Court, Focus, Story name.
- A quest, if any, is entered by hand.

## Qualification
- Always tied to a specific item; does not work for other items. 50 training per level.

## Professionalism [OWNER confirmed]
- A separate number (professionalism level), bought with training (old code: 300 for the feature).
- Owner text (verbatim, package 4): "Профессионализм - 300 очков. Вы получаете специализированными 1/2/3/4 навыков из
  списка Вашего класса (для классов с 2+, 4+, 6+, 8+ скп). Если у класса прописана иной "профессионализм", то опция в
  классе заменяет данную опцию."
  [OWNER, Q29] This 300-point option applies only IF THE CLASS HAS NO PROFESSIONALISM OF ITS OWN.
  The "professionalism level" number above is a placeholder for classes without their own professionalism:
  do NOT develop it further (no new code for it).
- Cannot exceed character level.
- Class abilities (ONLY class abilities) may reference professionalism level instead of character level.
- Professionalism may also be a REQUIREMENT for activating items.
- Example: a wizard gets Mage Tower: gives professionalism x2 slots, spendable on narrative bonuses; effectively base bonuses.

## Attention course (spend 1 attention; Str/Dex/Con/Int/Wis/Cha = modifiers, never below 2 when converted into something useful)
Mechanical options:
1. Raise injury healing rating by Str (min 2) [already implemented, see injuries.md].
2. Get training as if spending comfort equal to Dex/2 (min 1, rounded to tenths; Dex 3 -> 1.5 comfort).
   Lives next to "spend comfort for training".
3. Get Con (min 2) time points (OV); or double that, but then spend them only on professions, closing drives or lenses.
   OV = time points, a NARRATIVE resource. Unspent OV burn at "end of cycle" (the new cycle starts).
4. Get 0.2 * Int (min 0.4) base points. Fractions are kept (never lost). Example: 5 attention at minimum = 5 * 0.4 = 2.0 = +2 max base slots. Max base = 10*level, start 5, or buy slots with training.
Narrative options (entered by hand when relevant):
1. Get Wis (min 1) quests from courts until the next long rest.
2. Story power options: IGNORE for now (owner).
- Resources implied: time points (OV, narrative, burn at end of cycle), base points as fractions. Professionalism level: see above.

## Purchase and progression commands [package 15]
Every command validates, spends training (a non-training source spends nothing), refuses with a reason, is journaled,
and never refunds. Prices are the constants of wp/core/training.py (data, not scattered literals).
- level_up(hp_roll): level +1, training +100 * the NEW level (progression.md), the hit-die roll of the new level
  (1..die; set_hp_roll edits it later). Refused without a roll or outside 1..die. RULES give no level cap (Q103). The
  current HP are not raised (Q111).
- exchange_comfort(n): n comfort -> n * (level + 1) * 5 training. Refused above the comfort the character has. An
  item / class bonus to the rate has no field yet (Q107).
- buy_attention_course: +1 for 200; it adds to the stat bonus of EVERY attention conversion (OV, OT removal, RL raise:
  assumption Q102).
- buy_reaction: 200 * the new number of reactions (1 -> 2 costs 400, 2 -> 3 costs 600). Character.reactions starts at 1.
- buy_seed(name): 200, a new seed (id from the name); sprout_seed(seed_id): 200, refused twice (the quirk itself is
  narrative).
- make_language_native(lid): first native free, 50 while natives < Int mod, else 100; refused when already native.
- promote_skill(name, to_tier): normal -> advanced 40 + 20 * other advanced or specialized; advanced -> specialized
  200 + 50 * other specialized; normal -> specialized pays both; refused for the same or a lower tier (skills.md).
- buy_professionalism(skills, class_skill_points): 300; class skill points 2+ / 4+ / 6+ / 8+ -> exactly 1 / 2 / 3 / 4
  chosen skills become specialized; refused below 2 points, for a wrong number of skills, for an already specialized
  skill, and a second time (assumption Q105). "Only classes without their own professionalism" and "skills from the
  class list" cannot be checked yet: there is no class data (Q104).
- learn_spell(name, circle, discount): 20 + 10 * circle^2, half with discount (a class with a book, or learning from a
  teacher or a scroll); circle 0..9. A minimal spell record (id, name, circle, source, cost, upgrades).
- buy_spell_upgrade(spid, name, metamagic): 25 * (1 + circle^2) per upgrade; three slots per spell; an upgrade takes 1
  slot, the second identical one 2 (each further identical one 1 more: Q106); a metamagic takes slots = its circles;
  refused when the slots do not fit.
- buy_combat_basics(wid): 50 / 100 / 150 for scale 1 / 2 / 3, once per node, refused for Basic/simple (weapons.md).
- buy_maneuver(name, ...): 250, an entry in the maneuver list (edit its tags and numbers with edit_maneuver). Its
  `source` parameter is the purchase source, so the maneuver's own source label is set with edit_maneuver (Q112).
- buy_item_qualification(iid): 50 * N (N = Item.qualification_n); refused without N or twice. What the qualification
  unlocks is not modelled (Q109).
- Tests: package 15 (test_pkg15.py), every price with the numbers above.
