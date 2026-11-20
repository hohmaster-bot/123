# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 2-3 (rules core and model, no UI yet).
Last finished package: H (housekeeping: run_all, break_check, docs split). Last rules package: 15.
Last report: `Wp_claude/tests/PACKAGEH_REPORT.md`.

## Tests (last run in package H)
- `python Wp_claude/tests/run_all.py`: suites 41, passed 41, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 43, caught 43, missed 0.
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md)
- Waiting for the owner: Q103 (level cap), Q104 (professionalism checks), Q107 (comfort rate bonus),
  Q108 (long-rest recharge of statuses without a source), Q110 (attention options 2 and 4).
- Assumptions to confirm: Q23, Q96, Q98-Q102, Q105, Q106, Q109, Q111, Q112.

## Next
1. An independent review of the whole core by a fresh session.
2. Package 16: the remaining "core" items of tests/LEGACY_FEATURES.md (see ROADMAP.md).
3. Then the AC-zones package (RULES/ac_zones.md) once the owner gives the full table.

## Known gaps (rule exists, no code)
- Master / expert weapon picks without a numeric effect are stored only (weapons.md).
- Attention options 2 and 4 (Q110); what an item qualification unlocks (Q109).
- RULES/training_costs_draft.md kept: `spell_discount_extra` and "spell price at least 1" are not in training.md.

## Where things are
- Plan: ROADMAP.md. Finished packages: ARCH/history.md. Closed questions: ARCH/decision_log.md.
- Prompt template for new packages: Wp_claude/PROMPT_TEMPLATE.md.
