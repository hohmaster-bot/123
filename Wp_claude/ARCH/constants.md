# Rule constants (D23, package 20)

Every game-rule number is DATA: `wp/rules_data/constants.json` (id, value, type, group, unit, description, label).
Defaults are the values the code had before package 20. A character overrides any constant in
`Character.rules_settings.constants` with `set_rule_setting(key=<id>, value=...)` (checked by the settings schema, journaled);
`reset_rule_setting` / `reset_settings_group` bring the default back. Each constant is a rules-domain key of the
settings schema (ARCH/settings.md), group "rules.<group>".

## Reading a constant in code
- Module level: `NAME = rd.ref("group.name")` (`from wp.rules_data import rules as rd`). A ref behaves like its value
  in arithmetic, comparisons, indexing and int(); it reads the value of the CURRENT scope at each use.
- With the character at hand: `rd.const("group.name", ch)`.
- Record field defaults must be plain: `field: int = rd.default("group.name")` (a test forbids refs in records).
- Scope: `dispatch()` runs every command inside `rd.using(ch)`. Code that reads views of a character OUTSIDE a command
  (the UI) wraps the reads in `with rd.using(ch):`; otherwise the table defaults are used.

## Adding a constant
1. Add a row to `constants.json` (id `group.name`, value, type int / float / list / map, group, unit, description,
   label `rules.<id>`).
2. Read it through `rd.ref` / `rd.const` / `rd.default` as above. Never write the number in code.
3. Add a test that changes it with `set_rule_setting` and checks the result (numbers by hand), and a break_check
   entry that puts the literal back.
`Wp_claude/tests/test_rule_literals.py` fails on a new rule number in code (numbers that are not rules live in the
`allowlist` of the table, with a reason), on a ref used as a record default, and on a constant no code reads.

## Not a per-character value
`pain.death_cap`, `new.hit_die`, `new.reactions`, `training.start`, `training.base_start`, `speed.base_ft`,
`narrative.lens_start`, `training.feat_default_cost` are the defaults of NEW records (a new pain profile, a new
character, a new lens, a feat without a price); the character's own value lives in its record.
