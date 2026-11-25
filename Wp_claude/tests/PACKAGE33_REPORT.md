# Package 33 report: experience and level-up rules, the resources block (Phase 5 step 2), fonts, level test

## Done
A. Experience and level-up (owner decisions; RULES/progression.md "Level up", training.md, narrative.md; D33):
- Constants exp.level_cost = 1000, exp.max_banked = 1999, progression.hit_die_min = 1 (wp/rules_data/constants.json).
- level_up needs 1000 xp (below: refused not_enough_experience), SPENDS 1000 as a log entry of kind "level_up"
  (the rest stays), level +1, training +100 * new level, the roll counts at least 1 (warning hit_die_min_used),
  reminders "distribute the drive points" and "you got X training". The level history keeps the XP before the cost.
- add_experience / edit_experience_entry count only up to 1999; the entry keeps what was entered (XpEntry.entered);
  the result carries the reminder exp.remind.excess (no refusal). The goal is always 1000; set_next_level_at and
  Character.next_level_at are retired (no migration: the old field is dropped on load). Undo works as before.
B. The resources block (wp/ui/resources_block.py, tube.py, tube_logic.py without Qt, dialogs.py, data/resources.json):
- HP, balance, spirit, mana, then the class pools (first three large, the rest compact in their own scroll area;
  pool_order / pools_large). Each row: label (mana: the overload chip), "cur / max" (over the max in the warning
  colour, not clamped), the horizontal tube (QPainter: glass body, liquid gradient, highlight, segment ticks by
  resource_segments; style glass | flat; size resource_size x ui_scale; auto-switch big -> medium -> thin bar with
  the number), the temp HP strip (bottom third, segments of 5, may be longer than the HP fill).
- Click on a tube = the value editor: "+N" / "-N" -> adjust_value, a number -> set_value (a pool: adjust_value by the
  difference), HP: the temp HP field -> set_temp_hp. Mechanics buttons: Take damage (amount + one of the 12 damage
  types -> take_damage), Heal (restore), Damage to balance, -1 / +1 (spirit, mana, pools), overload - / +. Own
  buttons: app quick buttons of group "resource:<id>" through Session.run_quick. Refusals / warnings / reminders: the
  i18n text in the block's message line.
- The resources view gained damage_types and buttons; the experience view gained can_level_up.
- The experience strip got "Level up" (enabled at 1000): "Raise the level?" -> the roll dialog (minimum 1) ->
  level_up -> the two reminders in a message box.
- The demo character now has a fuller sheet (Cha 12, BP 4, balance, spirit 7, overload 1, temp HP 4, 1000 xp spent
  on its level-up, 1450 xp banked). The first-run hint text names the resources block.
C. Fonts: app settings font_family, font_family_numbers (new) and font_size (now USED; closes Q216); qss.fonts:
  app > theme (optional token fonts.numbers) > system font, a font not installed falls back, ui_scale on top; applied
  live (settings topic).
D. "What changes with the level" suite (model/test_pkg33.py): levels 2 -> 3 and 4 -> 5 of a sample fighter: BAB,
  saves, parry, attention per cycle, comfort -> training, max base points, the HP cap, the formula variables level /
  lvl, the level-up training; qualification unchanged. Everything changes as RULES say.
  Bugs found and fixed: buy_base_slot above 10 * level failed with a bare ValueError (reason invalid_value): now the
  refusal base_at_max with its text; spend_charge did not name the topic "rest" (its panel changes; found by the
  topics fuzz test once level_up started refusing).

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 73, passed 73, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 373, caught 373, missed 0.
- New: model/test_pkg33.py (19 cases: 1000 -> 0, 1500 -> 500, 999 refused, 1700 + 500 -> 1999 (counted 299),
  cap at 1999 and on edit, 2 -> 3 gives 300, roll 0 -> 1, the two reminders, the log entry -1000, undo, D numbers),
  storage/test_ui_logic33.py (16 cases without Qt: parse_edit, edit_command, fill, ticks, temp strip, auto-switch,
  pool split, fonts family / numbers / size 14 x 1.5 = 21 / fallback / optional theme token), ui/test_resources.py
  (17 cases offscreen: tubes of the demo, +5 / -3 / 30, temp HP field, negative mana refused with text, Take damage
  6 fire -> HP 9 OT 3 pain 2, Damage to balance 3 -> 1, Heal 3 -> 14, -1 / +1, glass -> flat, auto-switch thin,
  four pools, own button, Level up disabled at 999 / enabled at 1000, the dialog -> level 3, xp 450, training 1500;
  screenshots tests/ui_shots/resources_dark.png, resources_light.png, resources_grey_blue.png).
- Breaks tests/breaks/pkg33.py (31); pkg26 p26-progress and pkg28 p28-level-up follow the new code.

## Changes to old rules
- RULES (owner consent in the package text): progression.md "Level up" (cost 1000, cap 1999, roll minimum 1,
  reminders), training.md level_up line, narrative.md "Experience" (the hand-typed goal replaced).
- Old tests changed: every level_up test now banks 1000 xp first (pkg 15, 17, 25, 26, 28); pkg 15 b1-refusals (roll 0
  -> 1 now allowed); pkg 26 x-history (1700 xp, XP before the cost), x-progress / x-no-auto / x-roundtrip (no goal
  command), history id lv2; ui/test_shell s-xp (1450 of 1000 = 100 %) and s-command (add_experience instead of the
  goal).
- The app setting resource_size default changed to horizontal tubes (Q222).

## Assumptions
- Q222 tube sizes and auto-switch numbers; Q223 own buttons by group, pool editor, temp field; Q225 history XP before
  the cost, edit cap; Q226 roll below 1 counts 1 with a warning; Q227 font fallback order and small / large ratio.

## Open questions (ids)
- New: Q222-Q227; Q224 is a proposal (a plain-number command for mana max). Closed: Q216 (font_size is used).
