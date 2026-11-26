# Modes (D3, D20)

Exactly TWO modes: Classic and Lite (D20). There is no split mode. The overlay is not a separate mode:
it lives inside Lite (Lite = overlay; it is switched on there).
Two exclusive modes over the same core state. Exactly one is active. Enabling one disables the other.
Each mode has its own settings (separate profiles, nothing shared except language/theme if the owner wants).
Both modes have an edit mode; it works differently in each.

## Classic
- Normal window, in taskbar, reachable by Alt-Tab, full screen. Whole character sheet, easy to read.
- Editors open inside the window (pages/tabs), not as floating windows.
- Global hotkey shows/hides it: Ctrl+Shift+W.
- Edit mode: forms and lists inside the sheet.
- Screen layout v2 (owner approved, package 29, binding): `UI_WISHES.md` section "Classic screen v2"; gaps of the
  core for it: `ARCH/ui_gaps.md`. Regions: a full-width experience strip (top); the left column = avatar + resources;
  the middle = the AC block and the Parameters block on one row, then buffs / statuses, favourites, reminders; the
  right column = tabs (Combat by default); a full-width bottom strip (+ an optional second strip). Classic uses
  columns and grid-snapped cells; free placement only in Lite. Adaptation to a small window never rewrites the saved
  layout (D31).

## Lite (the overlay)
- Frameless always-on-top panels on the desktop. Empty space is click-through.
- Panels are user-chosen: chip groups, action buttons, log, mini-stats. Each has position, size, opacity.
- Lock mode (clicks only) vs edit mode (drag/resize/choose panels).
- Classic and Lite have different interfaces and different editors; no shared editor window.

## Tray
Switch mode (Classic <-> Lite), toggle Lite (overlay) edit mode, quit.

## Panel contract
- A panel type = id + factory + config schema, registered in a panel registry.
- Reads state from core, emits commands only (D5). Re-renders on the core `changed` signal.
- Panel types may be reused by both modes; placement and config are per mode.

## UI profile (per user, not per character)
Two independent blocks: `classic` and `lite` (Lite = the overlay: panels, positions per monitor, opacity, hotkeys), plus
language (RU / EN, D4) and theme.

## Risks for the spike
- Exclusive-fullscreen games draw above any overlay; borderless/windowed are fine.
- Multi-monitor and DPI scaling; positions must survive monitor changes.
- Global hotkey needs Win32 `RegisterHotKey` (Qt has no built-in global hotkey).

## Classic window shell (package 32, D32)
- Start: `python run_wp.py [--data DIR]` (wp/ui/app.py). Data folder <home>/WipeFinder (characters/, settings/; Q214).
  On start: the last character (app setting last_character), else the demo character (wp/ui/demo.py: plain Session
  commands from wp/ui/data/demo.json; name "Demo", "Demo 2" ...).
- wp/ui/window.py MainWindow: regions from the classic profile panel items: dock top = the experience strip, left /
  center / right = the three columns, bottom = the bottom strip; inside a region by position y then x; center items
  with the same y share a row (Q215). Column blocks keep their saved size; strips have the saved height and the full
  width; a too small window scrolls for now (the adaptation of UI_WISHES point 12 comes later, Q219).
- wp/ui/blocks.py: a block = a frame with its translated title (registry title); real data so far: the experience strip
  (training.experience: glass bar progress_pct, total, goal; the "Experience log" button is disabled until the journal
  tab) and the identity block (sheet: name, class, level; a portrait frame). Every other block names the views it
  will read (registry.reads).
- Menus (wp/ui/menus.py): Character (New demo character, Open, Save, Save as, Exit), View (Theme: the theme list +
  Follow the system; Language RU / EN; Scale 80-150 %), Help (Show hints again). Save as into the characters folder
  makes a new character; elsewhere it exports a copy (Q218). Open from another folder imports the file first.
- Live settings: theme, language, scale and follow-the-system go through session.settings (saved at once); the
  Session sends the topic "settings" and the window re-applies the style sheet (qss.build_qss), the texts and the gaps.
- The first-run hint (hints.json first_run) shows until "Understood!" (hint_dismiss); Help > Show hints again =
  hints_reset. The window geometry is the app setting window_classic (saved on close).
- Errors: a refusal is shown as its i18n text (a damaged file offers the newest valid backup); an unexpected error
  prints the traceback to the console and shows the short text shell.unexpected.
- Tests: tests/ui/test_shell.py (offscreen; screenshots of each shipped theme in tests/ui_shots/).
- Package 33 (D33): the RESOURCES block (wp/ui/resources_block.py, tube.py, tube_logic.py without Qt, dialogs.py,
  data/resources.json): HP, balance, spirit, mana, then the class pools (first three large, the rest compact in their
  own scroll area). A row: label (mana: the overload chip), "cur / max" (over the max in the warning colour, never
  clamped), the horizontal tube (glass / flat; segment ticks by resource_segments; HP: the temp HP strip along the
  bottom third, segments of 5), buttons. Tube size = resource_size (w, h px at 100 %) times ui_scale; the auto-switch
  shrinks the height to fit the block and picks big / medium / thin (thin = the number inside). A click on a tube =
  the value editor ("+N" / "-N" -> adjust_value, a number -> set_value; a pool number -> adjust_value by the
  difference; HP: a second field -> set_temp_hp). Buttons: HP Take damage (amount + one of the 12 damage types) and
  Heal (restore), balance Damage to balance, spirit / mana / pools -1 / +1, mana overload - / +; own buttons = app
  quick buttons with group "resource:<id>" (Session.run_quick). Refusals, warnings and reminders show as i18n text
  in the message line of the block. The experience strip got the Level up button (enabled at 1000 xp: ask, roll
  dialog with minimum 1, level_up, the reminders in a message box). Fonts: app settings font_family,
  font_family_numbers, font_size (qss.fonts; ui_scale on top). Tests: tests/ui/test_resources.py (shots
  tests/ui_shots/resources_<theme>.png), storage/test_ui_logic33.py (no Qt).
