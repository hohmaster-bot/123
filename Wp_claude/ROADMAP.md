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
- Deferred (from REVIEW_REPORT, not done yet): final item hardness/HP from mastery in the model; spell mastery cost
  25 * (1 + circle^2); level-up command (+100 * level training, HP roll); comfort -> training command;
  OT removal commands (comfort, attention, injury removal, RL raise); weapon card data from the owner's table.
- Rule exists, no code yet (package 4, training text; see training.md / progression.md / weapons.md):
  - comfort -> training command (rate (level+1)*5 exists in core);
  - level-up command (+100 * level training);
  - combat basics purchase command (cost 50/100/150 exists in core);
  - new combat maneuver 250 (record of maneuvers per weapon branch);
  - item qualification purchase 50 * N;
  - +1 reaction 200 * new number of reactions;
  - max HP +1 for 50 up to class hit die * level + Con * level;
  - professionalism 300 (1/2/3/4 specialized class skills), after Q29;
  - new spell 20 + 10 * circle^2 (half for book / teacher / scroll classes);
  - spell mastery 25 * (1 + circle^2), three slots, identical upgrade 2nd time = 2 slots, metamagic = its circle;
  - seed 200 / sprout seed 200;
  - make a known language native (50 / 100);
  - attention course +1 for 200 (adds to the stat bonus);
  - heavy/tower shields add the shield bonus to balance, tower +2 parry (after Q28);
  - master weapon picks have no mechanics yet: reroll one d20, one attack per turn without the [attack] tag,
    once per combat restore all balance (free action); expert picks "ignore first vulnerability",
    "ignore 20% cover", "first ranged attack can be parried" are stored but have no effect in numbers.

## Phase 4 - overlay spike
PySide6: click-through, always-on-top, global hotkey, tray, multi-monitor.

## Phase 5 - UI
Sheet, then overlay panels, then editors (see `UI_WISHES.md`), incl. pain editor and morale scale editor. Delete tkinter.

## Phase 6 - release v1.0
Archive old docs, final cleanup.
