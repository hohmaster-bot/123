# UI gaps of the core for Classic screen v2 (package 29 B audit; built in packages 30 and 31)

Status: every row is DONE (packages 30 / 31) or needs no core change. Names as built: adjust_value, set_attack_source,
set_favorite, Session.run_quick, Session.cell_sources, views sheet attack_melee / attack_ranged / class, items load,
defense shield_side / cell_lines / cell_labels, combat morale_active / action_squares / reaction_squares, statuses
favorites / reminders, Status.note; profile fields quick_cells / quick_columns / strips; settings hints_seen /
hints_off (hint_dismiss, hints_reset, screen_settings.hints_view), screen_settings.layout_warnings, profile_reset,
resource_style / resource_size / resource_autoswitch / pool_order / pools_large, theme_follow_system / theme_light /
theme_dark / background_image / background_dim / background_readable; themes theme_copy / theme_reset /
contrast_ratio / warnings / view, shipped dark (default) / light / grey_blue with every token below. Not built (no
core data): a race view (Q206); quick_view of button charges is read from the target records by the UI.
Package 33 (Phase 5 step 2 built): the resources view also gives damage_types (the 12 types) and buttons (own quick
buttons of group "resource:<id>"); the experience view gives can_level_up and the goal is always exp.level_cost
(set_next_level_at retired); resource_size defaults are now horizontal tubes (w, h). Mana max still has no plain
number command (edit_sheet needs a Pool; Q224).
Package 34 part 1 (step 3 built): the view "sources" (number=...) gives the sources of every number (D34), the
manual rows are the commands source_add / source_edit / source_toggle / source_remove (editor mode); mana max comes
only from its sources (Q224 closed). The rows parameters / ac_block below are now built blocks.

Spec: `UI_WISHES.md` "Classic screen v2". Names are the exact views (`session.view(...)`, ARCH/view_contract.md)
and commands of the registry. "Gap" = what the block needs and the core does not give yet; "Proposed" = the
smallest addition. The proposed additions are scheduled as Phase 5 steps in ROADMAP.md (step number in brackets).

## Editor mapping (spec 4: a correction, no game mechanics)
The tube editor "+N" / "-N" / "number" maps to ONE command per resource, computed from the shown current value:
`set_value(resource, current + N | current - N | number)` for hp, balance, bp, comfort, spirit, mana (set_value
refuses a negative value except HP, package 27 F19; no heal block, no pain: a correction). Temporary HP (second field
of the HP popup): `set_temp_hp(value)`. The mechanics stay buttons: `take_damage`, `restore(resource="hp")`,
`damage_to_balance`. NOT used by the editor: `restore` (it is blocked by healing blocks), `spend_balance` (mechanics).

