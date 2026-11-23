# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 3 (rules core and model done; data / settings next, no UI yet).
Last finished package: 21 (i18n key files RU / EN with fallback, themes as token data with a QSS builder, the panel
registry; Item.ilvl; the old iterative helper removed). Last report: `Wp_claude/tests/PACKAGE21_REPORT.md`.

## Tests (last run in package 21)
- `python Wp_claude/tests/run_all.py`: suites 50, passed 50, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 130, caught 130, missed 0.
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md)
- Waiting for the owner: Q104 (professionalism checks). Russian texts to fill: Wp_claude/TRANSLATION_TODO.md.
- Assumptions to confirm: Q23, Q96, Q98-Q102, Q105, Q106, Q109, Q112, Q114, Q116-Q121, Q123, Q124, Q126-Q129, Q131,
  Q132, Q134-Q144, Q146-Q149.

## Next (ROADMAP.md)
1. The independent review of RULES_PACK.md; the owner fills ru.json (TRANSLATION_TODO.md); a status catalog.
   (Phase 3 done: settings 19, rule constants 20, i18n / themes / panels 21.)
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
- Texts, themes, panels: ARCH/i18n.md, themes.md, panels.md (D24); wp/i18n, wp/theme, wp/panels.
- Catalogs: wp/catalog/data/<kind>.json (RULES/catalog.md "Catalog files", D21); rule data: sheet_targets.json,
  defense_layers.json, catalog_schemas.json.
