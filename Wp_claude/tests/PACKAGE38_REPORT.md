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
- P3 (rerolls; decisions 6, 7): wp/core/rerolls.py (Reroll: name, charges, recharge from the usage list) as a field
  rerolls on every carrier (feats, items, statuses, quirks, injuries, trainings) and in the catalog data (race
  abilities / statuses / quirks, feats, items, statuses); view rerolls (ref, source, name, left / max, rule); commands
  spend_reroll / restore_reroll (journal "charges", undo); usage.recharge refills them with the rests and the combat
  events; the Rerolls block (panels.json, default profile: right column under the combat tab); Mordon type 5 got its
  own reroll (1, long rest), separate from the -4 counter.
- P4 ("!" notes; decision 8): Qt-free wp/settings/notes.py (targets = the profile blocks and tab:<id>; add / edit /
  move / remove), settings commands note_add / note_edit / note_move / note_remove (classic profile field notes,
  saved with the UI settings, typed in the profile schema), profile_reset keeps the notes; the window draws a "!"
  mark (theme tokens warning / accent_text) with the text as tooltip and in an info box on click; a tab note shows
  while its tab is open; the layout editor has a notes part (wp/ui/notes_panel.py).
- P5 (the effect editor; decision 9, D37, closes Q276): Qt-free form wp/model/effect_form.py (targets of the view
  effect_targets, now with the core roll targets; value or formula; add / replace; condition kinds; scope; situational;
  bonus type); character commands effect_add / effect_change / effect_remove; wp/app/effect_editor.py (carriers,
  catalog edits through the new Session.catalog_command, saved into the user layer with the module tag); the dialog
  wp/ui/effect_dialog.py, opened by Effects in the Feats, Inventory, Injuries tabs (any carrier through its chooser)
  and in the catalog window.

## Tests and breaks
- P1: run_all: suites 100, passed 100, failed 0. break_check (full run, no code changed): entries 527, caught 527, missed 0.
- P2: run_all: suites 101, passed 101, failed 0 (checked on the P2 tree exported from the commit index).
  break_check (full run): entries 545, caught 545, missed 0. New suite model/test_pkg38a.py (16 cases); 18 breaks
  in tests/breaks/pkg38.py. Updated old expectations (owner change): test_races37 northerner (real feats) and
  wall-of-bones (the purchase passes the Toughness entry).
- P3: run_all: suites 103, passed 103, failed 0. break_check (full run on the P3 tree): BREAK_P3. New suites
  model/test_pkg38b.py (10), ui/test_p38a.py (4, shots rerolls_*); 12 breaks. Old expectation updated: test_shell
  s-regions (the right column has the Rerolls block).
- P4: run_all: suites 105, passed 105, failed 0. break_check (full run on the P4 tree): BREAK_P4. New suites
  app/test_notes38.py (8), ui/test_p38b.py (4, shots notes_*); 9 breaks.
- P5 (final): run_all: suites 107, passed 107, failed 0. break_check (full run): BREAK_P5. New suites
  model/test_pkg38c.py (9), ui/test_p38c.py (4, shots effect_editor_*); 12 breaks.

## Changes to old rules
- P1: none (docs and settings only).
- P2 (owner consent): RULES/races.md "Package 38", resources.md "Comfort per fight", catalog.md "Feats",
  buffs.md "Reminders from effects". New stored fields: Status.tags, Character.combat_morale_peak. New targets
  reminder:, check:; new condition status_tag:<tag>; constants comfort.fight_*; run_command allowlist +
  gain_fight_comfort. The P37 placeholders Endurance / Toughness are replaced.
- P3 (owner consent): RULES/buffs.md "Rerolls". New stored field rerolls on Feat, Item, Status, Quirk, Injury,
  TrainingTaken; the default classic profile has the Rerolls block.
- P4: none in RULES (UI_WISHES.md 13a, ARCH/settings.md). New profile field notes.
- P5: none in RULES (ARCH/decisions.md D37). The view effect_targets also lists the core roll and defence targets.

## Assumptions
- P1: "closed / answered / superseded" = an entry the owner answered or a later entry fully replaced; an "as is"
  assumption without the owner's answer is still open.
- P2: Q289 Hit Dice = level; Q290 Endurance targets; Q291 price 200, module core; Q292 the bleeding status;
  Q293 how the peak is counted, no cut at the comfort max; Q295 Toughness taken before.
- P3: Q296 the reroll carriers and refs; Q297 old profiles get the block by "Restore the default profile".
- P4: Q298 a note sits on a block or a tab page.
- P5: Q299 the editor is open in play, race catalog abilities are edited on the character; Q300 the form rules.

## Open questions (ids)
- P1: none new.
- P2: new Q289-Q295 (Q294 proposal: Banner of Blood "1 comfort less for fights"); closed Q280, Q287.
- P3: new Q296, Q297; closed Q283. P4: new Q298. P5: new Q299, Q300; closed Q276.
