# UI wishes (design, NOT rules)
Kept apart from RULES/. Nothing here changes numbers.
- Damage: [Take damage][gear]; gear = DR/- and Resistance picker by damage type.
- Dying: painful action slots highlighted red; player taps spent actions (or skips).
- Over-max values shown red (comfort, base, load); load/base overload icon.
- Shield bonus on/off in AC or small secondary number "AC with shield".
- Morale: one button start/end combat (label toggles); indicators "We are losing!" / "We are winning!" at -5 / +5; log min/max morale.
- Short rest: convenient menu of BP spends (list in RULES/rest.md); BP above max (overcap) shown.
- Chips/tooltips for quests, courts, stories, quirks; quirk "burn" = grey + status destroyed.
- Item/ability -> code to clipboard; PDF export (balance max only); copy character.
- Tooltip on resting in negatives: d100 90+ stabilizes.
- Weapon bonus picker: on 2nd/3rd specialist, expert, master picks hide or grey options that are no longer allowed (repeat limits, tier gate).
- Skill tier marks in work mode: normal none, advanced one star, specialized two stars (or diamond). Show only final bonus (ranks optional) outside edit/training mode.
- Skills auto-sorted by key stat; sort can be disabled or changed.
- Three modes: Play / Training / Edit (RULES/training.md).
- Exactly two UI modes: Classic and Lite (D20). No split mode. The overlay lives inside Lite and is switched on there.
- Language switch RU / EN (D4): texts from wp/i18n/ru.json and en.json; Russian only for now.
- Abilities/feats/items: field "source" and a separate field "cost".
- Quirks: a separate tab, plain list.
- "Spend comfort for training" and the attention course sit next to each other.
- Class abilities can reference professionalism level (instead of character level).
- Statuses: filter and favorite buttons.
- Pain editor (list of pain entries; turn one into a status).
- Morale scale editor.
- Crit confirmation tooltip (house-rule note): x2 -> +0, x3 -> +4, x4 -> +8.
- AC grid (package 13 H idea): show the 3x3 AC grid around the character (RULES/ac_zones.md) with the AC number in
  every cell (front / sides / back, shield side), once AC zones are built.

## Settings and layouts [OWNER, package 19: wishes, the structure exists in ARCH/settings.md]
- Classic: resize panels; put ANY parameter / ability / status / pool / skill into a cell; cells may change colour by
  thresholds and run an action on click.
- Lite: move every element; window opacity together with click-through (and a hotkey that toggles click-through);
  always on top; lock the layout; snap to a grid; per-monitor scale.
- Pictures for buttons, abilities, slots, statuses (image registry, placeholder when a file is missing).
- Quick buttons usable in both modes, with an icon, a hotkey and a macro of several commands.
- General program settings: language RU / EN, theme, scale, font size, weight units, autosave, backups,
  confirmations for dangerous actions, hotkeys, notifications, log filters, how each resource is shown (number / bar /
  both / percent), window positions, the last character, the default mode.

## Doll and AC cells (package 24 D)
- Doll, two views: "basic" (only the right and left hand) and "body" (slots drawn on a human figure picture: a
  minimal icon and the slot name in each rectangle). Hovering a slot shows the item (tooltip).
- AC cell: a big number in the centre (the primary variant) and a small second number bottom right (the secondary
  variant); or a slash list "A / B / C". Which variants and their order are settings.
- The owner will send sketches / AI pictures for the doll and the cells later; the shipped coordinates are samples.

## Classic screen v1 (package 26 D; from the owner's hand sketch and the AI reference A1-A6, files in UI/sketches/)
Every block reads ONE panel view through the Session (`session.view(panel)`, ARCH/view_contract.md) and changes the
character only with `session.dispatch(command)`; it refreshes on the topics of the result (D25).

### Layout
- Left / bottom column: identity and resources. Middle top: the always-visible strip and the cells block. Middle:
  buffs and statuses strip. Right: the switcher area (the combat block by default).
- Spacing between blocks and the gaps between cells are settings (layout profile, classic); light and dark themes.

### Identity and resources (left / bottom; views `resources`, `sheet`, `training`)
- Avatar picture: image registry target `character` (missing -> placeholder); the name (session file name) and the
  class (`sheet.class_id`, the class name from the snapshot).
