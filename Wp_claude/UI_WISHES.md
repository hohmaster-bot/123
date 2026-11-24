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
