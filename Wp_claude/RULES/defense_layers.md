# Defense layers (AC ladder) [OWNER]

AC = 10 + size + dodge + insight + morale + competence + luck + circumstance + deflection + shield + armor + natural armor.
(Dodge includes Dex: "Dex gives dodge", gear.md. Parry goes into the armor layer: max(armor, parry).)

Layer order: size, dodge, insight, morale, competence, luck, circumstance, deflection, shield, armor (parry here too), natural.
Layer i covers attack rolls from 10 + (sum of the bonuses of the earlier layers) to 10 + (sum including it) - 1.
- Rolls below 10: "did not find a position".
- A roll exactly equal to AC: "hit just barely" (can be played as a maneuver: disarm, trip).
- A roll above AC: "hit".
- A layer with a zero bonus has an empty range.

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
- отклонение: "текст не задан" (the owner will send it)
- щит: "атака попала в щит, полный урон щиту"
- доспех: "атака попала в доспех"
- натуральный доспех: "атака попала, но скользнула без вреда, возможны последствия, например отбросить"
- впритык: "атака попала, но обстоятельства не дали полноценный урон, можно как приём без вреда для атакующего"
- попал: "атака попала"

The UI is not built yet: only the calculation and the data exist.
