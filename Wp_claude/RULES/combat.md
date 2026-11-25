# Combat

## Actions [OWNER]
- Shift 1, Move 1, Standard 2, Full-round 3, Complete round 4 actions.
- [OWNER, package 26 A] Actions are a resource: 3 per turn (data constant), effects "actions_max" add more (spells,
  abilities, items, statuses; typed stacking). They come back on the zero-initiative tick and at the end of combat.
  Attack records, maneuvers, quick buttons and spells may show a cost in actions (the costs above are presets);
  nothing is spent automatically: the player presses spend.

## Attack tag and iteration [OWNER]
- Options spent in own turn may carry tag "attack" (player sets tags himself, spells needing attack roll too).
- 2nd tagged option: -5, 3rd: -10. Paired (two-weapon) attacks: penalty applies to both.
- Abilities without the tag take no iterative penalty.
- [OWNER, package 22 A5] A paired (two-weapon) combination is ONE action and ONE use: the iterative counter +1 per
  combination (not +2); the TWF table penalties stay. Test: a combination, then a normal attack -> -5, not -10.
- Some abilities/effects ignore the iterative penalty WITHOUT being tagged as an attack (effect flag, e.g. master bonus: one attack per turn has no [attack] tag).
- [OWNER, package 16 C] The iterative penalty is its own NEGATIVE line "iterative" on the attack, never typed by the
  player: Character.iterative_count = attacks already used in this round's series. use_attack(rid) (the "attack"
  button) adds 1; the zero-initiative tick (new round) and end_combat set it to 0; set_iterative_count(n) sets it by
  hand. Step: rules_settings.iterative_step (default -5, data) or the record's own iterative_step; effects
  "iterative_penalty" make each step smaller (a step never goes above 0). Penalty of the next attack = count * step.
  A status with ignores_iterative: no penalty. Effect.when_iterative is stored only (no formula yet).
  Tests: 3 attacks 0 / -5 / -10; reduction 2 -> 0 / -3 / -6; reset by the tick; manual set 2 -> -10; record step -3.

## Crit [OWNER]
- Notation 19+ / 20+ = threat range, x2. "x2/x3/x4" alone = crit on 20.
- [OWNER, package 17, closes Q113] Weapon mastery gives +1 crit range per "crit +1" pick, at most 3 picks (one in
  each tier: specialist, expert, master). Keen property or similar feat doubles the BASE threat range only.
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
  weapon). The cap 3 is for MASTERY picks only, as written above [OWNER, Q60: keep as written]. Tests: enchant +2 -> 18;
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
- Attack records [OWNER, package 12 B; replaces the package 9 record kinds]: every attack record of an item is a
  main attack record (its own group, grip and stat). The item-bound "maneuver" records of packages 9-11 are removed;
  old files drop them on load (D1). With several records of one item, the record whose group changes the item's HP
  and hardness is the PRIMARY one, else the first (assumption Q76).
- Maneuver list [OWNER, package 10 design, closes Q44; built in package 12]: maneuvers live in a CHARACTER-level list,
  not inside items. Each has: name, description, required tags (weapon groups, weapon kinds, unarmed), attack
  modifiers (to-hit, damage, other bonuses/penalties), cost in actions and in balance. A maneuver is AVAILABLE when a
  weapon in the hands has any matching tag (a weapon is in many groups, e.g. a long sword in "long swords" and "heavy
  weapons", so both maneuver lists open). It uses the numbers of that weapon's main attack. Losing the weapon never
  deletes it: it is only unavailable (grey).
- Maneuver fields [OWNER, package 12 B]: id (made by the program), name, description, required_tags (weapon group ids,
  weapon kind ids = the catalog card id of the weapon, and the special tag "unarmed"), tag_mode ("any" default |
  "all"), modifiers (to_hit and damage numbers, untyped, plus an optional effects list in the usual effect structure,
  applied to this maneuver's attack only with the usual stacking), cost_actions, cost_balance, cost_spirit (RECORD
  ONLY: nothing is spent automatically), required_feat (optional feat id: unavailable unless the feat is owned; a
  feat's granted_maneuvers ids are shown on the maneuver as "granted by"), condition_tag, favorite, source (free
  label: style / class / feat), notes, extra (unknown future keys, kept on save/load, never interpreted).
  Commands: add_maneuver, edit_maneuver (any field), remove_maneuver.
- Weapon tags = all groups of the weapon (a shield without groups: Contact) + its own kind id. maneuver_view: for every
  maneuver, available yes / no; ONE ENTRY PER matching weapon in the hands (numbers differ per weapon): to-hit and
  damage = that weapon's main attack record numbers (BAB, stat, pain, the record group's mastery, enchantment...)
  + the maneuver's modifiers, plus the CMB of that record. "unarmed" matches while the unarmed attack is possible: no
  weapon (an item with weapon groups) in the hands. Unavailable -> reason ids: no_matching_weapon, feat_missing,
  unarmed_not_possible, no_attack_record.
