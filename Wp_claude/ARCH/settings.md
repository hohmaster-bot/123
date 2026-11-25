# Settings (D13, D22, package 19)

Settings are DATA with a schema: `wp/settings/data/settings_schema.json` (id, domain, type, default, allowed / min /
max, group, i18n label and description ids). Code never lists setting keys by hand.

## Domains
| Domain | Where it lives | Changed by |
|---|---|---|
| rules | `Character.rules_settings` (character file) | character commands `set_rule_setting`, `reset_rule_setting`, `reset_settings_group` |
| character | `Character.char_settings` (character file) | `set_char_setting`, `reset_char_setting`, `reset_settings_group` |
| app | `<user data folder>/app_settings.json` (global) | settings commands (`settings_set`, `settings_reset`, `settings_reset_group`, `settings_export`, `settings_import`) |

## Layers (like catalogs, D21)
- Shipped: schema defaults and `default_profiles.json` (read-only, install folder).
- User: `app_settings.json` keeps only what the user changed, plus profiles, quick buttons, images. Unknown keys and
  record fields are kept, unknown top-level fields dropped, no migrations. Atomic save (temp file + replace).

## Layout profiles (per mode: classic, lite; many each, one active)
- Classic profile: panels (id, visible, size, position / dock, tab order) and cells (id, source, kind number / bar /
  icon / text / button, label, size, grid or position, colour rules, click action, icon, visible).
- Lite profile (the overlay, D20): elements (id, kind, source or action, position + monitor, size, visible, anchor,
  snap grid, opacity) and profile-wide opacity, click-through with its own hotkey, always on top, show / hide hotkey,
  lock layout, snap to grid, per-monitor scale.
- Commands: profile_create / duplicate / rename / delete / set_active / set / export / import; layout_add / edit /
  remove for panels, cells, elements.
- A cell source is a reference resolved by the model (`wp/settings/layout.py`): resource:, ability:, status:, pool:,
  skill:, value:. A broken reference gives a warning, never a crash.

## Quick buttons
- id, label, icon, action (a command id + params) or macro (a plain list of existing commands, run in order, all or
  nothing), hotkey, group, order. Usable in both modes.

## Images
- Registry records (id, name, file under `<user folder>/images/`, kind icon / picture / background, tags) and
  `image_for` ("kind:id" -> image id). A missing file gives a placeholder + warning. image_add / image_remove /
  image_rename / image_set_for; extensions and the size limit are app settings.

## Hotkeys
- Two actions on the same key (modifier order does not matter) are refused: app hotkeys, quick buttons and each
  Lite profile's own hotkeys are checked together.

- [package 26 B] resource_display allows "flask"; resource_segments[resource] = the tick step of a flask (0 = none).
- [package 27] Type folder_name (backups_folder): one folder name, not "", ".", "..", no separator. Rule constants
  carry min / max (dividers >= 1), map key sets and value types from constants.json; NaN / inf are refused; a character
  file with a constant outside its limits is damaged. New app settings: journal_mode (short | full, default full),
  journal_short_max 100, journal_archive_at 1000, journal_archive_keep 100. image_add checks the file content
  (png / jpg / gif / webp / svg); profile_set takes only the profile fields; settings_import refuses image records
  outside images/ and deep nesting.
- [package 31] Hints: hints_seen (dismissed ids), hints_off; hint_dismiss(hint_id), hints_reset;
  screen_settings.hint_visible / hints_view (ids in wp/settings/data/hints.json, texts hint.<id>). Layout:
  screen_settings.layout_warnings(app, mode, pid, window) -> block_under_minimum / hp_controls_hidden /
  block_outside_window (never refusals); profile_reset(mode, pid). Tubes: resource_style (glass | flat),
  resource_size {resource: [w, h]}, resource_autoswitch, pool_order, pools_large (max_items 3). Background:
  background_image, background_dim 0-100, background_readable. A list key may carry max_items.
