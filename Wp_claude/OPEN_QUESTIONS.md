# Open questions
Format: id | question | recommendation | status. Owner answers; Claude records the result in RULES/ or ARCH/decisions.md.
Closed questions (answered, removed from here): ARCH/decision_log.md (append-only).

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
