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

P2 (finished; the 12 races done properly, decisions 2-6):
- 2.1 Charges follow the race ability: a race ability may carry a usage (charges, recharge rule); a racial status may
  name its source (source_ref feat:<ability>), so the core refills it by that rule: Dance with blades at every combat
  start, Shadow of Santerra and Eradication of filth after the long rest.
- 2.2 Short effects: Heavy swing = a 1-tick status with 2 temporary HP (its button turns it on); the Rahim tail = a
  1-tick status -2 AC (button); Hunt for incarnations = an end-of-combat status +1 damage per stack (new: Status.stacks,
  the formula variable "stacks"; turning an active status on again by a trigger adds a stack) with the button "spend 4
  mana"; the Mordon -4 on the first five attacks = 5 charges of the history (refilled at the combat start) and the new
  condition charges_left:<kind>:<id>; its buy-out cancels the -4.
- 2.3 Copying and Universality have no effects (text: link the taken feat); the Mordon +2 stays six manual boxes; Lomit
  Adaptation, Ulstanger Rage (melee), Mordon Wall of Bones (no pain penalty) and Ankalian Adrenaline (BP back only by
  the long rest) use the P1 targets; Ragmal mana is the catalog training; Endurance and Toughness are placeholder feats
  (sample, price 0, "the owner's text is needed"); 9 races say "choose two languages of the region".
- 2.4 Decision 6: Ragmal mana -> catalog training (it is bought in units, repeatedly); the Skerde swim and the Rahim
  flight stay race abilities bought once with training (no units, a needs chain: good flight needs flight), so a
  catalog training would add nothing (Q288).

## Tests and breaks
- P1: run_all: suites 99, passed 99, failed 0. break_check: entries 512, caught 510, missed 2; the two missed
  entries had a target that P1 really changed (p33-d-attention: Attention now reads attention_level(ch);
  p35-tab-qualify: the Training page moved to wp/ui/tab_training.py); both updated, rerun: entries 1, caught 1 each.
- New suites P1: model/test_pkg37a.py (10: comfort rate 10 / 60 / 8 / 10 by const effects, the Sources rows, a typo
  warns; a manual row 5 + 7 = 12; the targets list; Ragmal 3 units = 600, mana 6 -> 9, one source row, locked for
  others; a limit of 2; undo 1400 -> 2000; links both ways and set_held_by; Lomit 15 -> 20 and Attention 1 -> 2;
  Rage +3 melee only; Adrenaline BP 0 after a short rest, 2 after the long rest), ui/test_p37a.py (3: the Training
  tab catalog, the Feats links, shots tab_training_*, links_*). Breaks tests/breaks/pkg37.py (P1: 16).

- P2: run_all: suites 100, passed 100, failed 0. Breaks P2: 15 new (code 7, data 8); break_check p37-: entries 31,
  caught 31, missed 0; the 29 older entries on the files P2 changed: caught 29; every other entry's pattern still
  applies (the one that did not, p36-condition, came from an extra edit of mine, reverted).
- New suite P2: model/test_races37.py (15: Dance / Shadow / Eradication charges, Heavy swing tick, Rahim tail, Hunt
  stacks, only a cumulative status stacks, the Mordon -4 counter, effect-less Copying / Universality, the placeholder feats, the language texts,
  Ragmal 3 units, Lomit, Rage melee, Adrenaline, Wall of Bones). The catalog feat count 3 -> 5 in test_ui_logic35c,
  test_p36a, test_tabs35 (the two placeholders).

## Changes to old rules
- P1 (owner consent in the package text): RULES/buffs.md "Rule constants as targets, links shown both ways",
  training.md "Catalog trainings", races.md "Package 37". New constants attention.level_offset and
  training.comfort_exchange_level_offset (0 = no change). New stored fields: Character.trainings, bp_long_rest_only;
  Effect.scope. The Training tab moved to wp/ui/tab_training.py.

- P2 (owner consent in the package text): RULES/races.md "Package 37 P2". New stored fields: Status.stacks; race
  data: ability usage, status source_ref / one_shot, race text; new condition charges_left:<kind>:<id>; new formula
  variable stacks; a trigger add_status on an active status whose effects read "stacks" adds a stack (any other is still
  refused as already active). The
  feat catalog has 2 placeholder entries. Heavy swing no longer sets temp HP by set_temp_hp (it is a 1-tick status).

## Assumptions
- P1: Q275 const effects; Q276 no effect editor yet; Q277 catalog trainings; Q278 links; Q279 the rage scope; Q280
  Mordon drawbacks without rules; Q281 Adrenaline BP.

- P2: Q282 charged racial statuses; Q283 Mordon type 5 counter; Q284 Mordon type 6 charge; Q285 Hunt; Q286 one tick;
  Q287 Northerner placeholders; Q288 decision 6 (mana training, swim and flight stay race purchases).

## Open questions (ids)
- New: Q275-Q288; proposals: Q280 (write the bleeding / comfort-per-fight rules), Q283 (the Mordon reroll counter),
  Q287 (the text of Endurance and Toughness).
