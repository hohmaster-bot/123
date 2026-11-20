# WIPEFINDER - instructions for Claude

Goal: a correct, fully tested rules core for the WipeFinder character sheet, then a Qt (PySide6) sheet and overlay.
Character sheet + desktop overlay for a homebrew PF1-based TTRPG. Python 3, Windows.
Owner is not a programmer: reply in Russian, plain words, one question at a time with a recommendation.

## Status
Branch `Rework`: architecture rework before the Qt UI. Where we are now: `Wp_claude/STATUS.md` (read it first).
Plan: `Wp_claude/ROADMAP.md`. Legacy tkinter code at repo root is reference only until replaced. Do not edit `main`.

## Hard rules
- No save migrations, ever. Never write migration or legacy-conversion code.
- Code files are ASCII only. All UI text lives in locale files (`wp/i18n/*.json`).
- UI never mutates the character directly; only through commands (`Wp_claude/ARCH/decisions.md` D5).
- Store base values only; derived values are computed on read, never written back.
- Game rules live in `Wp_claude/RULES/`. If code and RULES disagree, ask the owner; do not guess.
- Numbers in RULES/ are tests. Never change RULES/ without the owner's consent.
- UI wishes go only to `Wp_claude/UI_WISHES.md`, never into RULES/.
- The data contract is the storage dataclasses: `wp/storage/character_io.py` and the types it registers
  (`wp/model/character.py`, `wp/core/*`). Do not duplicate field lists in docs.
- Do not claim tests ran unless you ran them in this session.
- Branch Rework only. Never run commands that could discard uncommitted work.
- Anything not stated by the owner and not in RULES: do NOT choose silently and do not invent formulas;
  put it in OPEN_QUESTIONS.md (new id) and in the report.
- Every new rule constant or switch goes into data (Character.rules_settings / constants tables), not literals.

## Read only what the task needs
| Task | Read |
|---|---|
| any | this file + `Wp_claude/STATUS.md` + `Wp_claude/GOTCHAS.md` |
| game mechanics | `Wp_claude/RULES/index.md` (Sections block) + one domain file |
| effects, buffs, durations, charges | `RULES/buffs.md` |
| AC, typed bonuses, morale / attacks, crit, maneuvers | `RULES/defense.md` / `RULES/combat.md` |
| AC ladder (which layer a roll hit) | `RULES/defense_layers.md` |
| HP, balance, pain, mana, overload, comfort | `RULES/resources.md` |
| rest, BP / injuries, OT | `RULES/rest.md` / `RULES/injuries.md` |
| classes, spells cost / gear, weight, base, items | `RULES/classes_magic.md` / `RULES/gear.md` |
| training, skills, weapon mastery | `RULES/progression.md`, `RULES/skills.md`, `RULES/weapons.md` |
| quirks, courts, lenses / catalogs | `RULES/narrative.md` / `RULES/catalog.md` |
| UI design | `Wp_claude/UI_WISHES.md` + `Wp_claude/ARCH/surfaces.md` |
| architecture, new module | `Wp_claude/ARCH/decisions.md` + topic file in `Wp_claude/ARCH/` |
| known code vs rules gaps | `Wp_claude/tests/BASELINE_REPORT.md` |
| unresolved choices / closed ones | `Wp_claude/OPEN_QUESTIONS.md` / `Wp_claude/ARCH/decision_log.md` |
| what to do next / finished packages | `Wp_claude/ROADMAP.md` / `Wp_claude/ARCH/history.md` |

Reading rules:
- Big files: search by heading (`grep -n "^#"`) or by id, then read only that section.
- Never load `AUDIT.md` or old docs whole; search by finding id (`A0xx`).
- Of the package reports read only the LAST `Wp_claude/tests/PACKAGE*_REPORT.md`.
- `RULES/skills_list.md` only for catalog work.
- Do not re-read a file you just wrote or edited.

## Testing
Anything with numbers or state (formulas, effects, ticks, rest, purchases, save/load) gets a test.
Expected numbers are computed by hand from RULES, never copied from the code's output.
Visual and UX checks are done by the owner by hand.
- All suites of the new code: `python Wp_claude/tests/run_all.py` (one summary line, exit 1 on any failure).
- Break check: `python Wp_claude/tests/break_check.py [id-prefix]` breaks each rule in `Wp_claude/tests/breaks/*.py`
  on a temp copy and confirms a test fails (the working tree is never touched).
- The legacy baseline is run separately: `python Wp_claude/tests/test_rules_baseline.py` (known failures in BASELINE_REPORT.md).

## Standard package procedure
1. Start: read STATUS.md, the package text, the RULES sections it names; `git status` must be clean or understood.
2. Code: ASCII only, modules <= 500 lines (split before a file gets near it), commands are the only mutation path,
   base values stored / derived on read, ids made by the program, line endings of edited files unchanged.
3. Tests: numeric tests for every rule (numbers by hand); add a break_check entry for every new rule;
   `run_all.py` shows 0 failures and `break_check.py` shows all caught.
4. Docs: RULES only with the owner's consent (the package text is consent for what it asks); new questions to
   OPEN_QUESTIONS.md; closed ones to the END of ARCH/decision_log.md; one line to ARCH/history.md; update STATUS.md.
5. Commits: logical commits on Rework (code, tests, docs, report), then `git push origin Rework`.
6. Report `Wp_claude/tests/PACKAGE<N>_REPORT.md`, fixed sections:
   Done / Tests and breaks (run_all and break_check lines) / Changes to old rules / Assumptions / Open questions (ids).
7. Final chat message: Russian, at most 15 lines: what is done, test lines, what changed for the player,
   then ONE question with a recommendation.
