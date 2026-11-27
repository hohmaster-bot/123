# Resources

## HP and temp HP [OWNER]
- Temp HP = a SEPARATE pool "HP on top of normal". This is why HP can look above max: store temp_hp as its own field,
  never hp_current > hp_max.
- Damage hits temp HP first. Absorbed part does NOT reduce balance.
- Example: 3 temp HP, 7 damage -> temp 0, HP -4, balance -4.
- [OWNER, package 4] Two kinds of temp HP:
  - from a buff: given for N rounds, they live as long as the buff lives; a buff "until end of combat" loses its temp HP
    at the end of combat [OWNER, package 8 R1]. Test: such a buff gives 6 temp HP -> 6 in combat, 0 after end_combat.
    An instant buff keeps nothing itself: its temp HP go to the "by button" pool (until the short rest);
  - "by button" (entered by hand): live until the SHORT rest; the end of combat does NOT clear them.
  The short rest clears all temp HP after its spends (rest.md).
- Spend order (Q23, assumption): first the "by button" temp HP, then the buff temp HP (buffs in order).
- HP can go below 0.

## Damage pipeline [OWNER]
The ONE current order (all steps, data rules_settings.damage_order) is in defense.md "Damage pipeline" (package 22 B6).
What this section adds:
1. (Percent steps: defense.md, the old percent text of this list is REPLACED there.)
2. Flat reduction BY DAMAGE TYPE [OWNER]: one mechanism. "DR/-" is just the flat resist to PHYSICAL damage; fire resist etc. are other types.
   DR does not work on fire. Damage may have several components, each handled by its own type:
   fire sword hit = 8 physical + 3 fire -> physical part uses DR/physical resist, fire part uses fire resist.
   Overlap of two reductions on one component is not modeled for now. Before taking damage the player can pick which
   reduction applies (gear icon next to Take damage); a setting may allow summing them.
3. Temp HP.
4. Temp-HP analogs (e.g. racial: damage hits MANA first; others possible), in a configurable order.
5. HP (and balance, see below). Only the part that reaches HP touches balance.
Rounding [OWNER]: damage is never fractional; round UP (against the player). 10 dmg, 25% -> 7.5 -> 8.
Example (with the defense.md order): 10 fire, a percent reduction 50% -> 5, flat 2 -> 3, temp HP 0 -> HP -3, balance -3.
Spell Resistance is separate (vs spells, not a damage step).

## Balance [OWNER]
- Second bar next to HP, lost together with HP. Usually balance < HP max.
- Damage that would push balance to -1 or lower: +1 pain (per such hit, even if balance is already 0). Excess goes to trauma points.
- Restored at zero initiative (blocked while overload > 0).
- Trauma points: GM issues penalties for them unless removed otherwise (after session). Injury editor in Rest GUI [BETA].
- Balance FLOORS at 0 (never negative). Overflow = damage - balance. Pain +1 per hit with overflow > 0
  (also when balance is already 0). Overflow -> trauma points (ОТ). HP always loses the full damage.
- Example [OWNER]: balance 1, hit 10 -> HP -10, balance 0, overflow 9 -> trauma +9, pain +1.
  Then hits of 1 and 1 (balance not restored): each HP -1, pain +1, trauma +1 -> totals HP -12, pain 3, trauma 11.
- Damage input: button "take damage" + optional DR/- and Resistance selector (by damage type) applied before the above.
  DR/Resistance come from the sheet's effects. [UI wish]
- [OWNER, package 16 D] Damage types are data (wp/catalog/data/damage_types.json): piercing, slashing, bludgeoning,
  fire, cold, lightning, acid, sound, force, positive, negative, pure (12; "water" does not exist, owner); DR works on the physical ones (piercing,
  slashing, bludgeoning and the old default "physical"). Effect targets: "dr" (value; Effect.note = bypass text such
  as cold iron, silver, magic: narrative only, never math), "resist:<type>" (value), "spell_resistance" (value, shown
  only). take_damage applies them per part: the larger of DR (physical) and resist:<type> (one reduction per part,
  assumption Q119); skip=("dr", "resist:fire", "percent:fire") = the player's choice for this hit. The defense view
  lists every entry.
