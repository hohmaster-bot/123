# Rest

Terms: BP (БП) = pain threshold, a resource shown "cur of max" (e.g. 4/4). Balance is a separate bar (resources.md).

## BP and balance [OWNER]
- BP cap = ceil(max HP / 4) [OWNER, corrected]. Tests: 11->3, 15->4, 19->5, 20->5, 21->6.
- Balance max = current armor bonus (worn armor only; PARRY gives NO balance) + current BP (BP above max included)
  [OWNER] + bonuses (race, class, other) + the shield bonus of a heavy/tower shield in a hand (training.md).
  Example [OWNER]: 4 max HP -> BP 1; leather armor bonus 2; race +3 -> balance max 6.
  Note: BP is the CURRENT BP, so spending BP on short rest lowers balance max [confirmed by owner formula].
- Balance regen per zero-initiative tick = current level + Con modifier + other (e.g. +1 from unarmed mastery), min 1.
- BP can be lost to bad weather (GM decides) and during rest. BP cur may exceed max: e.g. 2 pain, BP 2/1,
  spend 2 BP to remove 2 pain -> 0/1.
- Overcap [OWNER, package 8]: BP above max (e.g. narrative temporary BP) is stored simply as BP above max; there is no
  separate temporary BP. Short rest: parameter keep_overcap (default off): off -> the excess is lost at "Apply";
  on -> it is kept. Long rest and end of cycle ALWAYS drop it (BP = max). The player may also fix it by hand.
  Tests: 5/5 short rest (+1) -> 5; keep_overcap -> 6/5 (balance max 6); long rest 7/5 -> 5; end of cycle 7/5 -> 5;
  ordinary BP 7/5 before a short rest -> 5 after.
- Balance shown as cur/max on sheet; PDF export shows only max.

## Action UI [OWNER]
- App shows the player his actions and which of them cause pain; player taps to mark an action spent
  (or skips if he remembers). Tap when pain is due.

## Long rest [OWNER]
- [OWNER, package 16 A5] Refused during combat (reason combat_active); the UI asks "end combat?" and then
  calls long_rest_end_combat (ends the combat exactly like end_combat, then the long rest).
- Long rest and end of cycle are separate buttons; one never triggers the other (narrative.md).
- Restores: all HP, all BP (exactly to max), all pain (except permanent pain from injuries and curses), all ability
  charges, all spells and mana (racial mana too, also when the "mana" magic option is off [OWNER, package 8 R18]),
  all spirit, all stats (stat damage; NOT permanent stat damage).
  HP is restored to max, so temp pain from negative HP is gone too.
- Long rest also resets overload to 0 and sets balance to its max [OWNER confirmed].
- Does NOT restore only injuries and curses. Temp HP is not touched (a possible checkbox "clear temp HP" later).
- Items with charges get checkbox "restore charges on long rest"; consumables are not restored.
- Long rest NEVER clears trauma points (OT), comfort, or injury charges: those are reset by hand only [OWNER confirmed].

## Short rest [OWNER]
- [package 17] Effects "short_rest_heal" (added to the free heal after the "larger of" rule) and
  "short_rest_bp" (extra BP) change the free gains.
1. No limit on how many short rests: narrative element, the GM decides.
2. Free gains: +1 BP (at max it goes above max: overcap) and 2 + level HP
   (if race or an effect gives more, the larger value is used).
3. Then the player spends BP from the table (all in one short rest). A repeated 2 + level HP heal costs 1 BP.
   | Effect | Cost |
   |---|---|
   | Repeat 2+LVL HP heal | 1 BP each |
   | Restore daily/session ability charges | 2 BP |
   | Restore all spirit | 2 BP |
   | Restore 1 stat: returns 1 point of stat damage (stats.md) | 1 BP |
   | Remove 1 pain | 1 BP |
   | Restore mana by regen (the rest regeneration; a GM / ability restore is restore_mana, classes_magic.md) | free once, then 1 BP |
   | Restore divine casts (chance from Court; only for a character with divine slots [OWNER, package 8]) | 1 BP |
4. Only options with something to restore are shown (stat not damaged -> "Restore 1 stat" hidden; same for every option).
5. Other BP sources (allies, skill checks, class, feats) add BP (may go above max). Effects can modify rest
   (e.g. owner's race doubles the natural recovery bonus on short rest).
6. "Apply" applies everything; the short rest window closes; excess BP (above max) is lost unless keep_overcap
   [OWNER, package 8]; ALL temp HP are cleared [OWNER].
7. Example: level 3, HP 1/20: free +5 HP (2+3); a second heal costs 1 BP.

## What is restored when [package 22 B8: a summary of the current rules, nothing new]
| What | Short rest | Long rest | Combat start | Combat end | Zero-initiative tick | Cycle end | Manual |
|---|---|---|---|---|---|---|---|
| HP | free 2 + level (or the larger effect), more for 1 BP each | to max | - | - | heals per tick; rule switch hp_regen_per_tick | - | restore, set_value |
| Temp HP | ALL cleared | not touched | - | "until end of combat" ones go | ended statuses take theirs | - | set_temp_hp |
| BP | +1 free (may go above max), overcap lost at Apply | exactly to max | - | - | - | BP above max dropped | spend_bp, set_value |
| Balance | - | to max | the cap is taken (snapshot) | the cap is computed again | regen (not while spell overload > 0) | - | restore, set_value, restore_all_balance (master pick) |
| Mana | "restore mana by regen" (free once, then 1 BP) | all | - | - | per_tick_restore of statuses | - | restore_mana |
| Spirit | "restore all spirit" (2 BP) | all | - | - | per_tick_restore of statuses | - | restore, set_value |
| Pools | restore "short_rest" | restore "long_rest" and "short_rest" | restore "combat_start" | - | per-round payments, per_tick_restore | - | restore_pool, edit_pool |
| Usage charges | recharge "short_rest" | "long_rest" and "short_rest" | "combat_start" | "combat_end" (master picks) | cooldowns -1 | - | restore_charges, set_charges |
| Status charges | follow the source; option "restore charges" (2 BP) | follow the source (Q108) | follow the source | follow the source | per-round payment | - | set_charges, restore_charges |
| Reactions | - | - | - | to max | to max | - | restore_reactions |
| Stats (damage) | "restore 1 stat" (1 BP) | all (not permanent damage) | - | - | - | - | edit |
| Pain | "remove 1 pain" (1 BP) | all except permanent | - | - | - | - | edit |
| Spell overload | - | 0 | - | 0 | -1 | - | edit |
| Morale scale | - | - | - | 0 | - | - | edit |
| Injuries / OT | never | never | - | - | - | - | add / remove injury, OT by comfort / attention |
| Comfort | never | never | - | - | - | - | exchange, edit |
| Attention, OV | - | - | - | - | - | attention + income, OV burned | convert, spend |
