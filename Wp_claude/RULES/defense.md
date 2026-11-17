# Defense

## Positioning [OWNER]
- Front attack: full AC.
- Flank (shield side): attacker may ignore shield bonus (incl. spell shields, e.g. weapon-side).
- Flat-footed ("in surprise"): AC without Dex and without ALL dodge bonus. Shield counts only if attack comes from shield side.
- Parry: same bonus type as armor. If no armor or parry > armor, player usually picks parry. Front only.
- Touch: ignores natural armor, shield, parry, armor bonuses.
- Need UI toggle: shield bonus on/off in AC, or show small secondary number "AC with shield".

## Typed bonus pools [OWNER]
- AC-only types: exactly five: armor (incl. parry), natural armor, shield, dodge, deflection.
  Can come from any ability/class/etc but apply only to AC.
- Other bonuses (list in modifiers.py) apply to rolls: attack, damage (usually not spells), saves, skills.
- Stacking [OWNER decision]: a bonus and a penalty of the SAME type do not add up; the value with the larger
  absolute value wins; equal absolute values -> 0. Examples: +3 and -4 -> -4; +3 and -1 -> +3; +2 and -2 -> 0.
- Only flat stacks with itself; on AC dodge also stacks. Weapon proficiency bonuses stack with themselves and apply
  only to attacks with that weapon.
- Computed separately for each target (attack, damage, save, skill, AC...).
  Example: morale scale +1 on everything and a spell's morale penalty -2 on attacks -> attacks -2, everything else +1.
  Heroism +4 morale on attacks with morale scale -1 -> attacks +4, everything else -1.
- Example: +1 enchanted sword, "magic weapon" status gives +1 enchant -> result +1, not +2.

## Morale (battle) [OWNER]
- Scale -10..+10. Bonus to ALL rolls (skills, saves, attacks, maneuvers, CMB, damage), type "morale";
  NOT to the lucky attack die, the crit die or AC.
- bonus = trunc(scale / 2): -10 -> -5, +10 -> +5, +/-1 per 2 steps.
- Only while combat is active. One button start/end combat (text switches). Inactive -> morale ignored.
- At <= -5 show "We are losing!", at >= +5 "We are winning!". Nice-to-have: record max/min morale of the fight.
- Examples: scale 3 -> +1; scale -4 -> -2; scale 1 -> 0.

## Does NOT receive roll bonuses
- Crit confirmation die and lucky attack die (see combat.md).
