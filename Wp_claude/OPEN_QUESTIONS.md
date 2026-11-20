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
Q75 injury ids never reused (counter, injuries.md), Q76-Q80 accepted as written, Q81 one stance per character (combat.md), Q82 block effects (buffs.md), pkg 13,
Q83/Q85/Q91 per-round status pays the first round at activation, own source instead of the single charge, Q84 an unpaid status ends at once, Q86 count removed (quantity), Q87/Q90 accepted, Q88 a long rest also restores short-rest pools, Q89 injury effects, Q92 every AC cell shows Full and Parry, modes become presets, Q94 item charges on the item (buffs.md, resources.md, gear.md, injuries.md, ac_zones.md, pkg 14),
Q93 parry with anything held, cells 1-3, shields by cells (ac_zones.md), Q95 a D-round status pays for exactly D rounds, Q97 no recharge field on statuses (buffs.md), pkg 15,
Q27 parry +1 per odd level from level 3, level 1 does not count (training.md),
Q37 attack list = in hands + unarmed, all_records for greying (combat.md, pkg 10), Q41 pay_hp_cost OT = overflow, pain by the damage rules (resources.md, pkg 10), Q42/Q45/Q47/Q48/Q50/Q52/Q53/Q54 accepted as written (pkg 10), Q43 spend_balance refused above balance (resources.md), Q44 maneuver list design, built in package 12 (combat.md), Q46 touch bonus not raised by enchantment, effect target touch_armor (gear.md), Q49 mana level = character level, refusal above it (classes_magic.md, gear.md), Q51 failed cancel: nothing refunded (gear.md),
Q33 spirit: floor 5 + 5 * Cha mod at 0 first, then bonuses (resources.md, pkg 9), Q34 non-proficient armor/shield: skill penalty also to attacks (training.md, pkg 9), Q35 balance cap snapshot at start of combat (resources.md, pkg 9), Q36 display-only condition tag (buffs.md, pkg 9), Q38 main record, order base -> enchantment -> mastery, additive percents (gear.md, combat.md, pkg 9), Q39/Q40 masterwork flag only, off while an enchantment is active, armor -1 then x2 (gear.md, pkg 9),
Q20 unarmed combat -4 until trained to Skilled (weapons.md), Q21 weight L = 1 L, N = N*10 L; quarterstaff is a double weapon; gauntlet zeros stay (catalog.md, weapons.md).

## Game rules (owner decides)
- Q23 | Temp HP spend order. ASSUMPTION (owner, package 4): first the "by button" temp HP, then buff temp HP in order (resources.md). Stacking flag: a non-stacking buff adds only up to its amount over the current total. | as is | assumption
- Q96 | Usage charges (items, feats, attack records, maneuvers): a long rest also restores "short_rest" charges, like pools (Q88). | as is | assumption (package 14)
- Q98 | block_restore: the restore and restore_pool commands REFUSE with a reason (they do not silently do nothing); rests and start_combat just keep the old value. | as is | assumption (package 14)
- Q99 | rest_regen_multiplier / rest_regen_bonus act on the HP gained by ONE rest command (the long rest heals to max, so the switch changes nothing there); no HP gained -> no bonus. | as is | assumption (package 14)
- Q100 | Formula numbers may be decimals (0.5); + - * are exact, / rounds down, the result rounds down. | as is | assumption (package 14)
- Q101 | Journal kinds are a fixed table by command id (commands/journal.py); a new command falls into "other" until it is added there. | as is | assumption (package 14)
- Q102 | Attention course "+1 ... adds to the stat bonus" (training.md, "transformation of attention into OV and others"): the code adds it to EVERY attention conversion (OV, OT removal, RL raise). Only OV? | all, as the text says "and others" | assumption (package 15)
- Q103 | level_up: RULES give no level cap. Add one (e.g. 20, like the class-system note)? | cap 20 in rules_settings | open (package 15)
- Q104 | Professionalism: "only classes without their own professionalism" and "skills from the class list" cannot be checked (no class data). The player chooses. | check when the class system exists | open (package 15)
- Q105 | Professionalism can be bought only once (assumption). Is a second purchase allowed? | once | assumption (package 15)
- Q106 | Spell mastery: a third identical upgrade would take 3 slots (1 more than the second); the text names only the second (2 slots). | as is (it never fits anyway) | assumption (package 15)
- Q107 | Comfort -> training rate: "item and class bonuses change it" (training.md), but there is no field for such a bonus. Add rules_settings.comfort_rate_bonus? | yes | open (package 15)
- Q108 | Q97 says a plain buff without a source has no recharge rule, but the package 8 rule (still in code) restores the charges of EVERY status on the long rest (and the short rest option). Stop restoring statuses without a source? | yes, restore only statuses whose source restores (needs a source link) | open (package 15)
- Q109 | Item qualification: training.md says "50 training per level" and "50 * N"; the code buys all N levels at once (50 * N) and does not model what it unlocks. Buy level by level instead? | as is | assumption (package 15)
- Q110 | Attention options 2 (training as if Dex/2 comfort) and 4 (0.2 * Int base points, fractions kept) have core functions but no command (fractional base points need a new field). Build them? | yes, package 16 | open (package 15)
- Q111 | level_up raises max HP (new roll + Con) but not the current HP. Heal the gained HP at level up? | no (the player heals) | assumption (package 15)
- Q112 | buy_maneuver: its `source` parameter is the purchase source (training / race...), so the maneuver's own free source label is set with edit_maneuver. | as is | assumption (package 15)
