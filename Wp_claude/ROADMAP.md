# Roadmap
Current: Phase 3 done (rules core, model, data, settings, session layer); next Phase 4-5 (overlay, UI). Last finished package and what is next: STATUS.md.
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
PHASE 3 DONE (package 23): session layer (D25, ARCH/app_layer.md), view contract (ARCH/view_contract.md), read
cache and perf budgets, AC zones as data. What is left (owner, package 23):
  1. Independent review 5 (RULES_PACK.md): DONE; its fixes are package 27.
  2. Overlay prototype (Phase 4) - needs the owner's screen drawings A1, A2.
  3. The UI (Phase 5).
  PDF export is NOT built (not in RULES; no package asked for it).
- Package 27 done: fixes of review 5 (input checks by declared types, file and constant limits, topics test, undo
  keeps settings and journal, journal modes with a history archive, D29).
- Package 24 done: hands with sides, AC cell variants and defence settings as data, doll layout data (D26).
- Package 25 done: undo / redo, class system v0 (data, one class), drives with level notes and principles,
  hidden item properties (Q109), the stored-only picks as flags, spell damage as data (D27).
- Package 26 done: actions as a resource, flask bars, experience log and level history, the Classic screen v1
  description (UI_WISHES.md; the owner's sketches go to UI/sketches/).
- What is left: independent review 5; overlay prototype (needs the owner's drawings); the UI; PDF export with Qt in
  the UI phase (QPdfWriter). Not built: multiclass, reverting an arbitrary journal line (undo / redo is the session
  stack), mechanics of the stored-only picks (they are flags), dice rolling (never, by design).
Commands (D5), stable ids (D7), persistence (D11), settings split (D13), effects (D14-D17), catalogs contract, i18n (D4: RU / EN switch, wp/i18n/ru.json and en.json, refusal reason ids as keys; Russian only
until then), theme, panel registry.
- Before Phase 4: the owner sends screen drawings with labels (A1, A2...), Claude turns them into screen descriptions.
- UI note (maneuvers): show only name, cost and numbers by default; everything else (description, tags, effects,
  source, notes) in a collapsed details area, so the interface is not cluttered. Stances get their own visual element.
- Owner goal: FULL control over bonuses and rules through settings. For now every NEW rule constant or switch goes into
  Character.rules_settings (data) instead of code.
- What is left after package 17 (owner, package 17):
  1. Phase 3 remainder: Russian texts in wp/i18n/ru.json (owner, TRANSLATION_TODO.md); a status catalog (buffs.md).
     Done: settings (19), rule constants (20), i18n files, themes, panel registry (21).
  2. AC zones: built as data in package 23 from the draft (Q154-Q157); the full table can replace the data.
  3. Phase 4 Lite (overlay) spike, Phase 5 UI (two modes: Classic and Lite, D20), Phase 6 release.
  4. Class system later (below).
- Q122 CLOSED (owner, package 17; XP changed in package 26: a log with notes, no threshold): money is narrative; there is no "start session" or "end session" button,
  only the end of cycle. Not built on purpose.
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
- Overlay (inside Lite, D20): plain Qt window flags and a global hotkey, tested in the Phase 4 spike. It is not shown over exclusive
  fullscreen, only over windowed / borderless games.

## Phase 4 - Lite (overlay) spike
PySide6: click-through, always-on-top, global hotkey, tray, multi-monitor. The overlay is part of Lite (D20).

## Phase 5 - UI
Exactly two modes: Classic and Lite (D20; no split mode). Sheet (Classic), then Lite panels (the overlay), then editors
(see `UI_WISHES.md`), incl. pain editor and morale scale editor. RU / EN switch (D4). Delete tkinter.
Binding spec: `UI_WISHES.md` "Classic screen v2" (package 29, D31); the core gaps per block: `ARCH/ui_gaps.md`.
Steps in order (each a package; the core additions of ui_gaps.md go into the step that needs them):
  1. Window shell + the three shipped themes (dark default, light, grey-blue), the Session wiring, one-time hints
     storage (hints_seen, hints_off).
  1b. Theme editor and background: every screen colour a token (the missing tokens of ARCH/ui_gaps.md "Themes"), live
     preview, copy / reset to shipped, follow the system, the 4.5:1 contrast warning, an own background picture with
     dimming and the readable overlay.
  2. Resources: horizontal tubes (glass / flat), the value editor, adjust_value, temp HP strip, pools (3 large),
     custom buttons through Session.run_quick, resource style / colour / size settings.
  3. Experience strip (training.experience).
  4. Parameters block and AC block: cell sources view, attack_melee / attack_ranged (Q198), load limits in
     items.weight, shield_side and cell lines in defense, ac_cell labels.
  5. Statuses, favourites (char setting favorites), reminders view; the combat tab (actions / reaction squares,
     quick access grid with quick_view, quick_cells / quick_columns).
  6. Bottom strip (+ a second strip: profile field strips).
  7. Tabs: Journal, Skills, Feats, Race, Class (class / race views), Injuries, Drives, Inventory / Doll, Training,
     Rest, Catalogs, Settings; expand to full screen without touching the profile.
  8. Layout editor: grid snap, resize, profiles, the three validation warnings, profile_reset.

## Phase 6 - release v1.0
Archive old docs, final cleanup.
