# Rule audit (package 36 P2.1): hard-coded rule numbers and behaviours of the core

Numbers: tests/test_rule_literals.py already proves that no rule NUMBER is written in code (every one is in
wp/rules_data/constants.json, read by rd.const / rd.ref; UI and math constants are named in its allowlist). So the
audit below lists BEHAVIOURS written in code that a race / feat / item may reasonably change, and how they are open now.

| place | what | now | planned as |
|---|---|---|---|
| core/derived.morale_bonus | morale counts only in combat | code | stays (RULES/defense.md); the morale scale is open to effects (morale_scale) |
| model/body_view.pain_total | effective pain = entries + HP pain | code | DONE: switch pain_reduction (target) |
| core/pain.is_dead | death at the pain cap | constant pain.death_cap + effect pain_cap | DONE: switch death_pain_cap = target pain_cap |
| commands/resource_cmds.restore | healing by the Heal button | code | DONE: switch heal_percent (decision 3) |
| commands/xp_cmds.add_experience | experience counted 1:1 | code | DONE: switch exp_percent |
| model/restores.rest_hp | HP a rest gives | rules settings multiplier / bonus | DONE: + switch natural_regen_percent |
| commands/combat_cmds.take_damage | HP below 0 -> dying (by hand) | code | DONE: switch at_negative_hp (dying / nothing / status:<id>) |
| core/damage._absorb | absorbers take every damage type | code | DONE: typed absorbers (effect absorber:<res>, note = types) |
| model/derived_view.temp_hp_total | spend order button -> own -> buffs | code (Q23, Q239) | stays; recorded in RULES/resources.md |
| commands/resource_cmds.short_rest | the short rest clears all temp HP | code (rest.md) | stays |
| core/tick | the zero-initiative tick order (balance, DoT, overload -1) | code + constants | stays (RULES/combat.md); triggers on zero_initiative added |
| model/sheet_numbers.at_base | items at the base give effects | code (gear.md) | stays; tagged_base_slots:<tag> reads them |
| core/effects.Effect.resolve | an effect always counts | code | DONE: condition / situational fields (decisions 7, 8) |
| commands (rests, cycle, combat) | events have no hooks | code | DONE: triggers (decision 6), reminders only, actions by a button |
| core/bonuses.Bonus | an unknown bonus type raised | code | DONE: untyped (decision 17) |
| model/drive_cmds | drive buy costs | constants | stays (data) |
| commands/training_cmds | prices of purchases | constants | stays (data); a race trait is an ordinary priced ability (decision 9) |

Not opened (no owner wish yet; a later package can add a switch the same way): the iterative step (a rules setting
already), the dying tick damage (constant dying.*), the balance cap homerule (one hit lowers the cap by 1).

## Package 37
- Every numeric constant is now an effect target const:<id> (decision 1): "a source may change any rule number" holds
  for all of them without a new target per case.
- New constants: attention.level_offset, training.comfort_exchange_level_offset (Lomit Adaptation).
- Not in data because no rule exists for them (no number to move): the bleeding loss and the comfort per fight
  (Mordon drawbacks stay text until the owner writes the rule). The wound penalty = the pain penalty
  (pain_penalty_per_pain already a target).
- damage_per_pain got a scope (melee / ranged); BP spent with restore_only long_rest (bp_long_rest_only).
