# Package 36 report: owner fixes + the core ready for races (parts P1-P4)

The owner's file Wp_claude/RACES_SOURCE.md was committed first (91a4e2d).

## Done
P1 (finished; fixes of the owner review of package 35):
- 1.1 tests/PACKAGE35_REPORT.md rebuilt (a docs step of package 35 P2 had emptied it: it opened the file for writing
  before reading it). Restored from the P1 commit, the package 35 commits, STATUS.md, ARCH/history.md and
  OPEN_QUESTIONS Q239-Q255. New test storage/test_reports.py: every report of package 23+ has the five fixed sections
  and is not truncated (the check is also run on a 3-line sample).
- 1.2 Decision 17: an unknown bonus type is untyped (counts as flat: stacks with everything); add_status and add_entry
  accept a typo like "moral" and the AC / attack / save views never raise. Q245 closed.
- 1.3 Settings and Catalog are top menus next to View and Help; each opens its own window with the existing page
  (wp/ui/page_window.py); the Settings and Catalogs tabs are gone from the right tab bar.
- 1.4 New tab Narrative (quests, courts, stories, quirks): list, the text on hover, Add / Set the text / Close or
  reopen a quest / Burn or restore a quirk / Remove through existing commands (add_note, edit_entry, burn_quirk,
  remove_entry: none was missing). Court quests are quests whose giver is the court (shown with its name). The Drives
  tab shows the drive's quest text (hover; a click on the quest state opens it).
- 1.5 Font / scale bug: after a change of font family, numbers font, size or scale the blocks kept their saved sizes
  while their content grew, so content stuck out and the right column overlapped the bottom strip. Now every block
  grows to at least the minimum its content needs (the saved size is the lower bound, nothing is saved), measured
  again after the new style sheet is polished; the layouts are invalidated. Test: three changes in a row, then no
  overlap, every block inside the window area and fitting its content; shots fonts_before / fonts_after.
P2 (finished; the engine "anything can change anything", D35):
- 2.1 Audit ARCH/rule_audit.md: rule numbers were already all data (test_rule_literals); the behaviours a race / feat /
  item may change are listed with how they are open now.
- 2.2 Formulas over the real sheet numbers (hp_max, mana_max, base_slots, pain, morale, balance / spirit / bp /
  comfort max, tagged_base_slots:<tag>), lazy and safe (one pass); the Sources dialog warns "cycle in formulas".
- 2.3 Effect conditions (hp_full, bp_full, in_combat, pressure =/>=/<= N, pain >= N, manual:<text> = a checkbox on the
  status and in the Feats tab) and situational texts (never in a total; a star and the hover on Parameters / AC cells;
  a row in the Sources dialog).
- 2.4 Rule switches in data (wp/rules_data/switches.json) read by one function: at_negative_hp, death_pain_cap,
  heal_percent, exp_percent, pain_reduction, natural_regen_percent, injury_points_reduction (a trigger action).
- 2.5 Triggers on feats, items, statuses, injuries, quirks: the events fire in dispatch (end_cycle, combat start /
  end, zero initiative, level up, rests, HP below 1) plus manual buttons (Feats tab "Trigger"); each becomes a
  reminder with an optional action button and Handled (reminders block); closed action list (triggers.json).
- 2.6 Item tags and the "held by" link (feat / status / quirk held by a feat, item, quirk, status or a text holder):
  "not backed" + a reminder, nothing removed.
- 2.7 Movement modes (effects move:<mode>, feet, quality in the note) on the speed hover. 2.8 Race languages (the
  first native). 2.9 Typed damage absorbers (absorber:<resource>, note = types; pools may absorb).
- 2.10 RULES/races.md (new, from the owner decisions), buffs.md, resources.md, narrative.md extended (the package text
  is consent); D35; view contract.
P3 (finished; a race in the character):
- 3.1 Catalog kind races (catalog_schemas.json): id, name (Russian, as feats.json) and name_en, module, type_tags,
  speed, effects, abilities (id, name, text, price, needs, effects, triggers, auto, held_by), statuses, pools,
  quirks, languages. The shipped entries live in one file per game module (wp/catalog/data/races/<module>.json),
  merged by the catalog store.
