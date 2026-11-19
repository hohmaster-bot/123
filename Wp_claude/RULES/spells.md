# Spell record [OWNER]
A spell is: name + damage (if any) + range or AoE (if any) + optional effect (bonuses/penalties) + link to the spell + description.
- The effect is quick to reach from the spell and from the buffs list (see buffs.md "is buff").
- Damage depends on level, types, areas, range [editor BETA].
- Cost: mana/slot/overload rules in classes_magic.md.
- Stance (combat.md): a feat with a checkbox "is stance". Feats can already give permanent bonuses and penalties through the universal
  bonus/penalty block, so a stance may e.g. disable the Dex bonus to AC. Only a checkbox, no special fields.

## Metamagic [OWNER, package 10, docs only; not built]
- Metamagic "+1 circle" raises the spell cost by 2 mana (circle table 0, 1, 3, 5, 7, 9, 11, 13, 15, 17 for circles 0-9).
- A cantrip (cost 0) with +1 circle costs 2, so it is available from level 2 (the per-spell limit = level of mana,
  classes_magic.md "Mana level").
- Slot casters use a slot of the needed circle; the same per-spell limit applies.
- Assumption (OPEN_QUESTIONS Q62): each further +1 circle adds another +2 mana.
