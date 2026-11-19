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
Q37 attack list = in hands + unarmed, all_records for greying (combat.md, pkg 10), Q41 pay_hp_cost OT = overflow, pain by the damage rules (resources.md, pkg 10), Q42/Q45/Q47/Q48/Q50/Q52/Q53/Q54 accepted as written (pkg 10), Q43 spend_balance refused above balance (resources.md), Q44 maneuver list design, built in package 11 (combat.md), Q46 touch bonus not raised by enchantment, effect target touch_armor (gear.md), Q49 mana level = character level, refusal above it (classes_magic.md, gear.md), Q51 failed cancel: nothing refunded (gear.md),
Q33 spirit: floor 5 + 5 * Cha mod at 0 first, then bonuses (resources.md, pkg 9), Q34 non-proficient armor/shield: skill penalty also to attacks (training.md, pkg 9), Q35 balance cap snapshot at start of combat (resources.md, pkg 9), Q36 display-only condition tag (buffs.md, pkg 9), Q38 main record, order base -> enchantment -> mastery, additive percents (gear.md, combat.md, pkg 9), Q39/Q40 masterwork flag only, off while an enchantment is active, armor -1 then x2 (gear.md, pkg 9),
Q20 unarmed combat -4 until trained to Skilled (weapons.md), Q21 weight L = 1 L, N = N*10 L; quarterstaff is a double weapon; gauntlet zeros stay (catalog.md, weapons.md).

## Game rules (owner decides)
- Q55 | Save stats: RULES (classes_magic.md) say only "good saves (Fort/Ref/Will), as in current program". Code: the stat of each save is data, default Fort Con, Ref Dex, Will Wis (legacy program and PF1). | confirm the default | open (package 10)
- Q56 | Morale on initiative: defense.md says morale goes to "ALL rolls (skills, saves, attacks, maneuvers, CMB, damage)" without naming initiative (P2-15). Pain goes (resources.md: every roll with a die). Code keeps morale on initiative. | confirm | open (package 10)
- Q57 | Size modifier for CMB / CMD: RULES say only "size affects attack, CMB, CMD". Code: a separate number Character.size_cmb typed by hand (in PF1 it is the opposite sign of the AC/attack size mod: small -1, large +1). | owner gives the table, or derive from size | open (package 10)
- Q58 | combat.md: "CMB gets weapon-group bonuses and others". Which group (CMB is a sheet number, not per weapon)? Code: no group bonuses on CMB yet. | CMB per attack record (the record's group) | open (package 10)
- Q59 | CMD formula is not in RULES. Code: 10 + BAB + Str + Dex + size CMB + bonuses "cmd", no pain and no morale (CMD is not a roll; the legacy program added both). | confirm | open (package 10)
- Q60 | Lucky attack cap: the package 10 prompt says "the existing cap of 3 from all sources", but combat.md and the code cap only the MASTERY picks at 3; enchantment and feats add on top (test: 14). Code follows RULES. | confirm | open (package 10)
- Q61 | Base saves: the class progression (good / poor save) has no formula in RULES. Code: base save typed by hand per save (like BAB). | owner gives the formula or keeps hand input | open (package 10)
- Q62 | Metamagic: each further +1 circle adds another +2 mana (assumption from the owner text, docs only). | as is | assumption (package 10)
- Q63 | P2-17: a switched-off status still loses 1 duration per tick (checked: 3 -> 2). buffs.md says only "duration drops by 1 each zero-initiative phase". | owner: should an off status pause? | open (package 10)
- Q64 | P2-25: advanced skills are capped at the character level too (checked: level 2, advanced rank 2 -> 3 refused); skills.md:9 writes the cap only for normal skills, line 11 says specialized have no cap. | confirm the cap for advanced | open (package 10)
- Q65 | P2-12: combat.md says "Dex instead of Str via an option on the attack/CMB or settings (has finesse): then the better of Str/Dex". Code: the record's stat field can be set to any stat by hand (option), and a finesse weapon + the Finesse feat picks the better of Str/Dex automatically; a finesse weapon without the feat uses Str (checked). | confirm | open (package 10)
- Q66 | Overload speed -10 ft (gear.md): there is no speed in the model yet, so nothing is computed. | add a speed stat in a later package | open (package 10)
- Q67 | character.schema.json at the repo root: CLAUDE.md calls it "the only data contract", but the new storage writes dataclasses and never reads it (the file describes the legacy format). | owner: replace it with a generated schema of the new model, or drop the CLAUDE.md line | open (package 10)
- Q68 | Feats in the model have only flags, no effects: a feat's bonus (lucky +1, crit range +1...) is entered as a status for now (tests do so). | effects on feats in a later package | open (package 10)
- Q23 | Temp HP spend order. ASSUMPTION (owner, package 4): first the "by button" temp HP, then buff temp HP in order (resources.md). Stacking flag: a non-stacking buff adds only up to its amount over the current total. | as is | assumption