- [OWNER, package 17, Q115] DR: every DR entry has the flag "stacks" (default false). Total DR = the largest
  NON-stacking entry + the sum of all stacking entries. The bypass text never changes the number. Example: DR 1/-
  stacking + DR 10/piercing = 11. Resistances to elements (resist:<type>) NEVER stack: the larger wins.
- Percent modifiers per element: see defense.md "Damage order and percent modifiers".
  Tests: DR 3, 10 physical -> HP 8 -> 1; 10 fire -> -2; resist fire 5 -> 3; 8 slashing + 3 fire with DR 3 and resist
  fire 2 -> 6 damage.
- Balance cap in combat [OWNER homerule, package 9, closes Q35; the stored snapshot accepted, Q54]: start of combat
  takes a SNAPSHOT of the balance max
  (armor + current BP + bonuses at that moment). During combat the cap changes ONLY by hits (below); it does NOT change
  from a max HP change (e.g. Con lowered), spending BP, taking armor off/on or any bonus change. End of combat
  recomputes the cap from scratch and clears the snapshot. Balance REGEN stays live (current Con etc.).
  Tests: snapshot 7 (armor 2 + BP 5); spend 2 BP -> 7; armor off -> 7; bonus +3 and Con 14 -> 8 -> 7 (regen 3 -> 1);
  a hit -> 6; end of combat with BP 3 and no armor -> 3.
  [OWNER, package 22 A3] While combat is active the balance never stays above the current cap: restores and
  manual sets are clamped to it (not refused). Outside combat the overcap rules stay.
  Hits: Each hit on the character lowers the cap by 1 until the end of
  combat, ONLY if the damage reached the balance (after percent, flat reductions, temp HP and analogs, HP were really
  lost). A fully blocked hit does not lower it. The current balance is NOT lowered by the cap drop. DoT does not lower
  the cap unless its effect has the flag "lowers cap". Counted only while combat is active; start and end of combat
  reset the counter. Example: balance 6/6, hit 5 -> 1/6, then cap 5 -> 1/5.
- Paying balance (maneuvers, abilities: command spend_balance) is a payment, not damage: the cap does not drop.
  More than the current balance cannot be paid: refused [OWNER, package 10, closes Q43]; for rare exceptions the
  player uses the "damage to balance" button.
- HP cost of an ability (command pay_hp_cost) [OWNER, package 9]: it lowers the CURRENT balance first, HP untouched;
  the part above the balance -> OT = the WHOLE overflow and +1 pain by the standard damage rules, exactly like
  "damage to balance"; it never lowers the cap [OWNER, package 10, closes Q41]. Test: balance 7,
  cost 9 -> balance 0, HP unchanged, OT +2, pain +1, cap 7; cost 3 -> balance 4, no OT, no pain.
- Empty-hand parry and damage to balance [OWNER]: parrying with an empty hand is allowed. The player sees that the
  enemy roll landed in the parry number (armor/parry layer, defense_layers.md) and presses "take damage to balance".
  Command damage_to_balance(amount): the damage goes straight to the balance; HP are not touched; percent and DR are
  not applied (the player types the number). If the balance would go below 0, the overflow goes to OT and gives
  +1 pain (like an ordinary overflow). In combat the balance cap drops by 1 if the balance really lost points.
  Examples: balance 6, damage 4 -> 2, HP unchanged; balance 2, damage 5 -> 0, OT +3, pain +1, HP unchanged.
- Heal/consumables without a special flag never exceed max; "over max" is an explicit exception flag on the effect.

## Pain [OWNER]
- Death at 8 pain (cap can be changed by race/class/feat -> must be editable).
- Pain is stored as a list of entries (amount, source, permanent or temporary); total pain = sum of all entries.
  Pain can be the price for activating an ability or an item.
