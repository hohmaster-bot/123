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
- P2 (Mordon, feats, comfort per fight; decisions 1-5):
  - Toughness and Endurance are real catalog feats (not samples, price 200, module core): Toughness hp_max
    max(3, level); Endurance seven situational +4 rows (Swim = Athletics, four Con checks on the new target check:con,
    two Fort saves). The feat catalog now reads condition / situational / scope / cells of effects.
  - Wall of Bones: buy_race_ability adds the granted feats (grants_feats) for free, held by the ability (the UI
    passes the catalog entries: ui_data.race_grants); -4 CMD; the reminder "bleeding x2"; comfort per fight -1 / max 3.
  - Bleeding x2 (decision 4): generic standing reminders from effects (target reminder:<key>, wp/model/
    effect_reminders.py) + the condition status_tag:<tag> + Status.tags; a sample catalog status Bleeding (tag
    bleeding, the player sets the loss). The buy-out adds -1: the reminder is gone.
  - Comfort per fight (decision 5): Character.combat_morale_peak (stored, cleared at the combat start, raised after
    every changing command in combat by dispatch), constants comfort.fight_cap / fight_minus / fight_max (const
    targets); the combat end leaves a reminder with the button "Take +N comfort" (run_command gain_fight_comfort,
    journal, undo); never silent. The reminders block translates note texts and names command buttons.

## Tests and breaks
- P1: run_all: suites 100, passed 100, failed 0. break_check (full run, no code changed): entries 527, caught 527, missed 0.
- P2: run_all: suites 101, passed 101, failed 0 (checked on the P2 tree exported from the commit index).
  break_check (full run): entries 545, caught 545, missed 0. New suite model/test_pkg38a.py (16 cases); 18 breaks
  in tests/breaks/pkg38.py. Updated old expectations (owner change): test_races37 northerner (real feats) and
  wall-of-bones (the purchase passes the Toughness entry).

## Changes to old rules
- P1: none (docs and settings only).
- P2 (owner consent): RULES/races.md "Package 38", resources.md "Comfort per fight", catalog.md "Feats",
  buffs.md "Reminders from effects". New stored fields: Status.tags, Character.combat_morale_peak. New targets
  reminder:, check:; new condition status_tag:<tag>; constants comfort.fight_*; run_command allowlist +
  gain_fight_comfort. The P37 placeholders Endurance / Toughness are replaced.

## Assumptions
- P1: "closed / answered / superseded" = an entry the owner answered or a later entry fully replaced; an "as is"
  assumption without the owner's answer is still open.
- P2: Q289 Hit Dice = level; Q290 Endurance targets; Q291 price 200, module core; Q292 the bleeding status;
  Q293 how the peak is counted, no cut at the comfort max; Q295 Toughness taken before.

## Open questions (ids)
- P1: none new.
- P2: new Q289-Q295 (Q294 proposal: Banner of Blood "1 comfort less for fights"); closed Q280, Q287.
