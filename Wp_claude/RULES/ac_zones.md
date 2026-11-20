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
| light shield | 1, 2, 3, 4 |
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

## Open items (OPEN_QUESTIONS Q92, Q93)
- How the cells combine with the existing flank / flat-footed / shield-side logic (defense.md): do the cells replace
  the modes, or do the modes stay as presets (for example "flank" = cells 4 / 6)?
- The owner's remark: "the side with no weapon has full AC without the shield". Which cells is that, and how does it
  combine with the shield coverage table above?
- The full owner table is still to come (then an AC-zones package, ROADMAP).