- Death: total pain >= cap (default 8). The cap is changed by race, template, feat (e.g. 12; some have "pain gives no penalties").
- Pain penalty: -1 to ALL rolls per pain (saves, damage, attacks, skills, anything with a die), EXCEPT the lucky attack.
  Races may ignore pain or morale, or get a damage bonus per pain.
- [package 10, R6] Attack damage = Str mod by grip + pain penalty (-1 per pain) + race bonus (PainProfile
  damage_per_pain * total pain) + typed bonuses. Tests (numbers by hand from this text): Str -2, pain 2, +1 per pain
  -> -2 - 2 + 2 = -2; Str +2, pain 3, +1 per pain -> 2 - 3 + 3 = 2; the same without the race bonus -> -1.
- In the editor one pain entry can be turned into a status (change the property of one pain).
- Sources: balance overflow; ability costs; GM punishment; curses/injuries (permanent, not removed by rest);
  temporary (situational); +1 temporary pain per 3 FULL HP below 0.
- Temp pain from HP = floor(-hp / 3) when hp < 0, else 0. Computed live from CURRENT hp, adds to other pain.
  Examples [OWNER]: hp 0 -> 0; -2 -> 0; -5 -> 1; -7 -> 2; -12 -> 4. Heal -7 by 2 -> -5 -> 1 temp pain gone.
  Do not store it; derive on read (D6).
- Statuses at hp < 0 [OWNER] (player sets manually, no auto-switch assumed). They exist only while HP < 0: at HP >= 0
  there is no HP loss per tick and the state is cleared (healing to 0+, long rest):
  * "resting in negatives": unconscious, cannot act until healed to 0+. Loses 1 HP per tick.
    Tooltip: d100 roll of 90+ stabilizes (rolled outside).
  * "stabilized": lies unconscious, no HP loss. Replaces the two others. Text: "you are stabilized and unconscious".
  * "dying" (below) = acting while in negatives.
- "Dying" is the BASE acting state for everyone (player picks: dying / resting in negatives / stabilized).
  Dying: -2 HP per tick (hits balance as usual, overflow -> trauma). Actions: 1 clean (first slot); 2nd and 3rd cost pain if used.
  Concentration DC 20 (rolled outside): each success clears one more action slot, repeat until all cleared or first failure, no limit.
- Pain per painful action = 1. Spending actions marks slots; painful slots (beyond clean ones) highlight RED in dying.
  Player rolls himself; app only records spent actions. Example: move (1 action, clean) + special attack (2 actions)
  in base dying -> 2 pain at the end of the calc.
- Pain removal: rest / long rest options, rare spells, events.
- Diehard (checkbox) changes dying: 2 clean actions, 3rd still costs pain, HP loss per tick 0 (custom amount possible).
- Auto-stabilize (separate trait): player may always choose "stabilized" while negative.
- Damage UI [OWNER]: [Take damage][gear icon]; gear opens DR/- and Resistance selection.
- Some abilities ignore death for a couple of rounds (not modeled), some change the cap (modeled).

## Zero initiative phase [OWNER]
After everyone acted, in this order [OWNER]:
1. Durations: statuses lose 1 duration (expired ones are removed).
2. Balance restoration (if spell overload == 0) and the damage of the tick (DoT statuses, the dying / resting loss),
   in the order MOST FAVOURABLE for the player [OWNER, package 22 A4]: the order with the smallest overflow (OT, then
   pain) and then the highest final balance (Q150). Every order is tried up to 6 items (data tick.max_order_items),
   beyond that a greedy order (damages ascending, the regen tried at every place). Only the tick; ordinary commands
   apply at once.
3. Heals per tick (fast healing, regeneration) after the damage.
   Tests: balance 5/5, dying -2, bleeding -4, regen +1 -> -2, +1, -4 = 3, 4, 0: no OT, no pain (regen first would
   give 5, 3, -1: OT 1, pain 1); balance 3 (cap 5), regen +1, damage -4 -> regen first: 0, no OT; at the cap the regen
   does not go above it; no DoT: plain regen.
