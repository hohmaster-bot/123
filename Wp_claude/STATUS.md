# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 3 DONE (rules core, model, data, settings, session layer); no UI yet.
Last finished package: 23 (session layer wp/app, read cache and perf budgets, ARCH/view_contract.md, AC zones as
data). Last report: `Wp_claude/tests/PACKAGE23_REPORT.md`.

## Tests (last run in package 23)
- `python Wp_claude/tests/run_all.py`: suites 55, passed 55, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 167, caught 167, missed 0.
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md)
- Waiting for the owner: Q104 (professionalism checks), Q151 (damage pipeline order: code vs the owner's list). Russian texts to fill: Wp_claude/TRANSLATION_TODO.md.
- Assumptions to confirm: Q23, Q96, Q98-Q102, Q105, Q106, Q109, Q112, Q114, Q116-Q121, Q123, Q124, Q126-Q129, Q131,
  Q132, Q134-Q144, Q146, Q148-Q150, Q152-Q159.

## Next (ROADMAP.md)
1. Independent review 5 of RULES_PACK.md; the owner fills ru.json (TRANSLATION_TODO.md).
2. Overlay prototype (Phase 4) - needs the owner's screen drawings A1, A2.
3. The UI (Phase 5, two modes Classic / Lite, D20) through the Session only (D25, ARCH/app_layer.md,
   ARCH/view_contract.md); Phase 6 release; the class system later. PDF export is not built.

## Known gaps (rule exists, no code)
- Weapon picks without a number that are not once-per-combat are stored only (one attack without the tag, ignore
  the first vulnerability, ignore 20% cover). What an item qualification unlocks (Q109).
- Not built on purpose: XP, money, start / end of session (narrative, owner package 17).

## Where things are
- Plan: ROADMAP.md. Finished packages: ARCH/history.md. Closed questions: ARCH/decision_log.md.
- Prompt template for new packages: Wp_claude/PROMPT_TEMPLATE.md.
- Settings: ARCH/settings.md (D22), wp/settings/. Rule constants: ARCH/constants.md (D23), wp/rules_data/.
- Texts, themes, panels: ARCH/i18n.md, themes.md, panels.md (D24); wp/i18n, wp/theme, wp/panels.
- Session layer for the UI: ARCH/app_layer.md (D25), ARCH/view_contract.md (tools/make_view_contract.py); wp/app.
- Catalogs: wp/catalog/data/<kind>.json (RULES/catalog.md "Catalog files", D21); rule data: sheet_targets.json,
  defense_layers.json, catalog_schemas.json.
