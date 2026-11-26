# Package 35 report: Classic screen v2, fixes of the owner review + steps 6, 1b and the tabs (parts P1-P5)

All five parts are finished (P1-P5), each committed and pushed on its own. (Rebuilt in package 36 P1.1: a docs step of
P2 had emptied this file; the text below is restored from the P1 commit, the package 35 commits, STATUS.md,
ARCH/history.md and OPEN_QUESTIONS Q239-Q255.)

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
P2 (finished; ROADMAP step 6):
- Bottom strip (full width, the profile region bottom): OT, Pain, Morale (only while the combat flag is on; the scale
  with its sources, so it equals the Sources dialog), Speed, Encumbrance ("X of max", the category and both limits).
  Every cell opens the Sources dialog (new sources numbers ot, pain, morale: OT and pain read-only, morale rows act on
  morale_scale). "+ strip" adds the optional second strip (profile field strips; empty by default), "- strip" removes
  it; the "Journal" button opens the Journal tab.
- Journal tab: lines from the Session, newest first; filter by kind and by text; Undo / Redo through the Session
  stack; the mode switch short / full (full = with the archive, D29); a note field (new command journal_note: a
  journal line with the text, undo works). Read-only otherwise.
- Settings tab: language RU / EN, theme (shipped and own) and follow the system, font family / numbers font / size,
  UI scale, one-time hints (show all again, hints off), journal mode, quick grid cells and columns, tube style, editor
  mode, restore the default profile. Every control is an existing settings command (or the Session editor mode).
- The tab pages of the right column are built on first use (combat_tab.PAGES); the UI reads the core data it may not
  import (journal kinds, catalogs, setting ranges, layout warnings, the background file) through wp/app/ui_data.py.
P3 (finished; ROADMAP step 1b):
- Theme editor (View > Theme editor, or the Settings tab): all 56 colour tokens of the schema are listed (the tokens of
  ARCH/ui_gaps.md "Themes" were all present since package 31); live preview (a colour change of an own theme restyles
  the window at once); "Copy" makes an own theme and makes it active; "Reset to the shipped one"; "Remove" (own
  themes); follow the system; the WCAG 4.5:1 contrast warning (shown, never forbidding). The three shipped themes are
  never edited (the Session refuses shipped_theme). Own themes are stored in the settings data, not in code.
- Background: an optional own picture (the image registry, kind background; none by default) with a dimming slider
  (a black layer of alpha dim x 255 / 100) and "keep numbers readable" (the token background_overlay behind blocks).
- New Session.theme_command (theme_copy / theme_edit / theme_reset / theme_remove; saved at once, topic settings).
P4 (finished; tab content, ROADMAP step 7):
- Injuries, Drives, Inventory, Training, Rest, Skills, Feats, Catalogs tabs from existing views and commands (one or
  two actions each), empty states, "Expand" for Skills, Inventory, Training, Catalogs (never saved). Race and Class
  stay placeholders. No core view or command was missing.
P5 (finished; ROADMAP step 8):
- Layout editor (editor mode: View > Layout editor, or the Settings tab): Up / Down, another column, width / height
  with grid snap (layout_grid 10 px), show / hide, the tab rows pin, "Restore the default profile", the warnings (never
  forbidding). The window rebuilds its regions from the profile; editor-mode borders (block_border_edit).
- Found and fixed: after a few rebuilds the program crashed when it closed (the statuses filter buttons were
  connected through lambdas that kept a deleted block alive); they use a bound slot now (Q255).

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
- P2: run_all suites 84, passed 84, failed 0; break_check entries 429, caught 429, missed 0. New suites
  model/test_pkg35b.py (4), storage/test_ui_logic35b.py (6), ui/test_p35b.py (9: the demo strip OT 1, pain 1, speed
  20, load 0 of 129 (light up to 79), morale +3 only in combat, the journal tab, the settings round trip; shots
  strip_*, journal_*, settings_*). Breaks P2: 15.
- P3: run_all suites 86, passed 86, failed 0; break_check entries 435, caught 435, missed 0. New suites
  storage/test_themes35.py (8: contrast 21.0 / 4.48 / 4.54 by hand, copy / locked / reset, dimming 50 -> 128),
  ui/test_themes35_ui.py (3; shots themes_*). Breaks P3: 6.
- P4: run_all suites 88, passed 88, failed 0; break_check entries 444, caught 444, missed 0. New suites
  storage/test_ui_logic35c.py (7), ui/test_tabs35.py (8, one per tab; shots tab_*_dark). Breaks P4: 9.
- P5: run_all suites 89, passed 89, failed 0; break_check entries 450, caught 449, missed 1 (p32-live-settings: its
  text moved); the entry was updated and re-run alone: caught. New suite ui/test_layout35.py (7; shots
  layout_editor_*). Breaks P5: 6.

## Changes to old rules
- No RULES change. New effect target temp_hp (data); new stored field Character.temp_hp_spent (a base value).
- Old break changed: breaks/pkg34.py p34-square-spend (the spent square is greyed by its "spent" property, no longer
  disabled).
- Old tests changed: model/test_pkg34.py e-refusals (temp HP is no longer read-only: the read-only example is now the
  effects of a status), ui/test_combat34.py c-actions (spent squares stay clickable: the test reads the "spent"
  property) and c-combat (the Zero initiative button).
- P2: breaks/pkg34.py p34-placeholder-tab follows the new placeholder line. P4: ui/test_combat34.py c-tabs checks the
  Race placeholder. P5: breaks/pkg32.py p32-live-settings follows the new settings branch of window.on_topics.
- New core pieces: journal_note + Character.journal_notes, sources numbers ot / pain / morale, Session.theme_command,
  wp/app/ui_data.py.

## Assumptions
- P1: Q239 own temp HP order and rest; Q240 return one / round text; Q241 show-all and dialog sizes settings; Q242 tab
  wrap inside the block and the pin field; Q243 the AC audit cause; Q244 the no-sources hint.
- P2: Q246 strip cells and the second strip; Q247 journal_note; Q248 journal modes; Q249 the Settings tab content.
- P3: Q250 theme editor scope; Q251 the background picture. P4: Q252 tab actions; Q253 expand.
- P5: Q254 the layout editor; Q255 the crash at close (fixed).

## Open questions (ids)
- Closed: Q229 (owner). New: Q239-Q255; Q245 is a proposal (closed in package 36).
- Not built on purpose (package boundary): Lite, class / race / weapon-group content, PDF export, drag handles of the
  layout editor.
