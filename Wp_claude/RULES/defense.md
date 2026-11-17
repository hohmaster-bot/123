# Defense

## Positioning [OWNER]
- Front attack: full AC.
- Flank (shield side): attacker may ignore shield bonus (incl. spell shields, e.g. weapon-side).
- Flat-footed ("in surprise"): AC without Dex. Shield counts only if attack comes from shield side.
- Parry: same bonus type as armor. If no armor or parry > armor, player usually picks parry. Front only.
- Touch: ignores natural armor, shield, parry, armor bonuses.
- Need UI toggle: shield bonus on/off in AC, or show small secondary number "AC with shield".

## Typed bonus pools [OWNER]
- AC-only types: armor (incl. parry), natural armor, shield, dodge, deflection(?) + one more (see modifiers.py).
  Can come from any ability/class/etc but apply only to AC. Dodge stacks with itself.
- Flat stacks with itself.
- Other bonuses (list in modifiers.py) apply to rolls: attack, damage (usually not spells), saves, skills.
  Same type: only the highest applies; only flat stacks.
- Weapon proficiency bonuses stack with themselves and apply only to attacks with that weapon.
- Example: +1 enchanted sword, "magic weapon" status gives +1 enchant -> result +1, not +2.

## Morale (battle) [OWNER]
- Scale -10..+10. Bonus to ALL rolls, type "morale" (highest only, like any typed bonus).
- bonus = trunc(scale / 2): -10 -> -5, +10 -> +5, +/-1 per 2 steps.
- Only while combat is active. One button start/end combat (text switches). Inactive -> morale ignored.
- At <= -5 show "We are losing!", at >= +5 "We are winning!". Nice-to-have: record max/min morale of the fight.
- Examples: scale 3 -> +1; scale -4 -> -2; scale 1 -> 0.

## Does NOT receive roll bonuses
- Crit confirmation die and lucky attack die (see combat.md).
