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
- Package 11 (planned): REPLACES the item-bound maneuver records (kind "maneuver") with the character-level maneuver
  list (combat.md "Maneuver list"); maneuver record stubs (name, base_record, to-hit mod, damage mod, action cost, balance cost,
  spirit cost, tags, free note, generic custom resource counters like "Spark", forward-compatible unknown fields);
  consumables (quantity decreases on use, at 0 grey and zero weight, manual delete); list of active attacks /
  abilities of equipped items with buffs and charges.
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
