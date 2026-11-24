# AC zones (AC by direction) [OWNER, package 13 H] - DRAFT, NOT IMPLEMENTED

This is a DRAFT of the owner's future AC-by-direction scheme. Nothing here is built yet; the current AC modes
(front, flank, flat-footed, parry, touch, shield side; defense.md) stay in force until the owner gives the full table.

## Cells
```
[1][2][3]
[4][5][6]
[7][8][9]
```
- Cell 5 is the character; he faces UP (towards 1, 2, 3).
- Cells 1, 2, 3 (front): full AC, or parry.
- Cell 8 (back): no Dex bonus and no dodge, unless a feature says otherwise.

## Shield coverage (shield in the LEFT hand)
| Shield | Cells with the shield bonus |
|---|---|
| buckler | 1, 2, 4 |
| light shield | 1, 2, 3, 4, 7 (package 15, Q93; was 1, 2, 3, 4) |
| heavy shield | 1, 2, 3, 4, 7 |
| tower shield | 1, 2, 3, 4, 7 |
- Shield in the RIGHT hand: mirror the cells: 1<->3, 4<->6, 7<->9.
- Cells 6, 8, 9 never get the shield bonus (for a left-hand shield).
- A tower shield itself gives NO parry bonus: the +2 parry comes from the tower shield proficiency rank (Q28).

## Features change cells
- Any feature, ability or status may change the rules of any cell (for example: give dodge in cell 8).
- The block effects (buffs.md "Block effects") must later be able to take a CELL as a scope.

## Requirement for the implementation
- It must be DATA: a table of cells with flags (Dex / dodge allowed, shield coverage by shield type, parry allowed),
  read by the AC code, NOT new hard-coded conditions per cell.

## Values per cell [OWNER, package 14, closes Q92]
- Every cell shows BOTH values: Full and Parry (parrying is the player's choice and may be done with an empty hand).
- The current flank / flat-footed / shield-side modes later become PRESETS of cells.

## Parry and shields [OWNER, package 15, closes Q93]
- Parry is possible with anything held: a weapon, a stick, a torch, an improvised weapon ("junk": the Contact group
  bonuses apply to improvised weapons), or unarmed with the Unarmed combat / Contact bonuses. Parry cells: 1, 2, 3.
- There is NO special "side with no weapon".
- A shield gives its bonus only in the cells it covers (shield in the LEFT hand; mirror for the right hand: 1<->3,
  4<->6, 7<->9): buckler 1, 2, 4; every other shield (light, heavy, tower) 1, 2, 3, 4, 7. Cells 6, 8, 9 never get a
  shield bonus. (The light-shield row of the table above was changed accordingly.)
- The cell logic is NOT implemented yet (a later, data-driven package).

## Variants and settings (package 24) [OWNER, package 24 B; built]
- Built as data: cells and variants in wp/rules_data/ac_zones.json; the cell rules are rule constants of group
  ac_zones (constants.json), changeable per character (set_rule_setting) and by effects. The draft above stays as written.
- Every cell returns a LIST of variants {id, label, ac, applies_when (melee | ranged), chance}:
  - melee = the full AC; melee_parry = with parry, only in the parry cells; ranged = parry does NOT work against
    ranged attacks (constant ac_zones.ranged_ignores_parry = 1), the shield counts where it covers
    (ac_zones.ranged_keeps_shield = 1).
  - A chance: in a cell that loses Dex / dodge, a cancel chance > 0 (ac_zones.dex_loss_chance_pct + effects, 0..100)
    gives every variant a second value WITH Dex and dodge and that chance ("AC without Dex / AC with Dex"). The app
    never rolls.
- Settings (defaults): parry cells 1, 2, 3; Dex / dodge lost only in cell 8; shield cells of a LEFT-hand shield:
  buckler 1, 2, 4, every other shield 1, 2, 3, 4, 7 (right hand: mirror); the default shield hand: left.
- Effects (feat, class trait, status, item): parry_cells, shield_cells, dex_loss_cells (effect cells added with
  value >= 0, removed with value < 0); dex_loss_chance_pct (a number); any AC bonus (also the shield type) and the
  parry layer may carry cells = the cells it counts in (empty = every cell). Stacking per cell by the typed rules.
- Hands have sides (gear.md, doll.md): a shield covers the cells of ITS hand; two shields (one per hand): per cell the
  larger shield bonus (one bonus type, the larger wins).
- Display (app settings): the primary variant (big number in the centre of the cell), the secondary (small number
  bottom right), the slash list "A / B / C" (order and visible variants).
- The old modes are presets: cell 2 = front and parry, cell 6 = flank, cell 8 = flat-footed (touch = cell 2).
