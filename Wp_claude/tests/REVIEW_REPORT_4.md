# Independent review 4: the whole core (rules vs code, architecture, tests, UI readiness)

Date: 2026-11-20. Branch `Rework`, HEAD `51d25c0` (package H merged: `run_all.py`, `break_check.py`, `STATUS.md`
exist). Nothing in `wp/`, `RULES/` or other docs was changed by this review. New files: this report and the scripts in
`Wp_claude/tests/review4/` (ASCII). Severity: **breaks rule** (the code does something the RULES or the owner's
principles forbid), **missing** (a RULES / principle requirement with no code at all), **ambiguous** (RULES unclear or
the code decided alone), **cosmetic**.

Read: CLAUDE.md, STATUS.md, GOTCHAS.md, RULES/index.md and every RULES file (skills_list.md: header only;
training_costs_draft.md: not read, it is marked "replaced"), ARCH/decisions.md, ARCH/surfaces.md, UI_WISHES.md,
OPEN_QUESTIONS.md; then the code of `wp/` (commands and views fully, core modules where a rule is computed).

What ran in this session (all results below are from these runs):
- `python Wp_claude/tests/run_all.py`: suites 41, passed 41, failed 0.
- `python Wp_claude/tests/break_check.py`: entries 43, caught 43, missed 0.
- `review4/probe_rules.py`: 87 probes of RULES examples and normative sentences through the REAL commands.
- `review4/run_breaks.py`: 60 of my own breaks, each against the WHOLE test set (run_all) on a temp copy.
- `review4/fuzz.py 300 50 1`: 300 seeded sequences x 50 random valid commands = 15 000 steps.
- `review4/behavior.py`, `review4/test_quality.py`, `review4/hardcoded.py`.

## Findings ranked by severity

