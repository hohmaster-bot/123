# Status (update at the end of every package; at most 40 lines)

Branch: `Rework`. Phase: 3 (rules core and model done; data / settings next, no UI yet).
Last finished package: 17 (remaining effect targets, level_up default die, DR stacks, percent per element, attack
kinds, master counters). Last report: `Wp_claude/tests/PACKAGE17_REPORT.md`.

## Tests (last run in package 17)
- `python Wp_claude/tests/run_all.py`: suites 44, passed 44, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 86, caught 86, missed 0.
- Legacy baseline (separate): 105 examples, 69 pass, 17 fail, 19 not built (BASELINE_REPORT.md).

## Open questions (OPEN_QUESTIONS.md)
- Waiting for the owner: Q104 (professionalism checks), Q130 (is "water" the same as "cold"?).
- Assumptions to confirm: Q23, Q96, Q98-Q102, Q105, Q106, Q109, Q112, Q114, Q116-Q121, Q123, Q124, Q126-Q129.

## Next (ROADMAP.md)
1. Phase 3 data / settings: rule constants from code to data, settings domains, wp/i18n texts for refusal reasons,
   theme, panel registry, a status catalog.
2. The AC-zones package (RULES/ac_zones.md) once the owner gives the full table.
3. Phase 4 overlay spike, Phase 5 UI, Phase 6 release; the class system later.

## Known gaps (rule exists, no code)
- Weapon picks without a number that are not once-per-combat are stored only (one attack without the tag, ignore
  the first vulnerability, ignore 20% cover). What an item qualification unlocks (Q109).
- Not built on purpose: XP, money, start / end of session (narrative, owner package 17).

## Where things are
- Plan: ROADMAP.md. Finished packages: ARCH/history.md. Closed questions: ARCH/decision_log.md.
- Prompt template for new packages: Wp_claude/PROMPT_TEMPLATE.md.
- Data: wp/catalog/data/sheet_targets.json, damage_types.json, doll_slots.json.
