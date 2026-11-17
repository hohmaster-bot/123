# Roadmap
Current: Phase 0.

## Phase 0 - setup
- [x] Branch `Rework`.
- [ ] Add `Wp_claude/` skeleton and `CLAUDE.md` to `Rework` (owner uploads zip or clones repo for Code).
- [ ] Owner reviews decisions marked P.
- [ ] Baseline: run legacy `_check.py` locally, then prove it can fail (break one formula on purpose).

## Phase 1 - rules (owner + Claude, one domain at a time)
Order: effects/bonuses -> AC/saves/attacks -> resources/tick/rest -> feats/stances -> injuries -> magic -> inventory -> training/skills/proficiencies -> catalogs.
Output per domain: `RULES/<domain>.md` + resolved OPEN_QUESTIONS + golden examples for tests.

## Phase 2 - core
Test runner that can fail. Golden tests from RULES. Fix core bugs. Split core into modules (D9).

## Phase 3 - nodes without visuals
Commands (D5), stable ids (D7), persistence (D11), settings split (D13), catalogs contract, i18n (D4), theme, panel registry.

## Phase 4 - overlay spike
PySide6: click-through, always-on-top, global hotkey, tray, multi-monitor.

## Phase 5 - UI
Sheet, then overlay panels, then editors. Delete tkinter.

## Phase 6 - release v1.0
Archive old docs, final cleanup.