| # | Severity | Finding | Where |
|---|---|---|---|
| F1 | breaks rule | Ability scores ignore effects: a status "+4 Str" (effect target `str`) does not change the Str score or modifier, so nothing derived from stats reacts to buffs (attack, damage, skills, AC Dex, saves, HP, carrying). buffs.md:6-7 uses exactly this example. | `wp/model/derived_view.py:31-41` (`ability_current` = stored score only) |
| F2 | breaks rule (owner principle) | Many sheet numbers have NO effect target, only hand-typed base fields: max HP, BP max, balance max, balance regen, spirit max, mana max, slots, comfort max, parry, max Dex, DR / resistances, carrying capacity, pain death cap, crit multiplier, spell cost / overload, reactions, base slots (table in section 1b). | `derived_view.py:55-305`, `combat_cmds.py:22-29` |
| F3 | missing (UI blocker) | The command set cannot build or edit a character: no `add_item` / `edit_item`, no command for the morale scale, pain entries (add / remove / turn into a status), the negative-HP state choice, BAB, base saves, ability base / race / bonuses (edit mode, training.md:8), caster type, mana max, slots, drives, rules_settings, weapon mastery nodes and mastery picks (`validate_picks` is never called), injury effects (`add_injury` takes no effects). Commands are the only mutation path (D5), so the UI cannot do these at all. | `wp/commands/*` (89 commands listed in section 6) |
| F4 | breaks rule (D4) | Refusals are English sentences inside `CommandError`; there is no reason id. The UI cannot translate them (all UI text must be in locale files) and cannot react by kind. Views already use reason ids; commands do not. `wp/i18n/` does not exist. | every `raise CommandError("...")` |
| F5 | breaks rule | `cast_spell(circle=10)` raises a raw `IndexError` (not a `CommandError`): `CIRCLE_MANA[10]` is read before the circle range check. The dispatch contract (validation error = `CommandError`, state unchanged) is broken; a UI would crash. | `combat_cmds.py:62` (`mg.circle_mana(circle)`), `core/magic.py` |
| F6 | breaks rule | `remove_item` removes the item's attack records but leaves another record's `twf_off` pointing at a removed record: that two-weapon record is shown as AVAILABLE with nothing missing, and `twf.combination` raises `KeyError`. | `item_cmds.py:79-84`, `records.required_items`, `twf.py` |
| F7 | breaks rule (minor) | The journal logs commands that changed nothing (resources.md:180 "nothing changed ... not logged"). Found by fuzz, shortest sequences of 1-3 steps: take_damage 0, damage_to_balance 0, pay_hp_cost 0, spend_balance 0, spend_bp 0, spend_pool 0, restore 0 / at max, restore_pool at max, set_temp_hp same value, set_status_duration 0 on an inactive status, set_active_stance same stance, damage_item 0, hit_item with 0 notches, tick with nothing to do, long_rest twice, short_rest with nothing to gain, resolve_spell_failure (no failure / cancel). | `commands/base.py:61` (logs whenever `CHANGED` is in events) |
| F8 | ambiguous | `long_rest` is accepted DURING combat and keeps the combat state (in_combat, round, cap snapshot, running statuses keep their time, a currently active rage gets its charges back). RULES do not say whether a long rest ends combat or is refused in combat. New question. | `resource_cmds.py:104-117` |
| F9 | missing | Iterative attacks (combat.md:6-10: 2nd attack-tagged option -5, 3rd -10, "ignores iterative" flag): only `wp/core/combat.py` has it; no command, no view, no turn counter. | `core/combat.py`; `attack_view.py` |
| F10 | missing | DR / resistance / percent reduction "come from the sheet's effects" (resources.md:41-42, docstring of `damage.Reductions`), but nothing derives them: `take_damage` only uses a `reductions` argument typed by the caller. An effect "DR 3 physical" does nothing (probe: 10 damage -> HP -10). | `core/damage.py:62`, `combat_cmds.py:22` |
| F11 | missing | Doll slots (doll.md:5 "each slot holds ONE item"): any number of items can be worn (two armors at once accepted; the larger armor bonus counts). | `item_cmds.equip_item` |
| F12 | missing | Narrative entities have no model or command: lens counter with 0..X clamp (narrative.md:108-114, numeric example), courts (level / tier), quests, quirks (seeds exist, quirk fields do not), stories, "morale X higher" (defense.md:45). | `wp/model/character.py` |
| F13 | ambiguous | combat.md:14 "weapon mastery can widen range by 2 (20 -> 18)" vs the "crit +1" pick (20 -> 19); weapons.md:96 notes the conflict, but it is NOT in OPEN_QUESTIONS. | RULES only |
| F14 | ambiguous (architecture) | Load-time legacy handling exists although CLAUDE.md says "never write migration or legacy-conversion code": 10 dropped fields, 2 skipped record kinds (item-bound maneuvers, by-name item charges), injury ids assigned on load. Every one was asked for by the owner in a package text, so this is a wording conflict to settle, not a hidden migration. | `storage/character_io.py:36-51, 126` |
| F15 | breaks rule (owner principle) | Rule constants are code, not data: 94 module-level numeric constants and 62 inline rule literals in `wp/` (e.g. `skills.py:77` 40 / 20, `skills.py:82` 200 / 50, `weapons.py` 30 / 5 / 30 / 70, `training.py` 24 constants, `derived.py` 10). `RulesSettings` holds 8 switches. | `review4/hardcoded.py` output (section 2) |
| F16 | ambiguous (D5) | `Character` is frozen but holds mutable dicts (`abilities`, `slots`, `resources`, `drives`, `save_base`, `save_stats`; `Status.per_tick_restore`, `Maneuver.extra`): UI code can change state in place without a command and without a journal entry. | `model/character.py` |
| F17 | ambiguous | Resource pools are read CLAMPED to their max, while resources.md "Over max" says ANY resource may exceed max (manual set must not be clamped). `edit_pool(current=...)` above max is stored but never shown. | `model/pool_view.py:14` |
| F18 | cosmetic | A command may still be given an id by the caller (`add_attack(rid=...)`, `add_status(status.sid=...)`); D7 says the program makes ids. Not wrong while the UI never passes one. | `attack_cmds.py`, `combat_cmds.py` |

Counts: breaks rule 7 (F1, F2, F4, F5, F6, F7, F15), missing 5 (F3, F9, F10, F11, F12), ambiguous 5 (F8, F13, F14,
F16, F17), cosmetic 1 (F18), plus 10 docs items (section 7, all cosmetic or stale text) and the test-quality notes.