| block | views / commands it uses | gap | proposed minimal addition |
|---|---|---|---|
| experience_strip | `training.experience` (total, next_level_at = exp.level_cost, progress_pct, can_level_up, log, level_history); `add_experience`, `level_up`, `edit_experience_entry`, `remove_experience_entry` (package 33: set_next_level_at retired) | "to next level" = next_level_at - total is derived by the UI; fine | none [3] no core change needed |
| identity (avatar) | image registry target `character` (`images.image_of`), app setting char_portrait | the avatar size is a layout value | profile block size only (layout editor) [8] no core change needed |
| resources: HP, balance, spirit, mana | `resources` (hp, balance, spirit, mana, temp_hp, overload, flasks); `set_value`, `set_temp_hp`, `take_damage`, `restore`, `damage_to_balance` | -1 / +1 on spirit and mana: no dedicated commands (set_value works as a correction); mana overload - / +: no command (only `edit_sheet(overload=)` or `cast_spell`) | an `adjust_value(resource, delta)` correction command (same checks as set_value) covering hp / balance / bp / comfort / spirit / mana / overload / pool:<id> [2] DONE (30) |
| resources: style and sizes | app settings `resource_display` (number / bar / both / percent / flask), `resource_segments` | no glass / flat style, no colours, no width / height, no auto-switch flag | app settings `resource_style` (glass / flat), the colours as THEME tokens (amendment, see "Themes" below; not an app setting), `resource_size` (w, h per resource), `resource_autoswitch` (bool) [2] DONE (31) |
| resources: temporary HP strip | `resources.temp_hp`, `flasks.hp` | segments by 5 for the temp strip | app setting key `resource_segments.temp_hp` (5) [2] DONE (31) |
| resources: class pools | `resources.pools` ((pid, name, {current, max, over_max})); `spend_pool(pid, n)`, `restore_pool(pid)` | "+1" on a pool: no command (restore_pool refills by its rule); set_value does not know class pools; "the first three large": no setting | `adjust_value("pool:<id>", 1)` (above); profile field `pools_large` (list of pool ids) [2] DONE (30) |
| resources: custom buttons | profile quick buttons (`quick_add`; `layout.run_quick` runs an action or a macro) | `run_quick` works on the Character directly, not through the Session (no undo step, no topics, no journal stamp); a macro step has fixed params, so "add X" / "write off X" on any resource needs a relative command | `Session.run_quick(button_id)` (one undo step, topics = union); `adjust_value` as the step command [2] DONE (30) |
| ac_block | `defense.cells` (variants, full, parry, shield, dex_loss), `defense.display`, `defense.modes`; sources: `stats`-like lines are not given per cell | zone labels (front-left ... back-right): i18n keys `ac_cell.<n>` do not exist; the shield SIDE (left / right) is not in `defense` (only `items.hands`); the per-cell source breakdown is not returned | i18n keys `ac_cell.1`..`ac_cell.9`; `defense["shield_side"]` (left / right / ""); `defense["cell_lines"][cell]` = the layer parts of `core/ac.layer_parts` [4] DONE (30) |
| parameters | `sheet.stats` (cmb, cmd, fort, initiative, ref, will), `items.weight` (carried_l, load) | no general melee / ranged attack number (only per attack record in `attacks`, Q198); no load limits (light up to, heavy up to) in a view; the load categories are light / heavy / overload (RULES/gear.md "Weight"; the spec names two, Q197) | `sheet.stats.attack_melee` / `attack_ranged` after the owner's formula (Q198); `items.weight.light_max_l` / `heavy_max_l` from `core.derived.load_thresholds_l` [4] DONE (30) |
| cell blocks (parameters, bottom strip) | profile `cells` (package 19: source = a sheet number, skill, pool, counter), `layout_add` / `layout_edit` | colour thresholds and the click action exist as cell fields (`color_rules`, `action`); the list of valid `source` ids is not published | a view `cell_sources()` listing every source id with its i18n label [4] DONE (30) |
| statuses | `statuses.container` (favorites, entries with favorite / hidden), `statuses.active`; `add_status`, `activate_status`, `remove_status`, `set_status_favorite` | the "note" of a chip: a Status record has no note field (the container entry gives name, rounds, charges) | `Status.note` (stored text, set by `edit_entry`) shown in the container entry [5] DONE (30) |
| favorites | `statuses.container.favorites` (status ids) | favourite ABILITIES (feats, items with charges, attack records): no flag, no list | char setting `favorites` (list of "kind:id") + `set_char_setting`; a favourites view combining both [5] DONE (30) |
| reminders | `notebook.drive_summary.reminders`; `level_up` / `end_cycle` `info["reminders"]` (one-shot) | no single reminders list: one-shot reminders vanish after the result; other sources (unspent training? missing class?) not defined | a `reminders` view joining drive reminders and the last one-shot reminders (kept until dismissed: char setting `reminders_seen`) [5] DONE (30) |
| combat tab | `combat` (in_combat, round, actions {current, max, sources}, reactions {current, max}), `attacks`; `start_combat`, `end_combat`, `short_rest`, `long_rest`, `end_cycle`, `tick`, `spend_actions(n)`, `restore_actions`, `spend_reaction(n)`, `restore_reactions`, `use_attack` | the numbered squares (amendment): the core keeps only current / max, so the squares are derived: squares 1..max; spending takes the SMALLEST numbers first, so after `spend_actions(n)` the spent squares are 1..(max - current) and the available ones (max - current + 1)..max; `restore_actions` (and the tick / end of combat refill) makes all available; the same for reactions; no command spends a chosen square | `combat.actions.squares` / `combat.reactions.squares` = ((number, spent), ...) derived on read, so the UI never computes the order; theme token `action_square` (one colour for every square) and `action_spent` [5] DONE (30) |
| quick access grid | profile quick buttons (label, icon, action / macro, hotkey, group, order, cost_actions); charges / cooldown: `usage` of the owner record | cells count 4-16 and the number of columns: no setting; charges of a button's target are not resolved by a view | profile fields `quick_cells` (8), `quick_columns`; a `quick_view()` giving each button its target's charges / cooldown [5] DONE (30) |
| bottom_strip | `resources.ot`, `resources.pain`, `combat.morale_scale` / `morale_bonus`, `sheet.speed`, `items.weight` | the encumbrance limits (as in parameters); a second strip: no profile field | `items.weight` limits (above); profile field `strips` (list of cell lists) [6] DONE (30) |
| journal tab | `log` view, `Session.journal_view(count, offset)`, `Session.history_view(from_date, to_date, page)` | none | none [7] no core change needed |
| tabs (Skills, Feats, Race, Class, Injuries, Drives, Inventory, Training, Rest, Catalogs, Settings) | `skills`, `sheet` (feats list), `injuries`, `notebook`, `items`, `training`, `rest`, `catalogs`, `settings` | Race and Class have no panel (Q177); feats are only (fid, title, charges, cooldown) in `sheet.feats` | `class` and `race` views (class snapshot, race data when defined) [7] DONE (30) |
| expand to full screen | layout runtime state (UI only) | must never write the profile: no core change | none (UI rule, D31) [8] no core change needed |
| one-time hints | none | no storage | app settings `hints_seen` (list of hint ids), `hints_off` (bool); settings commands `hint_dismiss(id)`, `hints_reset()`; i18n keys `hint.<id>` [1] DONE (31) |
| layout editor and validation | `registry.check_profile`, `registry.warnings(app)`, `profile_*`, `layout_*` | warnings for "a block under its minimum", "all HP controls hidden", "a block outside the window"; "restore the default profile" | `registry.warnings` gains these three checks; `profile_reset(mode)` command [8] DONE (31) |
| themes (amendment, spec 16) | `wp/theme` (themes.json shipped light / dark; theme_add / edit / remove / duplicate / set_active / export / import; qss.py), app setting `theme` (default "light") | no grey-blue theme; the default is light (spec: dark for a new profile); no "reset to the shipped one" command (only theme_remove of the user override); no follow-the-system option; no contrast check; no background picture settings; missing tokens: see "Themes" below | shipped `grey_blue`; app setting `theme` default "dark"; `theme_reset(tid)` (drops the user override); app setting `theme_follow_system` (bool) + `theme_light` / `theme_dark` ids; a contrast warning (4.5:1, main number colour vs its background) in the theme view, never a refusal; app settings `background_image` (image id, "" = none), `background_dim` (0..100), `background_readable` (bool overlay); the theme editor view with a live preview [1b] DONE (31) |

