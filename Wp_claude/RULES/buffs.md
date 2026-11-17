# Buffs / effects [OWNER]
Buff = status = debuff = situational: one concept, "Status" [OWNER]. Everything from spells, DoT and heal per tick are ordinary statuses. One generic effect system for ALL sheet parts (race, class, feat, item, injury, quirk, spell, buff).

## What an effect can change
Any parameter: stats, initiative, attack bonus, AC, actions, saves, skills, resources (max, regen, current), speed, etc.
Several at once or separately. May give penalties (e.g. -2 AC). May give a one-shot (e.g. temp HP) AND a timed part
(e.g. +4 Str for 8 rounds).

## Duration kinds
- N ticks (zero-initiative ticks). Duration is typed in by hand as a number; no "level x minutes" formulas [OWNER].
  Long statuses are removed by hand.
- Until end of combat.
- Narrative infinite: until the GM cancels.
- Instant/one-shot (applied once, e.g. temp HP).
- Duration drops by 1 each zero-initiative phase automatically (resources.md).

## Condition
- "in combat only" or "out of combat only" (e.g. items giving skill bonuses outside combat).

## Charges and activation
- A buff source (ability/item) may have charges (e.g. rage 2/3). If placed on screen/slot, tapping activates it;
  shows remaining rounds and remaining charges.
- Charges restore on long rest (rest.md) unless item without the "restore on long rest" checkbox.

## Stacking (see defense.md)
- Same type: highest only; only flat stacks; dodge stacks with itself.

## Ready-made buffs
- Any ability can be exported as a buff; catalog keeps templates (Entangled, Haste, Rage ...).

## Stacking flags [OWNER]
- Temp HP from buffs may or may not stack: per-effect flag. Same for DR, energy resistances, spell resistance.
- Duration is usually given in rounds.
- Spells, abilities, racial abilities are editable: mark "is buff" in the editor; buff list is searchable for activation
  when the source is not pinned to the panel. No charges left -> cannot activate.
- Test: removing an injury must NOT bring OT back.
