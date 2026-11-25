# AC cell variants (D26, package 24; RULES/ac_zones.md "Variants and settings")

- Data: `wp/rules_data/ac_zones.json` (cells with presets, mirror, variants melee / melee_parry / ranged).
  Cell rules: constants of group `ac_zones` (parry_cells, dex_loss_cells, shield_cells by type,
  ranged_ignores_parry, ranged_keeps_shield, dex_loss_chance_pct) and `hands.default_shield_side`; per character via
  `set_rule_setting`; listed by the defense view (`settings`).
- Effects change them: targets parry_cells / shield_cells / dex_loss_cells (effect cells, value sign = add / remove),
  dex_loss_chance_pct; `Effect.cells` scopes any AC bonus or the parry layer to cells (`Bonus.cells`).
- Code: `wp/core/ac_zones.py` (ZoneRules, cell_variants), `wp/model/ac_zones_view.py` (rules from the character,
  held shields with sides, parry per cell, display hints from the app settings ac_cell_primary / secondary / slash).
- `core/ac.layer_parts(..., cell)`: cell-scoped bonuses count only in their cell; the old modes use their preset
  cell (front / parry / touch 2, flank 6, flat-footed 8). Package 27 (owner, review 5 F15): the defense view takes
  the modes FROM the cells (`ac_zones_view.modes`): flank = the cell of the side without a shield (6, or 4 when every
  held shield is in the right hand); with the shield in the left hand the old numbers do not change.
