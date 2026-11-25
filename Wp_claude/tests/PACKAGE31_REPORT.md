# Package 31 report: settings, themes, hints, layout safety

## Done
- One-time hints: app settings hints_seen (the dismissed ids) and hints_off; settings commands hint_dismiss(hint_id)
  ("Understood!" / "Понятно!" = i18n hint.understood) and hints_reset; screen_settings.hint_visible / hints_view; the
  hint ids in wp/settings/data/hints.json, texts hint.<id> in en.json and ru.json.
- Layout safety (wp/settings/screen_settings.py): layout_warnings(app, mode, pid, window) gives block_under_minimum
  (the registry min_size), hp_controls_hidden (no visible resources panel and no cell / element with resource:hp),
  block_outside_window (needs the window size); never a refusal. profile_reset(mode, pid) puts the shipped default
  profile back (id and name kept).
- Tube settings: resource_style (glass | flat; display only), resource_size {resource: [w, h]}, resource_autoswitch,
  pool_order, pools_large (at most 3: a new max_items check of list settings); resource_segments already existed.
- Themes: three shipped themes dark (the default for a new profile and the fallback), light (background #f4f4f2,
  surface #fafaf7: never pure white), grey_blue (low contrast); 24 new colour tokens for the whole Classic screen
  (pool, overload_chip, temp_hp, bp, tube_glass / highlight / segment / empty, chip_*, threshold_*, action_square /
  action_spent / reaction_square, strip, editor border, hidden mark, hint, background overlay) and the scalar
  tube_gloss; resource defaults as the owner listed (HP red, balance muted orange, spirit teal, mana blue, overload
  chip magenta). theme_copy, theme_reset (to the shipped one), active(app, layers, system_dark) with
  theme_follow_system / theme_light / theme_dark; background settings background_image (default none),
  background_dim, background_readable; contrast_ratio (WCAG 2) and warnings (low_contrast below 4.5, never a
  refusal), themes.view.
- ui_gaps.md: every row marked DONE (30 / 31) or "no core change needed"; ROADMAP Phase 5 step 0 done, next step 1
  (the window shell + themes in PySide6).

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 68, passed 68, failed 0.
- `python Wp_claude/tests/break_check.py` (the whole registry after packages 30 and 31): entries 328, caught 328, missed 0.
- New suite storage/test_pkg31.py (14 cases: hints once / dismissed / reset / off / unknown; the three layout warnings
  and a normal layout without one; profile_reset 12 -> 8 cells, id and name kept; tube settings valid and refused;
  defaults; WCAG black on white 21, white on white 1, the dark text #e6e6e6 on #1b1d21 = 13.5 by hand; a low-contrast
  theme warns and still saves; the shipped themes without warnings; theme_reset back to #5b9bd5; copy -> dark_1, an
  own theme not_shipped; 9 bad colours refused; follow the system; three themes, light not pure white; tokens).
  Breaks tests/breaks/pkg31.py (13).

## Changes to old rules
- No RULES change. The default theme is now dark (owner): old tests in storage/test_themes_panels.py changed: the
  shipped themes are three (v-shipped, l-duplicate-remove) and an unknown active theme falls back to dark (l-active).
- The shipped dark / light colours of balance and mana changed to the owner's defaults (orange, blue).

## Assumptions
- Q209 hint ids and texts; Q210 the contrast pairs; Q211 the shipped colour values; Q212 tube sizes and three large
  pools; Q213 the window size for the outside warning, profile_reset keeps id and name.

## Open questions (ids)
- New: Q209-Q213 (assumptions). Nothing waits for the owner.
