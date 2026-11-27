# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 5 (UI) Classic steps 1-8 DONE; races DONE (packages 36, 37); Lite not started.
Last finished package: 37 (universal mechanisms D36: const:<id> targets, catalog trainings, links both
ways; the 12 races done properly). Last report: `Wp_claude/tests/PACKAGE37_REPORT.md`.

## Tests (last run in package 37)
- `python Wp_claude/tests/run_all.py`: suites 100, passed 100, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 527, caught 527, missed 0.
- UI suites tests/ui/*.py run headless inside run_all (skipped without PySide6); screenshots tests/ui_shots/.
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md)
- Waiting for the owner: the overlay spike test; nothing blocking. Russian texts to fill: Wp_claude/TRANSLATION_TODO.md.
- Assumptions to confirm: Q23, Q96, Q98-Q102, Q105, Q106, Q112, Q114, Q116-Q121, Q123, Q124, Q126-Q129, Q131,
  Q132, Q134-Q144, Q146, Q148-Q150, Q152, Q153, Q160-Q187, Q189-Q196, Q199-Q215, Q217-Q223, Q225-Q228,
  Q230-Q244, Q246-Q270, Q273, Q275-Q279, Q281, Q282, Q284-Q286, Q288; proposals for the owner: Q280
  (Mordon bleeding / comfort per fight), Q283 (Mordon reroll counter), Q287 (Endurance / Toughness text).

## Next (ROADMAP.md)
1. The owner: the Training tab (Ragmal mana), the links in the Feats tab, the race coverage table in
   PACKAGE37_REPORT.md; Q280, Q283, Q287.
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
