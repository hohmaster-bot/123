# Defense layers (AC ladder) [OWNER]

AC = 10 + size + dodge + insight + morale + competence + luck + circumstance + deflection + shield + armor + flat + natural armor.
(Dodge = dodge bonuses + Dex mod, gear.md "Dex gives dodge". Parry goes into the armor layer: max(armor, parry).)

Layer order: size, dodge, insight, morale, competence, luck, circumstance, deflection, shield, armor (parry here too),
flat, natural.
Layer i covers attack rolls from 10 + (sum of the bonuses of the earlier layers) to 10 + (sum including it) - 1.
- Rolls below 10: "did not find a position".
- A roll exactly equal to AC: "hit just barely" (can be played as a maneuver: disarm, trip).
- A roll above AC: "hit".
- A layer with a zero bonus has an empty range.

## Flat layer and penalties [OWNER, packages 4-5]
- The "flat" layer comes AFTER armor (before natural armor).
- It holds all untyped bonuses and ALL negative parts.
- No negative layers: a typed layer is never below 0; its negative part goes to "flat".
- Dodge layer [OWNER pkg 5] = dodge bonuses + Dex mod (they add up). If the sum is negative, the negative part goes
  to "flat" and the dodge layer is 0.
- Flat-footed [OWNER pkg 5]: ALL POSITIVE parts are lost (dodge bonuses and the Dex bonus); the low-Dex penalty stays
  (in "flat").
  Examples: Dex -2 and dodge +1: normal flat -1, flat-footed flat -2. Dex +2 and dodge +1: dodge 3, flat-footed 0.
- The ladder is a hint; the real AC = 10 + the sum of the layers (always equal, no "unlisted" part).
- Enhancement [OWNER, Q26]: armor enhancement raises the armor bonus itself (the "armor" layer), not "flat".
- Other types without a layer (sacred, profane, ...) are not shown in the ladder; in AC they go to "flat" (assumption).
- Tests: +2 untyped after armor moves natural armor up by 2; Dex -2 -> flat -2; flat-footed Dex -2 -> flat still -2;
  no typed layer is below 0; the examples above; enhancement +2 on armor 4 -> armor layer 6.

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
- flat: "текст не задан" (the owner will send it)
- натуральный доспех: "атака попала, но скользнула без вреда, возможны последствия, например отбросить"
- впритык: "атака попала, но обстоятельства не дали полноценный урон, можно как приём без вреда для атакующего"
- попал: "атака попала"

The UI is not built yet: only the calculation and the data exist.
