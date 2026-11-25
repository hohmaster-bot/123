# Package 32 report: the Classic window shell (Phase 5 step 1) and the overlay tray icon

## Done
A. The shell (D32; ARCH/surfaces.md "Classic window shell"):
- `python run_wp.py [--data DIR]` (wp/ui/app.py): QApplication + MainWindow; data folder <home>/WipeFinder
  (characters/, settings/; Q214). On start the last character (last_character), else the demo character.
- Regions from the classic layout profile (wp/ui/window.py): dock top = the experience strip, left / center / right =
  the columns, bottom = the bottom strip; ordered by position y then x; center items with the same y share a row
  (Q215). The panel registry got a "blocks" list (experience_strip, identity, ac_block, parameters, favorites,
  reminders, tabs, bottom_strip: title, min_size, defaults, reads); registry.BLOCKS / known / reads; the shipped
  classic default profile is now the Classic screen v2. Column blocks keep the saved size; strips the saved height.
- Real data: the experience strip (training.experience: glass bar, total, goal; the log button disabled until the
  journal tab) and the identity block (sheet: name, class, level; a portrait frame). The sheet view gained `name`.
  The other blocks show their translated title and the views they will read.
- Menus: Character (New demo character, Open, Save, Save as, Exit), View (Theme list + Follow the system, Language
  RU / EN, Scale 80-150 %), Help (Show hints again). Files only through the Session (backups, atomic save); Save as /
  Open from another folder: Q218. The demo (wp/ui/demo.py + data/demo.json) is built by plain commands only.
- Themes: wp/theme/qss.build_qss(theme, scale) (pure, no Qt): the template rules + the shell rules; a missing token
  falls back to dark; fonts at least 11 px, fonts and gaps times the scale; #rrggbbaa -> rgba(). Switched LIVE.
- Session.settings(command, **params): app settings for the UI, saved at once, topic "settings" to subscribers;
  Session.theme(system_dark), themes_view, hint_visible. The window re-applies theme / texts / gaps on that topic.
- The first-run hint (new text, Q220) with "Understood!" = hint_dismiss; geometry window_classic saved on close and
  restored; blocks refresh on the topics of every result (D25); refusals shown as i18n texts (a damaged file offers
  the newest valid backup); an unexpected error prints to the console and shows shell.unexpected.
- Docs: D32 (ARCH/decisions.md), ARCH/surfaces.md, panels.md, app_layer.md, themes.md, ROADMAP (step 1 done, next
  step 2 resources), view contract, TRANSLATION_TODO, review pack regenerated.
B. Overlay spike (tools/overlay_spike.py): a tray icon (green shown / grey hidden, orange corner = click-through),
  tooltip, menu Show / Hide, Click-through on / off, Exit; a close button (x); Ctrl+Alt+Q exits; Esc stays. Fixed: the
  Windows calls had no argument types and failed with a 64-bit window handle (RegisterHotKey OverflowError). Owner
  wishes added to UI_WISHES.md (Lite); OVERLAY_SPIKE.md (Russian) updated.

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 70, passed 70, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 342, caught 342, missed 0.
- New suite storage/test_qss_shell.py (9 cases, no Qt: the background and text colour of each theme; 12 px -> 18 px
  at 150 %, 9.6 -> 10 px at 80 %; small 10 -> 11 px minimum, 16.5 -> 16 px at 150 %; light never #ffffff; a missing
  token from dark; rgba 0x26 = 38; spacing 6 -> 9; dark != light; no Qt import).
- New suite ui/test_shell.py (18 cases, offscreen; run_all now also runs tests/ui; skipped without PySide6): opens
  with the demo; six regions and the AC / parameters row; saved sizes 330 x 300, strip 56; experience 72 % (1450 of
  2000 = 72.5 rounded down), 1450 xp, goal 2000; identity Demo / Sample fighter / Level 2; level_up -> Level 3 and
  every block refreshed, set_next_level_at 2900 refreshes only 4 blocks and gives 50 %; theme light live + saved;
  follow the system; language RU -> EN; scale 150 % = 18 px; the hint once / dismissed / reset; geometry 50, 60,
  1000 x 700 restored; a damaged file shows its text; save as inside / outside; the last character on restart; data
  folders; wp/ui imports nothing of the core (D25); screenshots tests/ui_shots/dark.png, light.png, grey_blue.png.
- Breaks tests/breaks/pkg32.py (14).

## Changes to old rules
- No RULES change. Old tests changed: storage/test_themes_panels.py q-no-qt (wp/ui is the one Qt package, D32),
  p-edit-refused (the item "combat" of the new default profile instead of "log"), p-load-warning (the first item of the
  new default profile is experience_strip). The shipped classic default profile changed (the v2 regions).
- Allowlist (constants.json): qss.py 16 (hex digits), blocks.py PCT_MAX, menus.py PERCENT (UI numbers, not rules).

## Assumptions
- Q214 data folder; Q215 regions from dock / rows by y; Q217 min font before scale, round; Q218 save as / open
  elsewhere; Q219 fixed block sizes, scroll; Q220 first-run hint text, disabled log button; Q221 tray icon colours.

## Open questions (ids)
- New: Q214-Q221; Q216 is a proposal (the app setting font_size is not used by the shell: drop it?).
