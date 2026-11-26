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

## Changes to old rules
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
- P3: Q268 taking a race; Q269 the Race tab.
- P2: Q259 formula variables; Q260 conditions; Q261 situational listing; Q262 at_negative_hp; Q263 trigger notes;
  Q264 held by; Q265 moves; Q266 typed absorbers; Q267 heal / exp percent.
- P1: Q256 top menus; Q257 the Narrative tab actions; Q258 the font fit.

## Open questions (ids)
- Closed: Q245 (owner decision 17). New: Q256-Q269.
