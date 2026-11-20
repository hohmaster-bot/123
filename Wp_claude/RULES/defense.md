# Defense

## Positioning [OWNER]
- Front attack: full AC.
- Flank (shield side): attacker may ignore shield bonus (incl. spell shields, e.g. weapon-side).
  [OWNER, package 8] The AC calculation has a checkbox "flank drops shield" (default on). Test: shield 2, flank: 10;
  checkbox off: 12.
- [OWNER, package 8] An attack made with a shield cancels the shield bonus to AC until the next turn (the attack view
  marks it; the AC is computed with the shield switched off).
- Flat-footed ("in surprise"): AC without the Dex BONUS and without ALL dodge bonus; a penalty from low Dex stays [OWNER].
  Shield counts only if attack comes from shield side. Example: Dex -2: front AC 8, flat-footed 8.
- Parry: same bonus type as armor. If no armor or parry > armor, player usually picks parry. Front only.
  Parry value [OWNER, package 5] = armor proficiency (none 0, light 2, medium 4, heavy 6) + 1 per odd level from 3
  + 2 for the "tower shields" proficiency grade + weapon mastery parry picks. It comes from PROFICIENCY, not from an
  item in the hand (training.md).
- Touch: ignores natural armor, shield, parry, armor bonuses; only the armor's "touch AC" bonus counts, as the armor
  layer of the touch AC (gear.md "Armor", package 9).
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

## Saves and initiative [package 10; Q55, Q56, Q61 answered in package 11]
- Save (Fort, Ref, Will) = base (typed by hand, like BAB [OWNER, Q61]) + stat mod ([OWNER, Q55] Fort Con, Ref Dex,
  Will Wis, as in PF; stored as data) + typed bonuses (target "save" = all
  saves, "save:fort" / "save:ref" / "save:will" = one save; stacked by the normal rules) + pain + morale.
  Tests: base 3/1/2 with Con 14, Dex 12, Wis 8 -> 5/2/1; +1 resistance to all and +2 resistance to Fort -> Fort 7,
  Ref 3, Will 2; pain 2 -> -2 each; morale scale 4 in combat -> +2 each.
- Initiative = Dex mod + typed bonuses (target "initiative") + pain (resources.md: every roll with a die) + morale.
  [OWNER, Q56] Morale applies to initiative. Morale exists only in combat and starts at 0, so the initiative roll
  before combat has no morale; a reroll during combat includes it. Test: Dex 14 + 2 competence -> 4; pain 1 -> 3;
  morale scale 2 in combat -> 5; the same scale out of combat -> 4.

## Morale (battle) [OWNER]
- Scale is physically -10..+10. A class effect may "count morale X higher at the player's choice".
  Bonuses and penalties to morale (typed bonuses) are not limited by the scale.
- Bonus to ALL rolls (skills, saves, attacks, maneuvers, CMB, damage, initiative [Q56]), type "morale";
  NOT to the lucky attack die, the crit die or AC.
- bonus = trunc(scale / 2): -10 -> -5, +10 -> +5, +/-1 per 2 steps.
- Only while combat is active. One button start/end combat (text switches). Inactive -> morale ignored.
- End of combat resets the morale scale to 0 [OWNER].
- At <= -5 show "We are losing!", at >= +5 "We are winning!". Nice-to-have: record max/min morale of the fight.
- Examples: scale 3 -> +1; scale -4 -> -2; scale 1 -> 0.

## Does NOT receive roll bonuses
- Crit confirmation die and lucky attack die (see combat.md).


## Damage order and percent modifiers [OWNER, package 17]
- Effect target "percent:<damage type>": a SIGNED percent: -100 = immunity, -50 = half, +50 = takes 50% more. One value
  per type on a character: with several sources the larger absolute value wins (equal + and - -> 0, like typed
  bonuses); never below -100. Rounded UP (against the player).
- Steps of one damage part, in the order of rules_settings.damage_order (data; default "percent", "flat", "modifier"):
  1. percent reduction typed for the hit (25 / 50 / 75 %); 2. flat: the larger of DR (physical) and resist:<type>;
  3. the signed percent modifier. Then temp HP, absorbers, HP (resources.md).
- Tests: cold -100: 10 -> 0; fire +50: 10 -> 15; +50 and -25 -> +50; +25 and -50 -> -50; resist fire 2 then +50:
  (10 - 2) * 1.5 = 12; with the modifier first: 15 - 2 = 13; 5 with +50 -> 7.5 -> 8.
- Damage types: data (wp/catalog/data/damage_types.json); "cold" added in package 17 (the owner's immunity example,
  Q130).
