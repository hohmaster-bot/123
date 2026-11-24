# Hands and doll layout (D26, package 24)

- Hands: `Item.hand` = "left" / "right" stored by `equip_hands(iid, side)` and `move_hand_item(iid, side, swap)`.
  `wp/model/hands.py` computes the sides on read: a valid stored side wins; held items without one get a side by
  the held order (shield: `hands.default_shield_side`; others: the first free of `hands.default_weapon_sides`);
  a two-handed item takes both. Nothing is written back (no migration).
- Attack records: `AttackRecord.main_hand` ("" = `hands.main_default`, right); the attack view returns `hand`,
  `main_hand`, `off_hand`. `set_twf` without an off record takes the record of the weapon in the other hand.
- AC: every held shield counts in the cells of its own hand (ac_variants.md).
- Doll layout: the classic layout profile field `doll` = {background image id, "basic": [entry], "body": [entry]};
  entry = {id, x, y, width, height (0..1), icon, label, visible}; ids = 21 single slots + left_hand + right_hand.
  `wp/model/doll_layout.py`: `view` (items per entry, background path or placeholder), `check` (warnings: missing,
  out of range, overlap). Commands `wp/commands/doll_cmds.py`: equip_to_slot, unequip_slot, swap_slots.
  The items view (`session.view("items", doll_view="basic" | "body")`) returns `hands` and `layout`.
