# Package 25 report

## Done
- A. Undo / redo in the Session:
  - `undo()` / `redo()` over a bounded stack of previous Character states (app setting `undo_depth`, default 50);
  - a new command clears redo; a refused command is not on the stack;
  - commands listed in `wp/app/data/undo.json` (character UI settings) are skipped; open / new clear the stacks;
  - "undo" / "redo" journal lines; undo returns the command's topics; autosave sees a change;
  - the states are frozen and share their unchanged parts (no copies): bench dispatch + undo + redo 1.9 ms; the
    perf budgets hold (dispatch + all views 32.2 ms, budget 200).
- B. Class system v0:
  - catalog kind `classes` with three SAMPLE entries; `set_class(class_id, catalog)` takes a snapshot;
  - BAB / saves derived from class + level, with `bab_override` / `save_override`; no class = everything as before;
  - the class hit die caps level_up;
  - professionalism refuses a class with its own professionalism and skills outside the class list (closes Q104);
  - the spellbook flag gives the learn_spell discount by default; the divine flag sets the failure mode default.
  - RULES/progression.md "Class system v0 (package 25)" appended, with the assumption values marked.
- C. Drives:
  - level notes per level and a principle;
  - the view shows the note of the current level and `principle_missing` (level >= 2, a data constant);
  - commands add_drive / edit_drive / remove_drive / set_drive_level_note / set_drive_principle;
  - RULES/narrative.md section with the owner text.
- D. Hidden item properties:
  - shown as "???" below the qualification level (N once bought, 50 * N kept);
  - when unlocked, the text shows and the effects act in their tab;
  - add_hidden_property / remove_hidden_property (closes Q109).
- E. Picks as flags:
  - no_attack_tag, ignore_vulnerability, ignore_cover_20 appear as available abilities in the attack view (per
    group) and the defense view;
  - ignore_vulnerability is once per fight: a usage charge (COUNTER_PICKS); no numbers change.
- F. Spell damage:
  - `Spell.damage` components (dice count formula, die size, flat formula, one of the 12 types, area from the
    constant spells.areas, range, save, save effect), set with set_spell_damage;
  - the spells view evaluates them for the level and adds the pain penalty and morale of the damage roll; no dice.
- G. Docs:
  - ARCH/classes.md and D27;
  - OPEN_QUESTIONS: Q104 and Q109 closed, new Q167-Q173;
  - ROADMAP: left = review 5, the overlay prototype (owner drawings), the UI; PDF export with Qt later;
  - STATUS, history, decision_log; view contract, review pack and TRANSLATION_TODO rebuilt.

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 57, passed 57, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 209, caught 209, missed 0.
- New suite: test_pkg25 (35 cases). New break entries: 23 (breaks/pkg25.py).
- Changed old test: test_catalogs w-kinds lists the new kind "classes".

## Changes to old rules
- None in numbers when no class is set.
- learn_spell `discount` now defaults to the class spellbook flag; with no class that is False, as before.
- The once-per-fight pick "ignore the first vulnerability" now has a usage charge.

## Assumptions
- Q167: BAB factors and save formulas.
- Q168: the class snapshot.
- Q169: the hidden property tab "base".
- Q170: caster level = character level.
- Q171: non-undoable commands, depth 50.
- Q172: the class die also caps training HP.
- Q173: skill ids for professionalism.

## Open questions (ids)
Q167, Q168, Q169, Q170, Q171, Q172, Q173 (assumptions, to confirm).
