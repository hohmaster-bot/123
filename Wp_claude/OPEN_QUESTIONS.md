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
Q27 parry +1 per odd level from level 3, level 1 does not count (training.md),
Q20 unarmed combat -4 until trained to Skilled (weapons.md), Q21 weight L = 1 L, N = N*10 L; quarterstaff is a double weapon; gauntlet zeros stay (catalog.md, weapons.md).

## Game rules (owner decides)
- Q33 | Spirit max with a negative Cha and a bonus. RULES (resources.md): "5 + 5 * Cha mod, never below 0, PLUS bonuses" -> Cha 6 (-2) with +3 = 3. The package 8 prompt writes max(0, 5 + 5 * Cha mod + bonuses) -> 0. Code and test m13 keep the RULES result (3). | keep RULES (3) unless the owner says the prompt formula is meant | open (package 8)
- Q34 | Shield without proficiency (rank below the shield's type): RULES have no number for the "non-proficient" penalty. Code: no balance bonus, `shield_proficient` = False in the item view; no attack/skill penalty is added. | owner gives the penalty (PF1: the shield's skill penalty also to attack rolls) | open (package 8)
- Q35 | Package 8 H says "the balance cap is NOT recomputed during combat", item I says "R12 live cap stays". The code keeps the live cap (spending BP or taking armor off mid-combat changes it at once); a Con change does not touch it either way (test h-con-mid-combat). | keep live (I is explicit) | open (package 8)
- Q36 | Package 8 G removes the "combat only" condition. The "out of combat only" value (buffs.md, items giving skill bonuses outside combat) was removed with it (the whole field is gone); such a bonus is switched on/off by hand. | confirm; if wanted back, add it as a plain flag | open (package 8)
- Q37 | combat.md: "attacks are shown only for weapons held in the hands". Package 8 B wants unavailable records greyed out. Code: all_attacks keeps the rule (in hands + unarmed), each view has `available`; new all_records lists EVERY record with `available` / `missing` for greying out. | UI uses all_records for the full list | open (package 8)
- Q38 | Item with several attack records of different groups: whose mastery picks change its HP/hardness? ASSUMPTION: the item's primary record, else its first record (one group, never two). | as is | assumption (package 8)
- Q39 | Masterwork flag vs the old way (gear.md: "masterwork +1 to attack" written into the "not activated" tab). Both at once give +1 only if the tab effect is typed enhancement; an untyped tab effect would add. | use the flag only; remove masterwork from tabs | open (package 8)
- Q40 | Masterwork armor penalty and a broken item: ASSUMPTION masterwork -1 first, then x2 (-3 -> -2 -> -4). | as is | assumption (package 8)
- Q23 | Temp HP spend order. ASSUMPTION (owner, package 4): first the "by button" temp HP, then buff temp HP in order (resources.md). Stacking flag: a non-stacking buff adds only up to its amount over the current total. | as is | assumption
