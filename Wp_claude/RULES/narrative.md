# Narrative

- Quirk: special narrative ability; like race/feat can change any part of sheet (even another ability, then by hand).
  "Burn": stays in list, grey, status "destroyed", reversible by hand. Deletion only manual.
- Quests, Courts, Stories, Quirks: template-based notes for the player; any can be a chip with tooltip showing text.
- Quests give Drives and Courts. Court-quests live next to quirks/stories tabs; drive-quests in the Drives tab.
- Drives may give roleplay resources such as Attention. Attention can be spent to remove pain(OT?), gain comfort, get bonuses.

## Courts (Dvory) [OWNER]
- Parameter with Level and Tier, written like "Skull 5t1" = level 5, tier 1. Narrative; player keeps a description note.
- Used for item requirements ("Court X level Y") and to see which items he can activate from the list of his courts.
- Courts give narrative quests. Drives and Lenses also give narrative quests.
- Court chance for divine slot restore: see rest.md (formula TBD).

## Cycle end button (idea) [OWNER]
- Button "end of cycle" [OWNER]: adds Attention (1 + levels reached that are multiples of 3: 3, 6, 9... + 1 per drive
  at level 4+) and burns unspent time points (OV). Nothing else. The cycle length is set by the GM (module).
  Example: level 7, two drives at 4+ -> 1 + 2 + 2 = 5.
- The end of a cycle implies a long rest, but they are separate buttons: one never triggers the other [OWNER].
- Attention is its own resource: no cap, never burns, accumulates.
- OV (time points): 1 Attention gives OV equal to the Con modifier (minimum 2). OV are spent on recipes (crafting) and
  narratively; unspent OV burn by hand or with the end-of-cycle button. No cap.

## Lens [OWNER]
- A quest-like goal with a counter shown on the interface: "New World" 11/15. Only the player changes +/- by hand.
- At 0/max: lens turns red, tooltip says ask the GM for a penalty. At max/max: green, tooltip says ask the GM for a reward.
- Player deletes it after the goal is reached; the GM gives the reward.
- Lens can also give an advanced skill (skills.md).
- Lens counter: starts at 1 of X (X set by the player). Range is strictly 0..X, the app clamps; 0 and X are the END states.
  Examples: new lens 1/15; at 11/15 + 4 -> 15/15 (green); at 1/15 - 1 -> 0/15 (red); cannot go to 16 or -1.
