# Package H report (housekeeping)

Date: 2026-11-20. Branch `Rework`. The program's behavior, the game rules and the test expectations did not change.

## Done
- `tests/run_all.py`: all suites of the new code, one summary line.
- `tests/break_check.py` + `tests/breaks/core.py` (22 entries) and `tests/breaks/model.py` (21 entries).
  It works on a temp copy, so the working tree is never touched.
- CLAUDE.md rewritten (74 lines):
  - a goal line;
  - all the hard rules, plus three rules from the packages: Rework only, no silent choices, constants in data;
  - the reading table and reading rules;
  - run_all / break_check (the legacy baseline is run separately);
  - the standard package procedure with the report and chat formats.
- `STATUS.md` (29 lines), new. CLAUDE.md points to it, and updating it is now part of the procedure.
- ROADMAP: the "Done in package 8-15" blocks and the stale "Deferred (from REVIEW_REPORT)" list moved word for word to `ARCH/history.md`.
- OPEN_QUESTIONS: the "Closed and removed" paragraph moved word for word to `ARCH/decision_log.md` (append-only). One pointer line stays.
- `tools/rules_index.py` (ASCII): regenerates the "Sections" block of `RULES/index.md`. For each file it writes:
  - its size and what it covers;
  - its `##` headings with line numbers.

  `--check` reports whether the block is out of date. This block is the only change in RULES/.
- `PROMPT_TEMPLATE.md`: Goal / Read / Owner decisions / Out of scope / Done when / Output format.

## Tests and breaks
- run_all: `suites 41, passed 41, failed 0`.
- break_check: `entries 43, caught 43, missed 0`.
- Checked that break_check catches its own mistakes: a harmless break shows MISSED, and a missing pattern shows "not applied".

## Sizes (chars / lines; tokens = chars / 4)
| File | Before | After |
|---|---|---|
| CLAUDE.md | 4949 / 60 | 5319 / 74 |
| OPEN_QUESTIONS.md | 8281 / 51 | 3656 / 22 |
| ROADMAP.md | 7501 / 96 | 4329 / 65 |
| Total | 20731 | 13304 |

- Saved: 7427 chars, about 1860 tokens per session that reads all three.
- The always-read set now also includes STATUS.md (1640 chars, about 410 tokens). Net saving: about 1450 tokens.

## training_costs_draft.md
Not deleted. Every price in it is in training.md, skills.md, weapons.md or progression.md, except two items from the legacy code:
- the class's `spell_discount_extra` (subtracted from the spell price);
- "spell price at least 1".

Some numbers in the draft differ from the RULES; the RULES win, and the draft says so itself:
- the non-native language costs 30 * projects;
- the native language is compared with the Int modifier;
- there are no refunds.

The draft also does not say outright that weapon picks are free (weapons.md only opens them by level).

## Changes to old rules
None.

## Assumptions
- The "Sections" block is placed at the end of RULES/index.md, between markers.

## Open questions
No new ones. Still open: Q103, Q104, Q107, Q108, Q110 (see STATUS.md).