- 3.2 Commands take_race(race), change_race(race, confirm), buy_race_ability(aid) and the view race (decision 15):
  copies with the source race:<id>, stat changes and HP as effects, the change list confirmed, no refund, one undo
  step, the snapshot (a catalog change never changes a taken copy).
- 3.3 The Race tab replaces the placeholder: the view, Take race / Change race (with the confirmation list), Take of
  a priced ability, the empty state. The Class tab stays a placeholder.

P4 (finished; acceptance on the owner's 12 races):
- All 12 races of Wp_claude/RACES_SOURCE.md are catalog data in two module files (wp/catalog/data/races/godbound.json:
  Ankalian, Lomit, Ulstanger; ranniag.json: Azana, White maiden, Moon elf, Mordon, Reflected, Rahim, Silver elf,
  Skerde, Ragmal), written by the mechanisms above only (no per-race code). Names in Russian with name_en (as
  feats.json); ability texts in English as in the owner's source. The data files are the source (no generator in the
  repo).
- Two small engine extensions the races needed: a compound condition "a&b" (Reflected: in combat AND pressure 0) and
  "a later equal movement value replaces" (good flight keeps 20 ft but changes the quality). Both in P3's commit.
- tests/model/test_races36.py: per race a character with the race and hand numbers (below).

Coverage table (every ability -> how it is expressed):

