# Package 23 report

## Done
- A. Session layer `wp/app/` (D25, ARCH/app_layer.md):
  - `Session`: views by panel id, `dispatch` returning `DispatchResult(ok, topics, info, reason, params)`, subscribers;
  - topics table `wp/app/data/topics.json` (115 commands; a missing command refreshes every panel);
  - character files: new / open / save / close, duplicate / rename / delete to trash / export / import;
  - backups before every save, kept to `backups_count`; a damaged file is the refusal `file_corrupt` and
    `restore_backup` opens the newest valid backup;
  - autosave: the new app setting `autosave_mode` (interval | every_command) and an injected clock.
- B. Performance:
  - `tools/bench.py [--profile]` and the heavy character `tests/perf/heavy.py`;
  - budgets as data in `wp/app/data/perf_budgets.json`;
  - read cache `wp/model/cache.py`: kept outside the data, keyed by the rule scope, cleared by every command;
    applied to ability_mod, picks, context, all_bonuses, active_effects, sheet_targets.value and item_bonuses.
- C. `tools/make_view_contract.py` generates `ARCH/view_contract.md` (18 panels: view, parameters, fields from the
  heavy character, commands with parameters and refusal reasons, topics). It is deterministic, and a test checks it
  is up to date.
- D. AC zones as data:
  - `wp/rules_data/ac_zones.json`, `wp/core/ac_zones.py`, `wp/model/ac_zones_view.py`;
  - cells 2 / 6 / 8 give exactly the old front / parry, flank and flat-footed values;
  - shield cover by type and hand (the right hand mirrors).
- E. Docs:
  - ARCH/app_layer.md and D25;
  - ROADMAP: phase 3 done; what is left is review 5, the overlay prototype (needs drawings A1, A2) and the UI;
    PDF export is not built;
  - OPEN_QUESTIONS Q154-Q159;
  - STATUS, history, decision_log;
  - TRANSLATION_TODO rebuilt; the review pack is unchanged (no RULES change).

## Timings (heavy character, this PC; best of 3, cache cleared before each run)
| measure | before (no cache) | after | budget |
|---|---|---|---|
| one command + all 18 views | 4630.8 ms | 28.8 ms | 200 |
| attacks view | 1405 ms | 13.3 ms | 50 |
| skills view | 1187 ms | 6.3 ms | 50 |
| defense view | 619 ms | 2.6 ms | 50 |
| open (load) | 45 ms | 45.1 ms | 500 |
| save (with backup) | 132 ms | 136.9 ms | none |

cProfile of all views, top 10 by cumulative time.

Before (cache disabled, 8.87 s in total):

| function | cumulative |
|---|---|
| session.view | 8.87 s |
| ability_mod | 7.89 s |
| active_effects | 7.12 s |
| sheet_targets.value | 6.91 s |
| context | 6.73 s |
| picks | 6.67 s (237801 calls) |
| ability_current | 6.45 s |
| stat_bonus | 6.45 s |
| item_bonuses | 6.13 s (237801 calls) |

After (0.085 s in total):

| function | cumulative |
|---|---|
| session.view | 0.085 s |
| attack_view.attack | 0.044 s |
| views.attacks | 0.035 s |
| cache wrapper | 0.025 s |
| attack_view.drum | 0.024 s |
| views.skills | 0.020 s |
| skill_bonus | 0.020 s |
| armor_skill_penalty | 0.015 s |

The cause was the same item and effect lists being recomputed for every stat and every attack. The read cache
removes that repeated work.

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 55, passed 55, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 167, caught 167, missed 0.
- New suites:
  - test_session (13);
  - test_perf (7: budgets, cached = uncached after random commands, cleared by a command, rule scope);
  - test_ac_zones (10);
  - test_view_contract (4).
- New break entries: 13 (breaks/pkg23.py).

## Changes to old rules
- None. Old AC modes are unchanged (tested equal to the cells).
- RULES/ac_zones.md is not edited; it stays a draft, and the data is a sample of it.

## Assumptions
- Q154: side cells keep Dex and dodge; only the back cell 8 loses them.
- Q155: parry only in cells 1-3.
- Q156: the shield hand is not on the sheet, so the default is left; a shield with no type covers like a light one.
- Q157: no cell-scoped effects.
- Q158: the default of autosave_mode is interval.
- Q159: the perf budget numbers.

## Open questions (ids)
Q154, Q155, Q156, Q157, Q158, Q159 (all assumptions, to confirm).
