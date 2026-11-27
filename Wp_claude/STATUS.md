# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 5 (UI) Classic steps 1-8 DONE; races DONE (packages 36, 37); Lite not started.
Last finished package: 38 (token rules; Toughness / Endurance, Wall of Bones, comfort per fight; rerolls;
"!" notes; the effect editor D37). Last report: `Wp_claude/tests/PACKAGE38_REPORT.md`.

## Tests (last run in package 38)
- `python Wp_claude/tests/run_all.py`: suites 107, passed 107, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 578, caught 578, missed 0.
- UI suites tests/ui/*.py run headless inside run_all (skipped without PySide6); screenshots tests/ui_shots/.
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md; closed ones word for word: ARCH/questions_archive.md)
- Waiting for the owner: the overlay spike test; nothing blocking. Russian texts to fill: Wp_claude/TRANSLATION_TODO.md.
- Assumptions to confirm: every "assumption" entry (Q23 ... Q300); proposal for the owner: Q294 (Banner of Blood
  "1 comfort less for fights").

## Next (ROADMAP.md)
1. The owner: look at the shots rerolls_*, notes_*, effect_editor_*; Q289-Q300.
2. Then Lite (Phase 5) or the classes / weapon groups data of the two game modules (owner).

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
- Catalogs: wp/catalog/data/<kind>.json, races / trainings one file per module (D21, D36); rule data: sheet_targets.json,
  defense_layers.json, catalog_schemas.json.