| race | ability | expressed as |
|---|---|---|
| Ankalian | stats +2 Str / Dex / Con / Cha, +8 HP, speed 20 | effects (race feat), speed |
| Ankalian | Universality | text (decision 2) |
| Ankalian | Shadow of the crown | effects skill:diplomacy / empathy +2; trigger cycle_end "+2 comfort" with a button |
| Ankalian | Adrenaline | manual trigger (run_command spend_bp 2) + status "Adrenaline" (+2 all rolls); fatigue text |
| Ankalian | Life among horrors | text (narrative, decision 5) |
| Ankalian | languages Kerez | language, native |
| Lomit | stats +2 Con / Int, +6 HP | effects |
| Lomit | Universality | text |
| Lomit | Adaptation | text (see "cannot yet") |
| Lomit | Flexible mind | trigger cycle_end reminder; the extra Attention is text |
| Lomit | Power of rationality | situational +2 saves "vs magical effects" |
| Ulstanger | stats +2 Str / +4 Con, +10 HP | effects |
| Ulstanger | Northerner | text (see "cannot yet") |
| Ulstanger | Rage | effect damage_per_pain 1 (note: melee weapons) |
| Ulstanger | Necromancy poisoning | switch heal_percent -50; situational +6 "vs death effects and necromancy"; pain_cap +4 (dies at 12) |
| Azana | stats +2 Con / -2 Int, +12 HP | effects |
| Azana | Four-legged run | effect speed +10 with a manual condition "running on all fours" |
| Azana | Red sun sight | text |
| Azana | Dynamo | pool "static" (10 x level) as a typed absorber (lightning); the melee spend is text |
| Azana | Unkillable monster | switch at_negative_hp = status:confused; trigger hp_below_one -> status "static regeneration" (5 per tick, pays 2 static per tick from the pool) |
| Azana | End of session -4 injury points | manual trigger (reduce_injury_points 4) |
| Azana | Hungry monster | text (owner: the potion comfort is text) |
| White maiden | stats +2 Int / Wis, -2 Con | effects |
| White maiden | Sight of the dead, Copying, Possession, spying | text (owner: text) |
| White maiden | Puppet | effects pain_reduction 2, heal_percent -50, own temp HP "2 * level" while in combat, switch at_negative_hp = nothing |
| White maiden | the smoke form | PARKED (needs the creature card) |
| White maiden | Principledness | quirk "the principle" (text) |
| Moon elf | stats, +6 HP, speed 25 | effects, speed |
| Moon elf | Vanguard, State keeping, Meditation | text |
| Moon elf | Primal sight | situational -4 on rolls "vs blinding and similar"; text |
| Moon elf | Dance with blades | status with 1 charge + text (spirit by hand) |
| Moon elf | Shadow of Santerra | status with 2 charges + text |
| Mordon | -2 Int, +8 HP, speed 25 | effects, speed |
| Mordon | +2 any characteristic | six effects with manual conditions "Mordon +2 <stat>" (tick one) |
| Mordon | Blood cleansing, sense of aggression | text |
| Mordon | Midnight instinct | effect dex_loss_cells -1 on the back cells (7, 8, 9) |
| Mordon | Red sun sight | text |
| Mordon | Survival history (d20 table) | text with the table; six history abilities (price 0, taken by choice) |
| Mordon | 1 Feast of Ravens | effects Dex +2, speed +5; manual trigger "pressure -5: leave"; immunity text; buy-out 300 |
| Mordon | 2 Wall of Bones | effects Con +2, CMD -4; buy-out 300 gives CMD +4 back; Toughness / wounds / bleeding text |
| Mordon | 3 Banner of Blood | effects Str +2, DR 2 with the manual condition "mounted"; mount, skill, comfort text; buy-out 400 |
| Mordon | 4 Fallen of Dantalian | effects Int +2, mana +3, exp_percent -25; buy-out 500 (exp_percent +25); group / focus / slot / spells text |
| Mordon | 5 Goddess of Humanity | effect Wis +2; rerolls, healing, caster level, the -4 drawback text; buy-out 500 |
| Mordon | 6 Return to zero | effects Cha +2, base slots -5; buy-out 500 (+5); the rest text |
| Mordon | Golden grandeur | held-by: an extra history held by the jewellery item ("not backed" when lost) |
| Reflected | stats +4 Cha / -2 Int, +4 HP | effects |
| Reflected | Rebirth | manual trigger reminder + text |
| Reflected | Red sun sight, Prophecy | text (owner: prophecy text) |
| Reflected | Chameleon | effects disguise / stealth +4, diplomacy / empathy / bluff +2 (racial) |
| Reflected | Blessing of goddess Zero | effect rolls +4 with the condition "in_combat&pressure_eq:0" |
| Rahim | stats +2 Str / Con, -2 Int, +10 HP | effects |
| Rahim | Dragon wings | effects sleight / athletics / acrobatics +4; flight 20 average for 600, good flight for 300 (chain) |
| Rahim | Dragon tail | manual trigger reminder + text (see "cannot yet") |
| Rahim | Dragon sight | text |
| Rahim | Dragon scales | effects spell_resistance "12 + level", resist:fire 5, resist:lightning 5 |
| Rahim | Intent clothed in word | effects diplomacy / intimidate +4, bluff -6; word-breaking text (owner: text) |
| Rahim | languages Draconic | language, native |
| Silver elf | stats, +4 HP, speed 25 | effects, speed |
| Silver elf | Vanguard, Primal sight | text; situational -4 |
| Silver elf | Integrity | effects AC +2 dodge, CMB / CMD +4 with the condition hp_full; bleeding text |
| Silver elf | Pure mind | effect Will +2 with the condition bp_full; immunities and rest text |
| Silver elf | Dance with blades | status 1 charge + text |
| Silver elf | Eradication of filth | status 2 charges + text (the GM rolls) |
| Skerde | stats +2 Int / -2 Str | effects |
| Skerde | Sea dweller, hold breath | swim 15 for 100 (price), hold breath for 100 more (chain, text) |
| Skerde | Trophy collection | formulas tagged_base_slots:trophy: skills +N, saves + N / 2, Cha + N / 4 |
| Skerde | Thorough expedition | effect hp_max "min(base_slots, 4 * level)" |
| Skerde | Sense of the swell, sea predator | text |
| Ragmal | stats +2 Con / -2 Cha | effects |
| Ragmal | Burning gaze, Bottomless belly | text |
| Ragmal | Magic body | effect mana_max +6, absorber mana (before HP), Str "mana_max / 10" |
| Ragmal | Blessing of the goddess of people | effects load_mod +3, Fort +2 racial, balance_max +3, natural_regen_percent +100 |
| Ragmal | Heavy swing | manual trigger: 2 temp HP (run_command set_temp_hp 2) |
| Ragmal | Hunt for incarnations | trigger combat_start "spend 4 mana" (change_resource mana -4); the +1 fire / acid text |