### Known planned gaps (listed by the owner, NOT counted as defects)
- Extra hit dice from sources with Con per die and min 1 per die: the code still uses sum of rolls + Con * level.
- Status charges restored without a source (Q108): confirmed by running: a plain status with charges 0/2 goes to 2/2
  on the long rest (`behavior.py`).
- Attention options 2 and 4 have no command (Q110); comfort-rate bonus (Q107) has no field.
- AC zones by cell (ac_zones.md, draft).
- Phase 3 remainder: settings domains, `wp/i18n` files, theme, panel registry; UI.

## 1. Rules vs code

Method: `review4/probe_rules.py` builds small characters and runs the REAL commands (dispatch) for every numeric
example and the main normative sentences of resources, buffs, combat, defense, defense_layers, rest, injuries, stats,
gear, training, skills, weapons, progression, narrative, classes_magic. Expected values were written by hand from the
RULES text (three of my own first guesses were wrong and are corrected in the script: the aura payment order, Str in
the size example, and an injury probe that forgot an injury needs OT). 87 probes: 75 match, 12 do not.

| Rule (file:line) | Code | Expected | Actual | Severity |
|---|---|---|---|---|
| buffs.md:6-7 "+4 Str for 8 rounds" | `derived_view.ability_current` | Str mod 0 -> +2 | 0 | breaks rule (F1) |
| buffs.md:5 "resources (max ...)" | `derived_view.hp_max` | status +5 to max HP -> 25 | 20 | breaks rule (F2) |
| buffs.md:5 "resources (... regen ...)" | `derived_view.balance_regen` | +2 -> 3 | 1 | breaks rule (F2) |
| resources.md:41-42 DR from the sheet's effects | `take_damage(reductions=...)` | 10 - DR 3 -> HP 13 | 10 | missing (F10) |
| resources.md:180 journal skips no-ops | `commands/base.dispatch` | 0 entries | 1 entry (3 probes) | breaks rule, minor (F7) |
| combat.md:8 iterative -5 / -10 | only `core/combat.py` | exposed in a view | no view / command | missing (F9) |
| combat.md:14 mastery widens by 2 | `weapons.crit_threshold` | 18 with one pick? | 19 | ambiguous (F13) |
| doll.md:5 one item per slot | `equip_item` | second armor refused | accepted | missing (F11) |
| narrative.md:113-114 lens 1/15, clamp | none | a lens model | none | missing (F12) |
| robustness of cast_spell | `combat_cmds.cast_spell` | `CommandError` for circle 10 | `IndexError` | breaks rule (F5) |

Matching (75), all through commands: temp HP order (resources.md:7), percent round up (:28), fire 50% + flat 2 (:29),
the overflow example 10/1/1 (:39-40), cap snapshot sequence (:48), 6/6 -> 1/5 (:54), pay_hp_cost (:61),
damage_to_balance (:67), temp pain 0/0/1/2/4 (:84), state cleared at HP >= 0 (:86), dying -2 per tick (:93), bleed 3
hits (:109), overload 1 blocks one regen (:111), spirit 15/0/18/0 (:120-122), mage 3 mana -3/-3/+2 and slots +4
(:129-130), pool restores on long rest (:157), ignore_pain (:172); stat_mod to Intimidation (buffs.md:36), 3-tick
status (:74), activation refusals (:61), aura 3 rounds = 3 Ki and the 1-round case (:130), rage formula pool 13/11
(:154), block dodge (:115); crit 19/18/17 (combat.md:18), Str by grip (:42), TWF table (:50), size table (:135),
speed (:136), CMB per record 7/4/4 (:142), Me Liquescit (:165), unarmed maneuver refused with a sword (:84); Dex -2
AC 8/8 (defense.md:11), saves 5/2/1 (:37), initiative 4/5/4 (:41), morale +1/-2/0 (:53), ladder base 8 / just
barely 16 (defense_layers.md:28), parry 8/9/6 (defense.md:12); BP caps (rest.md:6), balance example 6 (:9), overcap
5/6/5/5 (:17), long rest keeps OT, comfort, temp HP (:27-34), short rest example 6/11/5 (:55), status charges by the
short rest (:44); injuries 2/5/12, comfort 3, attention 3, ids cut_4, RL 5 (injuries.md); stat damage 17/18 -> 18/18
(stats.md:9); weights 115/85, thresholds, slowdown 15/18/5, item HP 13/7/5/8, hardness 11, notches 0/1/1/2,
consumables 15/10/0, cooldown (gear.md); prices 450/600, comfort 10/15/20, languages 90/50, reaction 400, spell 60/30,
upgrade 125, skill ranks 20/60/15/60, advanced cap, 60/300, grade 60, basics 4, qualification -4/-2, max HP 22,
level-up +200, end of cycle +5, cantrip 2X, short balance OT 3 DC 16.

