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
- Restores ALL charges automatically EXCEPT injuries (and not consumables/items).
- Items with charges get checkbox "restore charges on long rest".
- Class, race, feat, quirk charges, spirit, mana, slots, ki etc: all restored.
- Long rest NEVER clears trauma points (OT), comfort, or injury charges: those are reset by hand only [OWNER confirmed].
- Long rest removes ALL pain except permanent sources (injuries, curses). Permanent pain stays.
  HP is restored to max, so temp pain from negative HP is gone too.

## Short rest [OWNER]
- No limit on how many short rests: narrative element, the GM decides.
- BP is restored during a short rest.
- Then BP can be spent as a currency (all in one short rest):
  | Effect | Cost |
  |---|---|
  | Restore 1 BP | free, once |
  | Restore 2+LVL HP | free once, further times 1 BP each |
  | Restore daily/session ability charges | 2 BP |
  | Restore all spirit | 2 BP |
  | Restore 1 stat: returns 1 point of stat damage (stats.md) | 1 BP |
  | Remove 1 pain | 1 BP |
  | Restore mana by regen | free once, then 1 BP |
  | Restore divine casts (chance from Court) | 1 BP |
- Short rest gives +1 BP "temporary" even if BP is full: can be spent from the list (stat or pain). Allies can give more.
  Skill checks, class, feats etc can add more BP. Prepare logic for a convenient spend menu later.
- Effects can modify rest: e.g. owner's race doubles natural recovery bonus on short rest.
- Short rest heal: 2+level HP (free). Example: level 3, 1/5 HP: +5 free; a second restore costs 1 BP.
- Example: level 3, 1/5 HP: free HP restore +5 (2+3); second restore costs 1 BP.
- Short rest also restores 2 + level HP for free (if race or an effect gives more, the larger value is used).
  A repeated 2 + level HP heal costs 1 BP, as in the spend table.

### Short rest flow [OWNER decision]
- Short rest gives 1 BP for free: if BP < max, BP +1; if BP is already at max, +1 temporary BP.
- Then the player spends BP from the list. An option is shown only if there is something to restore
  (stat not damaged -> "Restore 1 stat" hidden; same for every option).
- Other BP sources may add BP or temporary BP.
- "Apply" applies everything. The short rest window closes; excess BP (above max) is lost.
- Short rest has no limit on how many times.
