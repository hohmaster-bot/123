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
- Numbers in RULES/ are tests. Never change RULES/ without the owner's consent.
- UI wishes go only to `Wp_claude/UI_WISHES.md`, never into RULES/.
- `character.schema.json` is the only data contract. Do not duplicate field lists in docs.
- Do not claim tests ran unless you ran them in this session.

## Read only what the task needs
| Task | Read |
|---|---|
| any | this file + `Wp_claude/GOTCHAS.md` |
| game mechanics | `Wp_claude/RULES/index.md` + one domain file |
| effects, buffs, durations, charges | `RULES/buffs.md` |
| AC, typed bonuses, morale / attacks, crit, maneuvers | `RULES/defense.md` / `RULES/combat.md` |
| HP, balance, pain, mana, overload, comfort | `RULES/resources.md` |
| rest, BP / injuries, OT | `RULES/rest.md` / `RULES/injuries.md` |
| classes, spells cost / gear, weight, base, items | `RULES/classes_magic.md` / `RULES/gear.md` |
| training, skills, weapon mastery | `RULES/progression.md`, `RULES/skills.md`, `RULES/weapons.md` |
| quirks, courts, lenses / catalogs | `RULES/narrative.md` / `RULES/catalog.md` |
| UI design | `Wp_claude/UI_WISHES.md` + `Wp_claude/ARCH/surfaces.md` |
| architecture, new module | `Wp_claude/ARCH/decisions.md` + topic file in `Wp_claude/ARCH/` |
| known code vs rules gaps | `Wp_claude/tests/BASELINE_REPORT.md` |
| unresolved choices | `Wp_claude/OPEN_QUESTIONS.md` |
| what to do next | `Wp_claude/ROADMAP.md` |

Never load `AUDIT.md` or old docs whole; search by finding id (`A0xx`).

## Testing
Anything with numbers or state (formulas, effects, ticks, rest, purchases, save/load) gets a test.
Visual and UX checks are done by the owner by hand.
Test commands (each exits 1 on any failure, no pytest needed):
- legacy baseline: `python Wp_claude/tests/test_rules_baseline.py` (known failures in BASELINE_REPORT.md)
- new core `wp/core/`: `python Wp_claude/tests/core/test_derived.py`, `python Wp_claude/tests/core/test_damage.py`,
  `python Wp_claude/tests/core/test_rest.py`, `python Wp_claude/tests/core/test_magic.py`,
  `python Wp_claude/tests/core/test_injuries.py`, `python Wp_claude/tests/core/test_bonuses.py`,
  `python Wp_claude/tests/core/test_ac.py`, `python Wp_claude/tests/core/test_skills.py`,
  `python Wp_claude/tests/core/test_weapons.py`, `python Wp_claude/tests/core/test_training.py`,
  `python Wp_claude/tests/core/test_combat.py`, `python Wp_claude/tests/core/test_effects.py`,
  `python Wp_claude/tests/core/test_pain.py`, `python Wp_claude/tests/core/test_tick.py`,
  `python Wp_claude/tests/core/test_statuses.py` (status in CORE_REPORT.md)
- model + commands: `python Wp_claude/tests/model/test_scenarios.py`, `python Wp_claude/tests/model/test_view.py`,
  `python Wp_claude/tests/model/test_commands2.py`, `python Wp_claude/tests/model/test_skills_catalog.py`
  (status in MODEL_REPORT.md)
- storage: `python Wp_claude/tests/storage/test_character_io.py`; module size: `python Wp_claude/tests/test_module_size.py`
