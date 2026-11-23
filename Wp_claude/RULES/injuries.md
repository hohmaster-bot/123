# Injuries and trauma points (OT)

## Trauma points (OT) [OWNER]
- Counter. Source: balance overflow (resources.md). GM turns them into penalties unless the player removes them first.
- OT are zeroed ONLY by hand (and by the removal ways below). Rest does not touch them. Same for comfort and injury charges.
- Removal ways (player follows wiki rules, then removes OT in the app; also manual delete of OT is always allowed):
  * Injury taken: light / medium / heavy removes 2 / 5 / 12 OT and gives an effect.
  * Comfort: 1 comfort removes 3 OT.
  * Attention: 1 attention removes max(2, Str modifier) OT [OWNER; 'strength mod' = Str modifier, confirmed by parallel RL wording].
  * Other ways exist (manual).
- Rules text lives in the wiki: UI should link (small icon) from relevant tabs. [UI wish]
- Commands [package 15]: add_injury (take an injury: -2 / -5 / -12 OT), remove_ot_comfort(n) (-3 OT per comfort),
  remove_ot_attention(n) (-(max(2, Str mod) + attention course) OT per attention), raise_heal_rating(injury_id)
  (1 attention -> RL + max(2, Str mod) + attention course). OT never below 0; refused without OT, comfort or
  attention.

## Injury [OWNER]
- Standard injury: penalty for N sessions, usually physical. Effects (generic effect system):
  -X to attack / damage / morale / any sheet value; lower or raise resource max; forbid options/limbs/actions.
- Roleplay-only injuries are recorded but have no mechanics.
- Permanent injury: separate row "Permanent injury". Cannot be healed normally; narrative removal only. Also feeds permanent pain (resources.md).
- Injuries can be added manually. Catalog may provide templates (light/medium/heavy).
- Injury effects [OWNER, package 14 D, Q89]: an injury has an effects list (the usual effect structure: penalties,
  bonuses, blocks, anything). They apply while the injury exists; the container view shows them; an injury can be a
  block source (e.g. block_balance_regen). The OT price rules stay. Tests: -2 attack, regen blocked, removing the
  injury removes the effect.
- Injury id [OWNER, package 12, Q70]: every injury has a stable id made by the program from its name (a number on a
  collision, the same scheme as other ids), stored on the injury and used by the status container view. Old files
  load: injuries without an id get one on load. Ids of the other injuries never change when one is removed.
  [OWNER, package 13, Q75] Ids are NEVER reused: the character keeps a counter (injury_counter, only grows); an id is
  "<name>_<N>" (cut_1, cut_2, ...). remove_injury(injury_id): manual, editor level, no resource cost; the counter
  stays, so the next injury gets a new number. Tests: remove by id, the others keep their ids, after removing cut_3 a
  new cut is cut_4.

## Healing rating (RL) [OWNER]
- Each injury has a Healing Rating. Once per cycle (a cycle = a large span of in-world time, e.g. a skip; narrative tool announced by the GM) the player rolls d12 in an outside app; roll <= RL means healed.
- Base RL: light 3, medium 2, heavy 1.
- 1 attention raises RL by max(2, Str modifier) (e.g. light 3 -> 5 at minimum); the attention course adds to it
  (+1 per course, Q102). Some consumables/items directly reduce OT when used.
- The injury is removed BY HAND by the player. The app tracks its status and the related resources (HP, attention, comfort, sheet state).
- No automatic countdown, no auto-removal, no "end session" button that edits injuries or comfort.
- The app never removes comfort or edits injuries without a player action; no such button for now.

- Active injury gives its persistent penalties while it exists (e.g. broken arm: -1 to attacks).