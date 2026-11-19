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
Q58 CMB per attack record, Q59 CMD formula, Q69 a status has no cost, Q70 stable injury ids, Q71 / Q73 accepted as written, Q72 armor slowdown with reduction (gear.md), Q74 stances = feats with active_stance (combat.md), pkg 12,
Q27 parry +1 per odd level from level 3, level 1 does not count (training.md),
Q37 attack list = in hands + unarmed, all_records for greying (combat.md, pkg 10), Q41 pay_hp_cost OT = overflow, pain by the damage rules (resources.md, pkg 10), Q42/Q45/Q47/Q48/Q50/Q52/Q53/Q54 accepted as written (pkg 10), Q43 spend_balance refused above balance (resources.md), Q44 maneuver list design, built in package 12 (combat.md), Q46 touch bonus not raised by enchantment, effect target touch_armor (gear.md), Q49 mana level = character level, refusal above it (classes_magic.md, gear.md), Q51 failed cancel: nothing refunded (gear.md),
Q33 spirit: floor 5 + 5 * Cha mod at 0 first, then bonuses (resources.md, pkg 9), Q34 non-proficient armor/shield: skill penalty also to attacks (training.md, pkg 9), Q35 balance cap snapshot at start of combat (resources.md, pkg 9), Q36 display-only condition tag (buffs.md, pkg 9), Q38 main record, order base -> enchantment -> mastery, additive percents (gear.md, combat.md, pkg 9), Q39/Q40 masterwork flag only, off while an enchantment is active, armor -1 then x2 (gear.md, pkg 9),
Q20 unarmed combat -4 until trained to Skilled (weapons.md), Q21 weight L = 1 L, N = N*10 L; quarterstaff is a double weapon; gauntlet zeros stay (catalog.md, weapons.md).

## Game rules (owner decides)
- Q23 | Temp HP spend order. ASSUMPTION (owner, package 4): first the "by button" temp HP, then buff temp HP in order (resources.md). Stacking flag: a non-stacking buff adds only up to its amount over the current total. | as is | assumption
- Q75 | Injury ids: a freed id (the injury was removed) may be given to a new injury with the same name (ids are made from the names on the sheet now). Keep a counter so an id is never reused? | as is until something refers to injuries by id | assumption (package 12)
- Q76 | Several attack records of one item: which record's group changes the item's HP and hardness (mastery picks)? Code: the primary record, else the first. | as is | assumption (package 12)
- Q77 | Maneuver tag "unarmed": possible when no item with weapon groups is in the hands. A shield without groups (improvised, Contact) or a torch does not block it. | as is | assumption (package 12)
- Q78 | A weapon in the hands that matches a maneuver's tags but has no attack record gives no numbers (reason no_attack_record). Build a default record from its first group instead? | as is | assumption (package 12)
- Q79 | A maneuver with no required tags: fits any weapon in the hands and the unarmed attack. | as is | assumption (package 12)
- Q80 | Armor slowdown with several worn items: the largest counts (like the armor bonus); a broken armor still slows fully (only HP 0 removes it). | as is | assumption (package 12)
- Q81 | Stances: combat.md also says "+ one class stance (class stances not built)". Now there is one field active_stance only. A second (class) stance slot later? | later, with the class system | open (package 12)
- Q82 | Effects that SWITCH OFF a bonus (stance "no dodge bonus to AC", spells.md "disable the Dex bonus to AC") and flags like "cannot be flanked" are not expressible. Add a "block" effect kind later? | yes, in a later package | open (package 12)
