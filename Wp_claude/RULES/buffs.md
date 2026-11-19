# Buffs / effects [OWNER]
Buff = status = debuff = situational: one concept, "Status" [OWNER]. Everything from spells, DoT and heal per tick are ordinary statuses. One generic effect system for ALL sheet parts (race, class, feat, item, injury, quirk, spell, buff).

## What an effect can change
Any parameter: stats, initiative, attack bonus, AC, actions, saves, skills, resources (max, regen, current), speed, etc.
Several at once or separately. May give penalties (e.g. -2 AC). May give a one-shot (e.g. temp HP) AND a timed part
(e.g. +4 Str for 8 rounds).

## Duration kinds
- N ticks (zero-initiative ticks). Duration is typed in by hand as a number; no "level x minutes" formulas [OWNER].
  Long statuses are removed by hand.
- [OWNER, package 8] Ticks, the zero-initiative phase and overload belong to the combat system. Long effects (5 min and
  more) are not simulated: they sit on the panel and the player lowers their duration with ticks or by hand
  (command set_status_duration; example: a spell lasting 10 min/level, the GM says 20 minutes passed, two ticks remove
  20 minutes), or deletes the buff. DoT and regen tick exactly like buff durations: a DoT for N ticks hits N times and
  ends. Tests: DoT -3 for 3 ticks -> 3 hits, then gone; regen 20 ticks set by hand to 2 -> 2 heals, then gone.
- [OWNER, package 8] An N-ticks status needs its number: adding one without ticks is refused with a clear message.
  A status id already on the sheet cannot be added a second time.
- Until end of combat.
- Narrative infinite: until the GM cancels.
- Instant/one-shot (applied once, e.g. temp HP).
- Duration drops by 1 each zero-initiative phase automatically (resources.md).

## Value from the current overload [OWNER]
- A status/ability may read the CURRENT overload as its number. Example: bonus to attack and damage with natural weapons
  equal to the current overload.

## Skills target [OWNER]
- An effect may target one skill (e.g. +2 to Stealth only) or all skills.

## Condition [OWNER, package 8]
- There is NO "combat only" condition: a status works while it is active and not expired, in or out of combat.
  The old "in combat / out of combat" field is removed (an "out of combat" item bonus is switched on/off by hand).
- Condition tag [OWNER, package 9, closes Q36]: abilities (feats), items and statuses have an optional display-only
  field condition_tag: none / combat_only / out_of_combat_only. It changes NO calculation; derived views show it so
  the UI can draw an icon. The player sets it by hand (command set_condition_tag). Test: a tagged item and status give
  the same numbers in and out of combat as untagged ones.

## Charges and activation
- A buff source (ability/item) may have charges (e.g. rage 2/3). If placed on screen/slot, tapping activates it;
  shows remaining rounds and remaining charges.
- Charges restore on long rest (rest.md) unless item without the "restore on long rest" checkbox.
  Charges kept on a status (rage 2/3) are restored too, on the long rest AND by the short rest option
  "restore charges" (2 BP) [OWNER, package 8]. Test: rage 0/3, short rest charges option -> 3/3.

## Stacking (see defense.md)
- Same type: the value with the larger absolute value wins, equal absolute values give 0; only flat stacks
  (on AC dodge also stacks; weapon proficiency stacks with itself). Details: defense.md "Stacking".

## Ready-made buffs
- Any ability can be exported as a buff; catalog keeps templates (Entangled, Haste, Rage ...).

## Stacking flags [OWNER]
- Temp HP from buffs may or may not stack: per-effect flag. Same for DR, energy resistances, spell resistance.
- Duration is usually given in rounds.
- Spells, abilities, racial abilities are editable: mark "is buff" in the editor; buff list is searchable for activation
  when the source is not pinned to the panel. No charges left -> cannot activate.
- Test: removing an injury must NOT bring OT back.
