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
Order for incoming damage of a type:
1. Percent reduction of damage: 25 / 50 / 75 % (usually race, items too). Official name TBD (owner: do not name it "resist"; GUI name later).
2. Flat reduction BY DAMAGE TYPE [OWNER]: one mechanism. "DR/-" is just the flat resist to PHYSICAL damage; fire resist etc. are other types.
   DR does not work on fire. Damage may have several components, each handled by its own type:
   fire sword hit = 8 physical + 3 fire -> physical part uses DR/physical resist, fire part uses fire resist.
   Overlap of two reductions on one component is not modeled for now. Before taking damage the player can pick which
   reduction applies (gear icon next to Take damage); a setting may allow summing them.
3. Temp HP.
4. Temp-HP analogs (e.g. racial: damage hits MANA first; others possible), in a configurable order.
5. HP (and balance, see below). Only the part that reaches HP touches balance.
Rounding [OWNER]: damage is never fractional; round UP (against the player). 10 dmg, 25% -> 7.5 -> 8.
Example: 10 fire, percent 50% -> 5, flat 2 -> 3, temp HP 0 -> HP -3, balance -3.
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
- Balance cap in combat [OWNER homerule, package 9, closes Q35; the stored snapshot accepted, Q54]: start of combat
  takes a SNAPSHOT of the balance max
  (armor + current BP + bonuses at that moment). During combat the cap changes ONLY by hits (below); it does NOT change
  from a max HP change (e.g. Con lowered), spending BP, taking armor off/on or any bonus change. End of combat
  recomputes the cap from scratch and clears the snapshot. Balance REGEN stays live (current Con etc.).
  Tests: snapshot 7 (armor 2 + BP 5); spend 2 BP -> 7; armor off -> 7; bonus +3 and Con 14 -> 8 -> 7 (regen 3 -> 1);
  a hit -> 6; end of combat with BP 3 and no armor -> 3.
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
2. Balance restoration (if overload == 0).
3. DoTs (bleed, fast healing, regeneration) - balance first, then DoT (best for the player).
- DoT and regen last exactly their duration [OWNER]: N rounds = N ticks (bleed for 3 rounds hits exactly 3 times).
- Overload is a number: -1 per zero-initiative tick; at 0 it is gone. End of combat resets it to 0 [OWNER].
  Order inside the tick: the regen check uses the overload at the START of the tick, then overload drops by 1
  (overload 1: no regen in this tick, overload 0, regen in the next tick).
- Damage from the "dying" state and from DoT goes through temp HP and balance like an ordinary hit (temp HP and
  analogs first, then HP and balance; overflow -> OT and +1 pain).

## Spirit, mana, overload [OWNER]
- Everyone has: HP, balance, balance regen, spirit, trauma points. Spirit pays item activations (1 spirit/day or 5 until the end of the cycle).
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

## Over max [OWNER, confirmed]
- ANY resource (HP, mana, spirit, comfort, ...) may exceed max: usually consumable effects, sometimes narrative (rare).
- Normal gameplay (regen, healing, rest, tick) never raises above max: clamp.
- Manual set / overfill is allowed and must NOT be clamped. Design: two ops: restore(clamps) and set(no clamp, flagged over-max).
- Over-max is shown (red chip), not auto-trimmed. Comfort: player must spend down before next session
  (starts session at its start value); no engine enforcement, only the red indicator.
- Temp HP is still its own pool (see above); over-max HP is a different, rare case.
- So audit A054 (no clamp) is NOT a bug; A053 (crash on HP setter) still is.

## Base, attention, money -> gear.md / narrative.md
