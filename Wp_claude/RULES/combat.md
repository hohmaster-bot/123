# Combat

## Actions [OWNER]
- Shift 1, Move 1, Standard 2, Full-round 3, Complete round 4 actions.

## Attack tag and iteration [OWNER]
- Options spent in own turn may carry tag "attack" (player sets tags himself, spells needing attack roll too).
- 2nd tagged option: -5, 3rd: -10. Paired (two-weapon) attacks: penalty applies to both.
- Abilities without the tag take no iterative penalty.
- Some abilities/effects ignore the iterative penalty WITHOUT being tagged as an attack (effect flag, e.g. master bonus: one attack per turn has no [attack] tag).

## Crit [OWNER]
- Notation 19+ / 20+ = threat range, x2. "x2/x3/x4" alone = crit on 20.
- Weapon mastery can widen range by 2 (20 -> 18). Keen property or similar feat doubles base threat range.
- Item must store: base crit + modifiers from mastery and properties. Crit range must be modifiable by feats.
- [package 10, R8] The attack view shows the crit range: the weapon's base range, "keen" (item property) doubles the
  BASE range, each mastery pick "crit +1" and each feat effect (target "crit_range", for this weapon) widen it by 1;
  never below 2; next to the multiplier hint. Tests: dagger 19+ -> 19 (x2, hint +0); with "crit +1" -> 18; keen -> 17;
  feat +1 -> 18.
- The crit confirmation roll already includes bonuses and penalties (rolled by the player); the core does not touch it [OWNER].
- Tooltip only (house-rule note, no calculation) when confirming a crit: x2 -> +0, x3 -> +4, x4 -> +8.

## Lucky attack [OWNER]
- Separate die, no bonuses/penalties. Base 20.
- +1 (lowers threshold) up to 3 times from mastery, plus X where X = weapon enchant level.
- Class/race/feat/ability can add +N for a specific weapon.
- [package 10, R7] Such an effect has target "lucky" (with a weapon id = that weapon only; no weapon id = every
  weapon). The cap 3 is for MASTERY picks only, as written above (OPEN_QUESTIONS Q60). Tests: enchant +2 -> 18;
  + one mastery pick -> 17; + a feat +1 for this weapon -> 16; a feat for another weapon -> no change; 4 mastery picks
  (forced) + enchant 2 + feat 1 -> 20 - 3 - 2 - 1 = 14. Never below 2.

## Attack records [OWNER]
- An attack record = weapon + chosen weapon group + grip (one hand, off-hand, two hands) + attack stat (default Str).
  One weapon may have several records (e.g. "Longsword + Long swords" and "Longsword + Heavy blades").
  Each record shows to hit, damage and parry with sources.
- Attacks are shown only for weapons held in the hands (doll: two hands, gear.md), plus the unarmed attack always.
- Primary records: the player marks up to two records as primary (e.g. one per hand). A single record is primary
  automatically. Passive group bonuses (balance regen +1 etc.) come from the primary records. Two primary records
  with DIFFERENT weapon groups: their passive bonuses add up; the same group counts once [OWNER, Q16].
- Grip [OWNER, Q19]: a one-handed weapon may be held with two hands (Str x1.5) only if it is NOT a finesse weapon.
  A finesse weapon: one hand or off-hand only. A two-handed weapon: two hands only.
- Str to damage by grip [OWNER]: one hand 1x, off-hand 0.5x, two hands 1.5x of the Str modifier; a positive value is
  multiplied and rounded DOWN (mod 3: two hands 4, off-hand 1); a negative modifier is NOT multiplied (-2 with any grip).

## Two-weapon fighting [OWNER, verbatim]
"If you wield a second weapon in your off hand, you can get one extra attack per round with that weapon. You suffer a -6 penalty with your regular attack or attacks with your primary hand and a -10 penalty to the attack with your off hand when you fight this way. You can reduce these penalties in two ways. First, if your off-hand weapon is light, the penalties are reduced by 2 each. An unarmed strike is always considered light. Second, the Two-Weapon Fighting feat lessens the primary hand penalty by 2, and the off-hand penalty by 6. Double Weapons: You can use a double weapon to make an extra attack with the off-hand end of the weapon as if you were fighting with two weapons. The penalties apply as if the off-hand end of the weapon was a light weapon. Thrown Weapons: The same rules apply when you throw a weapon from each hand. Treat a dart or shuriken as a light weapon, and a bolas, javelin, net, or sling as a one-handed weapon."

| Case | Primary hand | Off hand |
|---|---|---|
| Normal penalties | -6 | -10 |
| Off-hand weapon is light | -4 | -8 |
| Two-Weapon Fighting feat | -4 | -4 |
| Off-hand weapon is light and Two-Weapon Fighting feat | -2 | -2 |

- [OWNER] Both attacks are ONE combination (one action, one attack tag). Class and race features may lower the
  penalty down to 0: effect "two-weapon penalty reduction" (a number; the final penalty is never below 0, never a bonus).
