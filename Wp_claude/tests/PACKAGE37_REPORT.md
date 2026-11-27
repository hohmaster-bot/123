# Package 37 report: universal mechanisms + the 12 races done properly (parts P1-P3)

## Done
P1 (finished; universal mechanisms, D36):
- 1.1 Every numeric rule constant is an effect target const:<id> (decision 1), generated from the rule data
  (rules.numeric_ids, the view effect_targets); a source adds to it or replaces it (note "replace"); the Sources view of
  "const:<id>" lists the table value, the character's override and every source; an unknown name gives a warning
  (never raises). There is no effect editor in the UI yet (Q276): manual rows on a constant in the Sources dialog.
- 1.2 Catalog kind trainings (one data file per module, like races), the command buy_training (units, price per unit,
  limit, unlock; journal, undo, no refund), the bought units as TrainingTaken (one source row "training:<id>" with
  N x the unit effect), the view trainings and the catalog section of the Training tab (show locked with the reason,
  Buy units). First user: Ragmal mana training (unlocked by Magic body).
- 1.3 Links both ways (decision 5): the view links (held by, backed, holds) for feats, statuses, quirks, trainings and
  items; hover in the Feats, Inventory, Narrative (quirks), Training and statuses lists ("held by", "holds", a lost
  holder red); the Feats tab lists a dependent under its parent and links the selected ability to a chosen holder
  (command set_held_by: journal, undo; a missing holder or self refused).
- 1.4 The missing targets: level offsets of the comfort exchange and Attention (constants, so const: targets); a scope
  on damage_per_pain (melee / ranged); the Mordon "no wound penalty" = pain_penalty_per_pain (exists), bleeding and
  comfort per fight have no rule in RULES (Q280); BP restored only by the long rest (spend_bp restore_only).
- 1.5 RULES/buffs.md, training.md, races.md extended (the package text is consent); D36; rule_audit.md updated.

## Tests and breaks
- P1: run_all: suites 99, passed 99, failed 0. break_check: entries 512, caught 510, missed 2; the two missed
  entries had a target that P1 really changed (p33-d-attention: Attention now reads attention_level(ch);
  p35-tab-qualify: the Training page moved to wp/ui/tab_training.py); both updated, rerun: entries 1, caught 1 each.
- New suites P1: model/test_pkg37a.py (10: comfort rate 10 / 60 / 8 / 10 by const effects, the Sources rows, a typo
  warns; a manual row 5 + 7 = 12; the targets list; Ragmal 3 units = 600, mana 6 -> 9, one source row, locked for
  others; a limit of 2; undo 1400 -> 2000; links both ways and set_held_by; Lomit 15 -> 20 and Attention 1 -> 2;
  Rage +3 melee only; Adrenaline BP 0 after a short rest, 2 after the long rest), ui/test_p37a.py (3: the Training
  tab catalog, the Feats links, shots tab_training_*, links_*). Breaks tests/breaks/pkg37.py (P1: 16).

## Changes to old rules
- P1 (owner consent in the package text): RULES/buffs.md "Rule constants as targets, links shown both ways",
  training.md "Catalog trainings", races.md "Package 37". New constants attention.level_offset and
  training.comfort_exchange_level_offset (0 = no change). New stored fields: Character.trainings, bp_long_rest_only;
  Effect.scope. The Training tab moved to wp/ui/tab_training.py.

## Assumptions
- P1: Q275 const effects; Q276 no effect editor yet; Q277 catalog trainings; Q278 links; Q279 the rage scope; Q280
  Mordon drawbacks without rules; Q281 Adrenaline BP.

## Open questions (ids)
- New: Q275-Q281; Q280 is a proposal (write the bleeding / comfort-per-fight rules if they should count).
