# Weapon proficiency (mastery) [OWNER, pasted text]

## Levels 0-12
0 none, 1 Novice, 2 Apprentice, 3 Amateur, 4 Skilled, 5-7 Specialist I-III, 8-11 Expert I-IV, 12 Master.
Level is per weapon "target" (see scale). Weapon stores required level (qualification level) and difficulty.
- Not qualified (level < required): -4 to hit, no free attacks. One level below required: penalty -2 [owner, first message].
- Qualified: may use maneuvers of the weapon group; some weapons unlock extra bonuses at higher levels.

## Difficulty and scale
- Difficulty (learning complexity): set by GM, stored on the weapon group. Usually = weapon generation: 1 medieval, 2 first-gen firearms, etc.
  Some weapons have raised difficulty. App only records it.
- Scale: 1 = one named weapon (my sword Nirgod); 2 = a variety (long swords); 3 = a country/school group ("Fatom heavy blades").
  Hierarchy: group (3) contains variety (2) contains named weapon (1).

## Cost of +1 grade
cost = (30 + 5*X) * difficulty * scale
- X = number of weapon groups already developed to Expert (8) or higher, excluding the group being raised.
  [OWNER] Any node of any scale counts (child or not). Test: three experts (8, 9, 10): each expert X = 2, any other weapon X = 3.
- Cost grows only through OTHER groups at expert+.
- Examples: X=0, difficulty 1, scale 2 -> 60. X=2, difficulty 2, scale 3 -> (30+10)*2*3 = 240.

## Combat basics (one-time per weapon branch)
- Cost 50 / 100 / 150 for scale 1 / 2 / 3 [OWNER confirmed]. One-time raise by (5 - difficulty) grades
  (difficulty 1 -> +4) for the named weapon / variety / group.
- Does NOT stack with itself [OWNER confirmed]: effective basics bonus of a weapon = max over all its ancestors, never a sum.
  Example: grandpa's sword (scale 1, 50) + long swords (scale 2, 100) + heavy blades (scale 3, 150) -> grandpa's sword level stays 4, not 12.
  Taking the +4 on another ancestor never makes it 8.
- Data need: each weapon stores its parents (variety and group); one variety can sit in several groups
  (e.g. long swords in "Eastern fighting style", scale 3).
## Bonuses by tier (player picks)
Specialist I/II/III (levels 5,6,7): one pick each, 3 picks total. Need 3 specialist picks before expert picks start.
- Parry +1; weapon durability +30%; proficiency bonus to attacks +1; crit range +1; ranged range +10 ft; balance regen +1/turn.
Expert I-IV (levels 8-11): one pick each, from expert or specialist lists.
- Weapon HP +1; durability +70% (stacks with specialist); damage +3; ignore first vulnerability in a fight; ignore 20% cover;
  lucky attack +1; first ranged attack each round can be parried.
Master (12): one pick from master, expert or specialist lists.
- Reroll one d20 with this weapon; one attack per turn without [attack] tag; once per fight free action: restore all balance.
Repeat limits: a specialist bonus may be picked again (2nd time) from expert level; 3rd time at master.
An expert bonus may be picked a 2nd time at master.
Tests: after 3 specialist picks all different, expert picks open; at level 9, picking "crit range +1" a 2nd time is allowed; 3rd is not until 12.

## Mastery bonuses in the final numbers [OWNER]
- Weapon mastery bonuses stack with themselves by their own rules, then are added as FLAT to AC (parry), attack, damage.
- They change the FINAL durability (hardness) and HP of the item, not the value the author typed into the item.
  Durability: specialist +30%, expert +70% (they stack). Item HP: +1 per expert pick.
  Example: +30% and +70% picks -> +100% of the base durability.

## Notes
- This "qualification" is weapon level; item "Qualification N" in gear.md is a different mechanic (per-item, 50 training/level).
- Styles: similar branch rules; app can record one style per equipped weapon or two attack variants (progression.md).
- Crit range +1 here vs "mastery widens by 2" in combat.md: two specialist/expert picks give +2; check against source.