### 1b. Owner principle: every sheet number has an effect target

| Sheet number | Effect target exists | Where / note |
|---|---|---|
| Ability scores and modifiers | **no** | `Ability.bonuses` typed by hand; effect `str` ignored (F1); only `block_stat_bonus` can lower |
| Max HP | **no** | `hp_race`, `hp_bonus` fields |
| BP max | **no** | `bp_bonus` field |
| Balance max | **no** | `balance_bonus` field (+ heavy shield) |
| Balance regen | **no** | `balance_regen_bonus` field + mastery picks; `block_balance_regen` can only block |
| Spirit max | **no** | `spirit_bonuses` list typed by hand |
| Mana max / slots / class resources | **no** | `Pool` typed by hand (formula only for resource pools) |
| Comfort max / comfort rate | **no** | `comfort_bonus` field; rate: Q107 (known gap) |
| Temp HP | yes | one-shot of a status |
| AC (every layer type) | yes | target `ac` with the bonus type |
| Touch AC armor | yes | `touch_armor` |
| Parry | **no** | grades + mastery picks only |
| Max Dex cap of armor | **no** | item field only |
| Attack / damage (per weapon) | yes | `attack`, `damage`, weapon scope |
| Lucky attack threshold | yes | `lucky` |
| Crit range | yes | `crit_range`; crit multiplier: **no** |
| Saves (all / one) | yes | `save`, `save:<id>` |
| Initiative / CMB / CMD | yes | `initiative`, `cmb`, `cmd` |
| Skills (all / one) | yes | `skill`, `skill:<id>`; armor skill penalty itself: **no** (only masterwork) |
| Speed / armor slowdown | yes | `speed`, `armor_slowdown_reduction` |
| Load thresholds / carrying | **no** | Str mod only |
| Spell penalty mana / failure | yes | `spell_penalty_mana`, `spell_failure_pct` |
| Spell cost, overload, mana level | **no** | typed at the cast or fixed tables |
| Two-weapon penalties | yes | `twf_reduction` |
| DR / resist / percent reduction | **no** | argument of `take_damage` only (F10) |
| Pain penalty / death cap / damage per pain | **no** | `PainProfile` fields and `rules_settings` |
| Free heal / BP gain of the short rest | **no** | command arguments `other_heal`, `extra_bp`; `rules_settings` for regen |
| Reactions, base slots, attention per cycle | **no** | fields / formula |
| Item HP, hardness | **no** | mastery picks only |
| Morale bonus | partly | typed morale bonuses yes; "count morale X higher" no |

Also: buffs.md:2 and the owner's principle say statuses are taken from a catalog; there is no status catalog in
`wp/catalog/` (feats, skills, weapons, armor only).

## 2. Architecture

| Check | Method | Result |
|---|---|---|
| ASCII-only code | `test_ascii_code.py` | 112 files, 0 non-ASCII |
| Module size <= 500 | `test_module_size.py` | 64 files, largest `derived_view.py` 406 lines |
| Mutations only through commands | grep for `setattr`, in-place `[...] =`, `.append` on state; read the helpers that return a new Character | no in-place change of a Character found; helpers in `model/` (bridge, restores, usage, body_view) return new states and are called only from commands. Mutable dicts inside the frozen Character: F16 |
| Derived values never written back | read every command | only `balance_cap_start` (the owner-approved snapshot, Q54) and `add_pool` setting current = max at creation; no derived maximum is stored |
| Ids made by the program | read the add_* commands | all generate ids; some accept a caller id (F18) |
| No migration code | read `character_io.py` | load-time drops / skips / injury ids exist (F14) |
| No UI texts in code | grep `CommandError("` | every refusal is an English sentence (F4); `defense_layers.json` texts are data (good) |
| Journal by every mutating command | read `dispatch`, fuzz | every successful command with `CHANGED` is logged (fuzz: never missed); but no-ops are logged too (F7) |
| Rule constants as data | `review4/hardcoded.py` | 94 named numeric constants + 62 inline literals; `RulesSettings` has 8 switches (F15). Largest: `core/training.py` 24 + 8, `core/weapons.py` 13 + 16, `core/derived.py` 10 + 4, `model/derived_view.py` 7 + 3, `core/skills.py` 2 + 4 (the 40 / 20 / 200 / 50 tier prices are inline) |

