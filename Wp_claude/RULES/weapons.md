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
[package 15] Picks without a numeric effect are STORED ONLY (no mechanics): reroll one d20, one attack per turn
without the [attack] tag, once per combat restore all balance as a free action, ignore the first vulnerability,
ignore 20% cover, the first ranged attack can be parried. Combat basics are bought with buy_combat_basics.
- Reroll one d20 with this weapon; one attack per turn without [attack] tag; once per fight free action: restore all balance.
Repeat limits: a specialist bonus may be picked again (2nd time) from expert level; 3rd time at master.
An expert bonus may be picked a 2nd time at master.
Tests: after 3 specialist picks all different, expert picks open; at level 9, picking "crit range +1" a 2nd time is allowed; 3rd is not until 12.

## Weapon groups and attack records [OWNER]
- A weapon group is a list of weapons sharing bonuses created by mastery (e.g. "Basic/simple": dagger, club, staff,
  light crossbow, bolts). A weapon may be in any number of groups.
- Attack, damage, parry and other bonuses come from ONE chosen group only; bonuses of two groups at once are not
  possible. Bonuses of parent (higher) groups are NOT added. (Grade levels and combat basics still follow D16.)
- Group "Contact" (level 0) is in every new character and in the catalog. "Unarmed combat" is an ordinary WEAPON
  (catalog entry) in group Contact, with its own mastery node of scale 1 (or 2) [OWNER]. Unarmed combat needs no
  weapon in the hands. Its passive bonuses (parry, balance regen) work always, even when armed; its attack and damage
  bonuses work only on the unarmed attack [OWNER, Q18].
- Group "Basic/simple" is special: no qualification, no maneuvers or special abilities, it cannot be trained; attacks
  with these weapons take no -4/-2 qualification penalty.
- Weapon card fields (owner's table): name, price (gp/sp), damage small and medium (dice), crit (range and multiplier),
  range, weight (stored in L), type (P/S/B), qualification (e.g. "Skilled", "Specialist 2"), finesse, hands (1H/2H),
  hardness (HD), item HP, list of groups. A value "Vary." is allowed: the field stays empty and is marked variable.
  Ammunition (bolts) are separate items with a piece counter.
- Catalog rows (owner's table, more later):
  Contact: Unarmed combat (1d2/1d3, crit 20, B, Skilled, finesse, 1H, no HD/HP); Stiletto (5 sp, 1d3/1d4, x3, weight L,
  P, Skilled, finesse, 1H, HD 10, HP 1); Spiked gauntlets (5 sp, 1d3/1d4, x2, weight L, P, Skilled, finesse, 1H);
  Improvised weapon (damage, weight, type, hands variable, x2, Skilled); Hidden thief weapons (all variable,
  Specialist 2, finesse, 1H).
  Basic/simple: Dagger (1 gp, 1d3/1d4, 19+, 10 ft, weight L, P/S, finesse, 1H, HD 10, HP 1); Club (-, 1d4/1d6, 20+,
  weight 1, B, 1H, HD 5, HP 2); Quarterstaff (2 sp, 1d4/1d4 and 1d6/1d6, 20+, weight 1, B, 2H, HD 5, HP 2);
  Light crossbow (1 gp, 1d6/1d8, 19-20, 80 ft, weight 1, P, 2H, HD 3, HP 2); Bolts x10 (1 sp, weight L, HD 0, HP 1, ammo).

## Weapon card details [OWNER]
- Shield as a weapon [OWNER, package 5]: a shield can be used as a weapon, improvised (group "Contact") or as a
  separate weapon with its own rules (then the card lists its groups). A shield in a hand has BOTH its shield bonus to
  AC and an attack record; its hands are counted once. By default the shield's attack record is in group "Contact"
  (improvised). Test: shield + sword in hands, the shield has an attack record, AC with the shield stays, 2 hands used.
- Double weapon (quarterstaff): the card has two damage rows, one per end. A normal attack uses the TOP row.
  A double weapon counts as fit for two-weapon fighting; its other end counts as a light weapon.
  Quarterstaff "1d4/1d4 and 1d6/1d6" = small 1d4 on both ends, medium 1d6 on both ends.
- Light and finesse are ONE flag (column "F." of the table). An unarmed strike is always light.
- Spiked gauntlets: you cannot parry with them; it is the same as parrying with an empty hand.
- Unarmed combat has no privileges [OWNER, Q20]: its qualification is Skilled (4); until it is trained to level 4
  the unarmed attack takes the -4 "not qualified" penalty.

## Mastery bonuses in the final numbers [OWNER]
- Weapon mastery bonuses stack with themselves by their own rules, then are added as FLAT to AC (parry), attack, damage.
- They change the FINAL durability (hardness) and HP of the item, not the value the author typed into the item.
- Item HP [OWNER, package 6]: the weapon's HP is stored as the CURRENT number; max = base + mastery HP + enchantment N
  (while activated). Broken (HP <= 50% of max, > 0): -2 to attack and damage with the weapon. HP 0: the weapon does
  not work. HP below 0: destroyed for good. Full rules: gear.md "Item HP".
  Durability: specialist +30%, expert +70% (they stack). Item HP: +1 per expert pick.
  Example: +30% and +70% picks -> +100% of the base durability.
  [OWNER, package 9] The percentages ADD (x2, not x1.3 x1.7) and apply after the enchantment: (base + 2N) * (100 + %).
  Only the item's MAIN attack record's group counts (gear.md "Order of item numbers").

## Notes
- This "qualification" is weapon level; item "Qualification N" in gear.md is a different mechanic (per-item, 50 training/level).
- Styles: similar branch rules; app can record one style per equipped weapon or two attack variants (progression.md).
- Crit range +1 here vs "mastery widens by 2" in combat.md: two specialist/expert picks give +2; check against source.
