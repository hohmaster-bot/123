# Themes (D24, package 21)

- A theme is token data: colors (`#rrggbb` or `#rrggbbaa`: background, surface, text, muted, accent, accent_text, border,
  success, warning, danger, info; resources hp, balance, mana, spirit, comfort, pain, ot, morale; AC layers ac_*),
  fonts (family, base, small, large > 0), radius, spacing, border_width (>= 0), icon_style, overlay_opacity (0..100).
  The token list is data: `wp/theme/data/theme_schema.json`.
- Two layers like catalogs (D21): shipped `wp/theme/data/themes.json` ("light", "dark"; sample values) and the user
  file `<user folder>/themes.json` (overrides, tombstones, own themes); catalog store format, ids, atomic save.
- Commands (`wp/theme/themes.py`): theme_add, theme_edit (colors / fonts merged key by key; a shipped theme gets a
  user override), theme_remove, theme_duplicate, theme_set_active (the app setting `theme`), theme_export /
  theme_import (a text code). Refusals: missing_token, bad_color, bad_size, not_found, wrong_kind.
- `wp/theme/qss.py` builds the QSS text from the tokens with the template `wp/theme/data/qss_template.json`
  (selector -> declarations with `{token}`); pure Python, no PySide6 import anywhere (a test checks).
- [package 31] Shipped: dark (the default; an unknown active id falls back to it), light (soft, never pure white),
  grey_blue (low contrast). Tokens for the whole Classic screen v2 (pool, overload_chip, temp_hp, bp, tube_*, chip_*,
  threshold_*, action_square / action_spent / reaction_square, strip / editor / hidden / hint / background overlay;
  scalar tube_gloss). theme_copy, theme_reset (drops the user override of a shipped theme), active(app, layers,
  system_dark) with theme_follow_system / theme_light / theme_dark; contrast_ratio (WCAG 2) and warnings(theme)
  (low_contrast below theme_schema contrast_min 4.5, never a refusal); view(app, layers).
- [package 32] qss.build_qss(theme, scale=1.0, fallback=None): the window shell style sheet = the template rules + the
  "shell" rules of qss_template.json; a token the theme lacks comes from the dark theme; fonts at least min_font_px 11
  (before the scale), fonts and spacing times the scale (Python round); #rrggbbaa -> rgba(r, g, b, a) because Qt reads
  8-digit hex as #aarrggbb. qss.scaled(theme, scale) gives the same tokens to the UI (layout gaps).
