# Buffs / effects [OWNER]
Buff = status = debuff = situational: one concept, "Status" [OWNER]. Everything from spells, DoT and heal per tick are ordinary statuses. One generic effect system for ALL sheet parts (race, class, feat, item, injury, quirk, spell, buff).

## What an effect can change
Any parameter: stats, initiative, attack bonus, AC, actions, saves, skills, resources (max, regen, current), speed, etc.
Several at once or separately. May give penalties (e.g. -2 AC). May give a one-shot (e.g. temp HP) AND a timed part
(e.g. +4 Str for 8 rounds).

## Duration kinds
- N ticks (zero-initiative ticks). Duration is typed in by hand as a number; no "level x minutes" formulas [OWNER].
  Long statuses are removed by hand.
- [OWNER, package 8] Ticks, the zero-initiative phase and overload belong to the combat system. Long effects (5 min and
  more) are not simulated: they sit on the panel and the player lowers their duration with ticks or by hand
  (command set_status_duration; example: a spell lasting 10 min/level, the GM says 20 minutes passed, two ticks remove
  20 minutes), or deletes the buff. DoT and regen tick exactly like buff durations: a DoT for N ticks hits N times and
  ends. Tests: DoT -3 for 3 ticks -> 3 hits, then gone; regen 20 ticks set by hand to 2 -> 2 heals, then gone.
  ("Gone" = inactive since package 11: the entry stays in the container.)
- [OWNER, package 8] An N-ticks status needs its number: adding one without ticks is refused with a clear message.
  A status id already on the sheet cannot be added a second time.
- Until end of combat.
- Narrative infinite: until the GM cancels.
- Instant/one-shot (applied once, e.g. temp HP).
- Duration drops by 1 each zero-initiative phase automatically (resources.md).

## Value from the current overload [OWNER]
- A status/ability may read the CURRENT overload as its number. Example: bonus to attack and damage with natural weapons
  equal to the current overload.

## Value from a stat modifier [OWNER, package 11 B; closes Q65]
- An effect value is a plain number OR {stat_mod: <stat>, multiplier: 1 (default)}, computed on read from the CURRENT
  stat modifier (stat damage changes it at once). Works for every effect target (skills, attacks, damage, saves, AC
  layers, speed...) with the usual type / stacking rules.
