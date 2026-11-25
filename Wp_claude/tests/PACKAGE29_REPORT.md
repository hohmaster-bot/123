# Package 29 report: Classic screen v2 spec and the core gap audit

## Done
- A. `UI_WISHES.md`: the section "Classic screen v1" is replaced by "Classic screen v2 (owner approved, package 29)"
  with the 15 owner points and an ASCII wireframe of the regions; the correction list is kept (the AI pictures A1-A6
  are historical). `ARCH/surfaces.md` (Classic regions, D31), `ARCH/panels.md` (the v2 blocks: experience_strip,
  identity, resources, ac_block, parameters, statuses, favorites, reminders, combat, tabs, bottom_strip and the views
  each reads), `UI/sketches/README.md` (v2 is binding), D31 in ARCH/decisions.md, CLAUDE.md read table (ui_gaps.md).
- Encumbrance check (spec 7, RULES/gear.md "Weight"): RULES have light (to 5.9 B + Str mod), heavy (to 10.9 B + Str
  mod) and ABOVE heavy the encumbrance state (overload: dodge capped at +2, speed -10 ft, drag only). The code has
  the same three (`core.derived.load_status`: light / heavy / overload). So "only these two exist" does not match
  RULES: Q197 (recommendation: show the third state as overload, red).
- B. `ARCH/ui_gaps.md`: per block the exact views / commands, the gap and the minimal addition; the editor mapping
  (+N / -N / number -> `set_value(resource, computed)`, temp HP -> `set_temp_hp`). Main gaps: a correction command
  `adjust_value(resource, delta)` (pools, mana overload, custom buttons), `Session.run_quick` (quick buttons run
  outside the Session today), resource style / colour / size settings, load limits in `items.weight`, a general
  melee / ranged attack number (Q198), `shield_side` and per-cell lines in `defense`, ac_cell labels, a cell source
  list, a Status note field, favourite abilities, a reminders view, quick grid settings, a second bottom strip, class
  / race views, hint storage (hints_seen, hints_off, hint_dismiss, hints_reset), three layout warnings and
  profile_reset. Nothing implemented. ROADMAP.md Phase 5 lists the 8 steps in order.
- C. Tooling: `break_check.py` reruns a suite that fails on the clean copy once more alone before it counts (prints
  a "rerun" line); `tests/perf/test_perf.py` measures the best of 3 (BEST_OF = 3) for every budget, the journal save
  too.

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 66, passed 66, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 301, caught 301, missed 0. (no clean-copy rerun was needed)
- Perf numbers (tools/bench.py, best of 3, this machine): load 79.0 ms (budget 500), slowest view attacks 16.6 ms
  (50), dispatch + all views 36.4 ms (200), save 39.8 ms, dispatch + undo + redo 4.0 ms; test_perf 8 / 8 (the save
  with a 50 000-line journal under 300 ms).
- No new rule, so no new test case or break entry (docs and tooling only).

## Changes to old rules
- None. RULES untouched.

## Assumptions
- Q199: the tube editor maps to set_value / set_temp_hp; pools and the overload need adjust_value.

## Open questions (ids)
- Q197 (load categories: two in the spec, three in RULES), Q198 (general melee / ranged attack number) - waiting
  for the owner. Q199 assumption.

## Amendment (owner decisions, final)
- Themes and background: UI_WISHES.md Classic v2 point 1 and a new point 16: three shipped themes (dark default,
  light never pure white, grey-blue low contrast), own themes with every colour a token, live preview, copy / reset to
  shipped, an optional own background picture with dimming and a readable overlay (default none), follow the system,
  a 4.5:1 contrast warning (never a refusal); resource, chip, threshold and action square colours are theme tokens.
- Actions: point 9 rewritten: one colour for every action square, squares numbered 1, 2, 3 ..., spending takes the
  smallest numbers first, a spent square is grey; the reaction square in the same style.
- ARCH/ui_gaps.md: the themes row rewritten (no grey-blue theme, default is light, no theme_reset, no follow-system,
  no contrast check, no background settings) and a "Themes" section listing the missing tokens (pool, overload_chip,
  temp_hp, bp, tube_*, chip_*, threshold_*, action_square / action_spent / reaction_square, strip / editor / hint /
  background overlay tokens, scalar tube_gloss); the resource colours moved from an app setting to theme tokens; the
  combat row: the numbered squares are derived from current / max (spent = 1..max - current), proposed
  combat.actions.squares / combat.reactions.squares. ROADMAP Phase 5 step 1b "theme editor and background".
- Checked ARCH/themes.md: the present light theme background is #f4f4f2 (not pure white).
- Tests: run_all suites 66, passed 66, failed 0; break_check entries 301, caught 301, missed 0.
- New assumptions: Q200 (pool colours), Q201 (contrast pairs).