- DoT and regen last exactly their duration [OWNER]: N rounds = N ticks (bleed for 3 rounds hits exactly 3 times).
- Spell overload (from casting, B4 name) is a number: -1 per zero-initiative tick; at 0 it is gone. End of combat resets it to 0 [OWNER].
  Order inside the tick: the regen check uses the overload at the START of the tick, then overload drops by 1
  (overload 1: no regen in this tick, overload 0, regen in the next tick).
- Damage from the "dying" state and from DoT goes through temp HP and balance like an ordinary hit (temp HP and
  analogs first, then HP and balance; overflow -> OT and +1 pain).

## Spirit, mana, overload [OWNER]
- Everyone has: HP, balance, balance regen, spirit, trauma points. Spirit pays item activations (1 spirit per "day" = until the short rest, or 5 per "decade" = until the long rest).
- Spirit max [OWNER] = 5 + 5 * Cha modifier, never below 0 (Cha mod -1 or lower -> 0), plus bonuses/penalties by source.
  [OWNER, package 9, closes Q33] Order: max(0, 5 + 5 * Cha mod) FIRST, THEN the bonuses (race, class, feats, other; may
  be negative); the total is never below 0. Tests: Cha mod -2 (base -5 -> 0) + 3 = 3; + (-1) = 0; Cha mod +2 + 3 = 18.
  Not typed in by hand. Tests: Cha mod +2 -> 15; -1 -> 0; -2 -> 0; +2 with bonus +3 -> 18.
  The total after bonuses and penalties is never below 0 [OWNER] (Cha 8 with penalty -2 -> 0).
- Casters (mage): mana instead of slots. Divine casters: slots.
- Mage cast cost: mana 1/3/5 by circle AND the same amount of balance. Gains X overload
  (X = casting time in ACTIONS, usually 2; spell duration does not matter) [OWNER, changed].
- Overload > 0 forbids balance regen. New casts add. Other sources add; player may raise it deliberately.
- Non-mage: slots, no balance loss, gets 2X overload. Must be changeable (rule may change).
- The overload value is computed by the formula by default and can be typed in by hand at the cast.
- Examples: mage casts a 3-mana standard-action spell (2 actions): mana -3, balance -3, overload +2.
  Non-mage same spell: slot spent, balance unchanged, overload +4.

## Class resources [OWNER]
- Class pools (Ki, Darkness, Paladin defense points + Holiness) look/work like HP, mana, spirit. Players define in editor/catalog.
- Rage-like buffs show charges left (2/3) and duration; duration ticks with initiative.

## Comfort [OWNER]
- Resource burned during play or exchanged for training. Max formula 5 + 5*level, modifiable by class/race/items.
- Chip goes red when current > max; player spends it down by the next session (see Over max).

## Comfort per fight [OWNER, package 38, decision 5; closes Q280]
- A general rule for every character: during a combat the program keeps the largest absolute morale (combat
  pressure) reached; above 5 counts as 5. At the combat end: comfort = max(0, that value - 1), at most 4
  (|morale| 1 -> 0, 2 -> 1, 5 -> 4, 8 -> 4). The numbers (cap 5, minus 1, at most 4) are rule data
  (comfort.fight_cap / fight_minus / fight_max), so they are const: targets.
- The comfort is never added silently: the combat end leaves a reminder with a button "take +N comfort"; the
  button is a command (journal, undo); the next combat start forgets an unaccepted gain.
- Mordon Wall of Bones: 1 more off and at most 3 (2 -> 0, 5 -> 3); the buy-out brings the normal rule back.

## Over max [OWNER, confirmed]
- ANY resource (HP, mana, spirit, comfort, ...) may exceed max: usually consumable effects, sometimes narrative (rare).
- Normal gameplay (regen, healing, rest, tick) never raises above max: clamp.
- Manual set / overfill is allowed and must NOT be clamped. Design: two ops: restore(clamps) and set(no clamp, flagged over-max).
- Over-max is shown (red chip), not auto-trimmed. Comfort: player must spend down before next session
  (starts session at its start value); no engine enforcement, only the red indicator.
