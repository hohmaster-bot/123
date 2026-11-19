# Open questions
Format: id | question | recommendation | status. Owner answers; Claude records the result in RULES/ or ARCH/decisions.md.
Closed and removed (answered in RULES/): Q1 injury effects (injuries.md: active injury applies while it exists),
Q2 `enabled` (gear.md: means item activation), Q4 tick_mode (buffs.md duration kinds + rest.md charge restore),
A054 over max (resources.md "Over max", D5), Q10 decisions approved, R9 short rest unlimited (rest.md),
R8 short rest BP flow (rest.md), Q3 stance (spells.md), Q5 spells (spells.md), Q6 shop (catalog.md), Q7 catalogs global (catalog.md, D13),
Q8 no old characters (D1), Q9 hotkey Ctrl+Shift+W (surfaces.md), Q11 overlay editor (surfaces.md),
Q12 end of combat resets overload to 0 (resources.md),
Q13 end of combat resets the morale scale to 0 (defense.md),
Q14 activation "day"/"decade" is an item field, cost separate (gear.md),
Q15 feat "Finesse training" costs 200 (training.md),
Q16 passive bonuses of two primary records add up for different groups, same group once (combat.md),
Q17 no refund for a specialized rank the level caught up with (skills.md),
Q18 Unarmed combat attack/damage only on the unarmed attack, passives always (weapons.md),
Q19 two hands only for a non-finesse one-handed weapon (combat.md),
Q22 base point 100, max 10*level (training.md), Q24/Q25 flat = positive untyped only, no negative layers, penalties lower the base (defense_layers.md, pkg 5),
Q26 enhancement -> armor layer; other unlisted types: positive -> flat, negative -> penalty (assumption, defense_layers.md),
Q28 heavy/tower shield in hand adds its shield bonus to balance max; tower GRADE gives +2 parry (training.md),
Q29 professionalism 300 only for classes without their own; the level number is a placeholder (training.md),
Q30 enchantment = activation effect; no price -> ordinary item, always off (gear.md),
Q31 item HP stored as the current number, on +N / off scaled, broken/0/destroyed (gear.md "Item HP"),
Q32 item repair only by hand in edit mode (gear.md),
Q55 saves Fort Con / Ref Dex / Will Wis, Q56 morale on initiative (only in combat), Q60 lucky cap only on mastery picks, Q61 base saves by hand (class system plan in ROADMAP), Q62 +2 mana per extra circle, Q64 advanced ranks capped by level (defense.md, combat.md, spells.md, skills.md, pkg 11),
Q57 / Q66 size small/medium/large and speed (combat.md "Size and speed"), Q63 status container: no toggle, no pause (buffs.md), Q65 stat-mod effect value (buffs.md), Q67 schema deleted (tests/SCHEMA_REVIEW.md), Q68 feats with effects (training.md), pkg 11,
Q27 parry +1 per odd level from level 3, level 1 does not count (training.md),
Q37 attack list = in hands + unarmed, all_records for greying (combat.md, pkg 10), Q41 pay_hp_cost OT = overflow, pain by the damage rules (resources.md, pkg 10), Q42/Q45/Q47/Q48/Q50/Q52/Q53/Q54 accepted as written (pkg 10), Q43 spend_balance refused above balance (resources.md), Q44 maneuver list design, built in package 11 (combat.md), Q46 touch bonus not raised by enchantment, effect target touch_armor (gear.md), Q49 mana level = character level, refusal above it (classes_magic.md, gear.md), Q51 failed cancel: nothing refunded (gear.md),
Q33 spirit: floor 5 + 5 * Cha mod at 0 first, then bonuses (resources.md, pkg 9), Q34 non-proficient armor/shield: skill penalty also to attacks (training.md, pkg 9), Q35 balance cap snapshot at start of combat (resources.md, pkg 9), Q36 display-only condition tag (buffs.md, pkg 9), Q38 main record, order base -> enchantment -> mastery, additive percents (gear.md, combat.md, pkg 9), Q39/Q40 masterwork flag only, off while an enchantment is active, armor -1 then x2 (gear.md, pkg 9),
Q20 unarmed combat -4 until trained to Skilled (weapons.md), Q21 weight L = 1 L, N = N*10 L; quarterstaff is a double weapon; gauntlet zeros stay (catalog.md, weapons.md).

## Game rules (owner decides)
- Q58 | CMB per attack record: moved to package 12 (ROADMAP): the sheet shows a general CMB without weapon AND a CMB per attack record with that record's group bonuses; the UI may use either or both. | as planned | planned (package 12)
- Q59 | CMD formula is not in RULES. Code: 10 + BAB + Str + Dex + size CMB + bonuses "cmd", no pain and no morale (CMD is not a roll; the legacy program added both). | confirm | open (package 10)
- Q23 | Temp HP spend order. ASSUMPTION (owner, package 4): first the "by button" temp HP, then buff temp HP in order (resources.md). Stacking flag: a non-stacking buff adds only up to its amount over the current total. | as is | assumption
- Q69 | Status activation cost (package 11 A): which resources may pay it? The prompt says only "cost". Code: spirit, balance or mana (others refused with a reason). | confirm the list | assumption (package 11)
- Q70 | Injuries have no stable id (D7); the container view uses the list position "injury:N". Give injuries an id? | yes, with a later injury command | open (package 11)
- Q71 | Stat-mod effect value with a non-whole multiplier (0.5): rounded down (PF style). The prompt gives no rounding. | confirm | assumption (package 11)
- Q72 | Armor slowdown: the armor card field speed_penalty_ft is stored but not counted in speed (package 11 C names only overload -10 ft and speed effects). Count it (armor in a slot -> speed - N ft)? Abilities that ignore the slowdown (gear.md) then need a flag. | count it, with an ignore flag | open (package 11)
- Q73 | Old files with the hand-typed size_mod (package 10) load as size medium: the old number is dropped, not converted (no migrations, D1). Fine? | as is (no old characters, D1/Q8) | assumption (package 11)
- Q74 | Stances: the package 11 prompt says "stances already exist", but the new model has none (RULES spells.md: a stance is a feat with the checkbox "is stance"; the legacy code had it, the new Feat has no such flag and no command). How should a stance work now: a feat flag with its own effects switched by choosing the active stance, or a status in the container? | a status in the container (no feat toggle, matches "feats have no toggle modes") | open (package 11)
