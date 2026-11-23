# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 3 (rules core and model done; data / settings next, no UI yet).
Last finished package: 20 (all game-rule numbers into data: 134 constants with per-character overrides; the rules
pack for a reviewer: Wp_claude/REVIEW_PACK/RULES_PACK.md). Last report: `Wp_claude/tests/PACKAGE20_REPORT.md`.

## Tests (last run in package 20)
- `python Wp_claude/tests/run_all.py`: suites 49, passed 49, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 130, caught 130, missed 0.
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md)
- Waiting for the owner: Q104 (professionalism checks), Q133 (an ilvl field on sheet items), Q145 (drop the old
  core iterative helper).
- Assumptions to confirm: Q23, Q96, Q98-Q102, Q105, Q106, Q109, Q112, Q114, Q116-Q121, Q123, Q124, Q126-Q129, Q131,
  Q132, Q134-Q144, Q146.

## Next (ROADMAP.md)
1. Phase 3 remainder: wp/i18n texts (RU / EN) for refusal reasons and setting labels, theme, panel registry,
   a status catalog. (Rule constants: done in package 20.) The independent review of RULES_PACK.md.
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
- Settings: ARCH/settings.md (D22), wp/settings/. Rule constants: ARCH/constants.md (D23), wp/rules_data/.
- Catalogs: wp/catalog/data/<kind>.json (RULES/catalog.md "Catalog files", D21); rule data: sheet_targets.json,
  defense_layers.json, catalog_schemas.json.
