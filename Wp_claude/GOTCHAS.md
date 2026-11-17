# Gotchas - do not do X, it breaks Y
One line each. Remove a line when the cause is fixed and covered by a test.

- Legacy `_check.py` does fail on a broken formula (asserts are counted). Only `check_schema_v18` is dead: schema path points to missing `Старт/` (skipped), and its [FAIL] return value is ignored. A073, A013.
- target `lucky` (lucky attack threshold) is not bonus_type `luck`.
- `attack_lucky` must not read `item.passive_bonuses`: already synced into `situational_bonuses` (double count).
- `items{}` key must equal `item.id`.
- Weapon damage: `Item.damage` is canon; attacks use `Attack.damage_dice`. Different fields.
- Stance editor writes `effects/blocks`, core reads `stance_effects/stance_blocks`: GUI stances do nothing. A027, Q3.
- Feat editor has a second `is_stance` checkbox that defaults True and overwrites the first. A058.
- `injury_points` is skipped on load: resets to 0 after every save/load. A083.
- `recompute_derived` adds max_resource bonus to stored `class_resources.max` on every call. A087.
- HP chip setter calls `setattr` on a dict: right-click HP edit crashes. A053.
- Spell remove/mastery look up by name: with duplicate names they hit the first spell. A088.
- Chip ids contain display names (often Cyrillic): renaming orphans order/colors. D7.
- `long_rest` sets `injury_points = 0`; by rules rest never touches OT (only by hand). Test REST-long-keeps.
- `take_damage` never adds pain for balance overflow (rule: +1 pain per hit with overflow > 0). Tests RES-overflow-*-pain.
- Spell overload comes from the circle table (`SPELL_CIRCLE_TABLE`, always 2), not from spell duration. Tests MAG-*.
- `recompute_derived` builds balance max from BP max; rule says CURRENT BP. Test REST-balmax-curbp.
- tkinter workarounds (`withdraw` instead of `destroy`, `overrideredirect`, `grab_set` rules, window magnet) do not carry over to Qt.
- Never write migration code (D1).