## Themes: tokens the Classic v2 screen needs (amendment; ARCH/themes.md, wp/theme/data/theme_schema.json)
Present colour tokens: background, surface, text, muted, accent, accent_text, border, success, warning, danger,
info; hp, balance, mana, spirit, comfort, pain, ot, morale; ac_base ... ac_natural (the AC layers).
Missing in package 29, ADDED in package 31 (all shipped themes define them):
- resources: `pool` (the default class pool colour; a pool may carry its own colour in its record or a token
  `pool_<n>`), `overload_chip`, `temp_hp` (the grey / silver strip), `bp`;
- glass tube: `tube_glass` (the glass body, with alpha), `tube_highlight`, `tube_segment` (segment ticks),
  `tube_empty` (the empty part); the liquid uses the resource token;
- status chips: `chip_buff`, `chip_debuff`, `chip_neutral`, `chip_favorite`, `chip_text`;
- cell thresholds: `threshold_good`, `threshold_warn`, `threshold_bad` (the cell color_rules name these tokens, not
  raw colours);
- action squares: `action_square`, `action_spent`, `reaction_square`;
- strips and blocks: `strip_background`, `block_border_edit` (editor mode borders), `hidden_mark` (the "something is
  hidden" mark), `hint_background` (one-time hints);
- background picture: `background_overlay` (the readable overlay behind the panels, with alpha).
Scalars: `tube_gloss` (0..100, glass highlight strength) next to overlay_opacity.
