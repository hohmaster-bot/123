# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 3 (rules core and model done; data / settings next, no UI yet).
Last finished package: 18 (catalogs: one JSON file per kind, shipped + user layers, catalog commands, entry codes,
medicine = Int). Last report: `Wp_claude/tests/PACKAGE18_REPORT.md`.

## Tests (last run in package 18)
- `python Wp_claude/tests/run_all.py`: suites 45, passed 45, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 99, caught 99, missed 0.
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md)
- Waiting for the owner: Q104 (professionalism checks), Q133 (an ilvl field on sheet items).
- Assumptions to confirm: Q23, Q96, Q98-Q102, Q105, Q106, Q109, Q112, Q114, Q116-Q121, Q123, Q124, Q126-Q129, Q131,
  Q132, Q134-Q136.

## Next (ROADMAP.md)
1. Phase 3 data / settings: rule constants from code to data, settings domains, wp/i18n texts for refusal reasons,
   theme, panel registry, a status catalog.
2. The AC-zones package (RULES/ac_zones.md) once the owner gives the full table.
3. Phase 4 Lite (overlay) spike, Phase 5 UI (two modes: Classic and Lite, D20; RU / EN, D4), Phase 6 release;
   the class system later.

## Known gaps (rule exists, no code)
- Weapon picks without a number that are not once-per-combat are stored only (one attack without the tag, ignore
  the first vulnerability, ignore 20% cover). What an item qualification unlocks (Q109).
- Not built on purpose: XP, money, start / end of session (narrative, owner package 17).

## Where things are
- Plan: ROADMAP.md. Finished packages: ARCH/history.md. Closed questions: ARCH/decision_log.md.
- Prompt template for new packages: Wp_claude/PROMPT_TEMPLATE.md.
- Catalogs: wp/catalog/data/<kind>.json (RULES/catalog.md "Catalog files", D21); rule data: sheet_targets.json,
  defense_layers.json, catalog_schemas.json.
