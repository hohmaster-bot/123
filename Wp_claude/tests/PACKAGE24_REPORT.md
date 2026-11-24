# Package 24 report

## Done
- A. Hands with sides (D26, closes Q156):
  - `Item.hand` (left / right); `equip_hands(iid, side)` with defaults: a shield goes to the left hand, another
    item to the first free hand (right, then left); a two-handed item takes both;
  - `move_hand_item(iid, side, swap)`;
  - `wp/model/hands.py` computes the sides on read (older files: by the order of the held items, nothing written);
  - the items view shows both hands;
  - every shield counts in the cells of its own hand; two shields give the larger value per cell;
  - `AttackRecord.main_hand` and `set_main_hand`; the attack view returns `hand`, `main_hand`, `off_hand`;
    `set_twf` without an off record takes the record of the weapon in the other hand.
- B. AC cell variants:
  - every cell returns variants melee / melee_parry / ranged (ranged: no parry, shield where covered);
  - a Dex-loss cancel chance gives "<id>_dex" values with the percent (never rolled);
  - display hints are app settings (`ac_cell_primary`, `ac_cell_secondary`, `ac_cell_slash`);
  - the cell rules are constants of group `ac_zones` plus `hands.default_shield_side`, editable per character and
    listed with defaults and the changed flag in the defense view;
  - new effect targets: parry_cells, shield_cells, dex_loss_cells (the sign of the value adds or removes cells) and
    dex_loss_chance_pct;
  - `Effect.cells` / `Bonus.cells` scope any AC bonus (also the shield type) and the parry layer to cells;
  - the old modes use their preset cells (front / parry / touch = 2, flank = 6, flat-footed = 8).
  - RULES/ac_zones.md: the section "Variants and settings (package 24)" appended; the draft is unchanged.
- C. Doll layout data in the classic profile (`doll`: background, "basic", "body"):
  - 21 slots + left_hand + right_hand, SAMPLE coordinates, the new profile field kind `doll_slot`;
  - `wp/model/doll_layout.py`: view and check (warnings: missing, out of range, overlap);
  - commands equip_to_slot, unequip_slot, swap_slots; `session.view("items", doll_view=...)`;
  - a missing picture gives the placeholder.
- D. UI_WISHES: doll views, hover tooltip, the cell numbers, slash lists, sketches later.
- E. Not built (ROADMAP), each needs owner rules:
  - the class system;
  - principles;
  - journal revert;
  - what an item qualification unlocks (Q109);
  - the three stored-only weapon picks;
  - the spell damage engine;
  - PDF export (Qt in the UI phase, QPdfWriter).
- F. Docs:
  - ARCH/doll_hands.md, ARCH/ac_variants.md, D26;
  - Q151, Q154, Q155, Q156, Q157, Q158, Q159 closed (decision_log);
  - RULES/doll.md note, index, ROADMAP, STATUS, history;
  - view contract, review pack and TRANSLATION_TODO rebuilt.

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 56, passed 56, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 186, caught 183, missed 3 on the first full run: the three package 23
  zone entries named the replaced code lines; moved to the new lines, they are caught (`break_check.py p23-zone`: 4 of 4),
  so entries 186, caught 186.
- New suite: test_pkg24 (33 cases). New break entries: 19 (breaks/pkg24.py).

## Changes to old rules
- None in numbers: the old AC modes and every old test are unchanged.
- An unscoped parry no longer includes parry effects that carry cells (those count only in their cells).

## Assumptions
- Q160: default hand order and main hand.
- Q161: set_twf takes the other-hand record.
- Q162: unscoped shield bonuses without a held shield.
- Q163: cell effects (removal wins; absolute cells).
- Q164: 23 rectangles.
- Q165: an item fits only its own slot.
- Q166: the display hints are app settings.

## Open questions (ids)
Q160, Q161, Q162, Q163, Q164, Q165, Q166 (assumptions, to confirm).
