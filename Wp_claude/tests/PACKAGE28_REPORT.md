# Package 28 report: log_max removal, drives, overlay spike

## Done
- A. The unused app setting log_max is removed from the settings schema (Q188 closed). The journal settings stay:
  journal_mode, journal_short_max, journal_archive_at 1000, journal_archive_keep 100 (owner confirmed).
- B. Drives (RULES/narrative.md "Drives (package 28)", owner):
  - catalog kind drive_types (wp/catalog/data/drive_types.json): the 10 types with the owner's Russian descriptions
    verbatim; names in wp/i18n (drive_type.*);
  - Drive record: dtype, quest, quest_state (none / taken / closed), comfort_received; add_drive(dtype) and
    edit_drive take them; set_drive_quest(did, quest, state, comfort_received);
  - view per drive (wp/commands/drive_cmds.py): type, level, notes, principle, taboo_required, principle_missing,
    quest_allowed, quest_mandatory, quest_missing, obsessed, spirit_bonus hint, obligation and penalty text keys;
    drive_summary: distributed X of drives.start_points 12 (a hint only) and the reminders;
  - drive_buy_up (3 comfort) / drive_buy_down (2 comfort), level 0-5 (out_of_range), not_enough_comfort;
  - level_up result: the reminder "distribute the new drive points"; end_cycle result: "open quest of drive X,
    penalty: <text>" for every drive at 3+ with a taken quest; attention per cycle unchanged;
  - level texts (obligation / bonus / penalty, "You are obsessed") in en.json and ru.json;
  - constants drives.start_points 12, buy_up_cost 3, buy_down_cost 2, quest_allowed_level 3,
    quest_mandatory_level 4, spirit_bonus {2: 1, 3: 2, 4: 3, 5: 4}; parameter kinds and topics for the new commands.
  - The topics test found one more invisible change (spend_charge on a feat): the sheet view now lists feats with
    charges and cooldown; set_item_hp also refreshes spells.
- C. Overlay spike `tools/overlay_spike.py` (179 lines, PySide6 + ctypes): frameless, on top, opacity slider, drag
  strip, corner grip, stub rows and HP +1 / -1 buttons, Ctrl+Alt+O click-through (WS_EX_TRANSPARENT), Ctrl+Alt+H
  hide / show (RegisterHotKey), state in tools/overlay_spike.json (git-ignored). Guide: Wp_claude/OVERLAY_SPIKE.md.
  Checked here: py_compile, and `python tools\overlay_spike.py --smoke` (PySide6 6.12 is installed: the window
  opens, HP -1, click-through on / off, hide / show, close; prints "smoke: ok"). Over a real browser, the hotkeys
  from another window and the click-through to the browser were NOT checked here: that is the owner's test.

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 66, passed 66, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 301, caught 299, missed 2 (p23-cache-scope, p23-cache-clear "not applied": test_perf.py failed once on the clean copy, a timing budget under load; run again alone: test_perf 8/8, both entries caught). The 2 drive entries of pkg25 were moved to drive_cmds.py first (caught).
- New suite model/test_pkg28.py (18 cases: level 1 no flags; level 2 principle missing; level 4 quest missing;
  level 5 obsessed; level 7 + two drives at 4+ -> 5 attention; taken quest -> end-of-cycle reminder, closed -> none;
  buy up at comfort 3 -> +1, comfort 0; at 2 refused; down at 0 refused; down costs 2; 14 of 12 -> hint only;
  level_up reminder). New breaks tests/breaks/pkg28.py (12).

## Changes to old rules
- None of the numbers. RULES/narrative.md: the "Drives (package 28)" section appended (owner consent in the package).
- Old test changed: test_catalogs w-kinds lists drive_types.

## Assumptions
- Q191 Russian level texts and type names are Claude's translation (owner may edit); Q192 buying a level costs the
  player 3 / 2 comfort; Q193 thresholds as constants; Q194 reminders as text keys; Q195 custom drives and repeated
  types allowed; Q196 the spike lives at the root tools/.

## Open questions (ids)
- Q188 closed. New assumptions to confirm: Q191-Q196.