Cannot be expressed yet (with the reason):
- Lomit Adaptation: "one level higher" for the comfort exchange and Attention needs a level offset of those two rules
  (no such target); text.
- Ulstanger Northerner: the feats Endurance and Toughness are not in the feat catalog; text until they are.
- Ulstanger Rage: damage_per_pain has no "melee only" scope (the note says it).
- Ankalian Adrenaline: "these BP come back only by a full rest" needs a per-source BP restore rule; text.
- Azana Dynamo melee spend (pool -> electric damage), regeneration off for a round after self-damage: text.
- Rahim Dragon tail: a natural attack record needs a natural weapon item (weapon groups are not touched now); the -2
  AC until the next turn needs a timed status; reminder + text.
- Ragmal mana training at 200 per unit: a training price rule per race (no override of the price table); Heavy swing
  "until the start of the next turn" (sets the "by button" temp HP to 2, no duration); Hunt's +1 fire / acid damage.
- Mordon drawbacks "-4 on the first five attacks", "no wound penalty", "double bleeding", "1 comfort less for fights":
  no counters / targets for them; text. Golden grandeur: the extra history is linked to the jewellery by hand.
- Moon / Silver elf charges: the recharge per combat / per full rest is not wired to a rest (the status has no
  source_ref); restore by hand.