- It is a bonus ON TOP, never a replacement (e.g. "+Str mod to Intimidation" adds to the skill's own Cha).
- A negative modifier gives a negative value, as is.
- Assumption (OPEN_QUESTIONS Q71): a non-whole result (multiplier 0.5) is rounded down.
- Tests: +Str to Intimidation (Str 16, Cha 12) -> 4; +Dex to damage (Dex 18) -> 4; Str 16 with 4 damage -> +1;
  Str 6 -> -2; untyped +3 and +1 add up -> 4; competence +3 and +2 -> 3; multiplier 2 -> 6; dodge +Wis 14 -> AC 12.

## Skills target [OWNER]
- An effect may target one skill (e.g. +2 to Stealth only) or all skills.

## Condition [OWNER, package 8]
- There is NO "combat only" condition: a status works while it is active and not expired, in or out of combat.
  The old "in combat / out of combat" field is removed (an "out of combat" item bonus is switched on/off by hand).
- Condition tag [OWNER, package 9, closes Q36]: abilities (feats), items and statuses have an optional display-only
  field condition_tag: none / combat_only / out_of_combat_only. It changes NO calculation; derived views show it so
  the UI can draw an icon. The player sets it by hand (command set_condition_tag). Test: a tagged item and status give
  the same numbers in and out of combat as untagged ones.

## Status container [OWNER, package 11 A; closes Q63]
- A status is either ACTIVE or not. There is NO on/off toggle and NO pause.
- A status with a duration runs its full duration (ticks by the rules above) unless the player removes it earlier by
  hand (narrative reasons). A status with no duration (e.g. a situational bonus) stays active until the player removes it.
- An inactive status gives no effects and does not tick. The end of the duration makes the status inactive; the entry
  stays in the container.
- The CONTAINER is one list of every status of the character from every source (race, class, items, injuries, manual,
  catalog): a place to activate, remove, add new, take from the catalog.
- Fields per entry: id, source, active, duration kind, charges (count, duration per charge = full_ticks; optional),
  hidden (DISPLAY ONLY: hidden on the panel but still active, still gives effects, still
  ticks), favorite (pin for panel / screen), condition_tag.
- Commands: activate_status(sid): with charges, one is spent and the status starts with the full duration per charge;
  refused with a clear reason when no charge is left or when it is already active; an entry without charges just
  becomes active. remove_status(sid): ends it now (inactive, remaining time cleared, its temp
  HP gone), the entry stays. set_status_hidden, set_status_favorite. delete_status(sid): removes the entry entirely
  (by hand). add_status (catalog / by hand): a new entry starts INACTIVE unless the caller passes active=True.
- Injuries and item effects are only SHOWN in the container view (kind "injury" / "item"); they keep working as
  injuries.md and gear.md say (item effects stay tied to item activation, Q2).
- A STATUS HAS NO COST [OWNER, package 12, Q69]. A status is only the display of things that already exist (abilities
  with charges, spell / potion effects, debuffs, injuries). The ability or spell that creates it pays its own cost.
  Activation spends one charge (if it has charges) and nothing else. Old files with a status cost load; the cost is
  dropped.
- Injuries in the view use their stable id (injuries.md, package 12, Q70).
- Tests: activation with and without charges; refusals (no charge, already active); no cost (spirit unchanged);
  remove early; a 3-tick status
  is active 2 ticks with its bonus and inactive after the 3rd; an inactive status does not tick; hidden still gives the
  bonus and ticks; favorite flag; charges restore as before (long rest yes, a free short rest no).

## Charges and activation
- A buff source (ability/item) may have charges (e.g. rage 2/3). If placed on screen/slot, tapping activates it;
  shows remaining rounds and remaining charges.
- Charges restore on long rest (rest.md) unless item without the "restore on long rest" checkbox.
  Charges kept on a status (rage 2/3) are restored too, on the long rest AND by the short rest option
  "restore charges" (2 BP) [OWNER, package 8]. Test: rage 0/3, short rest charges option -> 3/3.

## Stacking (see defense.md)
- Same type: the value with the larger absolute value wins, equal absolute values give 0; only flat stacks
  (on AC dodge also stacks; weapon proficiency stacks with itself). Details: defense.md "Stacking".

## Ready-made buffs
- Any ability can be exported as a buff; catalog keeps templates (Entangled, Haste, Rage ...).

## Stacking flags [OWNER]
- Temp HP from buffs may or may not stack: per-effect flag. Same for DR, energy resistances, spell resistance.
- Duration is usually given in rounds.
- Spells, abilities, racial abilities are editable: mark "is buff" in the editor; buff list is searchable for activation
  when the source is not pinned to the panel. No charges left -> cannot activate.
- Test: removing an injury must NOT bring OT back.

## Block effects [OWNER, package 13 B; closes Q82]
- New effect kinds in the usual effect structure. They work from any source that is ACTIVE now: an active status, an
  owned feat (a stance feat only while it is the active stance), the acting tab of a worn / held item (an activated
  item: its "activated" tab). Injuries have no effects in the model yet, so an injury cannot carry a block (Q89).
- A block drops only POSITIVE values, never penalties.
- block_balance_regen: while at least one is active the balance does not regenerate (as with overload). The derived
  view lists the reasons: "overload" (when overload > 0) and the source ids. Overload works as before.
- block_bonus {block_type: a bonus type (morale, luck, sacred, dodge...) or "any"; block_scope: "all" or a list of
  targets: attack, damage, ac, save, save:fort, skill, skill:<id>, lucky, crit_range...}: before stacking, positive
  bonuses of that type to that scope are dropped. Type dodge on scope ac also drops the positive Dex part of the dodge
  layer (dodge + Dex are netted, defense_layers.md); the low-Dex penalty stays. The same for a positive size modifier
  when type size (or "any") is blocked on AC.
- block_stat_bonus {block_stats: stat names or "all"}: a positive modifier of those stats counts as 0 everywhere derived
  numbers use it (Dex in AC and Reflex, Str in attack and damage, carrying capacity...); a negative modifier stays.
- cannot_be_flanked (flag): the flank AC option behaves exactly like a front attack (no shield loss).
- Tests: regen blocked / overload + block / inactive source; no morale at all (attack and save); no sacred to attacks
  only (AC keeps it); no luck; no dodge to AC (Dex 14 + dodge 1: 13 -> 10; Dex 8: 10 -> 9); skill scope; two sources;
  penalties stay; Dex / Str / "all" stat blocks; cannot_be_flanked; the "Me Liquescit" stance.

## Per-round cost [OWNER, package 13 C]
- Status fields charge_source ("own" = its own charges, or a resource pool id, resources.md) and charge_per_round
  (default 0).
- Every tick, an ACTIVE status with charge_per_round > 0 pays that amount from its source. This happens in the
  zero-initiative phase at the duration step, BEFORE the duration drops. If it cannot pay, the status ends
  (inactive, the entry stays) and does not act in this tick (assumption Q84). The player may remove it earlier by hand.
- activate_status with a pool source needs at least charge_per_round in the pool but pays nothing yet (assumption
  Q85); with source "own" the usual activation charge is spent (one charge), then the per-round payment follows
  (Q91). A status has no other cost (Q69).
- Tests: pool 3, 1 per round: 3 paid ticks (2, 1, 0), the 4th tick ends it (Q83); manual removal stops the payment;
  a duration of 2 ends before the pool; own charges 2/2; refusals (empty pool, unknown pool); an unpaid regen does
  not heal.