## 3. Mutation testing

`break_check.py`: entries 43, caught 43, missed 0.

My own breaks (`review4/breaks_review4.py`, runner `review4/run_breaks.py`): 60 entries, each run against the
WHOLE test set (`run_all.py`) on a temp copy (the working tree untouched). Areas: training and prices 12, rests 11,
spells and mana 7, maneuvers and tags 6, charges and cooldown 6, pools 4, stances 3, AC / defense 3, item HP 4,
misc commands 4. Result: **58 caught, 2 missed** (one entry first did not apply because its pattern was found twice;
fixed and re-run alone: caught).

| Missed break | What I broke | Rule | Why no test fails |
|---|---|---|---|
| `mv-no-tags-fit-nothing` | a maneuver with NO required tags fits nothing (instead of every weapon) | combat.md:88 (assumption Q79) | no test has a maneuver without tags |
| `us-set-above-max` | `set_charges` accepts a value above the max | gear.md:202 (set_charges bounds) | the refusal tests cover only negative values |

Caught with interest (each by at least one suite): tier prices 40 + 20 / 200 + 50, native-language cheap limit, base
max 10 * level, reaction 200 * new number, spell discount, comfort rate, professionalism points, level-up roll range,
free heal "larger of", free +1 BP, free first mana restore, spirit 2 BP, permanent pain kept, stat restore, overload 0
and balance max on the long rest, temp HP cleared by the short rest, day items off, mage balance = mana, cantrip slot,
short-balance pain, mana level with penalty, divine default mode, upgrade slots, tag modes, kind tag, required feat,
unarmed only without a weapon, maneuver to-hit, cooldown refusal / start / tick, recharge rules, pool bounds and
restores, stance rules, odd-level parry, overload dodge cap, shield balance grade, broken at 50%, off never to 0, HP 0
not working, enchant HP, damage-to-balance cap, morale reset, consumable bounds, OT per comfort.

## 4. Fuzz / invariants

`review4/fuzz.py 300 50 1` (seeds 1-300, 50 steps each, rich character: mage level 5 with mana, circle-0 slots,
sword +2 activatable and masterwork, heavy shield, medium armor with spell penalties, potions with an on-use status,
ring with charges and cooldown, dagger, six statuses incl. a per-round Ki aura, a bleed, an end-of-combat temp-HP
buff, a per-tick spirit restore, a stance feat and a feat with charges, a maneuver, two pools incl. a formula pool,
two skills). Invariants after EVERY step: no exception except `CommandError`; temp HP, balance, BP, OT, overload,
OV, attention, comfort, spirit, training, mana, slots, status charges, item quantity >= 0; item usage charges in
bounds; pools read within 0..max; combat round >= 1 in combat and combat data cleared out of combat; no negative-HP
state at HP >= 0; at most 2 hands; no active N-tick status with 0 ticks; gameplay heals never above max HP; carried
weight = sum of unit weight * quantity; `loads(dumps(ch)) == ch`; the journal grows by exactly 1 per change and not
at all on a soft refusal; every derived view (all AC modes, attack views, stats, spell view, maneuvers, container,
active list, weight, item views, skills, speed, regen) runs without an error.

Result: 15 000 steps, 3 444 refusals, **no invariant violation except the journal no-ops (F7)**: 16 commands, each
with its seed and shortest sequence in the script output (e.g. seed 8: `take_damage{amount: 0}`; seed 3:
`long_rest ; long_rest`; seed 9: `long_rest ; tick`).
Second pass with destructive commands (`fuzz.py 80 40 1001 x`: remove_item, delete_status, remove_feat, set_twf,
remove_attack, add_attack, remove_pool added; the views also run `twf.combination` for every two-weapon record):
3 200 steps, 869 refusals, again only journal no-ops. The random sequences rarely reach a valid two-weapon record
(sword and shield fill both hands), so F6 was found by `behavior.py` (section 8), not by the fuzz.

