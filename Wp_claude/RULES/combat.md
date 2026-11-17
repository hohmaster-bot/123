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
- The crit confirmation roll already includes bonuses and penalties (rolled by the player); the core does not touch it [OWNER].
- Tooltip only (house-rule note, no calculation) when confirming a crit: x2 -> +0, x3 -> +4, x4 -> +8.

## Lucky attack [OWNER]
- Separate die, no bonuses/penalties. Base 20.
- +1 (lowers threshold) up to 3 times from mastery, plus X where X = weapon enchant level.
- Class/race/feat/ability can add +N for a specific weapon.

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

## Unarmed [OWNER]
- Unarmed combat is always available: the attack list always has the unarmed attack next to the weapons in hand.

## Maneuvers
- CMB / CMD / SR (SR not added yet, trait of race/class/feat).
- CMD does NOT follow AC rules. CMB gets weapon-group bonuses and others.
- Attack and CMB can use Dex instead of Str via option on the Attack/CMB or settings ("has finesse"):
  then the better of Str/Dex is used.
- Size (small/medium/large) affects attack, CMB, CMD.

## Spells damage
- Standard PF, but dice damage is affected by morale and pain. Editor unfinished [BETA]:
  level-scaled damage, damage types, areas, range.

## Stances
- Special feats with checkbox. One active stance at a time + one class stance (class stances not built).
- Example: "defensive": +2 dodge, -4 attack (flat). Player toggles by hand at fight start.
- No automatic stance prerequisites.