- White maiden Puppet: "temporary HP at the start of each combat" is own temp HP 2 x level while in combat (the spent
  part resets only at the short rest); natural regeneration "to the minimum" has no value (text); the smoke form is
  PARKED (needs the creature card, the owner's summons notes later).
- "Two city languages" (most Ranniag races) and the "extra languages" of the Godbound races are not entered: the names
  are the player's choice / unclear (Q272); the player adds them.

## Tests and breaks
- P1: `run_all.py`: suites 92, passed 92, failed 0. `break_check.py`: entries 459, caught 458, missed 1
  (p32-block-size: the blocks now fit their content, so dropping the old setFixedSize changed nothing); the entry now
  breaks the lower bound of the fit (the saved size) and was re-run alone: caught. So all 459 are caught.
- New suites P1: storage/test_reports.py (3), model/test_pkg36a.py (3: untyped AC 12 + 1 + 2 = 15, Fort 3, melee 1; a
  feat with "luk" twice 12 + 2 = 14; the narrative commands), ui/test_p36a.py (5: top menus and their windows, the
  Narrative tab, the drive quest text, the font fit, shots narrative_*). Breaks tests/breaks/pkg36.py (P1: 9).
- P2: `run_all.py`: suites 94, passed 94, failed 0. `break_check.py`: entries 480, caught 479, missed 1
  (formula-unknown-names: the variable check line changed for tagged_base_slots); the entry was updated and re-run
  alone: caught. After that full run a recursion fix went in (a condition "HP is max" read while HP max is computed is
  now guarded, found by the P3 race smoke test); after it run_all again 94 / 94 and the 30 package 36 breaks re-run:
  30 caught. New suites: model/test_pkg36b.py (18: mana 25 -> Str + 2; skerde HP 12 / 34; the cycle;
  trophies 2 + 3 + 2 = 7 -> saves + 3; HP / BP max conditions; situational; pressure 0 -> +4; in combat; manual
  checkbox; heal 7, xp 75, pain 1, rest 11; Azana confused; cycle_end comfort + 2; manual injury points 6 -> 2 -> 0; HP
  below 1; held by; moves; languages; typed absorbers 7 lightning -> pool 3 / 5 fire -> HP 3 / mixed / mana 6 -> 2),
  ui/test_p36b.py (4: star and hover, the Sources rows, the speed hover, the status checkbox 3 -> 5, the trigger
  reminder and its button, the manual trigger; shots engine_*). Breaks P2: 21.
- P3: `run_all.py`: suites 96, passed 96, failed 0. `break_check.py`: entries 488, caught 487, missed 1 (p36-moves:
  its line changed: a later equal value replaces); updated and re-run alone: caught. New suites: model/test_pkg36c.py (5: Str 12 / Int 8 from effects with the base 10, HP 8
  + 6 = 14, speed 25, languages; the chain refused, wings 1000 - 600 = 400; the change list, Dex 12, no refund; undo;
  the snapshot), ui/test_race36.py (3: the tab flow, Class stays a placeholder, shots race_*). Breaks P3: 8.
- P4: `run_all.py`: suites 97, passed 97, failed 0. `break_check.py`: entries 496, caught 496, missed 0. New suite model/test_races36.py (14: per race the stats, HP at level 1, speed and the key
  effects by hand: Ankalian 17 HP + comfort 2; Lomit 15 HP, situational +2; Ulstanger 20 HP, heal 5 -> 10, death at
  12; Azana 21 HP, static 10 takes 7 lightning, confused at -3, OT 6 -> 2, speed 30 on all fours; White maiden 7 HP,
  pain 3 -> 1, temp HP 2 in combat; Moon elf 13 HP, -4 situational, charges; Mordon 16 HP, +2 Str by the box, history
  1 Dex 12 / speed 30, history 4 xp 75 and its buy-out, held by the ring, back cells keep Dex 12; Reflected 12 HP,
  initiative 0 / 4 / 0; Rahim 19 HP, SR 13, flight chain 1100; Silver elf AC 11 / 13, CMB 1 / 5, CMD 12 / 16, Will +2;
  Skerde 12 HP, trophies Cha 11 / Fort 3, swim 1900; Ragmal 9 HP, mana 20 -> Str 12, mana takes 4 damage). Breaks P4: 8.

## Changes to old rules
- P4: the shipped module files races/godbound.json and ranniag.json hold the 12 races; no other old rule changed.
- P3: old test ui/test_combat34.py c-tabs checks the Class placeholder (Race has content). Empty module files
  races/godbound.json and ranniag.json shipped (filled in P4).
- P2: old break breaks/core.py formula-unknown-names follows the new variable check.
- P2 (owner consent in the package text): new RULES/races.md; RULES/buffs.md "Formulas over sheet numbers, conditions,
  situational", "Triggers", "Held by"; RULES/resources.md "Rule switches of races and abilities"; RULES/narrative.md
  "Race narrative and end of session". Old test model/test_pkg14.py c-effect-bad-refused: the allowed variable list
  is longer. New stored fields: Item.tags / triggers, Feat.triggers / held_by / held_kept / text / needs, Status and
  Quirk triggers / held_by / held_kept (Quirk.source), Injury.triggers, Character.manual_conditions / trigger_notes /
  trigger_counter / race_id; Effect.condition / situational.
- No RULES change in P1. Old break breaks/pkg32.py p32-block-size follows the content fit. Old tests:
  ui/test_combat34.py c-tabs (12 tabs), ui/test_p35b.py b-second (taller, not exactly twice), ui/test_tabs35.py
  t-catalogs (the own window of the Catalog menu). Old test core/test_bonuses.py unknown-type: an unknown type is now untyped (decision 17),
  not rejected.

## Assumptions
- P4: Q270 race data language; Q271 Mordon choices; Q272 race languages; Q273 White maiden; Q274 charges.
- P3: Q268 taking a race; Q269 the Race tab.
- P2: Q259 formula variables; Q260 conditions; Q261 situational listing; Q262 at_negative_hp; Q263 trigger notes;
  Q264 held by; Q265 moves; Q266 typed absorbers; Q267 heal / exp percent.
- P1: Q256 top menus; Q257 the Narrative tab actions; Q258 the font fit.

## Open questions (ids)
- Closed: Q245 (owner decision 17). New: Q256-Q274; Q272 asks the owner (are the extra languages known?).
