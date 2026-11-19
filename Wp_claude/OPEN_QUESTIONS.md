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
Q33 spirit: floor 5 + 5 * Cha mod at 0 first, then bonuses (resources.md, pkg 9), Q34 non-proficient armor/shield: skill penalty also to attacks (training.md, pkg 9), Q35 balance cap snapshot at start of combat (resources.md, pkg 9), Q36 display-only condition tag (buffs.md, pkg 9), Q38 main record, order base -> enchantment -> mastery, additive percents (gear.md, combat.md, pkg 9), Q39/Q40 masterwork flag only, off while an enchantment is active, armor -1 then x2 (gear.md, pkg 9),
Q20 unarmed combat -4 until trained to Skilled (weapons.md), Q21 weight L = 1 L, N = N*10 L; quarterstaff is a double weapon; gauntlet zeros stay (catalog.md, weapons.md).

## Game rules (owner decides)
- Q37 | combat.md: "attacks are shown only for weapons held in the hands". Package 8 B wants unavailable records greyed out. Code: all_attacks keeps the rule (in hands + unarmed), each view has `available`; new all_records lists EVERY record with `available` / `missing` for greying out. | UI uses all_records for the full list | open (package 8) Not answered in package 9: still open.
- Q41 | pay_hp_cost overflow: the package 9 prompt says "+1 OT + 1 pain exactly like damage to balance", but damage to balance gives OT = the WHOLE overflow (+1 pain). Code follows the existing command (cost 9, balance 7 -> OT +2). | confirm "OT = overflow" or "OT +1 always" | open (package 9)
- Q42 | Armor or shield with no category on the card: which proficiency rank does it need? Code: counts as light (rank 1). | as is | assumption (package 9)
- Q43 | spend_balance with more than the current balance: code refuses (a payment cannot go below 0). | as is, or allow with overflow like pay_hp_cost | open (package 9)
- Q44 | Removing a main attack record that maneuvers use: code refuses until the maneuvers are removed. | as is, or remove them with it | open (package 9)
- Q45 | Maneuver: inherits group and attack stat from its main record now; its own grip is kept; a different group on add_attack is refused. | as is until the maneuver package | assumption (package 9)
- Q46 | Touch AC bonus of armor: does enchantment N raise it (like the armor bonus)? Code: no. | owner | open (package 9)
- Q47 | Spell penalty reductions: effects with target spell_penalty_mana / spell_failure_pct use their value as is (a feat -2 lowers by 2; a positive value raises the penalty). | as is | assumption (package 9)
- Q48 | Mage armor penalty split: the base spell still costs mana = balance = its cost; only the extra is split (default: all extra from mana; the player sets the part from balance). | as is | assumption (package 9)
- Q49 | "Mana level" (the most one spell may cost) has no formula in RULES: a new field mana_level typed by hand (0 = no cap). When capped, the penalty is cut first, then the spell's own cost. | owner gives the formula | open (package 9)
- Q50 | Armor mana penalty on cantrips (circle 0, no mana cost): code adds it only to circle 1+ mana spells. | as is | assumption (package 9)
- Q51 | Spell failure in mode "cancel": which resources are spent? RULES are silent; code keeps everything already paid by cast_spell (no refund) and only reports "not cast". | owner | open (package 9)
- Q52 | Slot caster with failure chance 0: the view says failure_applies = True with chance 0 (nothing to roll). | as is | assumption (package 9)
- Q53 | Armor data set 1: the "magic" column is written negative in the source (-1, -4, -8); stored as a positive extra mana cost (1, 4, 8). Weight "(1)" read as the plain number 1 = 10 L. Columns "access class" and set 2 "special (+)" are kept as data only, no rule uses them. | confirm | open (package 9)
- Q54 | Balance cap snapshot is stored on the character (balance_cap_start) while combat is active: the owner rule needs the value from the moment combat started, so it cannot be computed on read. | as is | assumption (package 9)
- Q23 | Temp HP spend order. ASSUMPTION (owner, package 4): first the "by button" temp HP, then buff temp HP in order (resources.md). Stacking flag: a non-stacking buff adds only up to its amount over the current total. | as is | assumption
