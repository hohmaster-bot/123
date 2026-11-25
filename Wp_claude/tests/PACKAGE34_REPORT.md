# Package 34 report: Classic screen v2 steps 3 and 5 (two parts)

## Done
Part 1 (committed and pushed first: 2393c9a):
- 1A Sources of every number (D34): view `sources` (number=...; wp/model/sources.py) for HP max, balance max, spirit
  max, mana max, every pool max, temp HP, melee / ranged attack, initiative, CMB, CMD, Fort / Ref / Will, every AC
  cell, speed, load (encumbrance limits), attention. Rows: rule / stored / effect / manual, value, on, counted (a
  bonus that does not stack is shown, not counted), the RULES file of a derived row. The total is the sheet's real
  number (never stored); the counted rows add up to it for every number. Existing breakdowns reused (stats lines,
  attack_number lines, cell_lines; the "bonuses" line opened into one row per source).
- Manual rows: Character.source_rows; commands source_add / source_edit / source_toggle / source_remove (journal,
  undo), allowed only in the editor mode (Session.editor_mode, View > Editor mode; refusal editor_mode_needed). An ON
  row is a flat effect on the number's effect target (new targets attack_melee / attack_ranged). Temp HP sources are
  read-only (no effect target: Q229). Derived rows are corrected by manual rows, never written. Mana max is never a
  typed number (Q224 closed): the demo gets its mana from a manual row "Demo mage" +8 (mana 5 / 8).
- Sources dialog (wp/ui/sources_dialog.py): opened by a click on any Parameters cell, any AC cell and the "cur / max"
  text of a tube; read-only outside the editor mode; in it value / on / remove of manual rows and Add.
- 1B Parameters block (3x3: melee, ranged, initiative / CMB, CMD, load / Fort, Ref, Will; the layout item may carry
  its own "cells"); load "X of max" + light / load / overload, overload in the danger colour.
- 1C AC block (3x3 zones, "you" in the middle naming the shield side; primary large, secondary small; shield cells
  with the ac_shield border and the "[shield]" mark; flat-footed / touch line).
- 1D Small window: halve the gaps, hide captions, hide details, then scroll; the saved layout is never rewritten.
Part 2:
- 2A Statuses block (filter All / Active / Favourites, On / End, star, duration and charges, a click = the buff's
  effects in the Sources dialog), Favourites block, Reminders block (standing + one-shot reminders of results kept
  until dismissed: Session.reminders_view / dismiss_note).
- 2B Tab bar (13 planned tabs, only Combat has content; the others show a placeholder) and the Combat tab: Start /
  End combat, End of turn, End of cycle, round, numbered action squares (smallest first, spent grey), restore,
  reaction squares, attacks list (use_attack), quick grid (Session.quick_view: quick_cells 4-16, quick_columns).
- Found and fixed: removed list widgets stayed visible (they were only deleteLater-ed) and covered the top of a block.

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 78, passed 78, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 396, caught 396, missed 0.
- Part 1 (after its commit): run_all 76 / 76, break_check 387 / 387.
- New suites: model/test_pkg34.py (16: hand totals of every number, rows add up, no hidden remainder, stacking,
  add / edit / off / remove 11 -> 14 -> 16 -> 11 -> 11, editor gate and undo, refusals, not stored, Q224, attack
  numbers 4 / 7 / 3 / 6 / morale 4 -> 6, Dex source 7 and a manual row 8, load borders 79 / 80 / 129 / 130),
  storage/test_ui_logic34.py (10, no Qt), storage/test_ui_logic34b.py (6, no Qt: filters, smallest first, grid 4-16,
  tabs), ui/test_screen34.py (8: the demo numbers, AC 13 / back 10, shield cell 15, clicks open sources, editor
  changes Will 0 -> +2 -> +3 -> 0 -> undo +3, overload red, small window level 3, shots parameters_*, ac_*,
  sources_*), ui/test_combat34.py (9: filters and favourite, On / End, buff effects, one-shot reminder 549 of 1000,
  action squares 1 then 2, reaction, combat round 1 -> 2, quick grid 8 -> 12 and Drink 5 -> 6, tabs, shots
  statuses_*, combat_*).
- Breaks tests/breaks/pkg34.py (23).

## Changes to old rules
- No RULES change. New effect targets attack_melee / attack_ranged (data: sheet_targets.json); the general attack
  numbers got the line "bonuses" (0 without such effects: no number changed).
- Old tests changed: ui/test_resources.py (the demo mana is 5 / 8 now),
  ui/test_shell.py s-command (the combat tab also reads sheet), app/test_topics.py (the sources view is re-read on any
  topic: Session.ANY_TOPIC_VIEWS).

## Assumptions
- Q228 derived rows corrected by manual rows (flat); Q230 attack targets and load_mod; Q231 editor mode is a Session
  state; Q232 small-window steps; Q233 AC primary / secondary and base row; Q234 one-shot reminders not saved; Q235
  three blocks; Q236 square click spends one; Q237 quick grid buttons; Q238 injuries have no effects view.

## Open questions (ids)
- New: Q228-Q238; Q229 is a proposal (an effect target for temp HP). Closed: Q224 (owner: mana max only from sources).
- Not started on purpose (package boundary): the bottom strip, the other tabs' content, the layout editor, the theme
  editor, Lite.
