# Resources

## HP and temp HP [OWNER]
- Temp HP = a SEPARATE pool "HP on top of normal". This is why HP can look above max: store temp_hp as its own field,
  never hp_current > hp_max.
- Damage hits temp HP first. Absorbed part does NOT reduce balance.
- Example: 3 temp HP, 7 damage -> temp 0, HP -4, balance -4.
- Usually lasts to end of combat. Otherwise it is a buff with expiry in ticks; buffs can be instant one-shot or timed.
- HP can go below 0.

## Balance [OWNER]
- Second bar next to HP, lost together with HP. Usually balance < HP max.
- Damage that would push balance to -1 or lower: +1 pain (per such hit [?]). Excess goes to trauma points.
- Restored at zero initiative (blocked while overload > 0).
- Trauma points: GM issues penalties for them unless removed otherwise (after session). Injury editor in Rest GUI [BETA].
- Balance FLOORS at 0 (never negative). Overflow = damage - balance. Pain +1 per hit with overflow > 0
  (also when balance is already 0). Overflow -> trauma points (ОТ). HP always loses the full damage.
- Example [OWNER]: balance 1, hit 10 -> HP -10, balance 0, overflow 9 -> trauma +9, pain +1.
  Then hits of 1 and 1 (balance not restored): each HP -1, pain +1, trauma +1 -> totals HP -12, pain 3, trauma 11.
- Damage input: button "take damage" + optional DR/- and Resistance selector (by damage type) applied before the above.
  DR/Resistance come from the sheet's effects. [UI wish]
- Heal/consumables without a special flag never exceed max; "over max" is an explicit exception flag on the effect.

## Pain [OWNER]
- Death at 8 pain (cap can be changed by race/class/feat -> must be editable).
- Sources: balance overflow; ability costs; GM punishment; curses/injuries (permanent, not removed by rest);
  temporary (situational); +1 temporary pain per 3 FULL HP below 0.
- Temp pain from HP = floor(-hp / 3) when hp < 0, else 0. Computed live from CURRENT hp, adds to other pain.
  Examples [OWNER]: hp 0 -> 0; -2 -> 0; -5 -> 1; -7 -> 2; -12 -> 4. Heal -7 by 2 -> -5 -> 1 temp pain gone.
  Do not store it; derive on read (D6).
- Statuses at hp < 0 [OWNER] (player sets manually, no auto-switch assumed):
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
After everyone acted:
1. Buffs/statuses/debuffs lose 1 duration if they can.
2. DoTs (bleed, fast healing, regeneration).
3. Balance restoration. Player picks order of DoT vs balance; assume best for player = balance FIRST
   (while below cap), then DoT damage.
Spec: per tick restore balance (if overload == 0), then DoT.

## Spirit, mana, overload [OWNER]
- Everyone has: HP, balance, balance regen, spirit, trauma points. Spirit pays item activations (1 spirit/day or 5 until session end).
- Casters (mage): mana instead of slots. Divine casters: slots.
- Mage cast cost: mana 1/3/5 by circle AND the same amount of balance. Gains X overload (X = spell duration in rounds).
- Overload > 0 forbids balance regen. New casts add. Other sources add; player may raise it deliberately.
- Non-mage: slots, no balance loss, gets 2X overload. Must be changeable (rule may change).
- Examples: mage casts 3-mana spell lasting 4 rounds: mana -3, balance -3, overload +4.
  Non-mage same spell: slot spent, balance unchanged, overload +8.

## Class resources [OWNER]
- Class pools (Ki, Darkness, Paladin defense points + Holiness) look/work like HP, mana, spirit. Players define in editor/catalog.
- Rage-like buffs show charges left (2/3) and duration; duration ticks with initiative.

## Comfort [OWNER]
- Resource burned during play or exchanged for training. Max formula 5 + 5*level, modifiable by class/race/items.
- Chip goes red when current > max [?] (see OPEN_QUESTIONS).

## Over max [OWNER, confirmed]
- ANY resource (HP, mana, spirit, comfort, ...) may exceed max: usually consumable effects, sometimes narrative (rare).
- Normal gameplay (regen, healing, rest, tick) never raises above max: clamp.
- Manual set / overfill is allowed and must NOT be clamped. Design: two ops: restore(clamps) and set(no clamp, flagged over-max).
- Over-max is shown (red chip), not auto-trimmed. Comfort: player must spend down before next session
  (starts session at its start value); no engine enforcement, only the red indicator.
- Temp HP is still its own pool (see above); over-max HP is a different, rare case.
- So audit A054 (no clamp) is NOT a bug; A053 (crash on HP setter) still is.

## Base, attention, money -> gear.md / narrative.md
