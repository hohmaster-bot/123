# Package 35 report: Classic screen v2, fixes of the owner review + steps 6, 1b and the tabs (parts P1-P5)

## Done
P1 (finished; fixes of the owner review of package 34):
- 1 Zero initiative: the button "End of turn" is replaced by "Zero initiative" (ru "Нулевая инициатива" in ru.json); it
  runs the existing zero-initiative tick (actions and reactions back, durations tick); its hint says it is pressed
  when every character has acted and the circle ends, not tied to the own turn. No "end of turn" / "new round" text is
  left in the locale files or the UI docs (a test scans both locale files). "End of cycle" unchanged.
- 2 Actions one by one: a click on a free square spends one (smallest number first); a click on a SPENT square returns
  one (new commands return_action / return_reaction n=1: validation "nothing_spent", journal line, undo). Restore =
  restore all. The same for the reaction squares.
- 3 Sources dialog: rows of value 0 hidden by default with "Show all" (app setting sources_show_all; in the editor
  mode it starts ON and is not saved); a line says how many rows are hidden. Every sources view (AC layers too).
- 4 Dialogs scale to content: the Sources dialog and the small dialogs (value editor, amount, level-up roll) take the
  size of their content (the Sources table asks for its rows and columns, no empty area), keep the size the owner
  dragged them to (app setting dialog_sizes, one [w, h] per dialog id), never larger than the screen.
- 5 Tab bar wraps: the tabs flow onto further rows inside the tabs block and back when it is wider (no scroll, no
  clipping; the block height follows the rows). Editor mode: "Pin rows" / "- row" / "+ row" set the classic profile
  field tab_rows (0 = automatic). A resize never rewrites the saved layout (tested).
- 6 AC audit. Cause (reproduced with the demo after a level-up and with a fresh empty character): the core never
  disagreed; the cell showed its SECONDARY variant (melee WITH parry: 14 once the level-up raised the parry layer) as a
  bare small number under the big 13, while the Sources total and the flat-footed / touch line use the melee variant
  (13). Fix: the small number is named ("with parry 14"), the cell tooltip lists every variant, the Sources dialog of a
  cell names every variant. A test compares every place (cell, tooltip, Sources total and variants, flat-footed /
  touch line, flat-footed = the back cell) for an empty hero, the demo, a buff, a shield, morale on / off and level 3.
  Found in passing (not changed): add_status accepts an effect of an unknown bonus type and then the defense view
  raises (Q245).
- 7 Empty-state hint: a resource whose max is 0 with no source giving it a value shows "No sources - editor mode:
  click to add" under its tube (one-time hint no_sources: "Understood!" hides it; a click on the text opens the
  sources of that max).
- 8 Temp HP (owner, Q229 closed): new effect target temp_hp (data: sheet_targets.json) for the temp HP the character
  gives himself (manual source rows, own feats / items); it is added on read, damage spends it after the "by button"
  pool and before the buff temp HP (stored base value temp_hp_spent), the short rest clears it. The sources of temp HP
  are the button row, the own rows and the spent row; buff temp HP (an external effect) is a status: the Sources dialog
  names it in one line ("plus N from statuses"), never as a row. Q229 moved to decision_log.
- 9 Tests, breaks and screenshots (below).

## Tests and breaks
- P1: `python Wp_claude/tests/run_all.py`: suites 81, passed 81, failed 0.
- P1: `python Wp_claude/tests/break_check.py`: entries 414, caught 413, missed 1 (p34-square-spend: its text no longer
  existed because the spent squares stay clickable now); the entry was updated to the new code and re-run alone:
  entries 1, caught 1. So all 414 are caught.
- New suites: model/test_pkg35a.py (8: return 3 -> 1 -> 2 -> 3 and squares, reactions, undo, own temp HP 3 + 5 + buff
  4 = 12 with the sources total 8, the damage order 6 then 4 hand numbers, save / load, editable, AC variants 16 / 10),
  storage/test_ui_logic35.py (6, no Qt: zero rows, show-all start, fit sizes, flow rows 50 / 50 / 50, pinned 13 tabs,
  variant names), ui/test_p35a.py (8: Zero initiative, squares, zero rows 2 of 13, sizes 520 x 410 remembered and
  clamped, wrap 1 row wide / more rows narrow / pin, the AC audit, the hint, shots sources_rows_*, tabs_wrap_*,
  no_sources_* in the three themes).
- Breaks tests/breaks/pkg35.py (P1: 18).

## Changes to old rules
- No RULES change. New effect target temp_hp (data); new stored field Character.temp_hp_spent (a base value).
- Old break changed: breaks/pkg34.py p34-square-spend (the spent square is greyed by its "spent" property, no longer
  disabled).
- Old tests changed: model/test_pkg34.py e-refusals (temp HP is no longer read-only: the read-only example is now the
  effects of a status), ui/test_combat34.py c-actions (spent squares stay clickable: the test reads the "spent"
  property) and c-combat (the Zero initiative button).

## Assumptions
- P1: Q239 own temp HP order and rest; Q240 return one / round text; Q241 show-all and dialog sizes settings; Q242 tab
  wrap inside the block and the pin field; Q243 the AC audit cause; Q244 the no-sources hint.

## Open questions (ids)
- Closed: Q229 (owner). New: Q239-Q245.
