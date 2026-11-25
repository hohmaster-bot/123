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
