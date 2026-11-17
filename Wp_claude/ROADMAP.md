# Roadmap
Current: Phase 1 (rules written; a few open questions left) -> Phase 2.

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
- [ ] Open questions left: R8, Q3, Q5, Q6 (rules); Q7, Q8, Q9, Q11 (architecture). See OPEN_QUESTIONS.md.

## Phase 2 - core
Test runner that can fail (done: baseline script). Golden tests from RULES. Fix core bugs. Split core into modules (D9).

## Phase 3 - nodes without visuals
Commands (D5), stable ids (D7), persistence (D11), settings split (D13), effects (D14-D17), catalogs contract, i18n (D4), theme, panel registry.

## Phase 4 - overlay spike
PySide6: click-through, always-on-top, global hotkey, tray, multi-monitor.

## Phase 5 - UI
Sheet, then overlay panels, then editors (see `UI_WISHES.md`). Delete tkinter.

## Phase 6 - release v1.0
Archive old docs, final cleanup.
