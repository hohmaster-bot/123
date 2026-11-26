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

## Tests and breaks
- P1: `run_all.py`: suites 92, passed 92, failed 0. `break_check.py`: entries 459, caught 458, missed 1
  (p32-block-size: the blocks now fit their content, so dropping the old setFixedSize changed nothing); the entry now
  breaks the lower bound of the fit (the saved size) and was re-run alone: caught. So all 459 are caught.
- New suites P1: storage/test_reports.py (3), model/test_pkg36a.py (3: untyped AC 12 + 1 + 2 = 15, Fort 3, melee 1; a
  feat with "luk" twice 12 + 2 = 14; the narrative commands), ui/test_p36a.py (5: top menus and their windows, the
  Narrative tab, the drive quest text, the font fit, shots narrative_*). Breaks tests/breaks/pkg36.py (P1: 9).

## Changes to old rules
- No RULES change in P1. Old break breaks/pkg32.py p32-block-size follows the content fit. Old tests:
  ui/test_combat34.py c-tabs (12 tabs), ui/test_p35b.py b-second (taller, not exactly twice), ui/test_tabs35.py
  t-catalogs (the own window of the Catalog menu). Old test core/test_bonuses.py unknown-type: an unknown type is now untyped (decision 17),
  not rejected.

## Assumptions
- P1: Q256 top menus; Q257 the Narrative tab actions; Q258 the font fit.

## Open questions (ids)
- Closed: Q245 (owner decision 17). New: Q256-Q258.