## 5. Test quality

`review4/test_quality.py`: 905 cases in 39 suites, no duplicated case id inside a suite, the whole set runs in about
12.6 s (slowest suite 0.6 s): no slow suite.
- 79 cases (9%) expect a bare truth value, `None`, `()` or a refusal word. Most are fine (save / load equality, a
  refusal is the rule). Weak ones where an exact value is known: `test_pkg12.py:183 b-tag-any` and `:192 b-kind-tag`
  check only `available` (not the numbers of the matching weapon); `test_pkg5.py:149 g-shield-visible` checks only
  that the shield record exists; `test_attack.py:231 lines-sum` and `test_pkg4.py:81 sum-equals-ac` check a sum
  against the code's own total; `test_group_a.py:167 m48-long-rest-overcap` compares BP with `dv.bp_max` (the code's
  number, not a hand number).
- 45 refusal cases (`rejected` / `refused`) check only that a `CommandError` was raised, never that the state is
  unchanged or WHICH reason was given (there are no reason ids, F4).
- Weak areas shown by my mutations: see section 3.
- No test runs a long random sequence or a save / load after many commands; the fuzz script fills this gap.

## 6. UI readiness

Checked every line of UI_WISHES.md and ARCH/surfaces.md against the views and the 89 commands
(activate_item activate_status add_attack add_feat add_injury add_maneuver add_pool add_skill add_status burn_ov
buy_ability buy_armor_grade buy_attention_course buy_base_slot buy_combat_basics buy_hp buy_item_qualification
buy_language buy_maneuver buy_professionalism buy_reaction buy_seed buy_shield_grade buy_skill_rank buy_spell_upgrade
buy_weapon_grade cast_spell convert_attention damage_item damage_to_balance deactivate_item delete_status
edit_maneuver edit_pool end_combat end_cycle equip_hands equip_item exchange_comfort hit_item learn_spell level_up
long_rest make_language_native pay_hp_cost promote_skill raise_heal_rating remove_attack remove_feat remove_injury
remove_item remove_maneuver remove_ot_attention remove_ot_comfort remove_pool remove_status resolve_spell_failure
restore restore_charges restore_pool set_active_stance set_base_speed set_charges set_condition_tag set_hp_roll
set_ignore_bag_weight set_item_hp set_item_masterwork set_primary_attack set_size set_status_duration
set_status_favorite set_status_hidden set_temp_hp set_twf set_value short_rest spend_balance spend_bp spend_charge
spend_ov spend_pool sprout_seed start_combat take_damage tick unequip_hands unequip_item use_consumable).

| UI element (UI_WISHES / surfaces) | Data available | Missing |
|---|---|---|
| Take damage + DR / resistance picker | `take_damage(reductions)` | a derived list of the sheet's DR / resistances (F10) |
| Dying: painful action slots, tap spent actions | `core/statuses.action_pain` | a view of action slots and a command to mark spent actions / add the pain |
| Over-max shown red (comfort, base, load) | `Pool.over_max`, load status | base used vs base slots (no base items model); pool over max is hidden by the clamp (F17) |
| Shield on/off in AC | `dv.ac(shield_enabled=)` | - |
| Morale button and indicators, min / max of the fight | `morale_scale` | a command to change the scale; min / max not recorded |
| Short rest menu | `core/rest.options` | a model-level view (the UI must call bridge + core itself) |
| Chips for quests, courts, stories, quirks | seeds only | models and commands (F12) |
| Item / ability code, PDF, copy character | `character_io.dumps` | item code export / import |
| Weapon bonus picker (hide forbidden picks) | `core/weapons.validate_picks` | a view of allowed picks and a command to pick (F3) |
| Skill tier marks, sorting | `Skill.tier`, key stat | - |
| Modes Play / Training / Edit | - | edit commands for base values (F3); mode itself is UI |
| Source and cost fields | Feat.source / cost | Item has no source / cost |
| Statuses filter and favorite | `container_view` | - |
| Pain editor (list, turn one into a status) | `ch.pain` | commands add / remove / convert a pain entry |
| Morale scale editor | - | command (F3) |
| Crit tooltip | `AttackView.crit_hint` | - |
| AC grid | - | known gap (AC zones) |
| Panel contract, i18n | - | panel registry, `wp/i18n`, reason ids for refusals (F4) |
| Defense ladder hint | `core/ac_layers.ladder`, texts JSON | a model-level view (the UI must call `acm.parts(dv.ac_input(ch))`) |
| Iterative attack penalty | - | F9 |

