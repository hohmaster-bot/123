# History of finished packages
Moved here from ROADMAP.md (package H, unchanged text). Append-only: add a line per finished package.

- Done in package 8: final item hardness/HP from mastery in the model (records.item_picks); max HP +1 for 50 (buy_hp);
  attack availability (records.attack_available, attack_view.all_records); masterwork flag; bag weight flag;
  BP overcap; shield proficiency ranks. Report: tests/PACKAGE8_REPORT.md.
- Done in package 9: balance cap snapshot, spend_balance, pay_hp_cost; non-proficient armor/shield attack penalty;
  masterwork rules; condition tag; main / maneuver record kinds; item number order; notches (hit_item, durable);
  touch AC bonus; armor spell penalties and failure; armor / shield data sets. Report: tests/PACKAGE9_REPORT.md.
- Done in package 10: saves, initiative, CMB/CMD (stats_view), size in attack, racial damage per pain, lucky-attack
  effects, crit range display, touch_armor effects, mana level = level, circle cost table. Report:
  tests/PACKAGE10_REPORT.md. Open details: OPEN_QUESTIONS Q55-Q68.
- Done in package 11: status container (active only, no toggle / pause; activate / remove / delete / hidden /
  favorite; container_view), stat-mod effect values, race size (small / medium / large) and base speed with derived
  speed, feats with effects (+ granted_maneuvers, remove_feat), character.schema.json reviewed
  (tests/SCHEMA_REVIEW.md) and deleted. Report: tests/PACKAGE11_REPORT.md.
- Done in package 12: a status has no cost (Q69); armor slowdown with reduction (Q72); stable injury ids (Q70);
  stances = feats with is_stance and active_stance (Q74); item-bound maneuver records removed; character-level
  maneuver list by tags (maneuver_view); CMB per attack record (Q58). Report: tests/PACKAGE12_REPORT.md.
- Done in package 13: block effects (block_balance_regen, block_bonus, block_stat_bonus, cannot_be_flanked; Q82),
  resource pools and per-round status payment, consumables (quantity, use_consumable), active_list view, injury id
  counter (Q75) and remove_injury, weight/load views split out of derived_view, LEGACY_FEATURES.md, ac_zones.md
  draft. Report: tests/PACKAGE13_REPORT.md.
- Done in package 14: per-round payment at activation (Q83/Q91), count -> quantity (Q86), long rest restores short
  pools (Q88), charges and cooldown for items / statuses / feats / attack records / maneuvers (item charges on the
  item, Q94), a safe formula evaluator (effect values, pool max), injury effects (Q89), action / restore blocks and
  restore by effect, rule switches as data (rules_settings), the long journal; body_view split out of derived_view.
  Report: tests/PACKAGE14_REPORT.md.
- Done in package 15: Q95 (a D-round status pays for D rounds), the missing commands: level_up, exchange_comfort,
  remove_ot_comfort, remove_ot_attention, raise_heal_rating, buy_attention_course, buy_reaction, buy_seed, sprout_seed,
  make_language_native, promote_skill, buy_professionalism, learn_spell, buy_spell_upgrade, buy_combat_basics,
  buy_maneuver, buy_item_qualification; minimal Spell / SpellUpgrade / Seed records. Report: tests/PACKAGE15_REPORT.md.
- Deferred (from REVIEW_REPORT, not done yet): spell mastery cost
  25 * (1 + circle^2); level-up command (+100 * level training, HP roll); comfort -> training command;
  OT removal commands (comfort, attention, injury removal, RL raise); weapon card data from the owner's table.
- Done in package H (housekeeping, no behavior change): tests/run_all.py, tests/break_check.py + tests/breaks/ (43 entries),
  CLAUDE.md procedure, STATUS.md, history.md, ARCH/decision_log.md, tools/rules_index.py, PROMPT_TEMPLATE.md.
  Report: tests/PACKAGEH_REPORT.md.
- Done in package 16: review 4 fixes (refusal reason ids, no-op journal, circle and two-weapon bugs, long rest in combat,
  pools over max, read-only dicts, unknown fields dropped on load), effect targets for sheet numbers, edit commands,
  iterative attacks, DR / resist / SR, doll slots, notebook, templates, hit dice per die, Q108, attention 2 and 4,
  spell price, base contents. Report: tests/PACKAGE16_REPORT.md.
- Done in package 17: the remaining effect targets (pain, item HP / hardness, morale, short rest, spell cost /
  overload, mana level), level_up default die 1 with a warning, DR stacks flag, percent modifiers per element and the
  damage order as data, attack kinds melee / ranged / thrown, master counters as charges. Report: tests/PACKAGE17_REPORT.md.
- Done in package 18: catalogs as single JSON files per kind (weapons, armor_shields, items, spells, statuses,
  skills, weapon_groups, feats, damage_types, doll_slots), shipped + user layers (override, tombstone, reset),
  catalog commands, schema table, atomic save, entry codes; old loaders moved onto it; medicine = Int; break_check
  checks suites pass without a break. Report: tests/PACKAGE18_REPORT.md.
- Done in package 19: settings structure: schema in data, three domains (rules, character, app), app settings
  file with two layers and atomic save, settings / profile / layout / quick-button / image commands, cells resolved
  against the character, colour rules, macros of existing commands, hotkey conflicts. Report: tests/PACKAGE19_REPORT.md.
- Done in package 20: all game-rule numbers into data (134 constants, wp/rules_data/constants.json; code reads them
  through rules.py; per-character overrides; scan test), the rules pack for an independent reviewer
  (REVIEW_PACK/RULES_PACK.md). Report: tests/PACKAGE20_REPORT.md.
- Done in package 21: i18n (ru / en key files, fallback, refusal texts, TRANSLATION_TODO.md), themes as token
  data with a QSS builder (no Qt), the panel registry and profile checks, Item.ilvl, the old iterative helper removed.
  Report: tests/PACKAGE21_REPORT.md.
- Done in package 22: restore_mana, reactions as a resource, balance clamped to the cap in combat, the most favourable
  tick order, paired attack = one use, RULES text fixes (pipeline, rest table, encumbrance vs spell overload), ru.json
  names. Report: tests/PACKAGE22_REPORT.md.
- Done in package 23: session layer wp/app (views by panel, topics, files with backups / trash / corrupt recovery,
  autosave), read cache (dispatch + all views 4631 -> about 29 ms on the heavy character), perf budgets, generated
  ARCH/view_contract.md, AC zones as data. Phase 3 done. Report: tests/PACKAGE23_REPORT.md.
- Done in package 24: hands with sides (equip side, move / swap, sides by order for old files, main / off hand),
  AC cell variants (melee / parry / ranged, Dex-loss cancel chance), defence rules as per-character constants and
  effects (cells), cell-scoped bonuses, doll layout data (basic / body) with slot commands. Report: tests/PACKAGE24_REPORT.md.
- Done in package 25: undo / redo in the Session (bounded stack of shared states), class system v0 (catalog
  kind classes, derived BAB / saves / hit die, professionalism checks, spellbook and divine defaults), drives with
  level notes and principles, hidden item properties by qualification, stored-only picks as flags, spell damage as
  data. Report: tests/PACKAGE25_REPORT.md.
