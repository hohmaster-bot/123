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
  at level 4+) and burns unspent time points (OV); it also drops BP above max (overcap, rest.md) [OWNER, package 8].
  Nothing else. The cycle length is set by the GM (module).
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

## Notebook commands [OWNER, package 16 F]
- Records: quests, stories, courts (level + tier, label "Skull 5t1"), quirks (effects like a feat while not burned),
  lenses (counter), drives (level 0..5). add_note(kind, name, ...), change_lens(lid, delta) (clamped 0..X: 0 red,
  X green), set_drive_level(did, level) (0..5, else refused), burn_quirk(kid, burned) (reversible); any field without
  limits: edit_entry / remove_entry (edit mode). Only drives take part in the attention income (+1 per drive at 4+).
- Tests: lens 1/15 -> 11 -> 15 green, +3 stays 15; 1/15 - 1 -> 0 red; drives 4, 5, 3 at level 7 -> 5 attention; quirk
  +2 Str 12 -> burned 10 -> restored 12.

## Not built on purpose [OWNER, package 17, closes Q122]
- Money is NARRATIVE: no mechanics, no counters, no prices in the app. There is no "start session" and no "end of
  session" button: only the end of cycle (above).
- [OWNER, package 26 C; replaces "XP is narrative"] Experience (XP) is a tracked counter with a log and notes: every
  entry has an amount (may be negative), an optional note and a time stamp; the total is the sum of the log. The player
  may type a goal "next level at" shown as progress; it is NOT a rule: no threshold table, no automatic level-up.
  Every level-up writes the level history (level, XP at that moment, hit-die roll, note, time).

## Drives: level notes and principles (package 25) [OWNER]
- A drive list with numbers 0-5, the bonus/penalty text beside each level, and a principle = a narrative
  description the player must write when the drive is 2+.
- [package 25 C] The texts are narrative only (no calculation). From level 2 (data constant) the drive shows a
  reminder while the principle is empty; it never blocks anything. The attention income is unchanged.
