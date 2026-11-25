# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 3 DONE (rules core, model, data, settings, session layer); no UI yet.
Last finished packages: 30 (core data of the Classic screen v2) and 31 (hints, layout safety, tube settings, three
themes with all tokens, contrast warnings). Last report: `Wp_claude/tests/PACKAGE31_REPORT.md`.

## Tests (last run in package 31)
- `python Wp_claude/tests/run_all.py`: suites 68, passed 68, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 328, caught 328, missed 0.
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md)
- Waiting for the owner: the overlay spike test; nothing blocking. Russian texts to fill: Wp_claude/TRANSLATION_TODO.md.
- Assumptions to confirm: Q23, Q96, Q98-Q102, Q105, Q106, Q112, Q114, Q116-Q121, Q123, Q124, Q126-Q129, Q131,
  Q132, Q134-Q144, Q146, Q148-Q150, Q152, Q153, Q160-Q187, Q189-Q196, Q199-Q213.

## Next (ROADMAP.md)
1. Phase 5 step 1: the window shell + the three themes in PySide6 (core step 0 done: ARCH/ui_gaps.md all rows built).
2. The owner: ru.json texts (TRANSLATION_TODO.md), the overlay spike test (OVERLAY_SPIKE.md).

## Known gaps (rule exists, no code)
- Stored-only weapon picks are flags without mechanics (package 25 E). Multiclass, reverting an arbitrary journal
  line, PDF export (Qt, UI phase) are not built.
- Not built on purpose: money, start / end of session (narrative, owner package 17). XP is a log (package 26).

## Where things are
- Plan: ROADMAP.md. Finished packages: ARCH/history.md. Closed questions: ARCH/decision_log.md.
- Prompt template for new packages: Wp_claude/PROMPT_TEMPLATE.md.
- Settings: ARCH/settings.md (D22), wp/settings/. Rule constants: ARCH/constants.md (D23), wp/rules_data/.
- Texts, themes, panels: ARCH/i18n.md, themes.md, panels.md (D24); wp/i18n, wp/theme, wp/panels.
- Session layer for the UI: ARCH/app_layer.md (D25, D29: input checks, undo, journal archive), ARCH/view_contract.md
  (tools/make_view_contract.py); wp/app. Parameter kinds: wp/commands/data/params.json; app limits: wp/app/data/limits.json.
- Hands, doll layout, AC cell variants: ARCH/doll_hands.md, ARCH/ac_variants.md (D26). Classes, undo: ARCH/classes.md (D27).
- Catalogs: wp/catalog/data/<kind>.json (RULES/catalog.md "Catalog files", D21); rule data: sheet_targets.json,
  defense_layers.json, catalog_schemas.json.
