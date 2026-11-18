# Defense layers (AC ladder) [OWNER]

Base [OWNER, package 5] = 10 + the sum of ALL PENALTIES (low Dex, a negative dodge sum, any other negative value).
AC = base + size + dodge + insight + morale + competence + luck + circumstance + deflection + shield + armor + flat
+ natural armor. Every layer is >= 0.
(Dodge = dodge bonuses + Dex mod, gear.md "Dex gives dodge". Parry goes into the armor layer: max(armor, parry).)

Layer order: size, dodge, insight, morale, competence, luck, circumstance, deflection, shield, armor (parry here too),
flat, natural.
- Rolls below the base: "did not find a position" (no penalties: 1-9).
- The layers follow the base one after another: layer i covers rolls from base + (sum of the earlier layers) to
  base + (sum including it) - 1.
- A roll exactly equal to AC: "hit just barely" (can be played as a maneuver: disarm, trip).
- A roll above AC: "hit".
- A layer with a zero bonus has an empty range.

## Penalties, dodge, flat [OWNER, packages 4-5]
- No negative layers. Every negative part is a penalty and lowers the base.
- Dodge layer = dodge bonuses + Dex mod (they add up). If the sum is negative, the negative part is a penalty
  (lowers the base) and the dodge layer is 0.
- "flat" = only positive untyped bonuses; it comes after armor, before natural armor.
- Flat-footed: ALL POSITIVE parts of dodge are lost (dodge bonuses and the Dex bonus); the low-Dex penalty stays and
  still lowers the base.
- Enhancement [OWNER, Q26]: armor enhancement raises the armor bonus itself (the "armor" layer).
- Other types without a layer (sacred, profane, ...) are not shown as a layer; a positive one goes to "flat", a
  negative one is a penalty (assumption).
- The ladder is a hint; the real AC = base + the sum of the layers.
- Examples [OWNER]: Dex -2, armor 8: base 8, position 1-7, armor 8-15, hit just barely 16, hit 17+; flat-footed the
  same. Dex -2 and dodge +1: sum -1, base 9, dodge layer 0. Dex +2 and dodge +1: dodge 3, flat-footed 0.
- Tests: the examples above; +2 untyped after armor moves natural armor up by 2; untyped +3 and -1: flat 3, base 9;
  enhancement +2 on armor 4 -> armor layer 6; no layer below 0.

Example, +1 of every type: 1-9 position, 10 size, 11 dodge, 12 insight, 13 morale, 14 competence, 15 luck,
16 circumstance, 17 deflection, 18 shield, 19 armor, 20 natural armor, 21 hit just barely, 22+ hit.

## Owner texts (bound to the layer TYPE, stored as data: wp/catalog/data/defense_layers.json)
- позиция: "противник не нашёл позиции для атаки или промахнулся мимо стоящего противника"
- размер: "атака промахнулась из-за размера цели"
- уклонение: "цель увернулась и может отойти на 5 футов (малое и среднее), на 10 (большое и выше); при исключительной ловкости можно дальше"
- предвидение: "то же, что уклонение, но без смещения"
- мораль: "цель на кураже или по другим причинам приняла атаку без вреда"
- компетентность: "цель благодаря боевым навыкам не дала себя атаковать"
- удача: "цели повезло, атака прошла без вреда"
- обстоятельства: "обстоятельства помешали попасть, например укрытие"
- отклонение (оно же отражение): "атака отражена (отклонена) в сторону"
- щит: "атака попала в щит, полный урон щиту"
- доспех: "атака попала в доспех"
- flat (беззнаковые бонусы): "текст не задан" (the owner will send it)
- натуральный доспех: "атака попала, но скользнула без вреда, возможны последствия, например отбросить"
- впритык: "атака попала, но обстоятельства не дали полноценный урон, можно как приём без вреда для атакующего"
- попал: "атака попала"

The UI is not built yet: only the calculation and the data exist.
