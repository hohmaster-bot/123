# Package 30 report: core data of the Classic screen v2

## Done
Rows of ARCH/ui_gaps.md that are a command, a view field or a Session function (owner decisions 1-5):
- Load (gear.md "Load display", Q197 closed): `items.load` = carried_l, light_max_l, heavy_max_l, category
  (light / heavy / overload), label key `load.<category>` (light / load "Нагрузка" / "you are overloaded and can
  only drag"), text ("load.of", (carried, max)).
- General attack numbers (combat.md "General attack numbers", Q198 closed): `sheet.attack_melee` /
  `sheet.attack_ranged` {total, lines, source, weapon}: BAB + stat mod (melee str, ranged dex) + pain (always) +
  morale (only in combat); a source "record:<rid>" takes the record's to-hit and names the weapon;
  `set_attack_source(kind, source)`; Character.attack_sources.
- Pain / morale check (decision 3): the code already counts pain on every roll and morale only in combat
  (`core.derived.morale_bonus(scale, combat_active)`); nothing changed; `combat.morale_active` added.
- `adjust_value(resource, delta)`: hp, balance, bp, comfort, spirit, mana, overload, pool:<id> ("pool" = the first
  pool); a correction without mechanics; negative refused except HP; over max kept (over_max).
- `Session.run_quick(button | id)`: action or macro steps as ONE undo step; a refused step rolls the macro back
  (params step); "set / add / subtract X" = set_value / adjust_value steps.
- `defense.shield_side`, `defense.cell_lines` (layer parts per cell), `defense.cell_labels` (i18n `ac_cell.1..9`:
  front-left ... back-right, ru and en).
- Cell sources: `layout.resolve` knows `stat:<fort|ref|will|initiative|cmb|cmd|attack_melee|attack_ranged>` and
  `counter:<ot|pain|morale|speed|attention|ov|overload|load>`; `Session.cell_sources()` lists every source (Q207).
- `Status.note` shown in the container entry; favourite abilities `Character.favorites` + `set_favorite(kind, oid, on)`;
  `statuses.favorites` {statuses, abilities}; `statuses.reminders` (drive reminders + open drive quests, Q204).
- `combat.action_squares` / `combat.reaction_squares` ((n, spent), ...): spending takes the smallest numbers first.
- Classic profile fields `quick_cells` (4-16, default 8), `quick_columns` (1-16, default 4, Q203), `strips` (a second
  bottom strip); the default profile carries them.
- Class: `sheet.class` = the class snapshot; no race view (no race data in the core, Q206).
- Topics for the new commands; the topics test found the new dependencies (drive commands now refresh statuses for
  the reminders row; cast_spell refreshes rest).

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 67, passed 67, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 315, caught 314, missed 1 (p27-topics-damage: the random topics test no longer reached a take_damage that changes the attacks view; a deterministic case t-damage added to app/test_topics.py: the entry is caught alone). The final full run after package 31 is in PACKAGE31_REPORT.md.
- New suite model/test_pkg30.py (23 cases, numbers by hand: Str 14 -> limits 79 / 129 L, 40 L light, 100 L load,
  130 L overload; melee +4, ranged +7, Dex melee +7, pain 1 -> +3 / +6, morale 4 in combat +6; mana 12 + 3 = 15,
  HP 5 - 8 = -3, pool 7 + 10 = 17 over max, refusals; macro one undo step and rollback; squares; shield left cell 4
  = 12, right = 10; labels; note; favourites; reminders; cell sources; quick grid). Breaks tests/breaks/pkg30.py (14).

## Changes to old rules
- RULES/gear.md "Load display" and RULES/combat.md "General attack numbers" appended (owner consent in the package);
  no old number changed. Pain and morale already matched the owner decision: no code change there.
- Old tests: app/test_topics.py gained the case t-damage (no expectation changed).

## Assumptions
- Q202 "pool" = the first pool; Q203 quick grid defaults; Q204 standing reminders only; Q205 favourite kinds;
  Q206 no race view; Q207 cell sources as a Session function; Q208 the stat-source attack has no typed bonuses.

## Open questions (ids)
- Q197, Q198 closed. New: Q202-Q208 (assumptions).