## 7. Docs consistency

- gear.md:76 "mana level 4 -> capped" contradicts gear.md:66 "above it the spell CANNOT be cast (no cut)" (stale).
- resources.md:117 and gear.md:11 "5 spirit until the end of the cycle" vs gear.md:172 "decade = until the end of the
  LONG rest" (R13 of review 3, still in the text).
- spells.md:122-123 "'Disable a bonus' cannot be expressed ... (no block effect)": stale since package 13 block effects.
- combat.md:125-127: the package 10 size line is glued to the next heading `## Size and speed` (no blank line);
  combat.md:145 "size 1" refers to the removed hand-typed size CMB field (size now comes from small / medium / large).
- combat.md:36 "attacks are shown only for weapons held in the hands" vs combat.md:99-101 all_records: consistent, but
  worth one sentence that both views exist.
- weapons.md:96 open note (crit +1 vs "widen by 2") is not an OPEN_QUESTIONS entry (F13).
- UI_WISHES.md:8 "temp BP shown": temporary BP was removed in package 8 (overcap).
- Code comments: `character.py` `Item.speed_penalty_ft` "(stored, no calculation yet)" is stale (gear.md:33 computes
  it); the comment "character-level maneuver list" sits on the `rules_settings` line; `stats_view.py` docstring still
  points at "OPEN_QUESTIONS Q55-Q60" (closed).
- OPEN_QUESTIONS: no entry is already answered in RULES as far as I can see; Q108 is confirmed by running (still
  true). Missing entries: F8 (long rest in combat), F13, the iterative-attack gap, F17.
- Session start cost (CLAUDE.md "any" row): CLAUDE.md 5.3 KB + STATUS.md 1.6 KB + GOTCHAS.md 1.9 KB = 8.8 KB, about
  2 500 tokens. A mechanics task adds RULES/index.md (9.1 KB, about 2 600 tokens) and one domain file: the large ones
  are gear.md 17.7 KB (about 5 000 tokens), combat.md 15.0 KB, resources.md 15.1 KB, training.md 15.3 KB, buffs.md
  13.9 KB (about 4 000 each). The last package report is small (PACKAGEH 3.0 KB). Worst common start: about 10 000
  tokens before the package text. gear.md and the three 15 KB files are worth splitting by heading; the generated
  Sections block in index.md already allows reading one section.
