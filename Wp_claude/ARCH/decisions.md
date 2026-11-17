# Decisions
Status: A = accepted by owner, P = proposed (needs owner OK), X = superseded.

| id | status | decision | why |
|---|---|---|---|
| D1 | A | No save migrations, ever. New format may break old saves. Old characters are not carried over; create new ones. | Owner, 2026-11-17. Simplicity. |
| D2 | A | UI toolkit: PySide6. | LGPL; overlay prototypes already on PySide6; Qt has tray, frameless, opacity built in. |
| D3 | A | Two exclusive modes: Classic (full-screen sheet, Alt-Tab/hotkey) and Overlay (light, always-on-top panels). Never shown together: enabling one disables the other. Each has its own independent settings. Both have an edit mode that works differently. Split removed. | Owner, 2026-11-17. See `surfaces.md`. |
| D4 | A | i18n: every UI string in locale files; code is ASCII only. | Owner. RU/EN switch; PowerShell can no longer corrupt code. |
| D5 | A | Commands are the only mutation path: UI -> `dispatch(cmd)` -> validate -> mutate -> action_log -> `changed` signal. Resources get two ops: `restore` (gameplay: regen, heal, rest, tick; clamps to max) and `set` (manual/overfill; no clamp, flagged "over max"). Exceeding max is allowed (RULES/resources.md "Over max"). | One place for bounds, transactions, undo, refresh (A053, A059). |
| D6 | A | Store base values only; derived values computed on read. | A087 (max inflation), legacy display fields. |
| D7 | A | Stable ids for every entity (feats, spells, courts, buffs, chips...); no references by display name. | A045, A046, A088; renames orphan chip order/colors. |
| D8 | A | Docs for Claude in English; owner-facing docs in Russian. | Cyrillic costs noticeably more tokens. |
| D9 | A | Split core into domain modules; step 1 = mixins (`c.method()` calls unchanged), protected by tests. | Smaller files to read; no big-bang rewrite. |
| D10 | A | All new docs live in `Wp_claude/`; old docs go to `Wp_claude/archive/` later. | Owner. |
| D11 | A | One persistence service: validate, atomic temp+replace write, keep last good copy. | A063, A064, A065, A079. |
| D12 | A | Logic before UI. Exception: an early technical overlay spike (click-through, hotkey). | Owner; spike de-risks D3. |
| D13 | A | Three settings domains: character gameplay (in save), catalogs, UI profile (per user, not per character). Enabled catalogs: one list for the user (global). | A005, A014, A017; RULES/catalog.md. |
| D14 | A | One generic effect system for every sheet part (race, class, feat, item, injury, quirk, spell, buff): any effect can change any base parameter, with duration, condition, charges. | RULES/buffs.md, RULES/index.md "Cross-cutting". |
| D15 | A | Damage pipeline per damage component (by type): 1) percent reduction (25/50/75 %), 2) flat reduction by damage type (DR = flat vs PHYSICAL; fire etc. are other types), 3) temp HP, 4) temp-HP analogs (e.g. race mana) in a configurable order, 5) HP + balance (only the part reaching HP). Integer damage, round UP. | RULES/resources.md "Damage pipeline"; classes_magic.md "Racial damage absorbers". |
| D16 | A | Weapon stores a list of parents (variety, group; a variety may sit in several groups). Combat basics bonus = max over the weapon and its ancestors, never a sum. | RULES/weapons.md "Combat basics"; baseline WPN-basics-nostack. |
| D17 | A | Item has two tabs of effects: "not activated" and "activated". Exactly one set acts, never both; no mode flag (an additive item repeats base effects in the activated tab). | RULES/gear.md "Item activation data"; baseline GEAR-item-tabs. |
| D18 | A | Pain from HP and all other derived values are computed on read, never stored. | RULES/resources.md "Pain"; D6. |
| D19 | A | Skill tiers normal / advanced / specialized are data; all prices come from the formulas in RULES/skills.md. | RULES/skills.md; avoids hard-coded tier logic. |
