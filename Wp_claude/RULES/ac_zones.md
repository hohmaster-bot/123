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