- Resource FLASKS (style flask, `resources.flasks`): spirit, mana, every class pool (e.g. the owner's "darkness",
  key `pool:<id>`), segmented by 5 (app setting resource_segments). Click = the number breakdown; buttons call
  `restore` / `restore_pool` / `restore_mana`; spending is done by the actions that cost it.
- HP flask (separate, `resources.flasks.hp`, temp HP shown on top: `resources.temp_hp`): `take_damage(amount)`,
  `restore(resource="hp", amount)`.
- Balance: a VERTICAL bar with + / - buttons (`spend_balance`, `restore(resource="balance")`), the cap marker
  (`flasks.balance.cap`) and the restore per tick (`flasks.balance.restore`).
- EXP bar: `training.experience` (total, progress % of next_level_at); a button opens the experience log (newest
  first) and the level history timeline; commands `add_experience(amount, note)`, `set_next_level_at`, edit mode
  `edit_experience_entry` / `remove_experience_entry` / `edit_level_history` / `remove_level_history`.

### Always-visible strip (cells; views `sheet`, `resources`, `combat`, `training`)
- Temp HP, Pain and OT as TWO separate cells (`resources.pain`, `resources.ot`), Attention, OV, Initiative, the saves
  (Fort / Ref / Will), Speed, BAB / CMB / CMD (`sheet.stats`, `sheet.bab`, `sheet.speed`).

### Cells block (2-3 rows; number of rows, cell size and gaps are settings; layout profile `cells`, package 19)
- AC is the 3x3 ZONE GRID around the character (`defense.cells`): cell 5 = the character (avatar or an icon), every
  other cell shows the primary variant as a big number in the centre and the secondary variant as a small number
  bottom right (`defense.display`); cell 8 = the back. The four AC numbers of the early sketch (Full / Flat / Touch /
  Parry) are NOT used; the old modes are inside the grid (cell 2, 6, 8).
- Beside the grid: Initiative, Speed.
- "+" adds a custom cell (package 19 cells: source = any sheet number, a skill +x, ability or item charges, spell
  slots, OT, encumbrance, a custom counter).

### Buffs and statuses strip (view `statuses`)
- Chips: name, rounds left, charges; click = details and sources; "Add" opens the status catalog (`add_status`,
  `activate_status`, `remove_status`).

### Combat block (right, default switcher page; views `combat`, `attacks`, `maneuvers`, `items`, `spells`)
- Buttons: Start / End combat (`start_combat`, `end_combat`), Short / Long rest (`short_rest`, `long_rest`), End of
  cycle (`end_cycle`), Take damage (`take_damage`), Lose balance (`damage_to_balance` / `spend_balance`), Heal
  (`restore`), Zero initiative (`tick`), Restore mana X (`restore_mana(amount)`).
- Actions cells: current / max (`combat.actions`; more than 3 possible), tooltip = `actions.sources`; `spend_actions`,
  `restore_actions`. Reactions: `combat.reactions`, `spend_reaction`.
- Quick access: consumables (`use_consumable`), activated items and abilities with charges (`activate_item`,
  `spend_charge`), magic (`cast_spell`), attack records (`use_attack`).
- Ability icons show charges (a number in a corner), cooldown (dimmed), the hotkey (a small digit).

### Switcher (tabs) - replaces the right part together with the combat block
- Combat (the buttons above), Skills (`skills`), Feats (`sheet` for now), Race (`sheet`), Class (`sheet`; the class
  panel does not exist yet, Q177), Injuries (`injuries`), Drives / Quirks (`notebook`), Inventory / Doll (`items`:
  the item list or the doll; the doll Body view has the two hands and all 22 slots, `layout`), Training (`training`),
  Rest (`rest`), Catalogs (`catalogs`), Settings (`settings`: opens the settings menu).

### Rules of the screen
- Every number is clickable: the breakdown of its sources (the views' lines / sources data); tooltips everywhere.
- Lite mode is a separate compact overlay (A2), not this screen.

### Corrections to the AI reference (A1-A6)
- The training price unit is training points, not gp.
- Pain and OT are separate. Temp HP, Attention, OV, Initiative, saves, speed, BAB / CMB / CMD are cells of the
  always-visible strip.
- The doll Body view also has the two hands and all 22 slots.
- Ability icons: charges in a corner, cooldown dimmed, the hotkey as a small digit.
