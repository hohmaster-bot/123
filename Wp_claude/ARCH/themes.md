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
