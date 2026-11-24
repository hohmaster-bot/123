# Package 26 report

## Done
- A. Actions as a resource (RULES/combat.md "Actions"):
  - max = the constant actions.base (3) + effects "actions_max" (typed stacking); current = `Character.actions_current`;
  - the zero-initiative tick and the end of combat refill them;
  - `spend_actions(n)` (refusal not_enough_actions) and `restore_actions`;
  - `cost_actions` on attack records, spells and quick buttons (a profile field), as already on maneuvers; it is shown
    only, nothing is spent automatically;
  - the combat.md costs are the presets of the constant actions.cost_presets (`preset_cost`);
  - `actions_view`: current / max and the sources (the base, each effect), in the resources and combat views;
  - topics added.
- B. Flask bars:
  - the app setting resource_display allows "flask"; the new setting resource_segments (per resource; pool /
    pool:<id>);
  - `wp/model/flask.py`: segments(12, 5) = [5, 5, 2], fills(7, 12, 5) = [5, 2, 0];
  - the view covers HP, balance (cap marker, max before cap hits, restore per tick), BP, spirit, mana, comfort, class
    pools and reactions (`resources.flasks`).
- C. Experience (changes Q122; the owner's consent is in the package):
  - `xp_log` entries {id never reused, amount (may be negative), note, at}; the total is derived from the log;
  - `next_level_at` is a goal shown as a percent: no threshold, no automatic level-up;
  - `level_history` is written by level_up (level, XP at that moment, roll, note, at); level_up has a `note`;
  - commands: add_experience, edit_experience_entry, remove_experience_entry, set_next_level_at, and in edit mode
    edit_level_history, remove_level_history;
  - the Session stamps `at` from its clock (wp/app/data/stamps.json);
  - journaled and undoable; the view `training.experience`;
  - RULES/narrative.md and catalog.md updated; "XP not built" removed from STATUS.
- D. UI_WISHES.md "Classic screen v1": blocks, the view / panel that feeds each one, the commands of every button,
  the corrections to A1-A6. ARCH/surfaces.md links it. `Wp_claude/UI/sketches/README.md` lists the expected owner
  files; no image files were created.
- E. Docs:
  - D28; Q174-Q178; Q122 change in decision_log;
  - ARCH/settings.md, ROADMAP, STATUS, history;
  - view contract, review pack and TRANSLATION_TODO rebuilt.

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 58, passed 58, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 220, caught 220, missed 0.
- New suite: test_pkg26 (23 cases). New break entries: 11 (breaks/pkg26.py).

## Changes to old rules
- XP is no longer "narrative only": it is a log (Q122 changed by the owner). Money stays narrative.
- Actions are now tracked; no old number changes.

## Assumptions
- Q174: segment defaults.
- Q175: derived total and the time stamp.
- Q176: the A1-A6 subjects.
- Q177: no panels for Feats / Race / Class.
- Q178: costs are shown only.

## Open questions (ids)
Q174, Q175, Q176, Q177, Q178 (assumptions, to confirm).

## Note
- `Wp_claude/tests/REVIEW_REPORT_5.md` and `Wp_claude/tests/review5/` were already in the folder (not created by this
  package); they were left untouched and not committed.