- Assumptions (OPEN_QUESTIONS Q77-Q79): a shield or other item without weapon groups in the hand does not block
  "unarmed"; a matching weapon without any attack record gives no numbers (no_attack_record); a maneuver with no
  required tags fits any weapon in the hands and the unarmed attack.
- Tests: tag any / all; one weapon in two groups opens both; the weapon kind id is a tag; two matching weapons -> two
  entries (the expert one +3); numbers = main attack + modifiers; effects stack by type; unarmed with empty hands and
  refused with a sword; required_feat; weapon put away -> unavailable but kept; costs not spent; save / load with extra.
- What a combat STYLE can give [OWNER examples, package 12]: stances with restrictions, its own counters, maneuvers
  costing actions / balance / spirit with their own damage or number of attacks, changed weapon properties (finesse,
  free draw, damage die up), conditions on targets (vulnerability, burning), crit range overrides, start-of-round
  effects. These are intentionally NOT modeled: the player writes a maneuver with a name, cost, modifiers and a
  description and plays the rest by hand. The extra dict and the tags are the only stubs. Not built on purpose:
  automatic spending of actions / balance / spirit, stance restrictions, custom counters (like "Spark"), target
  conditions, start-of-round triggers, weapon property overrides.
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
  [package 10, R9] The attack roll gets the size modifier (the same number as the AC size layer).

