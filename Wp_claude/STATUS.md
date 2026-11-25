# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 5 (UI) steps 3 and 5 DONE (`python run_wp.py`, D34).
Last finished package: 34 (sources of every number + editor mode; Parameters, AC, statuses, favourites, reminders,
tab bar, combat tab). Last report: `Wp_claude/tests/PACKAGE34_REPORT.md`.

## Tests (last run in package 34)
- `python Wp_claude/tests/run_all.py`: suites 78, passed 78, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 396, caught 396, missed 0.
- UI suites tests/ui/*.py run headless inside run_all (skipped without PySide6); screenshots tests/ui_shots/.
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md)
- Waiting for the owner: the overlay spike test; nothing blocking. Russian texts to fill: Wp_claude/TRANSLATION_TODO.md.
- Assumptions to confirm: Q23, Q96, Q98-Q102, Q105, Q106, Q112, Q114, Q116-Q121, Q123, Q124, Q126-Q129, Q131,
  Q132, Q134-Q144, Q146, Q148-Q150, Q152, Q153, Q160-Q187, Q189-Q196, Q199-Q215, Q217-Q223, Q225-Q228,
  Q230-Q238; proposal Q229 (an effect target for temp HP).

## Next (ROADMAP.md)
1. Phase 5 step 6: the bottom strip (then step 7, the other tabs).
2. The owner: look at the window (python run_wp.py; View > Editor mode and a click on any number; the combat tab),
   tests/ui_shots/*.png, the overlay spike (OVERLAY_SPIKE.md), ru.json texts (TRANSLATION_TODO.md).

## Known gaps (rule exists, no code)
- Stored-only weapon picks are flags without mechanics (package 25 E). Multiclass, reverting an arbitrary journal
  line, PDF export (Qt, UI phase) are not built.
- Not built on purpose: money, start / end of session (narrative, owner package 17). XP is a log (package 26).

## Where things are
- Plan: ROADMAP.md. Finished packages: ARCH/history.md. Closed questions: ARCH/decision_log.md.
- Window shell, resources block: ARCH/surfaces.md "Classic window shell" (D32, D33); wp/ui, run_wp.py; tests/ui.
- Prompt template for new packages: Wp_claude/PROMPT_TEMPLATE.md.
- Settings: ARCH/settings.md (D22), wp/settings/. Rule constants: ARCH/constants.md (D23), wp/rules_data/.
- Texts, themes, panels: ARCH/i18n.md, themes.md, panels.md (D24); wp/i18n, wp/theme, wp/panels.
- Session layer for the UI: ARCH/app_layer.md (D25, D29: input checks, undo, journal archive), ARCH/view_contract.md
  (tools/make_view_contract.py); wp/app. Parameter kinds: wp/commands/data/params.json; app limits: wp/app/data/limits.json.
- Hands, doll layout, AC cell variants: ARCH/doll_hands.md, ARCH/ac_variants.md (D26). Classes, undo: ARCH/classes.md (D27).
- Catalogs: wp/catalog/data/<kind>.json (RULES/catalog.md "Catalog files", D21); rule data: sheet_targets.json,
  defense_layers.json, catalog_schemas.json.
