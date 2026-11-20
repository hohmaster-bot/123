# Roadmap
Current: Phase 2-3 (core and model). Last finished package and what is next: STATUS.md.
Finished-package history: ARCH/history.md.

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
- UI note (maneuvers): show only name, cost and numbers by default; everything else (description, tags, effects,
  source, notes) in a collapsed details area, so the interface is not cluttered. Stances get their own visual element.
- Owner goal: FULL control over bonuses and rules through settings. For now every NEW rule constant or switch goes into
  Character.rules_settings (data) instead of code.
- What is left after package 17 (owner, package 17):
  1. Phase 3 data / settings: rule constants still in code -> data files, settings domains (D13), wp/i18n texts for
     the refusal reason ids, theme, panel registry; a status catalog (buffs.md).
  2. The AC-zones package (RULES/ac_zones.md) once the owner gives the full table.
  3. Phase 4 overlay spike, Phase 5 UI, Phase 6 release.
  4. Class system later (below).
- Not built on purpose (owner, package 17): XP, money, start / end of session (narrative only).
- Rule exists, no code yet: weapon picks without a numeric effect that are not once-per-combat (one attack per turn
  without the [attack] tag, ignore the first vulnerability, ignore 20% cover) are stored only; what an item
  qualification unlocks (Q109); principles, PDF export, journal revert (not in RULES yet).

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