## Size and speed [OWNER, package 11 C; closes Q57, Q66]
- The race (the character's race fields) holds the size: small | medium | large only, and the base speed in feet
  (default 20). The hand-typed size CMB field is removed (old files: dropped on read).
- Size modifiers: attack and AC small +1, medium 0, large -1. CMB and CMD small -1, medium 0, large +1 (opposite sign).
- Effect target "speed": typed bonuses / penalties from any source (items, abilities, statuses, feats), stacked by the
  usual rules. Derived speed = base + bonuses; encumbrance gives -10 ft (gear.md). Speed is not a roll: no pain, no morale.
- One move = 1 action.
- Armor slowdown: REPLACED by gear.md "Armor" (package 12, Q72): the worn armor's speed_penalty_ft lowers the speed,
  minus effects "armor_slowdown_reduction" (the old line "stored but not counted" no longer applies).
- Tests: BAB 2, Str/Dex 12 -> (attack, AC, CMB, CMD) small (+1, 12, 2, 13), medium (0, 11, 3, 14), large (-1, 10, 4, 15);
  base 20; +10 ft item -> 30; -5 ft status -> 15 (inactive: 20); encumbrance -> 10.
- CMB / CMD in the sheet [package 10; Q58 and Q59 answered in package 12]:
  CMB = BAB + Str mod (with the Finesse feat: the better of Str / Dex) + size CMB mod + bonuses with target "cmb"
  + pain + morale (CMB is a roll). This is the general CMB without a weapon.
  CMB per attack record [OWNER, package 12 C, Q58]: every attack record view also shows its CMB = the general CMB
  + the record group's mastery attack bonus (the same "attack +1" picks the record gets). The UI may use either or
  both; a maneuver view shows the CMB of the matching weapon. Tests: two swords, one with mastery +3: CMB 7 and 4,
  general 4; with pain 1 and morale scale 4 in combat: 8, 5, 5.
  CMD [OWNER, Q59] = 10 + BAB + Str mod + Dex mod + size CMB mod + bonuses with target "cmd"; no pain, no morale.
  Tests: BAB 3, Str 16, size large (+1), +2 -> CMB 9 (pain 1 -> 8); Finesse and Dex 18 -> 8; CMD 10 + 3 + 3 + 2 + 1 + 1 = 20.

## Spells damage
- Standard PF, but dice damage is affected by morale and pain. Editor unfinished [BETA]:
  level-scaled damage, damage types, areas, range.

## Stances
- Special feats with checkbox. ONE active stance per character [OWNER, package 13, Q81]: classic (class) stances are
  ordinary stance feats.
- Attack records, maneuvers and feats may carry charges and a cooldown (gear.md "Charges and cooldown", package 14 B).
- Example: "defensive": +2 dodge, -4 attack (flat). Player toggles by hand at fight start.
- No automatic stance prerequisites.
- [OWNER, package 12, Q74; replaces earlier stance notes] A stance is a FEAT with the flag is_stance. The character
  has one field active_stance (a feat id or none). Command set_active_stance(feat id | none): refused when the feat
  is not owned or is not a stance. A stance feat's effects apply ONLY while it is the active stance; ordinary feats
  always. No lock flag and no combat rule: the player decides when to change it; end_combat does not change it.
  Removing the stance feat clears active_stance. Stances are NOT statuses in the container. The derived view lists the
  stances and the active one (the UI gives stances their own visual element).
- [package 13, Q82] Style "Me Liquescit" (no dodge bonus to AC, cannot be flanked) is expressed with block effects
  (buffs.md "Block effects"): block_bonus {type dodge, scope ac} + cannot_be_flanked on the stance feat. Test: Dex 14,
  dodge +1, shield 2: stance off -> front 15, flank 13; stance on -> front 12, flank 12.
- Tests: the stance effect applies only while active; switching stances; refusals (not owned, not a stance); removing
  the feat clears active_stance; end_combat keeps it; the view; not in the container.


## Attack kinds [OWNER, package 17, part of Q122]
- A weapon card (Item.attack_kind) and an attack record (AttackRecord.kind, "" = the card's) are melee | ranged |
  thrown. Defaults are data (rules_settings): ranged = attack with Dex, NO stat to damage; thrown = attack with Dex,
  Str to damage x1; melee unchanged (Str by grip x1 / x0.5 / x1.5, Finesse rule).
- Record overrides: stat (the attack stat), damage_stat ("none" or a stat id), damage_mult (a number). A positive
  stat modifier is multiplied and rounded down, a negative one counts once as is. This replaces the old "own damage
  stat and multiplier".
- Tests: Str 16, Dex 14: bow (ranged) -> Dex, damage 0; dagger (thrown) -> Dex, +3; sword one hand +3, two hands +4;
  bow with damage_stat str -> +3; sword damage_mult 2 -> +6; thrown with Str 6 -> -2.

## Reactions [OWNER, package 22 A2]
- Reactions are a resource with the fixed id "reactions": max = the bought reactions (start 1; +1 for 200 * the new
  number, training.md) + effects "reactions"; current = what is left this round.
- spend_reaction(n) (free attacks of opportunity, readied attacks: the player presses; refused at 0, reason
  not_enough_reactions); restore_reactions (manual, edit level). The zero-initiative tick (a new round) and the end of
  combat bring them back to max.
- Attack records, maneuvers and feats may carry cost_reactions: an attack record spends them in use_attack (refused
  when not enough); a maneuver is shown unavailable (reason not_enough_reactions); a feat keeps it as a record.
- Tests: start 1/1; spend -> 0, again refused; tick -> 1; 2 reactions for 400; an attack of opportunity record costs 1.

## Damage roll and pain [package 22 B5]
- The damage roll is a roll with a die: the pain penalty and morale apply to it, like to the attack roll
  (resources.md "Pain", defense.md "Morale").
- [package 25 F] Spell damage as data: components {dice count (formula, may use level), die size, flat
  (formula), damage type (one of the 12), area (single / cone / line / burst / other), range, save, save effect}.
  The spell view gives them for the caster level with the pain penalty and morale of the damage roll; the app
  never rolls dice.

## General attack numbers (package 30) [OWNER; closes Q198]
- MELEE = Str modifier + BAB by default; RANGED = Dex modifier + BAB. Each is editable per character: the source may
  be another stat + BAB (e.g. Dex + BAB for melee) or a SPECIFIC WEAPON (an attack record: its to-hit, and the view
  names the weapon). Command set_attack_source(kind, source).
- PAIN is always counted in these numbers (not only in combat). MORALE applies only DURING combat (the combat view
  has the flag morale_active = in combat).
- Tests: Str 14 (+2), BAB +2 -> melee +4; Dex 20 (+5), BAB +2 -> ranged +7; with pain 1 (penalty -1) -> +3 / +6;
  morale scale 4 out of combat -> no change, in combat +2.
