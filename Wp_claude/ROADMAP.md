# Roadmap
Current: Phase 2 (core).

## Phase 0 - setup
- [x] Branch `Rework`.
- [x] `Wp_claude/` skeleton and `CLAUDE.md` in `Rework`.
- [x] Owner rules in `Wp_claude/RULES/` (+ `UI_WISHES.md`).
- [x] Baseline tests from RULES examples: `Wp_claude/tests/test_rules_baseline.py`, results in `tests/BASELINE_REPORT.md`.
- [x] `.gitignore` (`characters/`, `__pycache__/`).
- [x] Legacy `_check.py` checked: fails on a broken formula; only the schema check is dead (see GOTCHAS).
- [x] Owner approved decisions D2-D19 (all A).

## Phase 1 - rules (owner + Claude, one domain at a time)
- [x] Rules written in `RULES/` for all domains (see `RULES/index.md`), numeric examples are tests.
- [x] Rules written, incl. stats, training, crafting, doll.
- [x] Rules written, no open questions.

## Phase 2 - core
Test runner that can fail (done: baseline script). Golden tests from RULES. Fix core bugs. Split core into modules (D9).

## Phase 3 - nodes without visuals
Commands (D5), stable ids (D7), persistence (D11), settings split (D13), effects (D14-D17), catalogs contract, i18n (D4), theme, panel registry.
- Before Phase 4: the owner sends screen drawings with labels (A1, A2...), Claude turns them into screen descriptions.
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
- UI note (maneuvers): show only name, cost and numbers by default; everything else (description, tags, effects,
  source, notes) in a collapsed details area, so the interface is not cluttered. Stances get their own visual element.
- Done in package 13: block effects (block_balance_regen, block_bonus, block_stat_bonus, cannot_be_flanked; Q82),
  resource pools and per-round status payment, consumables (quantity, use_consumable), active_list view, injury id
  counter (Q75) and remove_injury, weight/load views split out of derived_view, LEGACY_FEATURES.md, ac_zones.md
  draft. Report: tests/PACKAGE13_REPORT.md.
- Done in package 14: per-round payment at activation (Q83/Q91), count -> quantity (Q86), long rest restores short
  pools (Q88), charges and cooldown for items / statuses / feats / attack records / maneuvers (item charges on the
  item, Q94), a safe formula evaluator (effect values, pool max), injury effects (Q89), action / restore blocks and
  restore by effect, rule switches as data (rules_settings), the long journal; body_view split out of derived_view.
  Report: tests/PACKAGE14_REPORT.md.
- Owner goal: FULL control over bonuses and rules through settings. For now every NEW rule constant or switch goes into
  Character.rules_settings (data) instead of code.
- Package 15 (planned): the missing commands: level up (+100 * level training, HP roll), comfort -> training exchange,
  OT removal (comfort, attention, injury, RL raise), skill advancement and specialization commands, professionalism,
  spell learning and spell mastery, combat basics, item qualification, reactions, seeds, native language, attention
  course, and the rest of the "rule exists, no code yet" list below.
- Package 16 (planned): the remaining "core" items of tests/LEGACY_FEATURES.md (ranged / thrown attack flags, own
  damage stat and damage multiplier, master counters, XP and level threshold, start session, money, base contents,
  quirks / courts / quests / lens / principles, character templates, PDF export, journal revert).
- Then an AC-zones package (RULES/ac_zones.md) once the owner gives the full table.
- Deferred (from REVIEW_REPORT, not done yet): spell mastery cost
  25 * (1 + circle^2); level-up command (+100 * level training, HP roll); comfort -> training command;
  OT removal commands (comfort, attention, injury removal, RL raise); weapon card data from the owner's table.
- Rule exists, no code yet (package 4, training text; see training.md / progression.md / weapons.md):
  - comfort -> training command (rate (level+1)*5 exists in core);
  - level-up command (+100 * level training);
  - combat basics purchase command (cost 50/100/150 exists in core);
  - new combat maneuver 250 (record of maneuvers per weapon branch);
  - item qualification purchase 50 * N;
  - +1 reaction 200 * new number of reactions;
  - professionalism 300 (1/2/3/4 specialized class skills), only for classes without their own (Q29 closed);
    the "professionalism level" number is a placeholder: do not develop it;
  - new spell 20 + 10 * circle^2 (half for book / teacher / scroll classes);
  - spell mastery 25 * (1 + circle^2), three slots, identical upgrade 2nd time = 2 slots, metamagic = its circle;
  - seed 200 / sprout seed 200;
  - make a known language native (50 / 100);
  - attention course +1 for 200 (adds to the stat bonus);
  - master weapon picks have no mechanics yet: reroll one d20, one attack per turn without the [attack] tag,
    once per combat restore all balance (free action); expert picks "ignore first vulnerability",
    "ignore 20% cover", "first ranged attack can be parried" are stored but have no effect in numbers.

## Class system (future, Q61; not built)
- No multiclass. A class has flags for BAB growth and stat growth, and a good or poor progression per save
  (good grows to 12, poor to 6 by level 20).
- PF-like defaults (ASSUMPTION, to confirm when built): good save = 2 + level / 2, poor save = level / 3 (rounded down).
- Until then base saves and BAB are typed by hand.

## Ideas and UI-layer plans (package 10, not built)
- "What is worn" tab with item pictures (idea only).
- Icon registry for the UI: every button / slot / spell has an icon id; a file path is resolved by id; the user can
  override it; a placeholder when missing. Ready icon packs (e.g. game-icons.net: check the license, CC BY needs
  attribution) and AI-drawn icons both go through the registry.
- Library policy: libraries only in the UI layer, always behind a thin adapter, versions pinned; before writing
  something from scratch run a spike to check whether a ready library fits; license check; a THIRD_PARTY_LICENSES
  file at release. Candidates: PySide6-QtAds (docking panels, LGPL 2.1); a theme library only as a pattern for our
  own QSS theme system; qtawesome (icon placeholders, check icon-set licenses); pytest-qt (UI tests).
- Overlay: plain Qt window flags and a global hotkey, tested in the Phase 4 spike. It is not shown over exclusive
  fullscreen, only over windowed / borderless games.

## Phase 4 - overlay spike
PySide6: click-through, always-on-top, global hotkey, tray, multi-monitor.

## Phase 5 - UI
Sheet, then overlay panels, then editors (see `UI_WISHES.md`), incl. pain editor and morale scale editor. Delete tkinter.

## Phase 6 - release v1.0
Archive old docs, final cleanup.
