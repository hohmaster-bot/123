# Package prompt template (copy, fill in, send; one screen)

PACKAGE <N> - <short name>

## Goal
<One or two sentences: what must be true for the player when this package is done.>

## Read
- CLAUDE.md, Wp_claude/STATUS.md (always).
- RULES sections: <file.md "Heading">, <file.md "Heading">.
- Code / tests to look at: <paths, if known>.

## Owner decisions
- <Qxx: the answer, word for word.>
- <New rule text to write into RULES/<file>.md (this line is the consent to change RULES).>

## Out of scope
- <What NOT to touch in this package.>
- Branch Rework only; no game-rule changes beyond the decisions above.

## Done when
- <Concrete check 1, e.g. "command X refuses Y with a reason".>
- run_all.py: 0 failures; break_check.py: all caught (new entries for the new rules).
- STATUS.md, OPEN_QUESTIONS.md / ARCH/decision_log.md, ARCH/history.md updated.
- Report Wp_claude/tests/PACKAGE<N>_REPORT.md written; everything pushed.

## Output format
- Report: Done / Tests and breaks / Changes to old rules / Assumptions / Open questions (ids).
- Chat: Russian, at most 15 lines, ONE question with a recommendation.
