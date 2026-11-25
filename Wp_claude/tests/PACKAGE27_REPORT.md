# Package 27 report: fixes of independent review 5

Source: `Wp_claude/tests/REVIEW_REPORT_5.md` (F1-F30); the probe scripts in `tests/review5/` are kept untouched.

## Done

| finding | status | what changed |
|---|---|---|
| F1 backups "a" vs "a.b" | fixed | `files.backups_of` accepts only `<name>.<YYYYMMDD-HHMMSS-mmm>.json`; tests a / a.b / a.b.c, keep 1, restore, rename |
| F2 topics under-declared | fixed | `tests/app/test_topics.py` (method of topics_probe.py, seeds 5 and 6, 25 tries per command); topics.json fixed for the 15 commands (damage family: every panel reading HP / pain) |
| F3 undo erases a non-undoable setting | fixed | undo / redo keep `undo.json` keep_current (char_settings, log, log_seq) of the current state |
| F4 exceptions out of dispatch | fixed | declared parameter kinds (`wp/commands/params.py`, `data/params.json`) checked before the command; safety net TypeError / AttributeError / OverflowError / RecursionError / ZeroDivisionError -> invalid_value; fuzz on 6000 steps: 0 exceptions |
| F5 wrong types break the views | fixed | `wp/storage/typecheck.py`: every command result and every `_fields` value (edit_sheet ...) must fit the dataclass type; stat names, slots, sides, damage types from known sets |
| F6 constants without limits | fixed | every constant has min / max (dividers >= 1), maps keep their key set and value type, NaN refused; set_rule_setting, settings_set and the loader enforce them |
| F7 backups_folder any text | fixed | schema type folder_name (one name, not "", ".", "..", no separator) |
| F8 image_remove deletes any file | fixed | records must be `images/<id>.<ext>` (dropped at load, refused at import); delete only inside `<user>/images` |
| F9 loader without type check | fixed | the loader runs the type check (null, NaN, text in a number, a text for a list, duplicate ids, deep nesting -> file_corrupt with the backup offer); settings_import / profile_import catch deep nesting |
| F10 bad names crash | fixed | `files.name_problem`: control characters, > 100, reserved Windows names, trailing dot / space, .json end -> bad_name |
| F11 entry codes | fixed | code length, bounded decompress (1 MB), shape {kind, entry}; entry names <= 100 |
| F12 refusal texts | fixed | chain lang -> en -> ru -> key for reason.* (owner); 51 English texts written (the 33 of the report + the new reasons) |
| F13 NaN / non-strings | fixed | str / bool / finite numbers only (params), `json.dumps(allow_nan=False)` |
| F14 short_rest extra_bp < 0 | fixed | extra_bp, other_heal (and other counts) >= 0: out_of_range |
| F15 flank vs cell 6 | fixed (owner) | flank = the cell of the side without a shield (6, or 4 with the shield in the right hand); the modes show their cells |
| F16 changes visible only in the log | fixed | sheet: bab_override, save_override; attack view: primary, main_hand_set; training: weapons (grades, basics), languages; items: equipped, in_hands; hit_item with 0 notches changes nothing |
| F17 undo lines lost | fixed | the undo / redo line goes to the current journal (5 lines after 3 commands and 2 undo) |
| F18 no-op on the undo stack | fixed | no undo step, no subscriber, not dirty, topics () |
| F19 negative resources by hand | fixed (owner) | set_value < 0 refused except HP |
| F20 take_damage unknown type / skip | fixed | dtype from damage_types (unknown_damage_type), skip a list of texts |
| F21 floats truncated | fixed | int parameters refuse floats (wrong_type) |
| F22 literal 10 in attention -> training | fixed | `training.tenths_per_point`, tenths rounded half up (no number changes, Q187) |
| F23 cached list | fixed | active_effects returns a tuple |
| F24 non-ASCII digits | fixed | formula numbers and names: ASCII only |
| F25 image content, dock | fixed | image_add checks png / jpg / gif / webp / svg content; profile_set takes only profile fields (Q189) |
| F26 stale docs | fixed | defense.md Q151 line, review pack rebuilt, ROADMAP phase line, training.md Q109 line, CLAUDE.md read table |
| F27 review scripts ASCII | fixed (doc) | note in CLAUDE.md Testing |
| F28 pool above max | fixed (owner) | the pools view gets over_max, nothing clamped |
| F29 journal without limit | fixed (owner design) | journal_mode short / full, archive `<name>.history.jsonl` + date index, history_view, travels with the character; save budget 300 ms with 50 000 lines |
| F30 15 unprotected rules | fixed | `tests/model/test_pkg27_rules.py` (numbers by hand) + 15 break entries; break_check copies Wp_claude/ARCH |

Also found and fixed: the spell price could store a rule reference (`max(SPELL_MIN_PRICE, ...)` returned the Ref
object when the minimum won) - the new result type check caught it; `Effect.value` is annotated int or text (it holds
formulas). A flask bar with a huge maximum built a huge list (now one segment, limit in limits.json).

New suites: app/test_pkg27_files.py (12), model/test_pkg27_params.py (19), storage/test_pkg27_load.py (10),
app/test_pkg27_session.py (15), app/test_topics.py (4), app/test_fuzz.py (1 case, 3000 steps), model/test_pkg27_rules.py
(16); test_perf.py +1 (save with a 50 000-line journal). New breaks: `tests/breaks/pkg27.py`.

## Tests and breaks
- `python Wp_claude/tests/run_all.py`: suites 65, passed 65, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 289, caught 289, missed 0.
- `python Wp_claude/tests/review5/fuzz5.py 120 50`: 6000 steps, 0 exceptions; 2 findings left before the F19 fix and the
  F28 decision (set_value mana -1, a pool above its formula max): both are now as the owner decided.
- `python Wp_claude/tests/review5/topics_probe.py 25`: under-declared 15 before; test_topics.py now 0.

## Changes to old rules
- RULES/ac_zones.md: appended "Flank with the shield in either hand" (owner F15). With the shield in the right hand
  the flank number is now cell 4 (before: the old flank ladder, which counted cell-6 effects).
- RULES/defense.md, RULES/training.md: stale lines only (Q151 closed, Q109 closed); no number changes.
- Old tests changed: test_session d-dispatch (take_damage topics are now every panel reading pain, F2);
  test_i18n t-reason-ru-missing (a missing Russian refusal now shows the English text, owner F12);
  test_settings png helper writes the real PNG signature (F25).

## Assumptions
- Q179 app input limits in wp/app/data/limits.json; Q180 constant limits; Q181 journal_archive_keep 100; Q182 date
  index; Q183 short mode drops lines; Q184 export holds the whole journal; Q185 hit_item 0 notches; Q186 set_value for
  every resource but HP; Q187 tenths half up; Q189 profile_set fields; Q190 the safety net.
- The Session trims / archives the journal of the open character itself (a storage step, not a game change, D29).

## Open questions (ids)
- Q188 (waiting for the owner): remove the unused app setting log_max.
- New assumptions to confirm: Q179-Q187, Q189, Q190.