- Temp HP is still its own pool (see above); over-max HP is a different, rare case.
- So audit A054 (no clamp) is NOT a bug; A053 (crash on HP setter) still is.

## Base, attention, money -> gear.md / narrative.md

## Resource pools [OWNER, package 13 C]
- A pool is a character-level counter (Ki-like): id (made by the program), name, max (a number or a formula, buffs.md
  "Formulas"), current (shown as is, also above the max, package 16 A6), restore: "short_rest" | "long_rest" | "combat_start" | "manual";
  restoring sets it to max (an over-max value is not lowered).
- Commands: add_pool (current = max unless given), edit_pool, remove_pool, spend_pool(pool_id, n) (refused below 0),
  restore_pool(pool_id). The short rest restores "short_rest" pools; the long rest restores "short_rest" AND
  "long_rest" pools (a long rest includes a short one) [OWNER, Q88]; start_combat restores "combat_start" pools;
  "manual" pools never restore by themselves. Default restore of a new pool: "manual" [OWNER, Q90 accepted].
- Statuses may pay their per-round cost from a pool (buffs.md "Per-round cost").

## Rule switches [OWNER, package 14 G]
- Character.rules_settings holds rule switches as DATA (easy to extend; every NEW rule constant or switch goes there):
  - ignore_pain: pain gives no penalties; the pain count itself stays (REUSES PainProfile.no_penalty: death by pain
    still counts);
  - ignore_negative_morale: a negative morale scale counts as 0 (a positive one still works);
  - speed_multiplier (default 1): derived speed = floor(speed * multiplier);
  - rest_regen_multiplier and rest_regen_bonus: the HP one rest command gives -> floor(gain * multiplier) + bonus,
    never above the max; nothing when the rest gave no HP (assumption Q99);
  - hp_regen_per_tick (default 0): HP healed every tick (honours block_restore hp);
  - overload_enabled (default true): when false a cast adds no overload and the overload never blocks the regen;
  - log_limit (default 0 = unlimited): the journal keeps the last N entries.
- Tests: pain 2 -> attack 0 (count 2); scale -4 -> 0, +4 -> +2; 1.5 -> 30 ft, 0.5 of 25 -> 12; short rest 3 HP with
  x2 + 1 -> 7; hp_regen_per_tick 2; overload off: no overload from a cast, regen not blocked.

## Journal [OWNER, package 14 H]
- One journal for everything: every command that CHANGES the character logs itself through the command base (dispatch):
  order counter, kind (item / item_damage / spell / damage / heal / status / charges / rest / injury / stance / combat /
  other), command id, short params, result, combat round (1 at start_combat, +1 per tick, 0 out of combat).
- Entries store ids and numbers only, no texts (the UI translates through wp/i18n). Old text entries load with their
  command id only. Read-only or softly refused commands (nothing changed) are not logged. No cap by default
  (log_limit 0). No revert.

## Rule switches of races and abilities [OWNER, package 36, decisions 3, 17]
- A declared list in data (wp/rules_data/switches.json), read through one function: at_negative_hp (dying / nothing /
  status:<id>: HP below 0 turns that status of the character on instead of dying), death_pain_cap (= pain_cap),
  heal_percent (every heal by the Heal button is positive energy: -50 = half), exp_percent (-25 = a quarter less
  experience), pain_reduction (effective pain lowered by N, never below 0), natural_regen_percent (the HP of a rest:
  100 = double), injury_points_reduction (a trigger action: OT - N by a button).
- Tests: heal 10 at -50 % -> 5; xp 100 at -25 % -> 75; pain 3 - 2 = 1; a rest gain 3 at +100 % -> 6.
- Damage absorbers (classes_magic.md "Racial damage absorbers") may be limited to damage types and stand after temp HP,
  before HP: the static pool of an azana takes only electricity (7 electric -> the pool -7, HP untouched); mana before
  HP for a ragmal.
