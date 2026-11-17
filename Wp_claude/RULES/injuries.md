# Injuries and trauma points (OT)

## Trauma points (OT) [OWNER]
- Counter. Source: balance overflow (resources.md). GM turns them into penalties unless the player removes them first.
- Removal ways (player follows wiki rules, then removes OT in the app; also manual delete of OT is always allowed):
  * Injury taken: light / medium / heavy removes 2 / 5 / 12 OT and gives an effect.
  * Comfort: 1 comfort removes 3 OT.
  * Attention: 1 attention removes max(2, Str modifier) OT [OWNER; 'strength mod' = Str modifier, confirmed by parallel RL wording].
  * Other ways exist (manual).
- Rules text lives in the wiki: UI should link (small icon) from relevant tabs. [UI wish]

## Injury [OWNER]
- Standard injury: penalty for N sessions, usually physical. Effects (generic effect system):
  -X to attack / damage / morale / any sheet value; lower or raise resource max; forbid options/limbs/actions.
- Roleplay-only injuries are recorded but have no mechanics.
- Permanent injury: separate row "Permanent injury". Cannot be healed normally; narrative removal only. Also feeds permanent pain (resources.md).
- Injuries can be added manually. Catalog may provide templates (light/medium/heavy).

## Healing rating (RL) [OWNER]
- Each injury has a Healing Rating. Once per cycle (a cycle = a large span of in-world time, e.g. a skip; narrative tool announced by the GM) the player rolls d12 in an outside app; roll <= RL means healed.
- Base RL: light 3, medium 2, heavy 1.
- 1 attention raises RL by max(2, Str modifier) (e.g. light 3 -> 5 at minimum). Some consumables/items directly reduce OT when used.
- The injury is removed BY HAND by the player. The app tracks its status and the related resources (HP, attention, comfort, sheet state).
- No automatic countdown, no auto-removal, no "end session" button that edits injuries or comfort.
- The app never removes comfort or edits injuries without a player action; no such button for now.

- Active injury gives its persistent penalties while it exists (e.g. broken arm: -1 to attacks).