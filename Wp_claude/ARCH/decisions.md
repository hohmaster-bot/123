# Decisions
Status: A = accepted by owner, P = proposed (needs owner OK), X = superseded.

| id | status | decision | why |
|---|---|---|---|
| D1 | A | No save migrations, ever. New format may break old saves. | Owner, 2026-11-17. Simplicity. |
| D2 | P | UI toolkit: PySide6. | LGPL; overlay prototypes already on PySide6; Qt has tray, frameless, opacity built in. |
| D3 | A | Two exclusive modes: Classic (full-screen sheet, Alt-Tab/hotkey) and Overlay (light, always-on-top panels). Never shown together: enabling one disables the other. Each has its own independent settings. Both have an edit mode that works differently. Split removed. | Owner, 2026-11-17. See `surfaces.md`. |
| D4 | A | i18n: every UI string in locale files; code is ASCII only. | Owner. RU/EN switch; PowerShell can no longer corrupt code. |
| D5 | P | Commands are the only mutation path: UI -> `dispatch(cmd)` -> validate -> mutate -> action_log -> `changed` signal. | One place for bounds, transactions, undo, refresh (A053, A054, A059). |
| D6 | P | Store base values only; derived values computed on read. | A087 (max inflation), legacy display fields. |
| D7 | P | Stable ids for every entity (feats, spells, courts, buffs, chips...); no references by display name. | A045, A046, A088; renames orphan chip order/colors. |
| D8 | P | Docs for Claude in English; owner-facing docs in Russian. | Cyrillic costs noticeably more tokens. |
| D9 | P | Split core into domain modules; step 1 = mixins (`c.method()` calls unchanged), protected by tests. | Smaller files to read; no big-bang rewrite. |
| D10 | A | All new docs live in `Wp_claude/`; old docs go to `Wp_claude/archive/` later. | Owner. |
| D11 | P | One persistence service: validate, atomic temp+replace write, keep last good copy. | A063, A064, A065, A079. |
| D12 | A | Logic before UI. Exception: an early technical overlay spike (click-through, hotkey). | Owner; spike de-risks D3. |
| D13 | P | Three settings domains: character gameplay (in save), catalogs, UI profile (per user, not per character). | A005, A014, A017. Catalog scope: OPEN_QUESTIONS Q7. |
