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
- [owner, package 32] Lite tray icon: the icon shows whether the overlay is shown or hidden and whether
  click-through is on (colour / badge), a tooltip with the state, a menu Show / Hide, Click-through on / off, Exit;
  a visible close button (x) on the overlay; a hotkey to exit (the spike: Ctrl+Alt+Q).
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

## Classic screen v2 (owner approved, package 29) - the binding spec of the UI phase
Every block reads panel views through the Session (`session.view(panel)`, ARCH/view_contract.md) and changes the
character only with `session.dispatch(command)`; it refreshes on the topics of the result (D25, D31). What the core
still lacks for each block: ARCH/ui_gaps.md.

### Wireframe (regions)
```
+--------------------------------------------------------------------------------------------+
| EXPERIENCE strip: [glass bar ======-----]  1450 xp   to next level: 2000   [Experience log] |
+-------------------+------------------------------------------+-----------------------------+
| AVATAR            | AC block (3x3)       | Parameters (3x3)  | Tabs: Combat Journal Skills  |
| (portrait,        | FL  F   FR           | Melee Ranged Init | Feats Race Class Injuries    |
|  resizable)       | SL  You SR           | CMB   CMD   Enc   | Drives Inventory Training    |
+-------------------+ BL  B   BR           | Fort  Ref   Will  | Rest Catalogs Settings  [^]  |
| HP   [=====|...]  +------------------------------------------+-----------------------------+
|  [Take dmg][Heal] | Buffs / statuses: chips  [All|Active|Fav] [Add] | COMBAT tab:            |
| Balance [===...]  +-------------------------------------------------+ [Start/End] [Short]    |
|  [Dmg to balance] | Favourites: statuses and abilities              | [Long] [End of cycle]  |
| Spirit [==..] -1+1+-------------------------------------------------+ Actions [#][#][#] R[#] |
| Mana  [===.] -1+1 | Reminders: write the taboo of Growth; take ...  | [Zero initiative]      |
|  overload - +     |                                                 | attacks list           |
| Pools (3 large,   |                                                 | quick access 4x2       |
|  rest compact,    |                                                 |                        |
|  scrolls)         |                                                 |                        |
+-------------------+-------------------------------------------------+------------------------+
| BOTTOM strip: OT 2 | Pain 1 | Morale +2 | Speed 30 | Encumbrance 40 of 59 (light)  [+ strip]  |
|               [Journal]                                                                     |
+--------------------------------------------------------------------------------------------+
```

### 1. Regions
- A full-width EXPERIENCE strip at the top: a glass bar, the current experience, the "to next level" goal, the
  button "Experience log". Left column: the avatar, then the resources. Middle: TWO blocks on one row (the AC block
  and the Parameters block), then buffs / statuses. Right column: the tabs and the combat tab. A full-width BOTTOM
  strip. No background illustration by default (an optional own background picture: point 16). Three shipped
  themes: dark (the default), light, grey-blue (point 16).

### 2. Avatar
- A portrait only, its own block, resizable (small to large). A frame colour by the character state may be added
  later as a setting.

### 3. Resources (under the avatar, top to bottom: HP, balance, spirit, mana, class pools)
- Each: a label (with an optional coloured chip, e.g. the caster overload next to mana), the value text, a HORIZONTAL
  glass tube with liquid, a highlight and segments (app setting resource_segments, 5 or 10), buttons under it.
- Style glass or flat is a setting; changing the style never changes size, position or logic. The size is set
  separately in width and height. Auto-switch big glass -> medium -> a thin bar with the number inside when space is
  short (can be disabled).
- Colours are settings; defaults: HP red, balance muted orange, spirit teal, mana blue, class pools their own
  colours, the overload chip magenta.

### 4. Click on a tube = the value EDITOR (a correction, no game mechanics)
- "+N" adds, "-N" subtracts, a plain number replaces. For HP the popup has a second field for temporary HP.
- Negative values are refused (HP excepted), as in the rules.
- Game mechanics are BUTTONS: HP "Take damage", "Heal"; balance "Damage to balance" (they can cause pain); no separate
  + / - or "restore" buttons for them. Pools, spirit and mana get small "-1" / "+1" buttons; mana also has overload
  "-" / "+".
- The player may add custom buttons ("write off X", "add X", a macro) under any resource.

### 5. Temporary HP
- A thin grey / silver strip along the bottom third of the HP tube, filling left to right, segmented by 5 points; it
  may be longer than the HP fill.

### 6. Class pools
- Unlimited. The first three are drawn large (the player chooses which), the rest compact; the pool list scrolls on
  its own.

### 7. Middle row 1: two separate blocks on one level and one top line
- (a) AC block: the 3x3 zone grid, labels front-left / front / front-right / side left / "You" / side right /
  back-left / back / back-right; the shield side highlighted with an icon; each zone a big main number and a small
  second number; every number clickable (its sources).
- (b) Parameters block, 3x3 cells in this order: melee attack, ranged attack, initiative; CMB, CMD, encumbrance;
  Fortitude, Reflex, Will. The encumbrance cell shows "40 of X" and the category in small type under it and must fit
  the square. Categories by RULES/gear.md "Weight": light, heavy, and above heavy the encumbrance state (overload,
  "drag only or drop something"); see Q197.
