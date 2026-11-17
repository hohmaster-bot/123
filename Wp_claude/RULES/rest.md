# Rest

Terms: BP (БП) = pain threshold, a resource shown "cur of max" (e.g. 4/4). Balance is a separate bar (resources.md).

## BP and balance [OWNER]
- BP cap = ceil(max HP / 4) [OWNER, corrected]. Tests: 11->3, 15->4, 19->5, 20->5, 21->6.
- Balance max = current armor bonus (worn armor only; PARRY gives NO balance) + current BP + bonuses (race, class, other).
  Example [OWNER]: 4 max HP -> BP 1; leather armor bonus 2; race +3 -> balance max 6.
  Note: BP is the CURRENT BP, so spending BP on short rest lowers balance max [confirmed by owner formula].
- Balance regen per zero-initiative tick = current level + Con modifier + other (e.g. +1 from unarmed mastery), min 1.
- BP can be lost to bad weather (GM decides) and during rest. BP cur may exceed max (temporary BP): e.g. 2 pain, BP 2/1,
  spend 2 BP to remove 2 pain -> 0/1. Temp BP from rest is deleted after the rest is processed.
- Balance shown as cur/max on sheet; PDF export shows only max.

## Action UI [OWNER]
- App shows the player his actions and which of them cause pain; player taps to mark an action spent
  (or skips if he remembers). Tap when pain is due.

## Long rest [OWNER]
- Restores: all HP, all BP, all pain (except permanent pain from injuries and curses), all ability charges,
  all spells and mana, all spirit, all stats (stat damage; NOT permanent stat damage).
  HP is restored to max, so temp pain from negative HP is gone too.
- Does NOT restore only injuries and curses. Temp HP is not touched (a possible checkbox "clear temp HP" later).
- Items with charges get checkbox "restore charges on long rest"; consumables are not restored.
- Long rest NEVER clears trauma points (OT), comfort, or injury charges: those are reset by hand only [OWNER confirmed].

## Short rest [OWNER]
1. No limit on how many short rests: narrative element, the GM decides.
2. Free gains: +1 BP (if BP < max, BP +1; if BP is at max, +1 temporary BP) and 2 + level HP
   (if race or an effect gives more, the larger value is used).
3. Then the player spends BP from the table (all in one short rest). A repeated 2 + level HP heal costs 1 BP.
   | Effect | Cost |
   |---|---|
   | Repeat 2+LVL HP heal | 1 BP each |
   | Restore daily/session ability charges | 2 BP |
   | Restore all spirit | 2 BP |
   | Restore 1 stat: returns 1 point of stat damage (stats.md) | 1 BP |
   | Remove 1 pain | 1 BP |
   | Restore mana by regen | free once, then 1 BP |
   | Restore divine casts (chance from Court) | 1 BP |
4. Only options with something to restore are shown (stat not damaged -> "Restore 1 stat" hidden; same for every option).
5. Other BP sources (allies, skill checks, class, feats) add BP or temporary BP. Effects can modify rest
   (e.g. owner's race doubles the natural recovery bonus on short rest).
6. "Apply" applies everything; the short rest window closes; excess BP (above max) is lost.
7. Example: level 3, HP 1/20: free +5 HP (2+3); a second heal costs 1 BP.
