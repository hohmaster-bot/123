# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 2-3 (rules core and model, no UI yet).
Last finished package: 16 (review 4 fixes, effect targets for sheet numbers, edit commands, refusal reasons,
iterative attacks, DR / resistances, doll slots, notebook, templates). Last report: `Wp_claude/tests/PACKAGE16_REPORT.md`.

## Tests (last run in package 16)
- `python Wp_claude/tests/run_all.py`: suites 43, passed 43, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 67, caught 67, missed 0.
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md)
- Waiting for the owner: Q103 (level cap), Q104 (professionalism checks), Q113 (crit +1 or +2 per pick),
  Q122 (rules for XP, money, session, ranged / thrown, damage stat, master counters), Q125 (numbers still without
  an effect target).
- Assumptions to confirm: Q23, Q96, Q98-Q102, Q105, Q106, Q109, Q111, Q112, Q114-Q121, Q123, Q124.

## Next
1. Owner answers Q122 / Q125 / Q113; then a package for the remaining effect targets and the legacy items.
2. Then the AC-zones package (RULES/ac_zones.md) once the owner gives the full table.
3. Phase 3 remainder: wp/i18n texts for the refusal reason ids, settings domains, theme, panel registry.

## Known gaps (rule exists, no code)
- Master / expert weapon picks without a numeric effect are stored only (weapons.md).
- What an item qualification unlocks (Q109). Status catalog (buffs.md: statuses from a catalog) does not exist.

## Where things are
- Plan: ROADMAP.md. Finished packages: ARCH/history.md. Closed questions: ARCH/decision_log.md.
- Prompt template for new packages: Wp_claude/PROMPT_TEMPLATE.md.
- New data: wp/catalog/data/sheet_targets.json, damage_types.json, doll_slots.json.