- Both are cell blocks: the player can change which number every cell shows (any sheet number, skill, pool, counter),
  its colour thresholds and its click action.

### 8. Middle row 2
- Buffs and statuses: chips (name, note, rounds, charges); filters All / Active / Favorites; Add.
- Then a favourites row (favourite statuses and abilities), then a reminders row (e.g. a drive principle missing, a
  quest needed).

### 9. Right column
- Tab bar: Combat, Journal, Skills, Feats, Race, Class, Injuries, Drives, Inventory, Training, Rest, Catalogs,
  Settings. An "expand to full screen" button for Skills, Inventory, Doll, Training, Catalogs: expanding hides the
  other regions temporarily and NEVER rewrites the saved profile; closing returns the previous layout and state.
- Combat tab: Start / End combat, Short rest, Long rest, End of cycle; ACTIONS are squares of ONE colour (a theme
  token, the same for every action), each square NUMBERED 1, 2, 3 ... (with more than 3 actions every square keeps
  its own number); spending takes the squares from the SMALLEST number first; a spent square is greyed out. The
  REACTION is a square of the same style (numbered the same way if there are several). "Zero initiative"; the
  attack list; the quick access grid (default 8 cells, 4-16, the
  number of columns is a setting): a cell = name, icon, charges in a corner, dimmed on cooldown, the hotkey digit.

### 10. Bottom strip (full width, like the experience strip)
- OT, Pain, Morale (scale), Speed, Encumbrance as "40 of X (light)" with the limits (light up to, heavy up to). Its
  content is editable (any numbers, any order). A button "+ strip" adds a second optional strip (spell slots / quick
  access). A "Journal" button opens the journal as a tab of the right column (not a separate window).

### 11. Number hierarchy and sizes
- Critical numbers large (HP, AC, balance, initiative), working numbers medium, reference numbers by click / hover
  with the source breakdown. Minimum font 11 px at 100% scale.
- Sizes (px at 100%, orientation only): avatar 90-180, HP flask 150x300 recommended, other flasks 110x230, parameter
  card 100x85, quick cell 130x100, AC cell 110x110.

### 12. Small window
- Order: shrink the gaps, then the secondary captions, then the optional details, then the compact mode of blocks,
  scroll LAST. Data are never deleted; a mark shows that something is temporarily hidden and the player can open it.
  Adaptation never overwrites the saved layout.

### 13. Layout
- Classic = columns and cells with grid snap; the user resizes blocks; several saved profiles. Free placement without
  a grid only in Lite. Editor mode shows borders, names and resize handles.
- Validation WARNS (a block under its minimum, all HP controls hidden, a block outside the window) but never forbids;
  a "restore the default profile" action always exists.

### 13a. "!" notes (owner, package 38, decision 8)
- In the layout editor the owner places a note anywhere the editor places widgets (a block of the layout, the bottom
  strip, a tab) and writes its text himself; it shows as a "!" mark in the corner, the text on hover and on click.
  Add / edit the text / move / delete in the editor's notes part. Stored with the layout profile (UI settings, not in
  the character); a layout reset keeps them. Colours: theme tokens (warning, accent_text). A tab note shows while
  its tab is open.

### 14. One-time hints
- Every explanatory hint ("how to use this", first-run tips, a how-to picture) is shown once and stays until the
  player ticks "Understood!" ("Понятно!"). The per-hint state is stored in the app settings (a list of hint ids);
  there is a "show all hints again" action and a switch "hints off". Texts live in i18n.

### 15. Architecture rules (D31)
- Data and display are independent (one resource may be a large flask, a small flask or a flat bar: different views
  of the same data). Layout and content are independent (the resources block gets a list and draws it by settings).
  Adaptation to a small window changes the presentation, never the saved layout. Classic never changes the character
  except through Session commands.

### 16. Themes and background (owner, package 29 amendment)
- Three shipped themes: DARK (the default for a new profile), LIGHT (a soft light with a non-pure-white background,
  never pure white) and GREY-BLUE (a low-contrast calm theme for players with eye strain).
- Own themes: every colour of the screen is a theme token (ARCH/themes.md, wp/theme), editable in the settings with
  a live preview; actions "copy theme" and "reset to the shipped one".
- An optional OWN BACKGROUND picture (from the image registry) with a dimming / opacity slider and a "keep numbers
  readable" overlay behind the panels; default: no background picture.
- A follow-the-system option for light / dark.
- A theme WARNS (never forbids) when the main number colour against its background is below 4.5:1.
- Theme tokens too: the resource colours (HP, balance, spirit, mana, class pools, overload chip), the status chip
  colours, the cell threshold colours, the action square colours. The glass tube colours (liquid, glass, highlight)
  must read in all three themes.

### Corrections (kept from v1; the AI reference A1-A6 is historical)
- The training price unit is training points, not gp.
- Pain and OT are separate. Temp HP, Attention, OV, Initiative, saves, speed, BAB / CMB / CMD are cells of the
  always-visible strip.
- The doll Body view also has the two hands and all 22 slots.
- Ability icons: charges in a corner, cooldown dimmed, the hotkey as a small digit.
- [owner, package 27] Temporary HP in the flask: a grey strip at the bottom of the flask that may be longer than the
  HP, or a silver fill right after the red HP; the choice is a setting of the bar.
