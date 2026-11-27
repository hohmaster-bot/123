# Package 38 report - token rules, Mordon / feats fixes, rerolls, "!" notes, the effect editor

Parts P1-P5; one section per part under each fixed heading. Owner away: choices not in RULES / UI_WISHES / the
package text are written as open questions (Q289 and later).

## Done
- P1 (token rules, docs and settings only, no game code):
  - CLAUDE.md "Reading rules": never open PNG screenshots; break_check by id prefix during a part, the full run once
    at the end of the part; never paste long logs, only summary lines; closed questions live in the archive.
  - .claude/settings.json (project, committed): permissions deny Read(./Wp_claude/tests/ui_shots/**),
    Read(./Wp_claude/TRANSLATION_TODO.md), Read(./Wp_claude/AUDIT.md). These rules govern only Claude's own file
    reads; the Python tests and scripts (break_check copies TRANSLATION_TODO.md, the UI tests write ui_shots/*.png)
    are plain processes and are not affected, so no entry had to be left out.
  - OPEN_QUESTIONS.md cleanup: the closed / answered entries moved word for word with their ids to the new
    Wp_claude/ARCH/questions_archive.md: Q280, Q283, Q287 (answered by the owner decisions 1-6 and 10 of this
    package). Every other entry is still an assumption waiting for the owner's confirmation or a proposal, so it
    stays (Q212 is only partly replaced by Q222: its pools_large / pool_order parts are still open, kept).
    Size: 40433 -> 39652 bytes, 161 -> 158 entries; a one-line pointer to the archive. No rewording, no renumbering.

## Tests and breaks
- P1: run_all: suites 100, passed 100, failed 0. break_check (full run, no code changed): entries 527, caught 527, missed 0.

## Changes to old rules
- P1: none (docs and settings only).

## Assumptions
- P1: "closed / answered / superseded" = an entry the owner answered or a later entry fully replaced; an "as is"
  assumption without the owner's answer is still open.

## Open questions (ids)
- P1: none new.
