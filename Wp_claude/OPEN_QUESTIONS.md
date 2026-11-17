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
Q19 two hands only for a non-finesse one-handed weapon (combat.md).

## Game rules (owner decides)
- Q20 | Unarmed combat has qualification "Skilled" (level 4) in the table. A new character has the Unarmed combat node at level 0, so the unarmed attack gets the -4 "not qualified" penalty. Is that intended? Now: yes, -4 (the table is applied literally). | ? | open
- Q21 | Weight in the table: "L" and "1". Stored now as 1 L and 10 L (1 B). Is "L" = 1 L, and "1" = 1 B = 10 L? Quarterstaff damage "1d4/1d4 and 1d6/1d6" is stored as text (two ends?). Spiked gauntlets: no HD/HP in the table - left 0. | ? | open
- Q22 | Price of one base slot: 100 training is taken from the old code (training_costs_draft.md); RULES give no price. Confirm 100? | 100 | open
- Q23 | Temp HP pools: when combat temp HP and temp HP of a timed buff both exist, which are spent first? Now: combat temp HP first, then buffs in order. Stacking flag: a non-stacking buff adds only up to its amount over the current total. | ? | open
