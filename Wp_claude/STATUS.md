# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 3 DONE (rules core, model, data, settings, session layer); no UI yet.
Last finished package: 28 (log_max removed, drives with types / quests / reminders / buying with comfort, overlay
spike tools/overlay_spike.py). Last report: `Wp_claude/tests/PACKAGE28_REPORT.md`.

## Tests (last run in package 28)
- `python Wp_claude/tests/run_all.py`: suites 66, passed 66, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 301, caught 299, missed 2 (p23-cache-scope, p23-cache-clear "not applied": test_perf.py failed once on the clean copy, a timing budget under load; run again alone: test_perf 8/8, both entries caught). The 2 drive entries of pkg25 were moved to drive_cmds.py first (caught).
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md)
- Waiting for the owner: the overlay spike test (Wp_claude/OVERLAY_SPIKE.md), nothing blocking. Russian texts to fill: Wp_claude/TRANSLATION_TODO.md.
- Assumptions to confirm: Q23, Q96, Q98-Q102, Q105, Q106, Q112, Q114, Q116-Q121, Q123, Q124, Q126-Q129, Q131,
  Q132, Q134-Q144, Q146, Q148-Q150, Q152, Q153, Q160-Q187, Q189-Q196.

## Next (ROADMAP.md)
1. The owner fills ru.json (TRANSLATION_TODO.md; refusals show English until then, F12).
2. Overlay (Phase 4): the owner tries tools/overlay_spike.py over a browser / VTT and reports (OVERLAY_SPIKE.md).
3. The UI (Phase 5, two modes Classic / Lite, D20) through the Session only (D25, ARCH/app_layer.md,
   ARCH/view_contract.md); Phase 6 release. PDF export with Qt in the UI phase (QPdfWriter).

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
