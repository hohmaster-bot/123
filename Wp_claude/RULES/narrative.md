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
  entry has an amount (may be negative), an optional note and a time stamp; the total is the sum of the log. No
  automatic level-up. [OWNER, package 33; replaces the hand-typed goal] The goal is always 1000 (the level-up cost),
  the total is at most 1999, a level-up spends 1000 as a log entry (progression.md "Level up").
  Every level-up writes the level history (level, XP at that moment, hit-die roll, note, time).

## Drives: level notes and principles (package 25) [OWNER]
- A drive list with numbers 0-5, the bonus/penalty text beside each level, and a principle = a narrative
  description the player must write when the drive is 2+.
- [package 25 C] The texts are narrative only (no calculation). From level 2 (data constant) the drive shows a
  reminder while the principle is empty; it never blocks anything. The attention income is unchanged.

## Drives (package 28) [OWNER]
- Story power is narrative and kept OUTSIDE the program: no story-power number in the app; penalties are text only.
- Drive types (catalog drive_types, 10, each with a Russian description shown on hover, the owner may edit it):
  Idealism, Growth, Knowledge, Autonomy, Pleasure, Material, Triumph, Success, Society, Decadence. One drive record =
  one type + level 0-5 + principle (taboo text) + quest + per-level notes. Normally one record per type; a custom
  type by hand is allowed. Levels of different types are NOT summed.
- Start budget 12 points (constant drives.start_points): the view shows "distributed X of 12" as a hint only;
  nothing is blocked or clamped (edit mode changes levels freely).
- Levels (texts in the locale files, keys drive_level.<n>.obligation / bonus / penalty, editable):
  - 0: no obligations; the DM may appeal to the drive to make you oppose an ally's task (reward for success:
    comfort); no penalty.
  - 1: nothing.
  - 2: taboo (the principle). Bonus: may spend spirit for +1 to rolls while the drive is under threat (spirit is
    spent by hand).
  - 3: taboo, may take a quest. Spirit +2. Finishing the quest gives comfort (entered by hand). Penalty text: -1 story
    power each cycle until the quest is closed.
  - 4: taboo, the quest is mandatory. Spirit +3. The quest gives comfort. +1 extra attention per cycle. Penalty
    text: -2 story power each cycle until the quest is closed.
  - 5: as 4, spirit +4, penalty text -3; label "You are obsessed".
- Quest per drive: state none / taken / closed; comfort_received is a flag set by hand.
- Reminders (never blocking): "write the taboo" for a drive at 2+ without a principle; "take a quest" for a drive at
  4+ without a taken or closed quest; level_up reminds "distribute new drive points" (no number, the owner decides);
  the end of cycle lists "open quest of drive X, penalty: <text>" for a drive at 3+ whose quest is taken, not closed.
- Buying a level with comfort: +1 level for 3 comfort (drives.buy_up_cost), -1 level for 2 comfort
  (drives.buy_down_cost); the level stays 0-5 (out_of_range); not enough comfort -> not_enough_comfort. In edit mode
  the level changes for free (edit_drive).
- Attention at the end of cycle is unchanged: 1 + one per level multiple of 3 + 1 per drive at 4+.
- Tests: level 7 and two drives at 4+ -> 5 attention; level 3 with a taken quest -> the end-of-cycle reminder, closed
  -> none; level 1 -> no flags; level 2 without a principle -> principle missing; level 4 without a quest -> quest
  missing; level 5 -> obsessed; buy up at comfort 3 -> +1 level, comfort 0; at comfort 2 -> refused; buy down at 0 ->
  refused; buy down costs 2; levels 14 of 12 -> no refusal, hint only.