- Feat "Two-Weapon Fighting" (base) is in the catalog (default price 200, editable). Improved and Greater versions are not added.
- An attack record has the toggle "combination of two attacks" (available with two weapons in the hands or a double
  weapon). A weapon takes 1 or 2 hand slots. When on, both attacks get the table penalties (feat? light/finesse off
  hand?). The second attack of a double weapon uses the lower damage row. The view marks which attack is the main
  hand and which the off hand.
- Record kinds [OWNER, package 9, closes Q38]: an item's MAIN record (kind "main") is the plain weapon attack; its
  group and picks are the ones that matter (also for item HP / hardness). Every other record of the item is a
  "maneuver" with a reference to its main record (base_record): it inherits BAB, stat, mastery bonuses, pain etc. from
  the main record and only adds its own modifiers (a later package). add_attack: the first record of an item is main,
  later ones are maneuvers on it; a second main is refused; a maneuver with another group is refused; a main record
  that maneuvers use cannot be removed first [OWNER, package 10: accepted, Q45]. Package 11 replaces these
  item-bound maneuvers with the character-level maneuver list below.
- Maneuver list [OWNER, package 10 design, closes Q44; built in package 11]: maneuvers live in a CHARACTER-level list,
  not inside items. Each has: name, description, required tags (weapon groups, weapon kinds, unarmed), attack
  modifiers (to-hit, damage, other bonuses/penalties), cost in actions and in balance. A maneuver is AVAILABLE when a
  weapon in the hands has any matching tag (a weapon is in many groups, e.g. a long sword in "long swords" and "heavy
  weapons", so both maneuver lists open). It uses the numbers of that weapon's main attack. Losing the weapon never
  deletes it: it is only unavailable (grey).
- Attack list [OWNER, package 10, closes Q37]: shows what is in the hands plus unarmed combat (all_attacks); the full
  list with unavailable records greyed out stays available (all_records). A "what is worn" tab with item pictures is
  an idea only (ROADMAP).
- Attack availability [OWNER, package 8]: setting the toggle is not checked against the hands; instead a record is
  AVAILABLE only while every weapon it needs is in the hands (two-weapon: both weapons, in either hand order; double
  weapon: the one weapon; an unarmed off-hand strike needs a free hand). An unavailable record tells which weapons it
  needs and what is in the hands (ids, the UI greys it out and explains, e.g. "in hands: sword A, shield A").
  Tests: A+B and B+A available; only A -> missing B; sword + shield -> missing B; double weapon in / out of hands;
  a weapon in the bag -> unavailable.

## Empty-hand parry [OWNER]
- Empty-hand parry and damage to balance [OWNER]: parrying with an empty hand is allowed. The player sees that the
  enemy roll landed in the parry number (armor/parry layer, defense_layers.md) and presses "take damage to balance".
  Command damage_to_balance(amount): the damage goes straight to the balance; HP are not touched; percent and DR are
  not applied (the player types the number). If the balance would go below 0, the overflow goes to OT and gives
  +1 pain (like an ordinary overflow). In combat the balance cap drops by 1 if the balance really lost points.
  Examples: balance 6, damage 4 -> 2, HP unchanged; balance 2, damage 5 -> 0, OT +3, pain +1, HP unchanged.

## Unarmed [OWNER]
- Unarmed combat is always available: the attack list always has the unarmed attack next to the weapons in hand.

## Maneuvers
- CMB / CMD / SR (SR not added yet, trait of race/class/feat).
- CMD does NOT follow AC rules. CMB gets weapon-group bonuses and others.
- Attack and CMB can use Dex instead of Str via option on the Attack/CMB or settings ("has finesse"):
  then the better of Str/Dex is used.
- Size (small/medium/large) affects attack, CMB, CMD.
  [package 10, R9] The attack roll gets the size modifier (Character.size_mod, the same number as the AC size layer).
  CMB/CMD get the size CMB modifier (Character.size_cmb, typed by hand; OPEN_QUESTIONS Q57). Test: size +1 -> attack +1.
- CMB / CMD in the sheet [package 10; open details Q58, Q59]:
  CMB = BAB + Str mod (with the Finesse feat: the better of Str / Dex) + size CMB mod + bonuses with target "cmb"
  + pain + morale (CMB is a roll). Weapon-group bonuses are not added yet (Q58).
  CMD = 10 + BAB + Str mod + Dex mod + size CMB mod + bonuses with target "cmd"; CMD is not a roll: no pain, no morale.
  Tests: BAB 3, Str 16, size 1, +2 -> CMB 9 (pain 1 -> 8); Finesse and Dex 18 -> 8; CMD 10 + 3 + 3 + 2 + 1 + 1 = 20.

## Spells damage
- Standard PF, but dice damage is affected by morale and pain. Editor unfinished [BETA]:
  level-scaled damage, damage types, areas, range.

## Stances
- Special feats with checkbox. One active stance at a time + one class stance (class stances not built).
- Example: "defensive": +2 dodge, -4 attack (flat). Player toggles by hand at fight start.
- No automatic stance prerequisites.