- GOTCHAS.md is almost all about the legacy tkinter code; nothing about the new core (e.g. "every refusal must be a
  CommandError", "views must not raise on a broken formula").

## 8. Behavior questions (run with `review4/behavior.py`)

| Question | What happens |
|---|---|
| Long rest | active statuses keep running with their time; charges of every status come back, also an ACTIVE rage (1/3 -> 3/3) and a plain buff without a source (Q108, known gap); feat usage charges "long_rest" restored. Allowed during combat, combat state kept (F8). |
| end_combat | "until end of combat" statuses become inactive (temp HP gone); N-tick statuses keep running (rage keeps 3 ticks); morale 0, overload 0, snapshot cleared. |
| level_up | statuses and charges unchanged; training +100 * new level; current HP not raised (Q111). |
| Status of duration 1 activated in a round | active in that round with its bonus (+3); at the first tick its DoT part acts once (HP 20 -> 19) and it becomes inactive: matches buffs.md:132-134. |
| Removing an item with charges | the item and its usage charges vanish from the active list; a status the item started (on_use_status) stays active (correct: the entry is the container's). |
| Removing an item that is the off-hand of a two-weapon record | the other record keeps `twf_off` -> shown available, `twf.combination` raises KeyError (F6). |
| Stance feat removed while active | `active_stance` becomes None (correct, combat.md:161). |
| Maneuver whose required feat is removed | kept, unavailable, reason `feat_missing` (correct). |
| Extra: pool removed under an active per-round status | the next tick ends the status (cannot pay), no error. |
| Extra: consumable whose on-use status was deleted | refused with a clear message. |
| Extra: a finished status without charges | can be activated again at once (no recharge rule: matches Q97). |

## Comparison with earlier reviews

Written last, after sections 1-8. Read: REVIEW_REPORT.md (review 1), REVIEW_REPORT_2.md (review 2),
REVIEW_REPORT_3.md (review 3); of the package reports only the last one (PACKAGEH_REPORT.md), as CLAUDE.md says.
"Fixed" below = re-checked by running in this session (probes, behavior script, or the snippet noted).

### Found only by this review
- F1 ability scores ignore effects, and the systematic coverage table (F2): earlier reviews looked at single numbers.
- F4 refusals are text without reason ids (UI / i18n readiness was not a check before).
- F5 `cast_spell(circle=10)` IndexError (the circle table is from package 10).
- F6 dangling `twf_off` after `remove_item` (two-weapon records are from package 8).
- F7 the journal logs no-op commands (journal from package 14).
- F8 long rest during combat; F11 doll slots; F14 load-time legacy handling vs the CLAUDE.md hard rule; F15 count of
  rule constants in code; F16 mutable dicts inside the frozen Character; F17 pool clamp vs "Over max".
- Docs: gear.md:76 stale "capped", spells.md:122 stale "no block effect", UI_WISHES "temp BP", glued heading in
  combat.md, the weapons.md:96 note missing from OPEN_QUESTIONS.
- Fuzz with invariants and save / load round trip after every step (no earlier review had one): clean except F7.

### Found earlier and STILL open (re-checked now)
- DR / resistances not taken from the sheet's effects (review 2, section 1 "no command"): still F10.
- Mastery pick selection: `validate_picks` never called, no command (review 2, review 3 section 3): still (F3).
- Choosing the negative-HP state (`choose_state` / a command) and recording painful actions (review 2, review 3):
  still no command (F3, section 6).
- Lens, crafting DC (review 2): still not built (F12).
- "Count morale X higher" (review 1 #16, review 3): still not built (defense.md:45).
- Source / cost of purchases only on feats (review 2): Item still has no source / cost.
- Iterative penalties without a command (review 3 section 3): still (F9).
- Review 3 R13 "5 spirit until the end of the cycle" vs "decade until the long rest": the text contradiction is still
  in resources.md:117 and gear.md:11 (the owner decided "decade = until the long rest", I, package 10).
- Review 1 #8 "Item HP: +1 per expert pick" (weapons.md:88): wording unchanged; code gives +1 only for the "HP +1" pick.

### Fixed since the earlier reviews (verified in this session)
- Review 3 R1 temp HP of an end-of-combat buff: 6 -> 0 at end_combat (snippet).
- R2 enchantment at item HP 0: attack 0, damage 0, lucky 20 (snippet).
- R4 shield skill penalty, R3 mastery in item HP / hardness (probe gear.md:118 hardness 11).
- R6 damage per pain: Str -2, pain 2, +1 per pain -> -2 (snippet; also probe-equivalent numbers in resources.md:79).
- R7 lucky effect for one weapon: 20 -> 19 (snippet); R8 crit range shown (probe 19/18/17).
- R9 size in attack and CMB / CMD (probe combat.md:135).
- R16 status charges by the short rest option (probe 0/3 -> 3/3); R17 divine option only for divine casters and R18
  racial mana on the long rest (covered by passing suites, not re-probed).
- Review 2 P2-18 N-tick status without a number: refused; P2-19 duplicate status id: refused (snippet).
- Review 2 P2-17 a switched-off status losing duration: no longer applies (no on/off toggle, inactive statuses do not
  tick, package 11).
- Review 2 P2-15 morale on initiative: answered by the owner (Q56) and matches (probe defense.md:41-42).
- Review 2 P2-32 / review 3: the stale `character.schema.json` is gone from the repo root.
- Review 1 #14 flank always drops the shield: now a checkbox (defense.md:6).
- Review 1 #17 speed -10 ft at overload: computed (probe combat.md:136).
- Review 3 weak tests M13 (spirit) and M55 (BP overcap): covered (probes resources.md:120-122, rest.md:17).