- Package 34 part 1 (D34): the SOURCES dialog (wp/ui/sources_dialog.py) fed by session.view("sources", number=...):
  total, rows (name, kind + rule file, value, on; "does not stack" for a bonus that loses), read-only outside the
  editor mode (View > Editor mode = Session.set_editor_mode, topic "editor"); in it a manual row's value / on can be
  changed or removed and a new manual row added (source_* commands; journal + undo). Opened by a click on any
  Parameters cell, any AC cell and the "cur / max" text of a tube. PARAMETERS block (wp/ui/screen_blocks.py,
  params_logic.py without Qt, data/screen_blocks.json; the layout item may carry its own "cells"): melee, ranged,
  initiative / CMB, CMD, load ("X of max" + light / load / overload, overload in the danger colour) / Fort, Ref, Will.
  AC block: 3x3 zones (cell 5 = you, naming the shield side), primary variant large, secondary small, zone labels;
  shield cells get the border token ac_shield and the mark "[shield]"; flat-footed / touch line. Small window
  (window.adapt): halve the gaps, hide block captions, hide details, then scroll; the saved layout is never touched.
  Tests: model/test_pkg34.py, storage/test_ui_logic34.py, ui/test_screen34.py (shots parameters_*, ac_*, sources_*).
- Package 34 part 2: STATUSES block (wp/ui/status_blocks.py, combat_logic.py without Qt): filter All / Active /
  Favourites, a row per container entry (name = its effects in the Sources dialog, "status:<sid>", read-only; the
  rounds / until the end of combat / no end / off and charges; On = activate_status, End = remove_status; the star =
  set_status_favorite). FAVOURITES block: favourite statuses (chips) and abilities (a click removes the star:
  set_favorite). REMINDERS block: Session.reminders_view = the standing reminders + the one-shot reminders of command
  results (Session.notes, not saved; topic "reminders"; dismiss = Session.dismiss_note). TABS block: the 13 planned
  tabs (data/screen_blocks.json or the layout item's "tabs"); only Combat has content, any other tab shows its
  placeholder in the combat block. COMBAT tab (wp/ui/combat_tab.py): Start / End combat, Zero initiative (the tick:
  pressed when every character has acted and the circle ends; package 35), End of cycle, the round; numbered action
  squares (a click on a free one spends one, the core spends the smallest free number; spent ones grey; a click on a
  spent one returns one: return_action), Restore = restore all; reaction squares (return_reaction); the attacks (statuses.active, a click = use_attack); the quick grid
  (Session.quick_view: profile quick_cells clamped 4-16, quick_columns; app quick buttons without a resource group;
  a click = Session.run_quick). Tests: storage/test_ui_logic34b.py, ui/test_combat34.py (shots statuses_*, combat_*).
- Package 35 P1 (owner review of package 34): the tab bar wraps onto further rows inside the tabs block (TabFlow;
  the profile field tab_rows pins the rows, editor mode); the Sources dialog hides rows of value 0 unless "show all"
  (app setting sources_show_all; ON in the editor mode), names the AC variants and the buff temp HP; every dialog
  takes its content's size or the size the owner dragged it to (app setting dialog_sizes, wp/ui/dialog_size.py), never
  larger than the screen; a resource whose max is 0 without sources shows the one-time hint no_sources. Qt-free:
  wp/ui/dialog_logic.py. Tests: storage/test_ui_logic35.py, ui/test_p35a.py, model/test_pkg35a.py.
- Package 35 P2 (step 6): the BOTTOM STRIP (wp/ui/bottom_strip.py; Qt-free strip_logic.py): OT, pain, morale (only in
  combat, its sources total), speed, load; every cell opens the Sources dialog (new numbers ot / pain / morale);
  "+ strip" / "- strip" (profile field strips); "Journal" opens the Journal tab. The right column tabs build their
  pages on first use (combat_tab.PAGES): JOURNAL (tab_journal.py: newest first, kind / text filter, Undo / Redo,
  short / full mode, journal_note) and SETTINGS (tab_settings.py: every control a settings command). The UI reads
  core data it may not import through wp/app/ui_data.py (D25). Tests: model/test_pkg35b.py,
  storage/test_ui_logic35b.py, ui/test_p35b.py (shots strip_*, journal_*, settings_*).
- Package 35 P3 (step 1b): the THEME EDITOR (wp/ui/theme_editor.py, Qt-free theme_logic.py; View > Theme editor
  or the Settings tab): the theme list, Copy / Reset to the shipped one / Remove, every colour token (a click picks a
  colour of an own theme: Session.theme_command theme_edit, saved at once, live restyle), the contrast warnings (4.5:1,
  never a refusal), the own background picture (none by default) with dimming and the readable overlay (the central
  Backdrop of window.py). Tests: storage/test_themes35.py, ui/test_themes35_ui.py (shots themes_*).
