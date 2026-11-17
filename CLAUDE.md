# WIPEFINDER - instructions for Claude

Character sheet + desktop overlay for a homebrew PF1-based TTRPG. Python 3, Windows.
Owner is not a programmer: reply in Russian, plain words, one question at a time with a recommendation.

## Status
Branch `Rework`: architecture rework before the Qt (PySide6) UI. Current phase: `Wp_claude/ROADMAP.md`.
Legacy tkinter code at repo root is reference only until replaced. Do not edit `main`.

## Hard rules
- No save migrations, ever. Never write migration or legacy-conversion code.
- Code files are ASCII only. All UI text lives in locale files (`wp/i18n/*.json`).
- UI never mutates the character directly; only through commands (`Wp_claude/ARCH/decisions.md` D5).
- Store base values only; derived values are computed on read, never written back.
- Game rules live in `Wp_claude/RULES/`. If code and RULES disagree, ask the owner; do not guess.
- `character.schema.json` is the only data contract. Do not duplicate field lists in docs.
- Do not claim tests ran unless you ran them in this session.

## Read only what the task needs
| Task | Read |
|---|---|
| any | this file + `Wp_claude/GOTCHAS.md` |
| game mechanics | `Wp_claude/RULES/index.md` + one domain file |
| architecture, new module | `Wp_claude/ARCH/decisions.md` + topic file in `Wp_claude/ARCH/` |
| unresolved choices | `Wp_claude/OPEN_QUESTIONS.md` |
| what to do next | `Wp_claude/ROADMAP.md` |

Never load `AUDIT.md` or old docs whole; search by finding id (`A0xx`).

## Testing
Anything with numbers or state (formulas, effects, ticks, rest, purchases, save/load) gets a test.
Visual and UX checks are done by the owner by hand.
Test command: TBD (legacy `_check.py` reports OK even on failure, see GOTCHAS).
