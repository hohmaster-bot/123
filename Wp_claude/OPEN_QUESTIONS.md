# Open questions
Format: id | question | recommendation | status. Owner answers; Claude records the result in RULES/ or ARCH/decisions.md.

## Game rules (owner decides)
- Q1 | Injury effects: apply passively while the injury exists, or only after manual activation? (A016) | ? | open
- Q2 | `enabled = false` on feat/injury/buff: ignored in all calculations, cannot be activated, still visible? (A015, A028) | ignored everywhere, cannot activate, stays visible | open
- Q3 | Stance: which fields are canon - `stance_effects/stance_blocks` or `effects/blocks` + `is_stance`? (A027) | `effects/blocks` + `is_stance` | open
- Q4 | `tick_mode` values and meaning per entity (none/restore/decrease/spend/initiative?) (A031, A032) | ? | open
- Q5 | Spells: description only, or mechanically applied effects? (A033) | ? | open
- Q6 | Shop: can feats/spells/skills be bought there, or items only? (A069) | items only | open

## Architecture (owner confirms)
- Q7 | Catalog enable/disable lists: per character or global for the user? (D13) | global | open
- Q8 | Old characters will not open in v1.0 (D1). Any you want to recreate by hand? | - | open
- Q9 | Default global hotkey for the Sheet? | Ctrl+Shift+W | open
- Q10 | Approve proposed decisions D2, D5-D9, D11, D13. | approve | open
- Q11 | Overlay needs a full editor (e.g. edit a feat): switch to Classic automatically, or open a small editor window above the overlay? | small editor window | open
