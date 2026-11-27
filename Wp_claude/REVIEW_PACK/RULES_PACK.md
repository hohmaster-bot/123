# WipeFinder rules pack for an independent review

## What this is
WipeFinder is a character-tracking app for a homebrew tabletop RPG based on Pathfinder 1e with MANY house rules.
The app tracks resources (HP, balance, pain, mana, spirit, comfort...), statuses, abilities, items and training
purchases for one character. It does NOT roll dice and does NOT run the game: the players roll, the app records the
results and computes the derived numbers.

## What you get
- Every rule file of the project (the owner's rules; the text is the truth, the app follows it), in a fixed order.
- A glossary of the house terms.
- The data tables that hold rule numbers (each number can be changed per character in the app's settings).
Owner quotes in Russian are kept verbatim; the English text around them is the working translation.
Tags: [OWNER] = stated by the owner; [?] = unclear; [BETA] = unfinished; "package N" = the work step that added it;
"Qnn" = a question that was asked and answered (the answer is written next to it).

## What this is NOT
Not a play-test report, not the program code, not the test suite, not a design document of the screens.

## Your review task
1. Find contradictions between files and inside a file.
2. Find ambiguous rules that two readers would implement differently: quote the line and give both readings.
3. Find missing rules: a mechanic that is mentioned but has no numbers or no owner decision.
4. Find rules that are likely to cause bad play or exploits (stacking, resource loops, the balance cap, free actions)
   and say why.
5. Find unnecessary complexity: rules that could be merged or dropped without losing the intent.
6. Rate each domain 1-10 for clarity: combat, defense, resources, rest, gear, training, skills, spells, narrative;
   then give a top-10 list of fixes.

Please answer in one table:

| id | file / section | type (contradiction / ambiguity / missing / balance / complexity) | quote | suggested fix |
|---|---|---|---|---|

then the domain ratings and the top-10 list.

## Кратко по-русски

Это полный набор правил WipeFinder для независимой проверки. Приложение ведёт персонажа (ресурсы, статусы, способности) и не бросает кубики. Задача проверяющего: найти противоречия, неясности, пробелы, дыры в балансе и лишнюю сложность, оценить каждую область от 1 до 10 и дать список из 10 главных правок. Ответ — в таблице выше.

## Contents

- index.md
- defense_layers.md
- defense.md
- combat.md
- buffs.md
- rest.md
- injuries.md
- classes_magic.md
- resources.md
- gear.md
- progression.md
- skills.md
- weapons.md
- narrative.md
- catalog.md
- spells.md
- skills_list.md
- stats.md
- training.md
- crafting.md
- doll.md
- races.md
- Appendix (drafts, not built): ac_zones.md
- Data tables

## Glossary

| term | meaning |
|---|---|
| Balance | a second bar next to HP, lost together with HP; regenerates every round (zero-initiative tick). |
| Balance cap | the balance max taken at the start of combat; each hit lowers it by 1 until the end of combat. |
| BP | pain threshold points (cur / max); spent in the short rest; can be above max (overcap). |
| OT | trauma points: damage that went past the balance; removed by injuries, comfort, attention. |
| Pain | a counter; -1 to all rolls per pain (default); death at the death cap (default 8). |
| Temp HP | absorb damage first; 'by button' temp HP last to the short rest, a buff's temp HP last with the buff. |
| Spirit | pays item activations ('day' = until the short rest, 'decade' = until the long rest). |
| Overload | a counter from spell casting; blocks the balance regen while above 0; -1 per tick. |
| Comfort | a resource exchanged for training or for removing OT. |
| Attention | a narrative resource from the end of a cycle; converted into OV, training, base points, OT removal. |
| OV | time points (narrative); burn at the end of a cycle. |
| Zero-initiative tick | the end of a round: durations -1, balance regen, damage over time, overload -1. |
| Status | a buff / debuff / situation with effects, duration, charges; active or not. |
| Effect | a typed bonus on a target (any sheet number); same type: the larger wins; flat and dodge add. |
| AC ladder / layers | AC is built in layers (base, flat, armor/parry, natural, shield, dodge...); the layer an attack roll landed in decides what happens. |
| Parry | an AC layer from proficiency (armor grades, odd levels, tower shields) and weapon mastery. |
| Weapon mastery | grades 0-12 per weapon group; picks at specialist (5-7), expert (8-11) and master (12). |
| Training | points spent on purchases (stats, skills, weapon grades, feats, spells...). |
| Base | a home with slots for items and blessings; items at the base give effects. |
| Doll | 22 equipment slots; one item per slot; the hands slot holds up to 2 hands of items. |
| Court | a narrative parameter 'Name LtT' (level, tier). |
| Lens | a narrative goal counter 0..X; 0 = red end, X = green end. |
| Drive | a narrative motive, level 0..5; drives at 4+ give attention at the end of a cycle. |
| Quirk / seed | a narrative ability (may carry effects); a seed is bought and later sprouted into a quirk. |
| Template | a race / class-like package of effects, hit dice, feats, pools, statuses. |
| Pool | a character resource such as Ki (max may be a formula). |
| Iterative penalty | each further attack in a round: -5 (data), reset every round. |
| Package N / Qnn | the work step that added a rule / a question the owner answered. |

## File: index.md

### RULES index

WipeFinder = Pathfinder 1e + many house rules. Owner's rules are the truth; code and audit are not.
Status tags: [OWNER] stated by owner; [?] unclear, see OPEN_QUESTIONS; [BETA] owner says unfinished.
Each file: rules, then numeric examples (use them as tests).

| File | Covers |
|---|---|
| defense_layers.md | AC ladder: which layer an attack roll landed in, owner texts per layer |
| ac_zones.md | AC by direction, 3x3 cells, shield coverage (owner draft); variants and settings built in package 24 |
| defense.md | AC types, positioning, touch, typed bonuses, morale |
| combat.md | actions, iterative attacks, crit, lucky attack, maneuvers, size, spells dmg |
| buffs.md | effects, buffs, duration, charges |
| rest.md | short rest, long rest, BP |
| injuries.md | trauma points, injuries |
| classes_magic.md | class editor tabs, mana/slots restore |
| resources.md | HP, temp HP, balance, pain, trauma points, spirit, mana, overload, comfort, class resources, zero initiative, buffs |
| gear.md | doll, hands, belt, bag, weight/load, base, armor, qualification, item codes |
| progression.md | level up, training, weapon mastery, spell mastery |
| skills.md | skill categories and costs |
| weapons.md | weapon proficiency levels, costs, bonuses |
| narrative.md | quirks, stories, courts, quests, drives, attention |
| catalog.md | catalogs, sharing, sorting |
| spells.md | spell record, effect link, damage editor [BETA], stance = feat checkbox |
| skills_list.md | default skill catalog (45 templates, data, owner text) |
| stats.md | stat damage, current/max, permanent stat damage |
| training.md | modes (play/training/edit), sources and cost, ability/armor/shield/language prices, seeds, qualification, professionalism, attention course |
| crafting.md | recipes, OV, craft DC, unusual items, ILVL |
| doll.md | 22 doll slots |
| races.md | races: what a race stores, taking / changing a race, paid traits, languages, movement (package 36) |

Cross-cutting: ANY part of the sheet (item, feat, race, class, injury, quirk, buff) can change ANY base parameter
(stats, resources, regen, caps, forbid recovery, add resources). Model this as one generic effect system.

## File: defense_layers.md

### Defense layers (AC ladder) [OWNER]

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

#### Penalties, dodge, flat [OWNER, packages 4-5]
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

#### Owner texts (bound to the layer TYPE, stored as data: wp/catalog/data/defense_layers.json)
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

## File: defense.md

### Defense

#### Positioning [OWNER]
- Front attack: full AC.
- Flank (shield side): attacker may ignore shield bonus (incl. spell shields, e.g. weapon-side).
  [OWNER, package 8] The AC calculation has a checkbox "flank drops shield" (default on). Test: shield 2, flank: 10;
  checkbox off: 12.
- [OWNER, package 8] An attack made with a shield cancels the shield bonus to AC until the next turn (the attack view
  marks it; the AC is computed with the shield switched off).
- Flat-footed ("in surprise"): AC without the Dex BONUS and without ALL dodge bonus; a penalty from low Dex stays [OWNER].
  Shield counts only if attack comes from shield side. Example: Dex -2: front AC 8, flat-footed 8.
- Parry: same bonus type as armor. If no armor or parry > armor, player usually picks parry. Front only.
  Parry value [OWNER, package 5] = armor proficiency (none 0, light 2, medium 4, heavy 6) + 1 per odd level from 3
  + 2 for the "tower shields" proficiency grade + weapon mastery parry picks. It comes from PROFICIENCY, not from an
  item in the hand (training.md).
- Touch: ignores natural armor, shield, parry, armor bonuses; only the armor's "touch AC" bonus counts, as the armor
  layer of the touch AC (gear.md "Armor", package 9).
- Need UI toggle: shield bonus on/off in AC, or show small secondary number "AC with shield".

#### Typed bonus pools [OWNER]
- AC-only types: exactly five: armor (incl. parry), natural armor, shield, dodge, deflection.
  Can come from any ability/class/etc but apply only to AC.
- Other bonuses (list in modifiers.py) apply to rolls: attack, damage (usually not spells), saves, skills.
- Stacking [OWNER decision]: a bonus and a penalty of the SAME type do not add up; the value with the larger
  absolute value wins; equal absolute values -> 0. Examples: +3 and -4 -> -4; +3 and -1 -> +3; +2 and -2 -> 0.
- Only flat stacks with itself; on AC dodge also stacks. Weapon proficiency bonuses stack with themselves and apply
  only to attacks with that weapon.
- Computed separately for each target (attack, damage, save, skill, AC...).
  Example: morale scale +1 on everything and a spell's morale penalty -2 on attacks -> attacks -2, everything else +1.
  Heroism +4 morale on attacks with morale scale -1 -> attacks +4, everything else -1.
- Example: +1 enchanted sword, "magic weapon" status gives +1 enchant -> result +1, not +2.

#### Saves and initiative [package 10; Q55, Q56, Q61 answered in package 11]
- Save (Fort, Ref, Will) = base (typed by hand, like BAB [OWNER, Q61]) + stat mod ([OWNER, Q55] Fort Con, Ref Dex,
  Will Wis, as in PF; stored as data) + typed bonuses (target "save" = all
  saves, "save:fort" / "save:ref" / "save:will" = one save; stacked by the normal rules) + pain + morale.
  Tests: base 3/1/2 with Con 14, Dex 12, Wis 8 -> 5/2/1; +1 resistance to all and +2 resistance to Fort -> Fort 7,
  Ref 3, Will 2; pain 2 -> -2 each; morale scale 4 in combat -> +2 each.
- Initiative = Dex mod + typed bonuses (target "initiative") + pain (resources.md: every roll with a die) + morale.
  [OWNER, Q56] Morale applies to initiative. Morale exists only in combat and starts at 0, so the initiative roll
  before combat has no morale; a reroll during combat includes it. Test: Dex 14 + 2 competence -> 4; pain 1 -> 3;
  morale scale 2 in combat -> 5; the same scale out of combat -> 4.

#### Morale (battle) [OWNER]
- Scale is physically -10..+10. A class effect may "count morale X higher at the player's choice".
  Bonuses and penalties to morale (typed bonuses) are not limited by the scale.
- Bonus to ALL rolls (skills, saves, attacks, maneuvers, CMB, damage, initiative [Q56]), type "morale";
  NOT to the lucky attack die, the crit die or AC.
- bonus = trunc(scale / 2): -10 -> -5, +10 -> +5, +/-1 per 2 steps.
- Only while combat is active. One button start/end combat (text switches). Inactive -> morale ignored.
- End of combat resets the morale scale to 0 [OWNER].
- At <= -5 show "We are losing!", at >= +5 "We are winning!". Nice-to-have: record max/min morale of the fight.
- Examples: scale 3 -> +1; scale -4 -> -2; scale 1 -> 0.

#### Does NOT receive roll bonuses
- Crit confirmation die and lucky attack die (see combat.md).


#### Damage pipeline [package 22 B6: the ONE text, checked against the code wp/core/damage.py]
For every part of a hit (each damage type on its own), in this order:
1. the steps of rules_settings.damage_order (data; default):
   a. percent reduction typed for the hit (25 / 50 / 75 %), rounded up;
   b. flat reduction: the larger of the total DR (physical types; Q115 stacking) and resist:<type> (Q119);
   c. the signed percent modifier "percent:<type>" (-100 immunity ... +50 more), rounded up;
2. the parts are added up; the sum goes to temp HP first;
3. then to the temp-HP analogs (absorbers, e.g. racial mana), in their order;
4. what is left reaches HP, and the same amount lowers the balance (floored at 0);
5. what the balance could not take is the overflow: -> OT, and +1 pain for the hit.
(The owner's list in package 22 named "percent modifier -> flat -> absorbers -> temp HP"; the code does a, b, c as
above and temp HP BEFORE the absorbers; the owner confirmed this order: Q151, closed in package 24, ARCH/decision_log.md.)

#### Damage order and percent modifiers [OWNER, package 17]
- Effect target "percent:<damage type>": a SIGNED percent: -100 = immunity, -50 = half, +50 = takes 50% more. One value
  per type on a character: with several sources the larger absolute value wins (equal + and - -> 0, like typed
  bonuses); never below -100. Rounded UP (against the player).
- Steps of one damage part, in the order of rules_settings.damage_order (data; default "percent", "flat", "modifier"):
  1. percent reduction typed for the hit (25 / 50 / 75 %); 2. flat: the larger of DR (physical) and resist:<type>;
  3. the signed percent modifier. Then temp HP, absorbers, HP (resources.md).
- Tests: cold -100: 10 -> 0; fire +50: 10 -> 15; +50 and -25 -> +50; +25 and -50 -> -50; resist fire 2 then +50:
  (10 - 2) * 1.5 = 12; with the modifier first: 15 - 2 = 13; 5 with +50 -> 7.5 -> 8.
- Damage types: data (wp/catalog/data/damage_types.json); "cold" added in package 17 (the owner's immunity example);
  "water" does not exist [OWNER, closes Q130]: 12 types.

## File: combat.md

### Combat

#### Actions [OWNER]
- Shift 1, Move 1, Standard 2, Full-round 3, Complete round 4 actions.
- [OWNER, package 26 A] Actions are a resource: 3 per turn (data constant), effects "actions_max" add more (spells,
  abilities, items, statuses; typed stacking). They come back on the zero-initiative tick and at the end of combat.
  Attack records, maneuvers, quick buttons and spells may show a cost in actions (the costs above are presets);
  nothing is spent automatically: the player presses spend.

#### Attack tag and iteration [OWNER]
- Options spent in own turn may carry tag "attack" (player sets tags himself, spells needing attack roll too).
- 2nd tagged option: -5, 3rd: -10. Paired (two-weapon) attacks: penalty applies to both.
- Abilities without the tag take no iterative penalty.
- [OWNER, package 22 A5] A paired (two-weapon) combination is ONE action and ONE use: the iterative counter +1 per
  combination (not +2); the TWF table penalties stay. Test: a combination, then a normal attack -> -5, not -10.
- Some abilities/effects ignore the iterative penalty WITHOUT being tagged as an attack (effect flag, e.g. master bonus: one attack per turn has no [attack] tag).
- [OWNER, package 16 C] The iterative penalty is its own NEGATIVE line "iterative" on the attack, never typed by the
  player: Character.iterative_count = attacks already used in this round's series. use_attack(rid) (the "attack"
  button) adds 1; the zero-initiative tick (new round) and end_combat set it to 0; set_iterative_count(n) sets it by
  hand. Step: rules_settings.iterative_step (default -5, data) or the record's own iterative_step; effects
  "iterative_penalty" make each step smaller (a step never goes above 0). Penalty of the next attack = count * step.
  A status with ignores_iterative: no penalty. Effect.when_iterative is stored only (no formula yet).
  Tests: 3 attacks 0 / -5 / -10; reduction 2 -> 0 / -3 / -6; reset by the tick; manual set 2 -> -10; record step -3.

#### Crit [OWNER]
- Notation 19+ / 20+ = threat range, x2. "x2/x3/x4" alone = crit on 20.
- [OWNER, package 17, closes Q113] Weapon mastery gives +1 crit range per "crit +1" pick, at most 3 picks (one in
  each tier: specialist, expert, master). Keen property or similar feat doubles the BASE threat range only.
- Item must store: base crit + modifiers from mastery and properties. Crit range must be modifiable by feats.
- [package 10, R8] The attack view shows the crit range: the weapon's base range, "keen" (item property) doubles the
  BASE range, each mastery pick "crit +1" and each feat effect (target "crit_range", for this weapon) widen it by 1;
  never below 2; next to the multiplier hint. Tests: dagger 19+ -> 19 (x2, hint +0); with "crit +1" -> 18; keen -> 17;
  feat +1 -> 18.
- The crit confirmation roll already includes bonuses and penalties (rolled by the player); the core does not touch it [OWNER].
- Tooltip only (house-rule note, no calculation) when confirming a crit: x2 -> +0, x3 -> +4, x4 -> +8.

#### Lucky attack [OWNER]
- Separate die, no bonuses/penalties. Base 20.
- +1 (lowers threshold) up to 3 times from mastery, plus X where X = weapon enchant level.
- Class/race/feat/ability can add +N for a specific weapon.
- [package 10, R7] Such an effect has target "lucky" (with a weapon id = that weapon only; no weapon id = every
  weapon). The cap 3 is for MASTERY picks only, as written above [OWNER, Q60: keep as written]. Tests: enchant +2 -> 18;
  + one mastery pick -> 17; + a feat +1 for this weapon -> 16; a feat for another weapon -> no change; 4 mastery picks
  (forced) + enchant 2 + feat 1 -> 20 - 3 - 2 - 1 = 14. Never below 2.

#### Attack records [OWNER]
- An attack record = weapon + chosen weapon group + grip (one hand, off-hand, two hands) + attack stat (default Str).
  One weapon may have several records (e.g. "Longsword + Long swords" and "Longsword + Heavy blades").
  Each record shows to hit, damage and parry with sources.
- Attacks are shown only for weapons held in the hands (doll: two hands, gear.md), plus the unarmed attack always.
- Primary records: the player marks up to two records as primary (e.g. one per hand). A single record is primary
  automatically. Passive group bonuses (balance regen +1 etc.) come from the primary records. Two primary records
  with DIFFERENT weapon groups: their passive bonuses add up; the same group counts once [OWNER, Q16].
- Grip [OWNER, Q19]: a one-handed weapon may be held with two hands (Str x1.5) only if it is NOT a finesse weapon.
  A finesse weapon: one hand or off-hand only. A two-handed weapon: two hands only.
- Str to damage by grip [OWNER]: one hand 1x, off-hand 0.5x, two hands 1.5x of the Str modifier; a positive value is
  multiplied and rounded DOWN (mod 3: two hands 4, off-hand 1); a negative modifier is NOT multiplied (-2 with any grip).

#### Two-weapon fighting [OWNER, verbatim]
"If you wield a second weapon in your off hand, you can get one extra attack per round with that weapon. You suffer a -6 penalty with your regular attack or attacks with your primary hand and a -10 penalty to the attack with your off hand when you fight this way. You can reduce these penalties in two ways. First, if your off-hand weapon is light, the penalties are reduced by 2 each. An unarmed strike is always considered light. Second, the Two-Weapon Fighting feat lessens the primary hand penalty by 2, and the off-hand penalty by 6. Double Weapons: You can use a double weapon to make an extra attack with the off-hand end of the weapon as if you were fighting with two weapons. The penalties apply as if the off-hand end of the weapon was a light weapon. Thrown Weapons: The same rules apply when you throw a weapon from each hand. Treat a dart or shuriken as a light weapon, and a bolas, javelin, net, or sling as a one-handed weapon."

| Case | Primary hand | Off hand |
|---|---|---|
| Normal penalties | -6 | -10 |
| Off-hand weapon is light | -4 | -8 |
| Two-Weapon Fighting feat | -4 | -4 |
| Off-hand weapon is light and Two-Weapon Fighting feat | -2 | -2 |

- [OWNER] Both attacks are ONE combination (one action, one attack tag). Class and race features may lower the
  penalty down to 0: effect "two-weapon penalty reduction" (a number; the final penalty is never below 0, never a bonus).
- Feat "Two-Weapon Fighting" (base) is in the catalog (default price 200, editable). Improved and Greater versions are not added.
- An attack record has the toggle "combination of two attacks" (available with two weapons in the hands or a double
  weapon). A weapon takes 1 or 2 hand slots. When on, both attacks get the table penalties (feat? light/finesse off
  hand?). The second attack of a double weapon uses the lower damage row. The view marks which attack is the main
  hand and which the off hand.
- Attack records [OWNER, package 12 B; replaces the package 9 record kinds]: every attack record of an item is a
  main attack record (its own group, grip and stat). The item-bound "maneuver" records of packages 9-11 are removed;
  old files drop them on load (D1). With several records of one item, the record whose group changes the item's HP
  and hardness is the PRIMARY one, else the first (assumption Q76).
- Maneuver list [OWNER, package 10 design, closes Q44; built in package 12]: maneuvers live in a CHARACTER-level list,
  not inside items. Each has: name, description, required tags (weapon groups, weapon kinds, unarmed), attack
  modifiers (to-hit, damage, other bonuses/penalties), cost in actions and in balance. A maneuver is AVAILABLE when a
  weapon in the hands has any matching tag (a weapon is in many groups, e.g. a long sword in "long swords" and "heavy
  weapons", so both maneuver lists open). It uses the numbers of that weapon's main attack. Losing the weapon never
  deletes it: it is only unavailable (grey).
- Maneuver fields [OWNER, package 12 B]: id (made by the program), name, description, required_tags (weapon group ids,
  weapon kind ids = the catalog card id of the weapon, and the special tag "unarmed"), tag_mode ("any" default |
  "all"), modifiers (to_hit and damage numbers, untyped, plus an optional effects list in the usual effect structure,
  applied to this maneuver's attack only with the usual stacking), cost_actions, cost_balance, cost_spirit (RECORD
  ONLY: nothing is spent automatically), required_feat (optional feat id: unavailable unless the feat is owned; a
  feat's granted_maneuvers ids are shown on the maneuver as "granted by"), condition_tag, favorite, source (free
  label: style / class / feat), notes, extra (unknown future keys, kept on save/load, never interpreted).
  Commands: add_maneuver, edit_maneuver (any field), remove_maneuver.
- Weapon tags = all groups of the weapon (a shield without groups: Contact) + its own kind id. maneuver_view: for every
  maneuver, available yes / no; ONE ENTRY PER matching weapon in the hands (numbers differ per weapon): to-hit and
  damage = that weapon's main attack record numbers (BAB, stat, pain, the record group's mastery, enchantment...)
  + the maneuver's modifiers, plus the CMB of that record. "unarmed" matches while the unarmed attack is possible: no
  weapon (an item with weapon groups) in the hands. Unavailable -> reason ids: no_matching_weapon, feat_missing,
  unarmed_not_possible, no_attack_record.
- Assumptions (OPEN_QUESTIONS Q77-Q79): a shield or other item without weapon groups in the hand does not block
  "unarmed"; a matching weapon without any attack record gives no numbers (no_attack_record); a maneuver with no
  required tags fits any weapon in the hands and the unarmed attack.
- Tests: tag any / all; one weapon in two groups opens both; the weapon kind id is a tag; two matching weapons -> two
  entries (the expert one +3); numbers = main attack + modifiers; effects stack by type; unarmed with empty hands and
  refused with a sword; required_feat; weapon put away -> unavailable but kept; costs not spent; save / load with extra.
- What a combat STYLE can give [OWNER examples, package 12]: stances with restrictions, its own counters, maneuvers
  costing actions / balance / spirit with their own damage or number of attacks, changed weapon properties (finesse,
  free draw, damage die up), conditions on targets (vulnerability, burning), crit range overrides, start-of-round
  effects. These are intentionally NOT modeled: the player writes a maneuver with a name, cost, modifiers and a
  description and plays the rest by hand. The extra dict and the tags are the only stubs. Not built on purpose:
  automatic spending of actions / balance / spirit, stance restrictions, custom counters (like "Spark"), target
  conditions, start-of-round triggers, weapon property overrides.
- Attack list [OWNER, package 10, closes Q37]: shows what is in the hands plus unarmed combat (all_attacks); the full
  list with unavailable records greyed out stays available (all_records). A "what is worn" tab with item pictures is
  an idea only (ROADMAP).
- Attack availability [OWNER, package 8]: setting the toggle is not checked against the hands; instead a record is
  AVAILABLE only while every weapon it needs is in the hands (two-weapon: both weapons, in either hand order; double
  weapon: the one weapon; an unarmed off-hand strike needs a free hand). An unavailable record tells which weapons it
  needs and what is in the hands (ids, the UI greys it out and explains, e.g. "in hands: sword A, shield A").
  Tests: A+B and B+A available; only A -> missing B; sword + shield -> missing B; double weapon in / out of hands;
  a weapon in the bag -> unavailable.

#### Empty-hand parry [OWNER]
- Empty-hand parry and damage to balance [OWNER]: parrying with an empty hand is allowed. The player sees that the
  enemy roll landed in the parry number (armor/parry layer, defense_layers.md) and presses "take damage to balance".
  Command damage_to_balance(amount): the damage goes straight to the balance; HP are not touched; percent and DR are
  not applied (the player types the number). If the balance would go below 0, the overflow goes to OT and gives
  +1 pain (like an ordinary overflow). In combat the balance cap drops by 1 if the balance really lost points.
  Examples: balance 6, damage 4 -> 2, HP unchanged; balance 2, damage 5 -> 0, OT +3, pain +1, HP unchanged.

#### Unarmed [OWNER]
- Unarmed combat is always available: the attack list always has the unarmed attack next to the weapons in hand.

#### Maneuvers
- CMB / CMD / SR (SR not added yet, trait of race/class/feat).
- CMD does NOT follow AC rules. CMB gets weapon-group bonuses and others.
- Attack and CMB can use Dex instead of Str via option on the Attack/CMB or settings ("has finesse"):
  then the better of Str/Dex is used.
- Size (small/medium/large) affects attack, CMB, CMD.
  [package 10, R9] The attack roll gets the size modifier (the same number as the AC size layer).

#### Size and speed [OWNER, package 11 C; closes Q57, Q66]
- The race (the character's race fields) holds the size: small | medium | large only, and the base speed in feet
  (default 20). The hand-typed size CMB field is removed (old files: dropped on read).
- Size modifiers: attack and AC small +1, medium 0, large -1. CMB and CMD small -1, medium 0, large +1 (opposite sign).
- Effect target "speed": typed bonuses / penalties from any source (items, abilities, statuses, feats), stacked by the
  usual rules. Derived speed = base + bonuses; encumbrance gives -10 ft (gear.md). Speed is not a roll: no pain, no morale.
- One move = 1 action.
- Armor slowdown: REPLACED by gear.md "Armor" (package 12, Q72): the worn armor's speed_penalty_ft lowers the speed,
  minus effects "armor_slowdown_reduction" (the old line "stored but not counted" no longer applies).
- Tests: BAB 2, Str/Dex 12 -> (attack, AC, CMB, CMD) small (+1, 12, 2, 13), medium (0, 11, 3, 14), large (-1, 10, 4, 15);
  base 20; +10 ft item -> 30; -5 ft status -> 15 (inactive: 20); encumbrance -> 10.
- CMB / CMD in the sheet [package 10; Q58 and Q59 answered in package 12]:
  CMB = BAB + Str mod (with the Finesse feat: the better of Str / Dex) + size CMB mod + bonuses with target "cmb"
  + pain + morale (CMB is a roll). This is the general CMB without a weapon.
  CMB per attack record [OWNER, package 12 C, Q58]: every attack record view also shows its CMB = the general CMB
  + the record group's mastery attack bonus (the same "attack +1" picks the record gets). The UI may use either or
  both; a maneuver view shows the CMB of the matching weapon. Tests: two swords, one with mastery +3: CMB 7 and 4,
  general 4; with pain 1 and morale scale 4 in combat: 8, 5, 5.
  CMD [OWNER, Q59] = 10 + BAB + Str mod + Dex mod + size CMB mod + bonuses with target "cmd"; no pain, no morale.
  Tests: BAB 3, Str 16, size large (+1), +2 -> CMB 9 (pain 1 -> 8); Finesse and Dex 18 -> 8; CMD 10 + 3 + 3 + 2 + 1 + 1 = 20.

#### Spells damage
- Standard PF, but dice damage is affected by morale and pain. Editor unfinished [BETA]:
  level-scaled damage, damage types, areas, range.

#### Stances
- Special feats with checkbox. ONE active stance per character [OWNER, package 13, Q81]: classic (class) stances are
  ordinary stance feats.
- Attack records, maneuvers and feats may carry charges and a cooldown (gear.md "Charges and cooldown", package 14 B).
- Example: "defensive": +2 dodge, -4 attack (flat). Player toggles by hand at fight start.
- No automatic stance prerequisites.
- [OWNER, package 12, Q74; replaces earlier stance notes] A stance is a FEAT with the flag is_stance. The character
  has one field active_stance (a feat id or none). Command set_active_stance(feat id | none): refused when the feat
  is not owned or is not a stance. A stance feat's effects apply ONLY while it is the active stance; ordinary feats
  always. No lock flag and no combat rule: the player decides when to change it; end_combat does not change it.
  Removing the stance feat clears active_stance. Stances are NOT statuses in the container. The derived view lists the
  stances and the active one (the UI gives stances their own visual element).
- [package 13, Q82] Style "Me Liquescit" (no dodge bonus to AC, cannot be flanked) is expressed with block effects
  (buffs.md "Block effects"): block_bonus {type dodge, scope ac} + cannot_be_flanked on the stance feat. Test: Dex 14,
  dodge +1, shield 2: stance off -> front 15, flank 13; stance on -> front 12, flank 12.
- Tests: the stance effect applies only while active; switching stances; refusals (not owned, not a stance); removing
  the feat clears active_stance; end_combat keeps it; the view; not in the container.


#### Attack kinds [OWNER, package 17, part of Q122]
- A weapon card (Item.attack_kind) and an attack record (AttackRecord.kind, "" = the card's) are melee | ranged |
  thrown. Defaults are data (rules_settings): ranged = attack with Dex, NO stat to damage; thrown = attack with Dex,
  Str to damage x1; melee unchanged (Str by grip x1 / x0.5 / x1.5, Finesse rule).
- Record overrides: stat (the attack stat), damage_stat ("none" or a stat id), damage_mult (a number). A positive
  stat modifier is multiplied and rounded down, a negative one counts once as is. This replaces the old "own damage
  stat and multiplier".
- Tests: Str 16, Dex 14: bow (ranged) -> Dex, damage 0; dagger (thrown) -> Dex, +3; sword one hand +3, two hands +4;
  bow with damage_stat str -> +3; sword damage_mult 2 -> +6; thrown with Str 6 -> -2.

#### Reactions [OWNER, package 22 A2]
- Reactions are a resource with the fixed id "reactions": max = the bought reactions (start 1; +1 for 200 * the new
  number, training.md) + effects "reactions"; current = what is left this round.
- spend_reaction(n) (free attacks of opportunity, readied attacks: the player presses; refused at 0, reason
  not_enough_reactions); restore_reactions (manual, edit level). The zero-initiative tick (a new round) and the end of
  combat bring them back to max.
- Attack records, maneuvers and feats may carry cost_reactions: an attack record spends them in use_attack (refused
  when not enough); a maneuver is shown unavailable (reason not_enough_reactions); a feat keeps it as a record.
- Tests: start 1/1; spend -> 0, again refused; tick -> 1; 2 reactions for 400; an attack of opportunity record costs 1.

#### Damage roll and pain [package 22 B5]
- The damage roll is a roll with a die: the pain penalty and morale apply to it, like to the attack roll
  (resources.md "Pain", defense.md "Morale").
- [package 25 F] Spell damage as data: components {dice count (formula, may use level), die size, flat
  (formula), damage type (one of the 12), area (single / cone / line / burst / other), range, save, save effect}.
  The spell view gives them for the caster level with the pain penalty and morale of the damage roll; the app
  never rolls dice.

#### General attack numbers (package 30) [OWNER; closes Q198]
- MELEE = Str modifier + BAB by default; RANGED = Dex modifier + BAB. Each is editable per character: the source may
  be another stat + BAB (e.g. Dex + BAB for melee) or a SPECIFIC WEAPON (an attack record: its to-hit, and the view
  names the weapon). Command set_attack_source(kind, source).
- PAIN is always counted in these numbers (not only in combat). MORALE applies only DURING combat (the combat view
  has the flag morale_active = in combat).
- Tests: Str 14 (+2), BAB +2 -> melee +4; Dex 20 (+5), BAB +2 -> ranged +7; with pain 1 (penalty -1) -> +3 / +6;
  morale scale 4 out of combat -> no change, in combat +2.

## File: buffs.md

### Buffs / effects [OWNER]
Buff = status = debuff = situational: one concept, "Status" [OWNER]. Everything from spells, DoT and heal per tick are ordinary statuses. One generic effect system for ALL sheet parts (race, class, feat, item, injury, quirk, spell, buff).

#### What an effect can change
Any parameter: stats, initiative, attack bonus, AC, actions, saves, skills, resources (max, regen, current), speed, etc.
Several at once or separately. May give penalties (e.g. -2 AC). May give a one-shot (e.g. temp HP) AND a timed part
(e.g. +4 Str for 8 rounds).

#### Duration kinds
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

#### Value from the current overload [OWNER]
- A status/ability may read the CURRENT overload as its number. Example: bonus to attack and damage with natural weapons
  equal to the current overload.

#### Value from a stat modifier [OWNER, package 11 B; closes Q65]
- An effect value is a plain number OR {stat_mod: <stat>, multiplier: 1 (default)}, computed on read from the CURRENT
  stat modifier (stat damage changes it at once). Works for every effect target (skills, attacks, damage, saves, AC
  layers, speed...) with the usual type / stacking rules.
- It is a bonus ON TOP, never a replacement (e.g. "+Str mod to Intimidation" adds to the skill's own Cha).
- A negative modifier gives a negative value, as is.
- Assumption (OPEN_QUESTIONS Q71): a non-whole result (multiplier 0.5) is rounded down.
- Tests: +Str to Intimidation (Str 16, Cha 12) -> 4; +Dex to damage (Dex 18) -> 4; Str 16 with 4 damage -> +1;
  Str 6 -> -2; untyped +3 and +1 add up -> 4; competence +3 and +2 -> 3; multiplier 2 -> 6; dodge +Wis 14 -> AC 12.

#### Skills target [OWNER]
- An effect may target one skill (e.g. +2 to Stealth only) or all skills.

#### Condition [OWNER, package 8]
- There is NO "combat only" condition: a status works while it is active and not expired, in or out of combat.
  The old "in combat / out of combat" field is removed (an "out of combat" item bonus is switched on/off by hand).
- Condition tag [OWNER, package 9, closes Q36]: abilities (feats), items and statuses have an optional display-only
  field condition_tag: none / combat_only / out_of_combat_only. It changes NO calculation; derived views show it so
  the UI can draw an icon. The player sets it by hand (command set_condition_tag). Test: a tagged item and status give
  the same numbers in and out of combat as untagged ones.

#### Status container [OWNER, package 11 A; closes Q63]
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
  bonus and ticks; favorite flag; charges: see "Charges and activation" (Q108).

#### Charges and activation
- A buff source (ability/item) may have charges (e.g. rage 2/3). If placed on screen/slot, tapping activates it;
  shows remaining rounds and remaining charges.
- ONE rule for status charges [OWNER, Q108, package 16 G3; the package 8 line "every status is restored by the long
  rest" is REPLACED]: a status linked to a source (Status.source_ref) follows that source's recharge rule; a status
  without a source is NOT refilled by rests. The short rest option "restore charges" (2 BP) stays a choice of the
  player (Q121). Item usage charges follow the item's recharge rule (gear.md "Charges and cooldown").

#### Stacking (see defense.md)
- Same type: the value with the larger absolute value wins, equal absolute values give 0; only flat stacks
  (on AC dodge also stacks; weapon proficiency stacks with itself). Details: defense.md "Stacking".

#### Ready-made buffs
- Any ability can be exported as a buff; catalog keeps templates (Entangled, Haste, Rage ...).

#### Stacking flags [OWNER]
- Temp HP from buffs may or may not stack: per-effect flag. Same for DR, energy resistances, spell resistance.
- Duration is usually given in rounds.
- Spells, abilities, racial abilities are editable: mark "is buff" in the editor; buff list is searchable for activation
  when the source is not pinned to the panel. No charges left -> cannot activate.
- Test: removing an injury must NOT bring OT back.

#### Block effects [OWNER, package 13 B; closes Q82]
- New effect kinds in the usual effect structure. They work from any source that is ACTIVE now: an active status, an
  owned feat (a stance feat only while it is the active stance), the acting tab of a worn / held item (an activated
  item: its "activated" tab), an injury (package 14 D, Q89).
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

#### Per-round cost [OWNER, package 13 C]
- Status fields charge_source ("own" = its own charges, or a resource pool id, resources.md) and charge_per_round
  (default 0).
- [OWNER, package 14 A; replaces Q83, Q85, Q91] The ACTIVATION pays charge_per_round for the FIRST round; then
  every tick pays the next round. The source is a pool or the status's own charges; with source "own" the activation
  pays charge_per_round from the own charges INSTEAD of the usual single charge (no extra charge). If the source
  cannot pay at activation, the activation is refused with a reason.
- The tick payment happens in the zero-initiative phase at the duration step, BEFORE the duration drops. If it cannot
  pay, the status ends at once (inactive, the entry stays) and does not act in this tick (Q84). The player may remove
  it earlier by hand: then nothing more is paid and there is no effect.
- [OWNER, package 15, Q95] A per-round status that lasts D rounds pays for exactly D rounds in total: the activation
  pays round 1; a tick pays for the next round only if the status will still be active after that tick; the tick on
  which the duration ends pays nothing. Examples: aura of 3 rounds at 1 Ki costs 3 Ki; duration 1 costs 1 Ki at the
  activation and ends at the first tick without paying. A status without a duration pays at every tick.
  Acting rounds (checked, package 15 report): a duration-D status gives its bonuses in the activation round and the
  next D-1 rounds (D rounds), and its per-tick part (DoT / heal / restore) acts on ticks 1..D (D times, also on the
  tick it ends). A 1-round buff is active in the round it was activated in.
- [OWNER, Q97] Statuses have NO recharge field: the charges of a status follow the rule of its SOURCE (feat, race,
  pool, item); a plain buff without a source has no recharge rule.
- [OWNER, Q108, package 16 G3] Status.source_ref links a status to its source ("feat:<id>", "item:<id>",
  "attack:<id>", "maneuver:<id>" -> that source's usage recharge; "pool:<id>" -> the pool's restore rule;
  "template:<id>" -> none). Rests and start_combat refill a status only when its source's rule fires; a status without
  a source is NOT refilled by the long rest (the short rest option "restore charges" stays a choice of the player).
  Tests: unlinked 0/2 stays 0 after the long rest; feat long_rest -> 2; pool short_rest -> 2 after the short rest;
  item manual -> 0; feat combat_start -> 2 at start_combat.
- A status has no other cost (Q69).
- Tests: pool 3 at 1 per round gives exactly 3 rounds (activation 2, ticks 1 and 0, the 3rd tick ends it); own source
  2 per round, charges 4 -> activation 2; refused when the source cannot pay; monk aura, cursed darkness (3 per round),
  barbarian rage (formula pool max).

#### Formulas [OWNER, package 14 C]
- An effect value may be a number, a stat_mod value, or a FORMULA string; a resource pool's max may be a number or a
  formula. A small safe evaluator reads it (no eval / exec).
- Variables: level (also lvl), str_mod, dex_mod, con_mod, int_mod, wis_mod, cha_mod (CURRENT modifiers, block effects
  included), bab. Operators + - * /, parentheses, unary minus. Functions: min(a, b, ...), max(a, b, ...), floor(x).
- Numbers may be whole or decimal; + - * are exact. "/" is integer division rounding DOWN (towards minus infinity):
  7/2 = 3, -7/2 = -4. The final result is rounded DOWN to a whole number: level*0.5 at level 3 = 1; -level*0.5 = -2.
- A formula is validated when it is added or edited (add_status, add_maneuver / edit_maneuver, add_pool / edit_pool,
  the feat catalog): a clear error. A broken formula stored by hand never crashes a derived view: it counts as 0.
- Pool max on read: the formula on the current sheet. The stored current is stored AND shown as it is, also above
  the max (resources.md "Over max") [OWNER, package 16 A6]; spend starts from it, a restore never lowers it.
- Tests: rage pool max con_mod + 2*(level+1) with Con mod 3, level 4 -> 13; Con mod 1 -> 11 and the current stays 13 (over max);
  2*lvl, min / max, the rounding examples above; unknown names and quotes refused.

#### Action and restore blocks, restore by effect [OWNER, package 14 F]
- block_action {block_actions: attack | move | spell_cast | heal | any}: the derived view exposes blocked_actions with
  the reasons (source ids). cast_spell refuses while spell_cast is blocked; restore(resource "hp") refuses while heal
  is blocked. attack and move have no command: only the flag is exposed.
- block_restore {block_resources: hp | mana | spirit | balance | pool:<id> | any}: ticks, rests, start_combat pool
  restores and restore effects do not raise those resources while active (lowering is never blocked); the restore and
  restore_pool commands refuse with a reason (assumption Q98). block_balance_regen keeps working as the balance case
  (the old name is an alias).
- Restore by effect: per_tick_restore {mana | spirit | balance | pool:<id>: n} on a status restores every tick while
  the status acts; the one-shot part at activation may restore mana, spirit, balance, hp, pool:<id> (temp HP as
  before). Never above the max. Both honour block_restore. Unknown keys are refused when the status is added.
- Injuries carry effects too (injuries.md), so an injury can be the source of any block.


#### Effect targets of every sheet number [OWNER, package 16 A2]
- Owner: ALL sheet numbers have effect targets. The new targets are DATA: wp/catalog/data/sheet_targets.json (id and
  meaning): stat:<str..cha> (ability score), hp_max, extra_hit_dice, bp_max, balance_max, balance_regen, spirit_max,
  mana_max, slots:<circle>, pool_max:<pool id>, comfort_max, comfort_rate_bonus, parry, max_dex, armor_skill_penalty,
  load_mod, reactions, base_slots, attention_per_cycle, crit_mult, iterative_penalty, dr, resist:<type>,
  spell_resistance, spell_price_discount. Older ones: ac, attack, damage, save, save:<id>, skill, skill:<id>,
  initiative, cmb, cmd, speed, crit_range, lucky, touch_armor, armor_slowdown_reduction, spell_penalty_mana,
  spell_failure_pct, twf_reduction, block_*.
- Sources: active statuses, owned feats (stance feats while active), injuries, quirks not burned, templates, the
  acting tab of worn / held items and of items at the base. Typed bonuses stack by the normal rules (same type ->
  larger wins; flat and dodge add); block_bonus applies.
- Ability scores: score = stored score + stat:<id> effects; the modifier and everything built on it follow. A stat
  effect whose value comes from a stat modifier or a formula reads the STORED scores (no loops, assumption Q118).
- Stored maxima stay base values (mana Pool, slots): the effect is added on read; rests and casts write back the
  current only.
- Tests (test_pkg16a.py): +4 Str -> 14 / +2 / CMB 2; enhancement +4 and +2 -> +4; Con +4 -> HP 10; hp_max +5 -> 13,
  BP 4; mana 0/4 + 2 -> long rest 6; slots 2 + 1 -> 3; Ki 3 + 2 -> 5; armor penalty -3 + 2 -> -1 (never above 0).
- [OWNER, package 17, closes Q125] Also targets: pain_cap, pain_penalty_per_pain, damage_per_pain, item_hp and
  item_hardness (Effect.weapon = one item id, none = every item; read from statuses, feats, injuries, quirks and
  templates, not from item tabs, with no stat modifiers: Q127), morale_scale ("count morale X higher"),
  short_rest_heal, short_rest_bp, spell_cost, spell_overload, mana_level, percent:<damage type>.
  Tests (test_pkg17.py): pain 10 dies at cap 8, alive at cap 12; pain 2 -> -2, per pain +1 -> -4; sword HP 10 + 3 ->
  13, axe stays 10; hardness 5 + 2 -> 7; scale 4 + 2 -> morale +3; free heal 3 + 2; circle 2 mana 3 + 1; overload 2 + 1.

#### Formulas over sheet numbers, conditions, situational [OWNER, package 36, decisions 7, 8, 12, 13, 17]
- An effect value may be a formula over other sheet numbers: level (lvl), the stat modifiers, bab, hp_max, mana_max,
  base_slots, pain, morale, balance_max, spirit_max, bp_max, comfort_max and tagged_base_slots:<tag> (the BASE slots
  taken by the items with that tag lying at the base: trophies of 2 + 3 + 2 slots = 7, not the number of items).
  "/" is integer division rounding down. Cycles are NOT blocked: one pass, a value read while it is computed counts 0,
  and the Sources dialog warns "cycle in formulas". The GM watches cheats.
- Tests: mana_max 25 -> mana_max / 10 = 2; skerde HP = min(base slots, 4 x level): level 1 with 10 slots -> 4.
- Condition of an effect: automatic ones the core can read (HP is max, BP is max, pressure = / >= / <= N, in combat,
  pain >= N) or manual ones (a checkbox with the condition text). No other automatic conditions. The effect counts
  only while the condition holds; the Sources dialog shows the condition and whether it holds.
- Situational bonuses (vs magic, vs death effects, mounted ...) are NEVER in a total: hovering the cell lists them
  ("+2 vs magic"), a small star marks the cell, the Sources dialog has a "situational" row.
- An unknown bonus type is untyped (stacks with everything); a view never raises (decision 17, closes Q245).

#### Triggers [OWNER, package 36, decision 6]
- Any carrier (item, race, class, feat, spell, status, injury, quirk) may have triggers: a reminder text, an OPTIONAL
  action button (always pressed by the player) and a handled mark; unhandled reminders stay visible.
- Events: cycle_end, combat_start, combat_end, zero_initiative, level_up, short_rest, long_rest, hp_below_one, plus a
  MANUAL trigger = a button on the ability card (there is no "end of session" button: Q122).
- Actions (closed list): add_status(id), change_resource(id, n), add_reminder(text), add_pain(n),
  reduce_injury_points(n) (= OT, never below 0), run_command(name, params) from an allowlist (data).
- Test: cycle_end reminder "+2 comfort" with its button; unhandled stays visible.

#### Reminders from effects [OWNER, package 38, decision 4]
- A carrier may hold a standing reminder (effect target reminder:<key>, its text in the locale files): it stands
  while its effects add up above 0; a condition makes it count only while it holds; a source that removes it adds -1
  (a buy-out). The automatic condition status_tag:<tag> holds while an active status carries that tag (the catalog
  status Bleeding has the tag bleeding). Test: Mordon Wall of Bones + Bleeding -> "bleeding x2"; bleeding off or
  the buy-out -> no reminder.

#### Held by [OWNER, package 36, decision 14]
- Any ability / bonus may be held by another ability, an item or a quirk (or a text holder with a manual kept / lost
  checkbox). If the holder disappears the dependent gets a "not backed" mark and a reminder; nothing is removed
  automatically.

#### Rule constants as targets, links shown both ways [OWNER, package 37, decisions 1, 5]
- Every rule number that lives in data (wp/rules_data/constants.json) is also an effect target const:<id>: a source adds
  to it, or replaces it (the note "replace"). The Sources dialog lists such sources like any other. Test: the comfort
  rate base 5 + 50 -> a level-1 exchange gives 60 training instead of 10.
- Links are shown both ways: on hover "held by: X" and "holds: A, B"; a lost holder in red ("not backed"); the
  Feats tab lists a dependent under its parent ability; the link is set or removed by a command (journal, undo).
- damage_per_pain may be scoped to melee or ranged attacks (Ulstanger Rage: melee).

## File: rest.md

### Rest

Terms: BP (БП) = pain threshold, a resource shown "cur of max" (e.g. 4/4). Balance is a separate bar (resources.md).

#### BP and balance [OWNER]
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

#### Action UI [OWNER]
- App shows the player his actions and which of them cause pain; player taps to mark an action spent
  (or skips if he remembers). Tap when pain is due.

#### Long rest [OWNER]
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

#### Short rest [OWNER]
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

#### What is restored when [package 22 B8: a summary of the current rules, nothing new]
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

## File: injuries.md

### Injuries and trauma points (OT)

#### Trauma points (OT) [OWNER]
- Counter. Source: balance overflow (resources.md). GM turns them into penalties unless the player removes them first.
- OT are zeroed ONLY by hand (and by the removal ways below). Rest does not touch them. Same for comfort and injury charges.
- Removal ways (player follows wiki rules, then removes OT in the app; also manual delete of OT is always allowed):
  * Injury taken: light / medium / heavy removes 2 / 5 / 12 OT and gives an effect.
  * Comfort: 1 comfort removes 3 OT.
  * Attention: 1 attention removes max(2, Str modifier) OT [OWNER; 'strength mod' = Str modifier, confirmed by parallel RL wording].
  * Other ways exist (manual).
- Rules text lives in the wiki: UI should link (small icon) from relevant tabs. [UI wish]
- Commands [package 15]: add_injury (take an injury: -2 / -5 / -12 OT), remove_ot_comfort(n) (-3 OT per comfort),
  remove_ot_attention(n) (-(max(2, Str mod) + attention course) OT per attention), raise_heal_rating(injury_id)
  (1 attention -> RL + max(2, Str mod) + attention course). OT never below 0; refused without OT, comfort or
  attention.

#### Injury [OWNER]
- Standard injury: penalty for N sessions, usually physical. Effects (generic effect system):
  -X to attack / damage / morale / any sheet value; lower or raise resource max; forbid options/limbs/actions.
- Roleplay-only injuries are recorded but have no mechanics.
- Permanent injury: separate row "Permanent injury". Cannot be healed normally; narrative removal only. Also feeds permanent pain (resources.md).
- Injuries can be added manually. Catalog may provide templates (light/medium/heavy).
- Injury effects [OWNER, package 14 D, Q89]: an injury has an effects list (the usual effect structure: penalties,
  bonuses, blocks, anything). They apply while the injury exists; the container view shows them; an injury can be a
  block source (e.g. block_balance_regen). The OT price rules stay. Tests: -2 attack, regen blocked, removing the
  injury removes the effect.
- Injury id [OWNER, package 12, Q70]: every injury has a stable id made by the program from its name (a number on a
  collision, the same scheme as other ids), stored on the injury and used by the status container view. Old files
  load: injuries without an id get one on load. Ids of the other injuries never change when one is removed.
  [OWNER, package 13, Q75] Ids are NEVER reused: the character keeps a counter (injury_counter, only grows); an id is
  "<name>_<N>" (cut_1, cut_2, ...). remove_injury(injury_id): manual, editor level, no resource cost; the counter
  stays, so the next injury gets a new number. Tests: remove by id, the others keep their ids, after removing cut_3 a
  new cut is cut_4.

#### Healing rating (RL) [OWNER]
- Each injury has a Healing Rating. Once per cycle (a cycle = a large span of in-world time, e.g. a skip; narrative tool announced by the GM) the player rolls d12 in an outside app; roll <= RL means healed.
- Base RL: light 3, medium 2, heavy 1.
- 1 attention raises RL by max(2, Str modifier) (e.g. light 3 -> 5 at minimum); the attention course adds to it
  (+1 per course, Q102). Some consumables/items directly reduce OT when used.
- The injury is removed BY HAND by the player. The app tracks its status and the related resources (HP, attention, comfort, sheet state).
- No automatic countdown, no auto-removal, no "end session" button that edits injuries or comfort.
- The app never removes comfort or edits injuries without a player action; no such button for now.

- Active injury gives its persistent penalties while it exists (e.g. broken arm: -1 to attacks).

## File: classes_magic.md

### Classes and magic

#### Class editor, 3 tabs [OWNER]
1. Basics: name, HP die (player picks), BAB progression, good saves (Fort/Ref/Will), as in current program.
   Checkboxes: has mana (has spellbook?), has slots, special resource 1, 2, 3 (name entered right here).
2. Abilities: same as race/feats: name + effect. E.g. rage, school of magic. Effects = generic effect system.
3. Maximums per level: slots max, mana max, ki/darkness/etc max; a formula may be used. Editable.
   Current mana/slots displayed elsewhere. Specific prepared spells live in the Spells tab.

#### Restore [OWNER]
- Slots: full rest, some narrative situations, short rest. On short rest slots may or may not return despite resource spent.
- Mana [OWNER, package 22 A1], two separate things:
  1. Rest regeneration (rest.md): the short rest option "Restore mana by regen" (free once, then 1 BP; the amount X is
     typed in, decided by the GM, no formula); the long rest restores all mana.
  2. Manual restore: command restore_mana(amount): a GM narrative effect or an ability gives mana at any time; up to
     the max (an over-max value is kept, never raised); refused while a block_restore covers mana; journaled.
  Tests: 2/10 + 5 -> 7; + 20 -> 10; 12/10 stays 12; blocked -> refused.
- Slots on short rest: the GM decides whether they return (manual).
- Other per-class pools: full restore on long rest (see rest.md).

#### Where abilities live [OWNER]
- Abilities paid with mana or slots belong to SPELLS.
- Abilities paid with ki, adrenaline or other special class pools live in class tab 2, tagged "ability" (RU: "sposobnost").
- Spells vs abilities are separate lists; no overlap in cost types.

#### Mana source [OWNER]
- Each class has its OWN mana table, entered by hand per level. Race/feats/abilities can add mana too.
  Example: race gives 6, class level 1 gives 2 (or put 2 in class and 6 in a racial ability).

#### Spell cost [OWNER, confirmed]
- Circles 0-9 as in Pathfinder. Mana cost per spell is whatever the spell says (1, 3, 5 ... by circle); entered per spell.
  Circle table [OWNER, package 10]: circles 0-9 cost 0, 1, 3, 5, 7, 9, 11, 13, 15, 17 mana (used when no cost is typed).
- Mana level [OWNER, package 10] = the character's level: one mana spell (cost + armor penalty) costs at most that
  much (gear.md "Armor"). Checks (package 10 tests): table 0..17; overload = actions spent (usually 2), double for
  non-mana spells (slots: divine, bardic) and cantrips; a mana spell costs balance = its mana cost; OT from a short
  balance -> concentration DC 10 + 2 * OT or the spell fails; a spell from a magic item: no overload, no balance, no
  mana (item activation still costs spirit).
- Mage (mana user): balance cost = mana cost (0 mana -> 0 balance). Overload X = casting time in actions
  (standard action = 2, usually 2) [OWNER, changed]. Spell duration does not affect overload.
  Default from the formula; the player may type another value at the cast.
- Non-mana caster: spends a slot of that circle, no balance loss, overload 2X.
- Cantrips (circle 0): characters with a circle-0 slot spend it, EVEN mana users have slots for circle 0 only.
  Characters who can cast cantrips but have no circle-0 slot at all: unlimited. Cantrip overload 2X for everyone.
- Examples: mage, circle 2 (3 mana), standard action (2): mana -3, balance -3, overload +2.
  Non-mage circle 1, standard action (2): slot -1, overload +4. Full-round (3 actions): mage +3, non-mage +6.
- Mage with less balance than the spell cost [OWNER]: balance drops to 0, +1 pain, OT = the missing part.
  The app shows the DC at once: "Concentration DC = 10 + 2 * OT gained, otherwise the spell fails".
  Example: balance 2, cost 5 -> OT 3, pain 1, DC 16.
- Spells from magic items and consumables give no overload and cost no balance [OWNER]. Item activation still costs spirit.
- Armor and shield spell penalties (extra mana cost, failure chance, failure mode "cancel" / "zero_balance"):
  gear.md "Armor" [OWNER, package 9].

#### Racial damage absorbers [OWNER]
- Absorption is 1:1; absorbed part does not hit balance (like temp HP). Other traits/classes/races may add other absorbers.
- Some races redirect damage: after temp HP, before HP, damage hits MANA and acts like temp HP.
  Model damage as an ordered list of absorbers (temp HP -> race pool -> HP), configurable per character.

- [OWNER, package 16 B] Circles 0-9 ONLY: no circle 10 or above anywhere (rules, data, code). cast_spell and
  learn_spell refuse any other circle with a reason.

## File: resources.md

### Resources

#### HP and temp HP [OWNER]
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

#### Damage pipeline [OWNER]
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

#### Balance [OWNER]
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

#### Pain [OWNER]
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

#### Zero initiative phase [OWNER]
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

#### Spirit, mana, overload [OWNER]
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

#### Class resources [OWNER]
- Class pools (Ki, Darkness, Paladin defense points + Holiness) look/work like HP, mana, spirit. Players define in editor/catalog.
- Rage-like buffs show charges left (2/3) and duration; duration ticks with initiative.

#### Comfort [OWNER]
- Resource burned during play or exchanged for training. Max formula 5 + 5*level, modifiable by class/race/items.
- Chip goes red when current > max; player spends it down by the next session (see Over max).

#### Comfort per fight [OWNER, package 38, decision 5; closes Q280]
- A general rule for every character: during a combat the program keeps the largest absolute morale (combat
  pressure) reached; above 5 counts as 5. At the combat end: comfort = max(0, that value - 1), at most 4
  (|morale| 1 -> 0, 2 -> 1, 5 -> 4, 8 -> 4). The numbers (cap 5, minus 1, at most 4) are rule data
  (comfort.fight_cap / fight_minus / fight_max), so they are const: targets.
- The comfort is never added silently: the combat end leaves a reminder with a button "take +N comfort"; the
  button is a command (journal, undo); the next combat start forgets an unaccepted gain.
- Mordon Wall of Bones: 1 more off and at most 3 (2 -> 0, 5 -> 3); the buy-out brings the normal rule back.

#### Over max [OWNER, confirmed]
- ANY resource (HP, mana, spirit, comfort, ...) may exceed max: usually consumable effects, sometimes narrative (rare).
- Normal gameplay (regen, healing, rest, tick) never raises above max: clamp.
- Manual set / overfill is allowed and must NOT be clamped. Design: two ops: restore(clamps) and set(no clamp, flagged over-max).
- Over-max is shown (red chip), not auto-trimmed. Comfort: player must spend down before next session
  (starts session at its start value); no engine enforcement, only the red indicator.
- Temp HP is still its own pool (see above); over-max HP is a different, rare case.
- So audit A054 (no clamp) is NOT a bug; A053 (crash on HP setter) still is.

#### Base, attention, money -> gear.md / narrative.md

#### Resource pools [OWNER, package 13 C]
- A pool is a character-level counter (Ki-like): id (made by the program), name, max (a number or a formula, buffs.md
  "Formulas"), current (shown as is, also above the max, package 16 A6), restore: "short_rest" | "long_rest" | "combat_start" | "manual";
  restoring sets it to max (an over-max value is not lowered).
- Commands: add_pool (current = max unless given), edit_pool, remove_pool, spend_pool(pool_id, n) (refused below 0),
  restore_pool(pool_id). The short rest restores "short_rest" pools; the long rest restores "short_rest" AND
  "long_rest" pools (a long rest includes a short one) [OWNER, Q88]; start_combat restores "combat_start" pools;
  "manual" pools never restore by themselves. Default restore of a new pool: "manual" [OWNER, Q90 accepted].
- Statuses may pay their per-round cost from a pool (buffs.md "Per-round cost").

#### Rule switches [OWNER, package 14 G]
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

#### Journal [OWNER, package 14 H]
- One journal for everything: every command that CHANGES the character logs itself through the command base (dispatch):
  order counter, kind (item / item_damage / spell / damage / heal / status / charges / rest / injury / stance / combat /
  other), command id, short params, result, combat round (1 at start_combat, +1 per tick, 0 out of combat).
- Entries store ids and numbers only, no texts (the UI translates through wp/i18n). Old text entries load with their
  command id only. Read-only or softly refused commands (nothing changed) are not logged. No cap by default
  (log_limit 0). No revert.

#### Rule switches of races and abilities [OWNER, package 36, decisions 3, 17]
- A declared list in data (wp/rules_data/switches.json), read through one function: at_negative_hp (dying / nothing /
  status:<id>: HP below 0 turns that status of the character on instead of dying), death_pain_cap (= pain_cap),
  heal_percent (every heal by the Heal button is positive energy: -50 = half), exp_percent (-25 = a quarter less
  experience), pain_reduction (effective pain lowered by N, never below 0), natural_regen_percent (the HP of a rest:
  100 = double), injury_points_reduction (a trigger action: OT - N by a button).
- Tests: heal 10 at -50 % -> 5; xp 100 at -25 % -> 75; pain 3 - 2 = 1; a rest gain 3 at +100 % -> 6.
- Damage absorbers (classes_magic.md "Racial damage absorbers") may be limited to damage types and stand after temp HP,
  before HP: the static pool of an azana takes only electricity (7 electric -> the pool -7, HP untouched); mana before
  HP for a ragmal.

## File: gear.md

### Gear

#### Doll [OWNER]
- Doll = worn or ready items. Two hands: items in hands needing > 2 hands total cannot be equipped. Rest of doll is worn.
- Hands [OWNER]: there is no separate shield slot. The two hands are one shared slot for everything that needs hands:
  weapon, shield, any special item (misc). An item has a field "hands" (0, 1 or 2); the hands of items held in the hands
  add up to at most 2 (a two-handed weapon takes both; shield + two-handed is impossible). Allowed: shield + weapon,
  weapon + weapon, two-handed weapon, special item + weapon. The shield bonus to AC (type shield) works only while the
  shield is held in a hand, not while it lies in the bag.
- Armor, helm, glasses, etc. Character slots: see doll.md.
- Magic items may need activation: 1 spirit per "day" (until the short rest) or 5 per "decade" (until the long rest,
  package 10 decision I); cost may scale or have an alternative.
- Requirements: "Qualification N" or Court level X.

#### Qualification
- Tied to a specific item; does not work for other items (training.md). In levels, each level costs 50 training. Unlocks hidden properties of unusual items.

#### Belt (unload) [OWNER]
- Consumables slots (potions, scrolls). Base 10 L. Activation usually 1 spirit, can differ.
- Special slot, buffs or injuries can add bonus belt slots.

#### Bag
- Everything not worn and not a weapon. Button "drop bag" excludes its weight until picked up again.
- [OWNER, package 8] The button is the character flag ignore_bag_weight (default off, command set_ignore_bag_weight).
  While on, the bag weight (carried, not worn, not in the hands, not a weapon) is not counted in the carried weight;
  the weight view shows the flag. Tests: bag 30 + sword 20 + armor 50 + axe 15 = 115 L; flag on -> 85 L.

#### Weight [OWNER]
- Unit "balk" B: 5.9 B = 59 L. Stored as L.
- Load thresholds [OWNER confirmed]: base light 0-5.9 B, heavy to 10.9 B, above = encumbrance (weight overload;
  package 22 B4: not the same thing as the spell overload of casting, resources.md).
  Both thresholds shift by Str MODIFIER (in B). Examples: +2 -> 7.9 / 12.9; -2 -> 3.9 / 8.9; +3 -> 8.9 / 13.9; -1 -> 4.9 / 9.9.
  Above heavy: drag only or drop something (encumbrance icon).
- Encumbrance effect: dodge bonus to AC capped at +2; Dex gives dodge; speed -10 ft. [package 11 C: the speed -10 ft is computed, combat.md "Size and speed"]
- Armor slowdown [OWNER, package 12, Q72]: a WORN armor (on the doll, not at 0 HP: the same items as the armor bonus)
  subtracts its speed_penalty_ft from the derived speed. Effect target "armor_slowdown_reduction" (feats, abilities,
  statuses, items): a positive value reduces the slowdown, never below 0 slowdown in total; the value "all" ignores it
  completely. The encumbrance -10 ft stacks with it. Assumptions (OPEN_QUESTIONS Q80): with several worn items the
  largest slowdown counts (like the armor bonus); a broken armor still slows fully.
  Tests: worn 5 ft -> 15, in the bag 20; broken 15, at 0 HP 20; reduction 3 -> 18, 10 -> 20; "all" -> 20;
  with encumbrance -> 5.
- Abilities may ignore slowdown from armor/encumbrance (editor/settings/doll section).

#### Base (resource for strengthening) [OWNER]
- Blessings, immaterial and material things at player's home. Start 5 slots, max 10*level.
- Item = 1 slot normally, some items/buffs more. "Grey" items take 0 slots.
- Example: item "Strong" gives +2 Str and takes 10 slots.
- Base can temporarily exceed limit: player must carry something away or drop; show red indicator (like encumbrance).
- [package 22 B7] 1 base point = 1 base slot; attention base points are kept in tenths, every whole point is +1 slot.
- Buffs from base give abilities, permanent parameters, or improve modifiers.

#### Armor [OWNER]
- Skill penalty (Str/Dex skills), arcane spell failure chance (slot magic & mana, NOT ki-like abilities).
- Weight, armor bonus. May slow. Mwk/special may reduce penalty (rarely give bonus).
- Touch AC bonus [OWNER, package 9 H]: armor may have a "touch AC" bonus (catalog column "touch AC"). It adds ONLY to
  the touch AC, as the armor layer of the touch AC; it gives NO balance and does not change other AC types. Worn armor
  only, same rules as the armor bonus (nothing at HP 0, halved down when broken); enchantment does NOT raise it
  [OWNER, package 10, closes Q46]. Other sources may: effects with target "touch_armor" (statuses, spells, items,
  feats) are typed bonuses to the armor layer of the touch AC only, stacked with the armor's touch bonus (type armor)
  by the normal rules. Tests: touch 2 + flat +1 -> 13 (front 14); touch 2 + armor-type +3 -> 13; no armor, +2 -> 12;
  +2 armor activated: front 16, touch 12. Tests: armor 4 touch 2: touch 12, front 14, balance 4; broken: touch 11, front 12; HP 0: 10/10.
- Spell casting penalties [OWNER, package 9 I]: armor and shields have spell_penalty_mana (extra mana cost, >= 0;
  set 1 column "magic") and spell_failure_pct (0-100; "divine" / "spell failure" column). The numbers of worn armor and
  held shields ADD UP, then effects with target "spell_penalty_mana" / "spell_failure_pct" (feats, class traits) change
  them like normal bonus entries (a value -2 lowers by 2; accepted Q47); never below 0; the chance at most 100.
  - Mana casters: the extra cost is added to every mana spell (circle 1+; not cantrips, accepted Q50), paid in any
    mix of mana and balance (the player says how much from balance; the spell's own cost stays mana = balance,
    accepted Q48). Mana level = the character's level [OWNER, package 10, closes Q49]: one spell (its cost + the armor
    penalty after reductions) can cost at most that much; above it the spell CANNOT be cast (clear refusal, no cut).
    Tests: level 5, cost 3 + 2 -> cast; level 4 -> refused; level 4, cost 5 -> refused; level 4, penalty lowered to 1
    -> cast. Source note: the "magic" penalty adds extra mana/balance cost in any combination.
  - Failure: slot casters always have the failure chance; mana casters only if the chance > 0. The app rolls no dice:
    the player reports the roll (command resolve_spell_failure). Failure mode of the caster (data): "cancel" = the
    spell is not cast and nothing paid is refunded [OWNER, package 10, closes Q51]; "zero_balance" = the spell still
    works and the balance drops to 0 as an extra cost. A slot caster with chance 0 has nothing to roll (accepted Q52). Divine
    casters default to "zero_balance" (source note: the "divine" penalty does not cancel the spell on failure but
    zeroes all balance), others to "cancel".
  - Tests: armor 2/20% + shield 1/15% -> 3 / 35%; shield in the bag not counted; feat -2 / -50% -> 1 / 0; 60% + 60% ->
    100; mage cost 3 + 2: mana 10 -> 5, balance 6 -> 3; 2 paid with balance: mana 7, balance 1; mana level 4 -> refused (no cut, see above);
    failure modes.
- A shield counts as armor: a shield held in a hand applies its Str/Dex skill penalty too [OWNER, package 8 R4].
  Test: shield -2 in hand -> climb -2; in the bag -> 0; shield -2 + armor -3 -> -5.

#### Masterwork [OWNER, package 8; package 9 closes Q39, Q40]
- An item flag "masterwork" (command set_item_masterwork). The flag is the ONLY way: masterwork is never written into
  the "not activated" tab.
- Masterwork weapon: +1 to attack, type enhancement. While the weapon is ACTIVATED with enchantment +1 or higher,
  masterwork is OFF and cannot turn on (the item view shows masterwork_active = False with the reason id
  "enchant_active"). Not activated, the weapon counts as masterwork. An activated tab without enchantment N (an active
  ability like fire arrow 3/day) does not switch it off. Opposite signs of equal size cancel (+1 masterwork and a -1
  enhancement penalty -> 0). No damage, no lucky attack. Tests: plain +1; +2 not activated +1; +2 activated: off, +2;
  fire tab only: +1.
- Masterwork armor / shield: its Str/Dex skill penalty is permanently 1 smaller, never above 0 (-1 -> 0, 0 -> 0),
  whether activated or not. Enchantment on armor does not lower the penalty; both apply (enchantment adds AC,
  masterwork lowers the penalty). Broken: masterwork -1 first, then x2 (-3 -> -2 -> -4). Test: +2 masterwork armor -3
  activated: penalty -2, AC 10 + 4 + 2.
- Item HP 0: masterwork gives nothing either.

#### Enchantment [OWNER, package 5]
- An item has an enchantment level N (weapons, armor, shields).
- Weapon: +N to attack, damage and the lucky attack (type enhancement).
- Armor and shield: +N to the armor / shield bonus (raises the "armor" / "shield" layer).
- ALL three kinds: hardness (HD) +2*N, item max HP and current HP +1*N.
- Other enchantment effects (crit protection 25%, fire d6 on attacks, ...) are ordinary item effects in the common
  effect system (D14); no code per kind, the number of kinds is not limited. An effect may carry dice and a text note.
- Tests: sword +3 -> hardness +6, HP +3; armor +2 -> armor layer +2, hardness +4, HP +2; shield +1 -> shield bonus +1;
  "fire d6" stays an item effect.
- [OWNER, Q30] Enchantment is an ACTIVATION effect. All bonuses of the enchantment level N (attack, damage, lucky
  attack of a weapon; armor and shield bonus; hardness +2N; item max HP and current HP +N) count ONLY while the item is
  activated.
- A not activated item gives its base values (the item's own armor / shield bonus, weapon damage) plus its "not
  activated" tab (e.g. a special non-magic material writes its non-magic bonus there; masterwork is the item flag,
  see "Masterwork").
- An item with no activation price is an ordinary item: always off, it cannot be activated (soft refusal), and its
  enchantment never counts.
- Extra weapon effects (fire d6 and the like) go into the "activated" tab and work only while activated.
- Deactivation (the short rest for "day" items, the long rest for all) removes the enchantment bonuses.
- Order of item numbers [OWNER, package 9, closes Q38]: the item's own base first, then enchantment N (only while
  activated), then the mastery picks. Hardness = (base + 2N) * (100 + mastery percent) / 100, rounded down; the picks
  "+30%" and "+70%" are ADDITIVE (both = +100%, x2, not x1.3 x1.7). Max HP = base + N + "HP +1" picks.
  Tests: hardness 5, +2 activated, +30% -> (5 + 4) * 1.3 = 11; +30% and +70% -> 18; not activated -> 10.

#### Item HP [OWNER, package 6, closes Q31]
- Item HP is stored as the CURRENT number (not as "damage taken"; no migrations, D1).
  Max = base max + HP from weapon mastery + N from enchantment (enchantment only while the item is activated).
- Switching an enchanted item ON: current HP +N (the enchantment bonus, flat, not proportional).
  Switching OFF: current HP * (new max / old max), rounded to nearest; a positive value is never rounded to 0
  (switching off never breaks the item by itself).
  Example: base 10, enchantment +3, active 13/13, damage 6 -> 7; off -> 7*10/13 = 5; on -> 8.
- Broken = item HP <= 50% of max (and > 0).
  Weapon: -2 to attack and damage with this weapon.
  Armor and shield (a shield counts as armor): the AC bonus is halved, rounded down; the armor skill penalty doubles.
- Item HP 0: the item does not work, no bonuses at all (no base values, no enchantment, no tabs). [OWNER, package 8
  R2] This includes an ACTIVATED item: +N attack/damage/lucky, armor/shield +N, hardness +2N and extra effects are all
  gone. Test: +3 sword activated at HP 8/13: +3/+3, lucky 17, hardness 16; at HP 0: 0/0, lucky 20, hardness 10.
- Mastery in item numbers [OWNER, package 8 R3]: the weapon mastery picks "weapon HP +1" and "durability +30% / +70%"
  of the item's group change its max HP and hardness (weapons.md). The group is the one of the item's main attack
  record (package 12: every record is a main record; with several, the primary one, else the first, Q76; no record ->
  no picks). A shield attacks
  through group Contact, so Contact picks reach a shield the same way. Tests: base 11 + HP pick -> 12 (6 of 12 is
  broken, 6 of 11 is not); hardness 10 with +30% -> 13, with +30% and +70% -> 20.
- Item HP below 0: destroyed for good (state "destroyed": cannot be activated, cannot be healed; stays in the list,
  grey, removed only by hand).
- Commands: damage_item(iid, amount), set_item_hp(iid, value) (manual, edit mode).
- Repair [OWNER, Q32]: only by hand in edit mode (set_item_hp); there is no repair command.
- Notches [OWNER, package 9 G]: command hit_item(item, damage) (damage_item stays the raw HP change). 1 notch = 1 item
  HP lost; notches = floor(damage / FINAL hardness) (base + 2N while activated + mastery). A durable item (flag; default
  yes for armor and shields, no for others) loses at most 1 HP per attack (source note: armor and shields cannot take
  more than one notch per attack). Hardness 0 or not set: no automatic notches, a clear refusal (use damage_item).
  Tests: hardness 5: damage 4 / 5 / 9 / 10 -> 0 / 1 / 1 / 2; durable 10 -> 1; +2 activated (hardness 9): 17 -> 1,
  18 -> 2; broken 5/10 hit 10 -> 3, then 15 -> 0.
- [OWNER, package 7] Armor and a shield at item HP 0 cannot be put on: the equip command refuses with a clear message.
  If such an item is already worn (its HP fell to 0 after damage), it counts as taken off: no AC bonus and no armor
  skill penalty. A weapon at HP 0 can be held, but gives no bonuses and no damage dice.
- A destroyed item (HP below 0) stays in the list, grey, gives nothing, cannot be activated or healed. Only the player
  removes it by hand (command remove_item, works for any item). Items are never removed automatically.
- Tests: the example above; a positive HP is not rounded to 0 when switching off; broken at exactly 50% and below,
  not at 51%; broken sword -2 attack and damage; broken armor 5 -> 2, armor penalty x2; shield like armor; HP 0 gives
  nothing; HP -1 destroyed and cannot be activated; a broken weapon shows -2 in the attack table.
- An item without HP (no base HP and no current HP entered, e.g. a ring) is not tracked: always working.
- Tests (package 7): armor at 0 HP -> equip refused; worn armor that drops to 0 -> AC without armor and no skill
  penalty; a shield the same; a weapon at 0 HP is held without bonuses; a destroyed item stays in the list and is
  removed only by remove_item; remove_item works for an ordinary item.
- Tests: +5 masterwork sword not activated: attack +1 (masterwork flag), damage +0; activated: +5; no price -> cannot be
  activated, no enchantment; +2 armor not activated -> base armor only; fire d6 only while activated; the short rest
  switches a "day" item off and the enchantment is gone.

#### Item codes / sharing [OWNER]
- Any item/ability/etc -> code copied to clipboard. Code -> import as item. [package 18] Built for catalog entries:
  store.export_entry / catalog_import_entry (catalog.md "Catalog files").
- Whole character copy, PDF export. UI must not block copy.

#### Enabled / disabled (activation) [OWNER]
- "Enabled/disabled" mainly means activation of enchanted/special items.
- Passive requirements: Qualification, skill X with Y ranks, Court X level Y.
- Activation has two kinds [OWNER]: "day" (active until the end of the SHORT rest) and "decade" (until the end of the LONG rest).
  The item card has a spirit price for each kind (usually 1 for day, 5 for decade, any X possible); a kind without a
  price is not offered. An item with no price for day nor decade is NOT activatable: activation gives a soft refusal
  "activation price not set" and nothing changes. If only one price is set, that one works.
  Short rest switches "day" items off, long rest switches off all.
  Cost may also be stat damage, HP, etc.
- Consumables: usually 1 spirit to activate.
- Not activated items give fewer bonuses. Example: +5 magic sword (+5 attack, damage and lucky attack = enchant bonus):
  inactive it is only a masterwork sword (flag) giving +1 attack, nothing else.
- Item activation data [OWNER, simplified]: item has two tabs: "not activated" and "activated". Either one set of effects or the other, never both.
  (An additive item just repeats the base effects in the activated tab.) No mode flag.

#### Consumables [OWNER, package 13 D]
- Item fields quantity (default 1) and consumable (bool). Weight counts unit weight * quantity (for every item).
- Command use_consumable(item_id, n=1): quantity -n, refused below 0 (and for a non-consumable). At quantity 0 the item
  stays in the list, greyed (derived flag spent) and weighs 0; only remove_item deletes it. Items are never removed
  automatically.
- Optional field on_use_status (a status id in the container): using the consumable activates that status; if the
  status cannot be activated (already active, no charge...) the whole use is refused (assumption Q87).
- [OWNER, Q86] The older field count is removed; only quantity remains (old files: count is dropped on load; the
  weapon catalog uses quantity, e.g. bolts x10).
- Tests: 3 potions of 5 L -> 15 L, after one use 10; at 0: spent, weight 0, still in the list; refusals; the status
  starts; remove_item deletes a spent item.

#### Charges and cooldown [OWNER, package 14 B; closes Q94]
- Anything usable may have charges and a cooldown: an item (and its abilities), a status entry, a feat, an attack
  record, a maneuver. Optional fields (Usage): charges_max, charges_current, recharge ("short_rest" | "long_rest" |
  "combat_start" | "combat_end" (package 17) | "manual"), cooldown_rounds, cooldown_current. A status keeps its existing charges (rest rules as
  before, Q97) and gets cooldown_rounds / cooldown_current.
- Commands: spend_charge(owner_kind, owner_id, n=1) (refused below 0 or while cooldown_current > 0; with
  cooldown_rounds > 0 the spending starts the cooldown), set_charges, restore_charges.
- The tick lowers cooldown_current by 1 for every owner. Rests and start_combat restore by the recharge rule (a long rest
  also restores "short_rest" charges, like pools: assumption Q96).
- Item charges live on the item (Q94); the old by-name item charges (Character.charges kind "item") are dropped on
  load (D1). The active list shows charges only of worn / held items.
- There is no separate "class / race ability" entity: such abilities are resource pools or statuses.

#### Base contents [OWNER text above; built in package 16 G7]
- An item left at the base = not carried, not worn, not held. It takes Item.base_slot_cost slots (default 1; grey
  items: spent or destroyed, 0) and gives the effects of its acting tab ("Strong": +2 Str, 10 slots). base_view =
  (used, max, over); max = base slots (+ whole attention base points + effects "base_slots"); over the max is shown red,
  never refused. Tests: Strong at the base -> Str 12, 10 of 5 red; two items + a spent potion -> 2 of 5.

#### Load display (package 30) [OWNER; closes Q197; the numbers do not change]
- From 0 to the light limit: "light". Above light up to the maximum (the heavy limit): "load" (the old "heavy" state,
  shown as "Нагрузка"). Above the maximum: overload, shown as "you are overloaded and can only drag" (red).
- The view gives the carried weight, the category key (light / heavy / overload), both limits and the text "40 of X"
  (X = the maximum). Example: Str 14 (+2): light up to 7.9 B = 79 L, maximum 12.9 B = 129 L.

## File: progression.md

### Progression

#### Level up [OWNER]
- [OWNER, package 33] A level-up needs exp.level_cost = 1000 experience and SPENDS it; the rest stays (1500 -> 500;
  999 -> refused "not_enough_experience"). The goal shown is always 1000 (the hand-typed goal is retired). Experience
  never goes above exp.max_banked = 1999 (no two banked level-ups): an entry that would pass it counts only up to 1999,
  the result reminds "the excess is not counted" (not a refusal), the log entry keeps what was entered and what was
  counted. The cost is a log entry of kind "level_up" (-1000); the level history keeps the XP before the cost.
  The hit-die roll counts at least 1 (a roll of 0 counts 1). Reminders of the level-up: "distribute the new drive
  points" and "you got X training" (X = 100 * new level).
  Tests: 1000 -> 0; 1500 -> 500; 999 refused; 1700 + 500 -> 1999 (counted 299); level 2 -> 3 gives 300 training;
  roll 0 -> 1.
- Hit die rolled OUTSIDE app, result entered; HP recorded. [OWNER, package 17, Q111] level_up without a roll takes
  1 and its result carries the warning "hit_die_default_used" (the UI shows "die not entered, 1 taken"); the value
  is editable by hand in edit mode. Max HP grows, the current HP is NOT healed. No level cap [OWNER, Q103].
- Max HP [OWNER, package 8; per die since package 16 G1] = the sum over ALL hit dice of max(1, die HP + CURRENT Con
  modifier) + race bonus (may be 0) + other bonuses (feats, class, quirks, items, effects "hp_max"); at least 1.
  Dice: one per level (level 1 = the maximum of the die, later levels = the value the player entered at level up,
  editable, at most the die), plus extra dice from templates and effects "extra_hit_dice" (one die per effect, its
  value = the HP of that die; no level cap).
  Tests (package 16): rolls 8 and 1 with Con 4 (-3) -> 5 + 1 = 6; extra die 6 with Con 14 -> 10 + 8 = 18.
  Training HP (50 per point, training.md) raise the hit-die HP only and never above die * level.
  Tests: rolls 10+6+6, Con 8 (-1), race 2, other 1 -> 22; Con 1 at level 1 with roll 4 -> 1; Con 14 with 4 damage ->
  mod 0; rolls 10+6 at d10: +1 for 50 -> 10+7; rolls 10+10 -> refused.
- Balance regen follows the CURRENT Con live (also after stat damage in combat). Test: Con 12 -> 8 mid-combat: regen
  3 -> 1, balance cap unchanged (9).
- Training gained at level-up = 100 * new level. At creation (level 1) the player gets 1000 training [OWNER]. Spend on almost anything: e.g. raise HP (per level roll up to theoretical hit die max),
  weapon mastery, styles, etc. (list in old editor). Many training options already work.
- Comfort can be exchanged for training.

#### Weapon mastery
See weapons.md (full rules). Training cost = (30+5X)*difficulty*scale per grade.

#### Spell mastery [OWNER]
- Spell has up to 3 upgrades, each costs 25*(1+circle^2) training, each upgrade takes >= 1 star, spell max 3 stars.
- One upgrade may take all 3 stars.
- Example: circle 2 upgrade = 25*(1+4) = 125.
- Owner text (verbatim, package 4): "Мастерство заклинания - 25*(1+круг^2)". "Вы можете изучить какое-то заклинание на
  продвинутом уровне. Каждое заклинание обладает тремя т.н. "слотами". Вы можете заучить любые улучшения в эти слоты,
  в т.ч. дублирующиеся. Обычно улучшение занимает 1 слот, второе идентичное улучшение занимает 2 слота.
  Метамагия занимает количество слотов, равное своему кругу усложнения. Вам нет необходимости обладать соответствующей
  чертой метамагии, и Вы все еще можете использовать бонусы от других черт метамагии при произнесении этого заклинания
  по обычным правилам."
  ("slots" here = the "stars" above.) Tests for later code: two identical upgrades = 1 + 2 = 3 slots (full);
  a metamagic of +2 circles takes 2 slots.

#### Class system v0 (package 25) [OWNER consent, package 25 B; ASSUMPTION values marked]
- One class per character (no multiclass); a class is a catalog entry (kind "classes"): hit die, BAB growth
  (good / medium / poor), a progression per save (good / poor), class skill list, spellbook flag, divine flag, spell
  failure mode default, own professionalism flag, notes. Shipped entries are SAMPLES (fighter-like, mage-like with a
  spellbook, cleric-like divine).
- No class: BAB and base saves are typed by hand, as before. With a class they are derived from class + level; a
  hand-typed override wins when it is set.
- ASSUMPTION (data constants, editable): BAB = level * factor (good 1, medium 0.75, poor 0.5), rounded down;
  good save = 2 + level / 2, poor save = level / 3, rounded down. Tests: good level 5 = 4, poor level 5 = 1.
- The class hit die caps level_up. The spellbook flag makes learn_spell half price by default; the divine flag
  makes the spell failure mode default "balance to 0".
- Professionalism (training.md, closes Q104): a class with its own professionalism refuses the 300 option; the
  chosen skills must be in the class skill list.

## File: skills.md

### Skills [OWNER]
No skill points for classes. Everyone has training points; skills are trained with training.
Skills are SORTED by key stat: Str, Dex, Con, Int, Wis, Cha. Auto-sort can be turned off or changed (by name etc.). "Class" of a skill = tier (normal/advanced/specialized), not a group.

#### Roll bonus
skill = ranks + key stat mod + bonuses (race/class/items...) + armor penalty (if it applies) [+3 if advanced].

#### Categories
- Normal: default for ALL skills (even 0 ranks). Ranks cannot exceed character level.
- Advanced (formerly "class skill"): +3 to the roll, cheaper ranks. Gained via training, specialization, lenses, loot, etc.
  [OWNER, Q64] Advanced ranks are capped by the character level too (like normal); only specialized have no cap.
  Test: level 2, advanced rank 2 -> 3 refused.
- Specialized: only an advanced skill can become specialized. No rank cap; ranks auto rise to character level (floor = level);
  more ranks bought with training above the level limit (cheapest). Twice per cycle after a roll: take 13 or reroll.
  Gained by training (expensive) or class feat "Professionalism" (TBD, cheaper).
- "Cycle" = GM-announced big time span (see injuries.md).

#### Skill catalog [OWNER]
- The default skill catalog (45 templates) is DATA, not hard-coded: the catalog file wp/catalog/data/skills.json,
  made from skills_list.md (package 18; a test checks they agree). [OWNER, package 18] Medicine is an Int skill. The player may add own templates (catalog.md).
- A new character starts with ONLY two skills: Perception (perception) and Search (search), both 0 ranks.
  Every other skill is added by the player from the catalog (picking a template creates the skill with 0 ranks).
- Templates flagged `param` are families: on adding, the player names the sub-skill. Examples: "Craft (smith) III" =
  template craft_3 named "smith"; "Culture knowledge: North"; "Piloting: air". Each sub-skill has its own ranks;
  several sub-skills of one family may exist.

#### Training cost
- Normal +1 rank: 20 * rank.
- Make a skill Advanced: 40 + 20 per OTHER advanced skill; specialized skills count as advanced here (a skill goes
  normal -> advanced -> specialized) [OWNER, package 8]. Advanced +1 rank: 15 * rank.
  Test: 1 advanced + 2 specialized: the next advanced costs 40 + 20*3 = 100; specializing the advanced one 200 + 50*2 = 300.
- Make a skill Specialized: 200 + 50 per OTHER specialized skill. Specialized +1 rank: 10 * rank.
- "rank" in the cost = the NEW rank [OWNER]. Tests: normal 0->1 = 20, 2->3 = 60, 19->20 = 400; advanced 0->1 = 15; specialized: ranks above level only (e.g. level 5, rank 5->6 = 60).
- Specialized ranks up to the character level are free/automatic; the 10*new_rank price applies only to ranks ABOVE the level [OWNER confirmed].
  A rank bought above the level that later becomes free (the level catches up) is NOT refunded [OWNER, Q17].
  So tests: specialized 19->20 = 200 is a purchase only for a level < 20 character. 0->1 is never bought.
- Examples: 2nd advanced skill costs 40+20*1 = 60. 3rd specialization costs 200+50*2 = 300.

#### Creation and free grants [OWNER]
- At character creation (level 1) the player gets 1000 training, spent on anything: feats, new class and race abilities, skills, weapon groups.
- A class feat taken at creation (e.g. Professionalism) can give a specialization of another skill for free.
- Free advanced/specialized skills STILL COUNT as "other" advanced/specialized skills for the price of later ones.
  Example: free specialization + buying 1 more: the second one costs 200 + 50*1 = 250.

## File: weapons.md

### Weapon proficiency (mastery) [OWNER, pasted text]

#### Levels 0-12
0 none, 1 Novice, 2 Apprentice, 3 Amateur, 4 Skilled, 5-7 Specialist I-III, 8-11 Expert I-IV, 12 Master.
Level is per weapon "target" (see scale). Weapon stores required level (qualification level) and difficulty.
- Not qualified (level < required): -4 to hit, no free attacks. One level below required: penalty -2 [owner, first message].
- Qualified: may use maneuvers of the weapon group; some weapons unlock extra bonuses at higher levels.

#### Difficulty and scale
- Difficulty (learning complexity): set by GM, stored on the weapon group. Usually = weapon generation: 1 medieval, 2 first-gen firearms, etc.
  Some weapons have raised difficulty. App only records it.
- Scale: 1 = one named weapon (my sword Nirgod); 2 = a variety (long swords); 3 = a country/school group ("Fatom heavy blades").
  Hierarchy: group (3) contains variety (2) contains named weapon (1).

#### Cost of +1 grade
cost = (30 + 5*X) * difficulty * scale
- X = number of weapon groups already developed to Expert (8) or higher, excluding the group being raised.
  [OWNER] Any node of any scale counts (child or not). Test: three experts (8, 9, 10): each expert X = 2, any other weapon X = 3.
- Cost grows only through OTHER groups at expert+.
- Examples: X=0, difficulty 1, scale 2 -> 60. X=2, difficulty 2, scale 3 -> (30+10)*2*3 = 240.

#### Combat basics (one-time per weapon branch)
- Cost 50 / 100 / 150 for scale 1 / 2 / 3 [OWNER confirmed]. One-time raise by (5 - difficulty) grades
  (difficulty 1 -> +4) for the named weapon / variety / group.
- Does NOT stack with itself [OWNER confirmed]: effective basics bonus of a weapon = max over all its ancestors, never a sum.
  Example: grandpa's sword (scale 1, 50) + long swords (scale 2, 100) + heavy blades (scale 3, 150) -> grandpa's sword level stays 4, not 12.
  Taking the +4 on another ancestor never makes it 8.
- Data need: each weapon stores its parents (variety and group); one variety can sit in several groups
  (e.g. long swords in "Eastern fighting style", scale 3).
#### Bonuses by tier (player picks)
Specialist I/II/III (levels 5,6,7): one pick each, 3 picks total. Need 3 specialist picks before expert picks start.
- Parry +1; weapon durability +30%; proficiency bonus to attacks +1; crit range +1; ranged range +10 ft; balance regen +1/turn.
Expert I-IV (levels 8-11): one pick each, from expert or specialist lists.
- Weapon HP +1; durability +70% (stacks with specialist); damage +3; ignore first vulnerability in a fight; ignore 20% cover;
  lucky attack +1; first ranged attack each round can be parried.
Master (12): one pick from master, expert or specialist lists.
[package 15] Picks without a numeric effect are STORED ONLY (no mechanics): reroll one d20, one attack per turn
without the [attack] tag, once per combat restore all balance as a free action, ignore the first vulnerability,
ignore 20% cover, the first ranged attack can be parried. Combat basics are bought with buy_combat_basics.
- Reroll one d20 with this weapon; one attack per turn without [attack] tag; once per fight free action: restore all balance.
Repeat limits: a specialist bonus may be picked again (2nd time) from expert level; 3rd time at master.
An expert bonus may be picked a 2nd time at master.
Tests: after 3 specialist picks all different, expert picks open; at level 9, picking "crit range +1" a 2nd time is allowed; 3rd is not until 12.

#### Weapon groups and attack records [OWNER]
- A weapon group is a list of weapons sharing bonuses created by mastery (e.g. "Basic/simple": dagger, club, staff,
  light crossbow, bolts). A weapon may be in any number of groups.
- Attack, damage, parry and other bonuses come from ONE chosen group only; bonuses of two groups at once are not
  possible. Bonuses of parent (higher) groups are NOT added. (Grade levels and combat basics still follow D16.)
- Group "Contact" (level 0) is in every new character and in the catalog. "Unarmed combat" is an ordinary WEAPON
  (catalog entry) in group Contact, with its own mastery node of scale 1 (or 2) [OWNER]. Unarmed combat needs no
  weapon in the hands. Its passive bonuses (parry, balance regen) work always, even when armed; its attack and damage
  bonuses work only on the unarmed attack [OWNER, Q18].
- Group "Basic/simple" is special: no qualification, no maneuvers or special abilities, it cannot be trained; attacks
  with these weapons take no -4/-2 qualification penalty.
- Weapon card fields (owner's table): name, price (gp/sp), damage small and medium (dice), crit (range and multiplier),
  range, weight (stored in L), type (P/S/B), qualification (e.g. "Skilled", "Specialist 2"), finesse, hands (1H/2H),
  hardness (HD), item HP, list of groups. A value "Vary." is allowed: the field stays empty and is marked variable.
  Ammunition (bolts) are separate items with a piece counter.
- Catalog rows (owner's table, more later):
  Contact: Unarmed combat (1d2/1d3, crit 20, B, Skilled, finesse, 1H, no HD/HP); Stiletto (5 sp, 1d3/1d4, x3, weight L,
  P, Skilled, finesse, 1H, HD 10, HP 1); Spiked gauntlets (5 sp, 1d3/1d4, x2, weight L, P, Skilled, finesse, 1H);
  Improvised weapon (damage, weight, type, hands variable, x2, Skilled); Hidden thief weapons (all variable,
  Specialist 2, finesse, 1H).
  Basic/simple: Dagger (1 gp, 1d3/1d4, 19+, 10 ft, weight L, P/S, finesse, 1H, HD 10, HP 1); Club (-, 1d4/1d6, 20+,
  weight 1, B, 1H, HD 5, HP 2); Quarterstaff (2 sp, 1d4/1d4 and 1d6/1d6, 20+, weight 1, B, 2H, HD 5, HP 2);
  Light crossbow (1 gp, 1d6/1d8, 19-20, 80 ft, weight 1, P, 2H, HD 3, HP 2); Bolts x10 (1 sp, weight L, HD 0, HP 1, ammo).

#### Weapon card details [OWNER]
- Shield as a weapon [OWNER, package 5]: a shield can be used as a weapon, improvised (group "Contact") or as a
  separate weapon with its own rules (then the card lists its groups). A shield in a hand has BOTH its shield bonus to
  AC and an attack record; its hands are counted once. By default the shield's attack record is in group "Contact"
  (improvised). Test: shield + sword in hands, the shield has an attack record, AC with the shield stays, 2 hands used.
- Double weapon (quarterstaff): the card has two damage rows, one per end. A normal attack uses the TOP row.
  A double weapon counts as fit for two-weapon fighting; its other end counts as a light weapon.
  Quarterstaff "1d4/1d4 and 1d6/1d6" = small 1d4 on both ends, medium 1d6 on both ends.
- Light and finesse are ONE flag (column "F." of the table). An unarmed strike is always light.
- Spiked gauntlets: you cannot parry with them; it is the same as parrying with an empty hand.
- Unarmed combat has no privileges [OWNER, Q20]: its qualification is Skilled (4); until it is trained to level 4
  the unarmed attack takes the -4 "not qualified" penalty.

#### Mastery bonuses in the final numbers [OWNER]
- Weapon mastery bonuses stack with themselves by their own rules, then are added as FLAT to AC (parry), attack, damage.
- They change the FINAL durability (hardness) and HP of the item, not the value the author typed into the item.
- Item HP [OWNER, package 6]: the weapon's HP is stored as the CURRENT number; max = base + mastery HP + enchantment N
  (while activated). Broken (HP <= 50% of max, > 0): -2 to attack and damage with the weapon. HP 0: the weapon does
  not work. HP below 0: destroyed for good. Full rules: gear.md "Item HP".
  Durability: specialist +30%, expert +70% (they stack). Item HP: +1 per expert pick.
  Example: +30% and +70% picks -> +100% of the base durability.
  [OWNER, package 9] The percentages ADD (x2, not x1.3 x1.7) and apply after the enchantment: (base + 2N) * (100 + %).
  Only the item's MAIN attack record's group counts (gear.md "Order of item numbers").

#### Notes
- This "qualification" is weapon level; item "Qualification N" in gear.md is a different mechanic (per-item, 50 training/level).
- Styles: similar branch rules; app can record one style per equipped weapon or two attack variants (progression.md).
- Crit range +1 per pick, at most 3 (specialist, expert, master) [OWNER, package 17, Q113]; keen doubles the base range.
- [OWNER, package 17] "Once per combat" picks (reroll one d20, free action "restore all balance", the first ranged
  attack can be parried) are USAGE CHARGES: max 1, recharge at the end of combat; owner kind "pick", id
  "<weapon node id>:<slot>" (spend_charge / set_charges / restore_charges). restore_all_balance(pick_id) spends the
  charge and sets the balance to its max (no dice, nothing else; refused while a block_restore covers the balance,
  Q128). The app tracks abilities and never rolls dice.
- [package 25 E] The stored-only picks "one attack per turn without the [attack] tag", "ignore the first
  vulnerability in a fight" and "ignore 20% cover" are shown as available abilities in the attack and defense
  views. "Ignore the first vulnerability in a fight" is once per fight: a usage charge (max 1, recharge at the end
  of combat). No numbers change.

## File: narrative.md

### Narrative

- Quirk: special narrative ability; like race/feat can change any part of sheet (even another ability, then by hand).
  "Burn": stays in list, grey, status "destroyed", reversible by hand. Deletion only manual.
- Quests, Courts, Stories, Quirks: template-based notes for the player; any can be a chip with tooltip showing text.
- Quests give Drives and Courts. Court-quests live next to quirks/stories tabs; drive-quests in the Drives tab.
- Drives may give roleplay resources such as Attention. Attention can be spent to remove pain(OT?), gain comfort, get bonuses.

#### Courts (Dvory) [OWNER]
- Parameter with Level and Tier, written like "Skull 5t1" = level 5, tier 1. Narrative; player keeps a description note.
- Used for item requirements ("Court X level Y") and to see which items he can activate from the list of his courts.
- Courts give narrative quests. Drives and Lenses also give narrative quests.
- Court chance for divine slot restore: see rest.md (formula TBD).

#### Cycle end button (idea) [OWNER]
- Button "end of cycle" [OWNER]: adds Attention (1 + levels reached that are multiples of 3: 3, 6, 9... + 1 per drive
  at level 4+) and burns unspent time points (OV); it also drops BP above max (overcap, rest.md) [OWNER, package 8].
  Nothing else. The cycle length is set by the GM (module).
  Example: level 7, two drives at 4+ -> 1 + 2 + 2 = 5.
- The end of a cycle implies a long rest, but they are separate buttons: one never triggers the other [OWNER].
- Attention is its own resource: no cap, never burns, accumulates.
- OV (time points): 1 Attention gives OV equal to the Con modifier (minimum 2). OV are spent on recipes (crafting) and
  narratively; unspent OV burn by hand or with the end-of-cycle button. No cap.

#### Lens [OWNER]
- A quest-like goal with a counter shown on the interface: "New World" 11/15. Only the player changes +/- by hand.
- At 0/max: lens turns red, tooltip says ask the GM for a penalty. At max/max: green, tooltip says ask the GM for a reward.
- Player deletes it after the goal is reached; the GM gives the reward.
- Lens can also give an advanced skill (skills.md).
- Lens counter: starts at 1 of X (X set by the player). Range is strictly 0..X, the app clamps; 0 and X are the END states.
  Examples: new lens 1/15; at 11/15 + 4 -> 15/15 (green); at 1/15 - 1 -> 0/15 (red); cannot go to 16 or -1.

#### Notebook commands [OWNER, package 16 F]
- Records: quests, stories, courts (level + tier, label "Skull 5t1"), quirks (effects like a feat while not burned),
  lenses (counter), drives (level 0..5). add_note(kind, name, ...), change_lens(lid, delta) (clamped 0..X: 0 red,
  X green), set_drive_level(did, level) (0..5, else refused), burn_quirk(kid, burned) (reversible); any field without
  limits: edit_entry / remove_entry (edit mode). Only drives take part in the attention income (+1 per drive at 4+).
- Tests: lens 1/15 -> 11 -> 15 green, +3 stays 15; 1/15 - 1 -> 0 red; drives 4, 5, 3 at level 7 -> 5 attention; quirk
  +2 Str 12 -> burned 10 -> restored 12.

#### Not built on purpose [OWNER, package 17, closes Q122]
- Money is NARRATIVE: no mechanics, no counters, no prices in the app. There is no "start session" and no "end of
  session" button: only the end of cycle (above).
- [OWNER, package 26 C; replaces "XP is narrative"] Experience (XP) is a tracked counter with a log and notes: every
  entry has an amount (may be negative), an optional note and a time stamp; the total is the sum of the log. No
  automatic level-up. [OWNER, package 33; replaces the hand-typed goal] The goal is always 1000 (the level-up cost),
  the total is at most 1999, a level-up spends 1000 as a log entry (progression.md "Level up").
  Every level-up writes the level history (level, XP at that moment, hit-die roll, note, time).

#### Drives: level notes and principles (package 25) [OWNER]
- A drive list with numbers 0-5, the bonus/penalty text beside each level, and a principle = a narrative
  description the player must write when the drive is 2+.
- [package 25 C] The texts are narrative only (no calculation). From level 2 (data constant) the drive shows a
  reminder while the principle is empty; it never blocks anything. The attention income is unchanged.

#### Drives (package 28) [OWNER]
- Story power is narrative and kept OUTSIDE the program: no story-power number in the app; penalties are text only.
- Drive types (catalog drive_types, 10, each with a Russian description shown on hover, the owner may edit it):
  Idealism, Growth, Knowledge, Autonomy, Pleasure, Material, Triumph, Success, Society, Decadence. One drive record =
  one type + level 0-5 + principle (taboo text) + quest + per-level notes. Normally one record per type; a custom
  type by hand is allowed. Levels of different types are NOT summed.
- Start budget 12 points (constant drives.start_points): the view shows "distributed X of 12" as a hint only;
  nothing is blocked or clamped (edit mode changes levels freely).
- Levels (texts in the locale files, keys drive_level.<n>.obligation / bonus / penalty, editable):
  - 0: no obligations; the DM may appeal to the drive to make you oppose an ally's task (reward for success:
    comfort); no penalty.
  - 1: nothing.
  - 2: taboo (the principle). Bonus: may spend spirit for +1 to rolls while the drive is under threat (spirit is
    spent by hand).
  - 3: taboo, may take a quest. Spirit +2. Finishing the quest gives comfort (entered by hand). Penalty text: -1 story
    power each cycle until the quest is closed.
  - 4: taboo, the quest is mandatory. Spirit +3. The quest gives comfort. +1 extra attention per cycle. Penalty
    text: -2 story power each cycle until the quest is closed.
  - 5: as 4, spirit +4, penalty text -3; label "You are obsessed".
- Quest per drive: state none / taken / closed; comfort_received is a flag set by hand.
- Reminders (never blocking): "write the taboo" for a drive at 2+ without a principle; "take a quest" for a drive at
  4+ without a taken or closed quest; level_up reminds "distribute new drive points" (no number, the owner decides);
  the end of cycle lists "open quest of drive X, penalty: <text>" for a drive at 3+ whose quest is taken, not closed.
- Buying a level with comfort: +1 level for 3 comfort (drives.buy_up_cost), -1 level for 2 comfort
  (drives.buy_down_cost); the level stays 0-5 (out_of_range); not enough comfort -> not_enough_comfort. In edit mode
  the level changes for free (edit_drive).
- Attention at the end of cycle is unchanged: 1 + one per level multiple of 3 + 1 per drive at 4+.
- Tests: level 7 and two drives at 4+ -> 5 attention; level 3 with a taken quest -> the end-of-cycle reminder, closed
  -> none; level 1 -> no flags; level 2 without a principle -> principle missing; level 4 without a quest -> quest
  missing; level 5 -> obsessed; buy up at comfort 3 -> +1 level, comfort 0; at comfort 2 -> refused; buy down at 0 ->
  refused; buy down costs 2; levels 14 of 12 -> no refusal, hint only.

#### Race narrative and end of session [OWNER, package 36]
- Narrative race abilities with no mechanics are text only. "End of session" effects (Azana: injury points - 4) are a
  manual trigger button on the ability (there is no session button, Q122). Comfort per cycle (a reliable rear) is a
  cycle_end trigger with a button "+2 comfort".

## File: catalog.md

### Catalog [OWNER]

- The catalog is a DATABASE of everything: items, weapons, weapon groups, feats, class/race abilities, spells, injuries, recipes...
  Loaded from files dropped into a folder on the PC (and later maybe from a shared link, e.g. cloud drive: give a link, others get the data).
- Any character can buy or copy (get) anything from it: feat, class ability, race ability, etc.
- Filters COMBINE: category + sub-filter + source/country.
  Examples: Items = all items; Items + Weapons = weapons only; Items + country X = items of X; Weapons + country X;
  Weapon groups + country X = all groups of X (add at level 0, then train); filter by class name "wizard" = all its class abilities
  (take those needed for the level).
- Sort/filter axes: weapons, armor and shields, source (tag = player name or module), magic items, spells, feats, "other".
- Users create their own catalogs and entries; players share files. Anything a player creates can be put into a catalog.
- Enabled catalogs: one list for the user (global), not per character.
- Weight in catalog rows [OWNER]: "L" = 1 L; a plain number N = N * 10 L (1 = 10 L = 1 B). The unit "B" is not
  written in the rows.
- Skills: the default skill catalog ships with the app as data (skills_list.md, 45 templates); see skills.md "Skill catalog".
- Armor and shields [OWNER, package 9]: two example data sets ship as data (since package 18 both live in the
  catalog file armor_shields.json, field "set": set_1 "Country 1", 8 rows; set_2 "Country 2", 15 rows). They are tables from a game, rules may differ per game: plain
  selectable data sets, not hard rules; another value of "set" is one more set. Row fields: id, name, kind
  (armor / shield), category (armor light / medium / heavy; shield light / heavy / tower), weight, price (text as
  written), access_class (set 1 only), ac_bonus, touch_bonus, max_dex, skill_penalty (positive = penalty),
  speed_penalty_ft, spell_penalty_mana, spell_failure_pct, special ("+" column of set 2), hardness, hp, durable.
  English names for now; the owner adds Russian names later. [OWNER, package 10, closes Q53] Set 1 "magic" numbers
  are a positive extra mana cost (source -1 -> 1); weight "(1)" = 1 = 10 L as usual; access class and set 2 "+" are
  data; rules per game may change.
- Shop is just a layer on the catalog [OWNER]: taking an item from the catalog can buy it at once (gold deducted automatically);
  taking a feat can buy it for training (only if the checkbox "pay with training" is on). Items only for gold.
  [OWNER, package 17] Money is NARRATIVE: the app keeps no money and deducts nothing (Q122 closed); the shop layer
  only copies an item from the catalog.
  Old characters are not migrated (D1).

#### Feats [OWNER, package 38, decisions 2, 3]
- Toughness: +3 HP; for every Hit Die beyond 3, +1 HP: HP bonus = max(3, Hit Dice); Hit Dice = the character level.
  Tests: level 1 -> +3, level 3 -> +3, level 7 -> +7.
- Endurance: +4 situational (with a note each, never in a total) on Swim checks vs nonlethal damage from exhaustion;
  Con checks to continue running, vs nonlethal damage from a forced march, to hold breath, vs nonlethal damage from
  starvation or thirst; Fort saves vs nonlethal damage from hot or cold environments and vs suffocation damage.
  "May sleep in light or medium armor without becoming fatigued" is text only.

#### Two names [OWNER]
- Everything can store two names: the list name and a short name (used on chips and buttons).
- Plan (not rule): button label may be replaced by an image.

#### Catalog files [OWNER, package 18, D21]
- Every catalog is ONE self-contained JSON file that the program (and later the UI) loads, lists, edits, adds to,
  deletes from and creates from scratch with no code change. One shipped file per kind in wp/catalog/data/:
  weapons, armor_shields, items, spells, statuses, skills, weapon_groups, feats, damage_types, doll_slots. A user can
  create more catalog files of a kind.
- Format: {"kind", "format": 1, "title", "counter", "retired", "meta", "entries": [...]}. Every entry: a stable id (made
  by the program from the name: transliteration, a number from the file's counter on a collision; a deleted id goes
  to "retired" and is never given again), name (free text), sample (bool), the fields of its kind. Unknown entry
  fields are KEPT on edit and save and never interpreted; unknown top-level fields are dropped on load (no
  migrations). The fields of each kind (name, type, required, allowed values) are DATA: catalog_schemas.json.
- Two layers: shipped catalogs (read-only, the install folder) and user catalogs (a folder next to the characters,
  catalogs/<kind>.json; more user files of the same kind are named <kind>__<name>.json, package 22 B9, Q152).
  A user entry with the same id wins ("override"); removing a shipped entry writes a
  tombstone into the user file; reset drops the override or the tombstone. The program never writes into the
  shipped folder. The program's own loaders (weapons, groups, armor, feats, skills, damage types, doll slots) read
  through this layer.
- Catalog commands are the ONLY way to change a catalog (like character commands, D5): catalog_add_entry,
  catalog_edit_entry, catalog_rename_entry (id stays), catalog_remove_entry, catalog_duplicate_entry,
  catalog_reset_entry, catalog_import_entry, catalog_create. Refusals carry a reason id + params. Saving is atomic
  (temp file + replace; a failed save keeps the old file). The UI later reads catalogs through the catalog view (list
  with a filter text and a sort; get, with the layer shipped / user / override) and writes them only through these
  commands.
- [package 26 C] Experience is not a catalog: it is a log on the character (narrative.md "Experience").
- Sharing: one entry -> a text code (export) and back (import as a new entry, gear.md "Item codes"); a whole
  catalog file can be exported / imported as it is.
- The rows shipped in package 18 for weapons, armor / shields, items, spells and statuses are TEST SAMPLES
  (sample = true) [OWNER]: the owner replaces them through the future UI.

## File: spells.md

### Spell record [OWNER]
A spell is: name + damage (if any) + range or AoE (if any) + optional effect (bonuses/penalties) + link to the spell + description.
- The effect is quick to reach from the spell and from the buffs list (see buffs.md "is buff").
- Damage depends on level, types, areas, range [editor BETA].
- Cost: mana/slot/overload rules in classes_magic.md.
- Stance (combat.md): a feat with a checkbox "is stance". Feats can already give permanent bonuses and penalties through the universal
  bonus/penalty block, so a stance may e.g. disable the Dex bonus to AC. Only a checkbox, no special fields.
  [package 12] Built as combat.md "Stances" (is_stance + active_stance). "Disable a bonus" (Dex to AC, dodge) is a block
  effect since package 13 (buffs.md "Block effects", e.g. block_bonus dodge on ac).

#### Metamagic [OWNER, package 10, docs only; not built]
- Metamagic "+1 circle" raises the spell cost by 2 mana (circle table 0, 1, 3, 5, 7, 9, 11, 13, 15, 17 for circles 0-9).
- A cantrip (cost 0) with +1 circle costs 2, so it is available from level 2 (the per-spell limit = level of mana,
  classes_magic.md "Mana level").
- Slot casters use a slot of the needed circle; the same per-spell limit applies.
- [OWNER, Q62 accepted] Each further +1 circle adds another +2 mana.

## File: skills_list.md

### Skills list (default catalog) [OWNER text, verbatim Russian; structure added]

For Claude (English): this is the DEFAULT catalog of skills, shipped as data (a catalog file), not hard-coded.
The player can edit/add skills (catalog rules: catalog.md). Costs and tiers: skills.md. Each skill has:
id (ASCII), stat, name (RU/EN via i18n), description (owner text), flags.
Flag `param` = "(х)": a family; the player adds named sub-skills, each with its OWN ranks
(e.g. Piloting: air / water / space; Culture knowledge: one per region; Acting: one per art; Craft: three TYPES I/II/III, each with a named craft).
Counts: STR 1, DEX 7, CON 1, INT 23, WIS 5, CHA 8 = 45 entries. [OWNER, package 18] Medicine is an Int skill.
Mechanical hooks mentioned by the owner (only these are rules, the rest is flavor text for the tooltip):
- Concentration: helps to act in negatives (DC 20, see resources.md "Dying").
- Self-hypnosis: may help to restore balance (hook for effects, not an automatic rule).
- Linguistics: for learning languages (training.md "Languages").
- Decipher: finds patterns, good for training (flavor, no automatic rule).
- Flight: useless for people without wings (flag `needs_flight`, informational).

#### СИЛА (STR)
- athletics | Атлетика — Физическая компетенция - плавания, подтягивания, перенос грузов

#### ЛОВКОСТЬ (DEX)
- acrobatics | Акробатика — Контроль собственного тела. Может быть использовано в бою для избегания противника. Обычно считается стрессовым броском, может пригодиться во время падений, контроля собственного тела в воздухе и подобного.
- sleight | Сноровка — Мелкая моторика и умение точно двигать руками. Сюда же могут подойти кража кошельков, подложить что-то, вдеть нитку в иголку, показ карточных фокусов и пр.
- stealth | Скрытность — Умение скрывать себя либо какие-то предметы. Подразумевает как умение выбрать позицию, психологический навык "не отсвечивать", так и физическую подготовку, умение притворяться статуей и так далее.
- piloting (param) | Пилотирование (х) — Использование воздушной техники, водной техники и космической техники. Применяется редко. (каждый вид техники отдельный навык)
- driving | Вождение — Управление любым наземным устройством, способным нести несколько пассажиров - машины, танки, колесницы и т.д.
- siege_operation | Управление — Управление боевой техникой, например, баллистами, катапультами и т.д. Включает в себя компетенцию как стрелять, так и перезаряжать.
- flight (needs_flight) | Полет — Способность эффективно перемещаться в воздухе и справляться со стрессовыми ситуациями, когда тело не касается земли. Для людей без крыльев бесполезно.

#### ВЫНОСЛИВОСТЬ (CON)
- concentration | Концентрация — Умение делать свое дело под внешним стрессом, например, когда тебя трясут, тыкают ножом, заламывают и так далее. Преимущественно боевой навык. Позволяет эфективнее действовать в минусах (кс 20).

#### ИНТЕЛЛЕКТ (INT)
- appraisal | Оценка — Умение отличить дорогое от дешевого, определить цену, теоретическую экономическую базу. Обычно помогает в определении лута.
- decipher | Расшифровка — Умение взламывать шифры, ключи, электронное или магическое ПО. Также это умение позволяет находить паттерны, что позитивно влияет на тренировки.
- mechanics | Механика — Взлом замков + взлом устройств + физические изменения в любой технике. Починить колесо у телеги, заклинить дверь и т.д. Не позволяет создавать что-то новое с нуля, если это только не какая-то простая вещь.
- craft_1 (param) | Ремесло (х) I — Добывающие ремесла (первый тип) позволяют из дикой природы добывать ингредиенты - травы, кожу, руду и пр.
- craft_2 (param) | Ремесло (х) II — Обрабатывающие ремесла (второй тип) позволяют заниматься обслуживающей или поддерживающей активностью - обучать солдат, стричь людей, красить дома, управлять агентурной сетью.
- craft_3 (param) | Ремесло (х) III — Производственные ремесла (третий тип) помогают создавать необычные вещи по рецептам для личного пользования или продажи.
- forgery | Подделка — Найти подлоги, создать подлоги, борьба с активным соперником (вирусы, антивирусы и пр.). Фальшивые документы и подобная техническая база. Узко специализированный навык.
- search | Поиск — Умение искать и находить спрятанные объекты и другие неодушевленные предметы. Ключевой навык мам, ищущих одежду в шкафе или еду в холодильнике. Не позволяет искать живых существ - для этого нужен навык "восприятие", так как поиск больше в себя включает внимательность и методичность, а восприятие - знание психологии и интуицию.
- magic_art | Искусство магии — Умение изменять магию относительно ее классических рамок. Часто используется для магических предметов.
- linguistics | Лингвистика — Навык для изучения новых языков.
- know_magic | Знание (магия) — Теоретические нания о магии, магических существах, псионике, магических предметах, школах магии, мане и подобному. Не включают в себя практические знания.
- know_engineering | Знание (инженерия) — Теоретические знания об архитектуре, технике, зданиях и механизмах.
- know_monsters | Знание (монстроведение) — Теоретические знания о монстрах вообще, довольно широкие и из-за этого менее эффективные, чем профильные. Помогают понять, чем отличается серебрянный медведь от белого, определить какие-то изменения у них, а также что может быть самым ценным на продажу.
- know_geo_econ | Знание (география и экономика) — Теоретические широкие познания в экономических моделях, что дешевле/дороже, чем примечателен какой-то город или населенный пункт. Также может помочь с нахождением какого-то старого местного знакомого, способного о чем-то рассказать или выполнить простое поручение.
- know_history | Знание (история) — Теоретические знания о прошлом, различных сценариях, паттернах вроде "паттерна трех", умение находить аналогии и проецировать опыт на текущую ситуацию.
- know_culture (param) | Знание (культура) (х) — На самом деле это целое дерево навыков, так как для каждого региона нужно свое знание культуры. Наличие знакомых в данной культуре, умение разбираться в их боевых стилях, поведении, одежде, примечательных личностях вроде политиков, медийных личностей и так далее.
- know_nature | Знание (природа) — Умение разбираться в травах, животных, ландшафтах, погоде и так далее. Опять же, в первую очередь это теоретические познания.
- know_politics | Знание (политика) — Знание этикета, умение подстраиваться под окружение, разбираться в геральдике и находить командира/главное лицо. Включает в себя умение держать лицо, вести себя соответствующе образу, подбирать одежду и так далее.
- know_religion | Знание (религия) — Понимание церквей, Дворов и нежити. Часто используется, когда происходит какая-то непонятная белиберда, явно содержащая в себе сверхъестественное. Не помогает определять, какой двор за что отличает.
- know_war | Знание (бой и война) — Понимание стилей боя, армейской и военной рутины, патрулей, военной разведки. Помогает определить, насколько серьезный противник перед вами.
- know_planes | Знание (другие миры) — Они же "планы". Умение разбираться в пришельцах, контрактах, призывах.
- know_it | Знание (IT) — Теоретические познания в том, как работают информационные технологии. Могут косвенно помочь в том числе и в магических устройствах. Позволяют анализировать работы различных "черных ящиков", а также базовые познания в программировании. Обычным людям доступно редко.
- medicine | Медицина — "Тяжелая" медицина. Необходима для обработки полученных травм, ухода за тяжело раненными и так далее. На сессиях применяется редко, обычно работает как "знание", отражающее теоретические познания, либо между сессиями и в пост-обработке.

#### МУДРОСТЬ (WIS)
- first_aid | Первая помощь — Полевая медицина. Экстренно остановить кровотечение союзнику, помочь с ядом или переломом, а также уход за товарищами на отдыхе. Помогает определить характер ран или смерти. С серьезными травмами не помогает.
- perception | Восприятие — Навыки и психология, позволяющие определить, что что-то не так, найти прячущегося человека или кого-то, кто ведет себя подозрительно.
- empathy | Эмпатия — Умение понять, что тебе врут. Сбор информации. Также пригодится для общение с существами, общающихся эмоциями или телепатией, например, с феями.
- survival | Выживание — Полевой навык. Умение найти себе еду, укрытие, определить погоду, очистить воду и так далее.
- self_hypnosis | Самогипноз — Подавление ментальных эффектов, стресса, самообман. Может пригодиться для восстановления баланса.

#### ХАРИЗМА (CHA)
- bluff | Блеф — Умение врать, обманывать и выкручиваться. Бросается только если вас подозревают - если вам достаточно доверяют, необходимости в броске нет. О необходимости броска сообщает мастер.
- intimidate | Запугивание — Умение выдавать себя за кого-то больше, чем ты есть. Умение внушать ужас, убеждать с позиции силы и допытываться информации у враждебно настроенных к вам людям.
- diplomacy | Дипломатия — Базовая "болтология". Умение договариваться, убеждать, торговаться и обещать. Бесполезна, если с вами никто не хочет разговаривать. Не является палочкой-выручалочкой, а просто внушает симпатию.
- disguise | Маскировка — Камуфляж. Умение выдавать себя за кого-то другого или просто скрыть характерные черты. Что-то вроде "социальной скрытности" - не когда нужно проскочить, а когда нужно пройти у всех на виду.
- animal_handling | Обращение с животными — Обращение с животными, верховая езда, эмпатия для диких существ, тренировки существ.
- acting (param) | Актерское мастерство (х) — Дерево навыков. Умение играть на музыкальных инструментах, вести себя определенным образом.
- weapon_tricks | Оружейные трюки — Разновидность актерского мастерства для использования с оружием и магией. Эффектный бой позволяет обнадежить союзников и напугать противников. Кроме того, позволяет разыгрывать сцены для наблюдателей, например, пронзить оппонента в не жизненно важную точку, оставив его в живых, и так далее.
- magic_devices | Магические устройства — Умение перенастраивать магические устройства без активной защиты либо изменять их свойства. Часто пригождаются при определении лута.

## File: stats.md

### Stat damage [OWNER]

- Ability scores can take damage: shown "current/max", e.g. Str 17/18 after a ghost drains 1 (was 18).
- Damage to a stat lowers the CURRENT value only; max stays. It can be restored (short rest: 1 BP restores 1 point, see rest.md).
- Some curses and injuries deal PERMANENT stat damage: they lower the MAX AND the CURRENT value by the same amount
  [OWNER, corrected] (e.g. Con max -1 and current -1). This is what makes them a
  permanent injury (injuries.md): not healed by normal means, narrative removal only.
- Derived values (HP, balance, saves, skills) use the CURRENT stat value.
- Tests: Str 18/18, drain 1 -> 17/18; short rest 1 BP -> 18/18; permanent damage 1 on 18/18 -> 17/17;
  Str 18 with damage 3 (15/18), permanent damage 1 -> 14/17 [OWNER].

## File: training.md

### Training, modes, purchases [OWNER]

Old beta had no real edit or training mode: just an "add X" button. The new app has three modes.

#### Modes
- Play: normal use.
- Training: spend training points to buy things (feats, race/class abilities, skills, etc.). Needs resources.
- Edit: change anything with NO resources, up to HARD caps (e.g. HP not above level * max hit die value). Counts as fixing mistakes.
  New abilities/spells added in edit mode are treated as obtained at creation or similar.
- Each ability/feat/item stores its SOURCE (race, class, training, loot, quirk, template...) and separately the COST paid
  (editable, e.g. to change what a feat cost).
- Rule: only source = training spends training points. Other sources (race, class, loot, quirk) never spend them
  (old code wrongly spends for any source). Race and class abilities and feats can ALSO be bought with training.
- Price is editable on any purchase except feats (feat price is entered by its author, default 200 [beta behavior]).
- Feat "Finesse training" (finesse_training): 200 [OWNER confirmed].
- Feats with effects [OWNER, package 11 D; closes Q68]: a feat has an effects list with the same structure as statuses
  (buffs.md), permanent while the feat is owned: bonuses to parameters, skills, attacks, damage, speed, any part of the
  sheet; values may be a stat modifier (buffs.md "Value from a stat modifier"). Removing the feat removes its effects
  (command remove_feat; no training refund: the rules give none). A feat may hold granted_maneuvers (a list of
  maneuver ids, used from package 12). Feats have NO toggle modes: "power attack" is a maneuver (package 12) and
  stances already exist. Catalog feats carry their effects and granted_maneuvers to the sheet.
  Tests: feat +1 attack / +2 damage reach the attack view; +Str to Intimidation; +10 ft speed; remove -> gone.

#### Ability score cost
- Score used for pricing = base + RACE bonus. Item and quirk bonuses do NOT raise the price; injuries usually do not lower it.
- Cost of +1 = 150 * max(1, new modifier).
- Example: base 13 + race 2 = 15. 15->16 = 150*3 = 450; 16->17 = 450; 17->18 = 150*4 = 600.
  If a race bonus is lost narratively, the price follows the new score.

#### Comfort for training [OWNER]
- 1 comfort = 5 + 5 * level training (10, 15, 20 at levels 1, 2, 3). Item and class bonuses change it.

#### Armor / shield grades [OWNER confirmed, package 4]
- Shield: 100 per grade: none -> light -> heavy -> tower.
- Armor: 250 per grade: none -> light -> medium -> heavy.
- Owner text (verbatim):
  "Парирование растет на каждом нечетном уровне на 1."
  "Владение новой категорией доспехов - 250 очков
  Не владеет, 0 парирование -> Легкие, 2 парирование -> Средние, 4 парирование -> Тяжелые, 6 парирование. Парирование растет на 1 каждый нечетный уровень."
  "Владение новой категорией щитов - 100 очков. Тяжелые и ростовые щиты добавляют свой бонус щита к балансу персонажа.
  Легкие -> Тяжелые, рост баланса -> Ростовые, рост баланса, +2 парирование"
- Code reading: parry = armor proficiency parry (0/2/4/6) + 1 per odd level + weapon mastery parry picks.
  [OWNER, Q27] Level 1 does NOT count: growth starts at level 3 (level 1 -> +0, 3 -> +1, 5 -> +2, 7 -> +3).
  Tests: none at level 1 -> parry 0; heavy at level 5 -> 6 + 2 = 8.
- [OWNER, package 5] Parry comes from PROFICIENCY (armor categories 0/2/4/6, the "tower shields" grade +2), not from an
  item in the hand. Tests: level 1, heavy armor + tower shields grade -> 8; level 3 -> 9; without shield proficiency -> 6.
- Shields [OWNER, Q28]: the shield bonus (layer "shield") comes from the shield held in a hand. A shield card has a type:
  light / heavy / tower. Heavy and tower shields ALSO add their shield bonus to the balance max while in a hand
  (in the bag: no). Tests: heavy shield +2 in hand -> balance max +2; in the bag -> +0; light shield -> +0.
- Shield proficiency ranks [OWNER, package 8 D1] (buy_shield_grade, 100 per rank):
  rank 0 (none) = cannot use shields; rank 1 (light) = light shields without penalty; rank 2 (heavy) = heavy shields
  without penalty AND a heavy shield in hand adds its shield bonus to the balance max; rank 3 (tower) = tower shields
  without penalty AND a tower shield in hand adds its shield bonus to the balance max AND parry +2 (from the grade,
  counted once). Light shields never add balance. Below the shield's rank: no balance bonus. Tests: every rank x
  light / heavy / tower.
- Non-proficient armor / shield [OWNER, package 9, closes Q34]: wearing armor or holding a shield with a proficiency
  rank below its type (armor: light 1, medium 2, heavy 3; shield: light 1, heavy 2, tower 3) applies its Str/Dex skill
  penalty (after the masterwork reduction, doubled if broken) ALSO to every attack roll while worn / held. Proficient:
  no attack penalty. An item without a category counts as light [accepted, Q42]. Tests: every rank x type for
  armor (-2) and shields (-3); masterwork -3 -> -2, broken -> -4; the weapon attack gets it too; a shield in the bag
  gives none.

#### Languages [OWNER confirmed]
- First native language free. Further native languages: buy with training or get narratively.
- CHEAP native purchase only while (number of native languages) < Int MODIFIER; otherwise the EXPENSIVE option.
  Int +2: 1 free + 1 cheap = 2 native. Int +3: 1 free + 2 cheap = 3 native. Int +1 or less: only the expensive option.
- Prices [OWNER confirmed, package 4]: cheap 50, expensive 100.
- Non-native language (verbatim): "Выучить язык - 30*число проектов от ближайшего родного."
  Test: 1 project -> 30, 3 projects -> 90. The number of projects is entered at the purchase (no language map yet).
- Native (verbatim): "Сделать язык родным - 50 (если родных меньше Инт). Сверх этого числа - 100." ("Инт" = Int
  MODIFIER, owner confirmed earlier.) Making an already known language native: rule only, no command yet.
- Old code compared with the Int SCORE (not the modifier): bug.
- Tests: Int mod 2, natives 1 -> next native 50; natives 2 -> 100. Int mod 3, natives 2 -> 50; natives 3 -> 100. Int mod 1, natives 1 -> 100.

#### Other purchases [OWNER, package 4, verbatim; commands since package 15, see below]
- "Каждый уважающий себя приключенец старается держать себя в форме, оттачивать свое владение оружием, изучать
  подходящие заклинания и подобное. Для этого раз он может обменивать комфорт очки тренировок по курсу (ЛВЛ+1)*5."
  ((level+1)*5 = 5 + 5*level, same as "Comfort for training" above.)
- "Новый прием боя - 250 очков (Вы разрабатываете прием для оружия, которым владеете. Прием на 0-3 уровней сложнее,
  чем выбранный прием в ветке данного оружия. Вы можете выбирать в качестве стартового приема стандартные, вроде
  "базовая атака", "захват", "двойная атака". Минимальный уровень равен требуемому уровню владения оружием. Суть приема
  определяет мастер, и обычно она связана с прошлым приемом в "ветке")."
- "Новая черта или изменение классовых способностей - 200+ очков, по договоренности с ДМом. Вы можете придумывать
  бонусы самостоятельно."
- "Квалификация с предметом - 50*N, где N - указанное в предмете число (требуется для специфических предметов, чтобы
  раскрыть их более потенциал)."
- "Получить +1 реакцию - 200*новое число реакций." Test: 1 reaction -> 2nd costs 400.
- [OWNER, package 8] Command buy_hp: +1 hit-die HP for 50, up to die * level (progression.md "Max HP").
- "Увеличение макс хитов на 1 - 50 очков. Увеличивать макс хиты можно до капа, который можно было получить естественным
  образом (классовый КХП*уровень + ВЫН*уровень)." (КХП = class hit die, ВЫН = Con modifier.)
- "Новое заклинание - 20 + 10*круг^2. Классы с книгой или возможностью изучить заклинание от учителя или из свитка
  получают скидку в 2 раза." Test: circle 2 -> 60, with a book 30.
- "Повысить курс трансформация внимания на 1 - 200 (имеется в виду трансформация внимания в ОВ и пр., складывается с
  бонусом от характеристики)."

#### Base points [OWNER, Q22]
- One base point costs 100 training. Max base points = 10 * level (start 5).

#### Seeds, quirks, stories
- Seed ("new seed" (1), price 200): adds a seed entry to the Quirks tab (a separate tab, plain list).
- Sprout seed: narratively obtain a quirk. Price (verbatim): "Получить зерно - 200." "Прорастить зерно - 200."
- Stories are NOT listed separately in the sheet; a story is part of a quirk. Quirk fields: Seedling, Court, Focus, Story name.
- A quest, if any, is entered by hand.

#### Qualification
- Always tied to a specific item; does not work for other items. 50 training per level.

#### Professionalism [OWNER confirmed]
- A separate number (professionalism level), bought with training (old code: 300 for the feature).
- Owner text (verbatim, package 4): "Профессионализм - 300 очков. Вы получаете специализированными 1/2/3/4 навыков из
  списка Вашего класса (для классов с 2+, 4+, 6+, 8+ скп). Если у класса прописана иной "профессионализм", то опция в
  классе заменяет данную опцию."
  [OWNER, Q29] This 300-point option applies only IF THE CLASS HAS NO PROFESSIONALISM OF ITS OWN.
  The "professionalism level" number above is a placeholder for classes without their own professionalism:
  do NOT develop it further (no new code for it).
- Cannot exceed character level.
- Class abilities (ONLY class abilities) may reference professionalism level instead of character level.
- Professionalism may also be a REQUIREMENT for activating items.
- Example: a wizard gets Mage Tower: gives professionalism x2 slots, spendable on narrative bonuses; effectively base bonuses.

#### Attention course (spend 1 attention; Str/Dex/Con/Int/Wis/Cha = modifiers, never below 2 when converted into something useful)
Mechanical options:
1. Raise injury healing rating by Str (min 2) [already implemented, see injuries.md].
2. Get training as if spending comfort equal to Dex/2 (min 1, rounded to tenths; Dex 3 -> 1.5 comfort).
   Lives next to "spend comfort for training".
3. Get Con (min 2) time points (OV); or double that, but then spend them only on professions, closing drives or lenses.
   OV = time points, a NARRATIVE resource. Unspent OV burn at "end of cycle" (the new cycle starts).
4. Get 0.2 * Int (min 0.4) base points. Fractions are kept (never lost). Example: 5 attention at minimum = 5 * 0.4 = 2.0 = +2 max base slots. Max base = 10*level, start 5, or buy slots with training.
Narrative options (entered by hand when relevant):
1. Get Wis (min 1) quests from courts until the next long rest.
2. Story power options: IGNORE for now (owner).
- Resources implied: time points (OV, narrative, burn at end of cycle), base points as fractions. Professionalism level: see above.

#### Package 16 additions [OWNER, package 16 G2, G4, G5, A10]
- Comfort for training: the rate is (level + 1) * 5 + effects "comfort_rate_bonus" (closes Q107). Test: level 1, +3,
  2 comfort -> 26.
- New spell price: 20 + 10 * circle^2; a spellbook class (or a teacher / scroll) pays half, rounded down; THEN effects
  "spell_price_discount" subtract X (the old code's class spell_discount_extra); never below 1. Tests: circle 2 -> 60,
  book 30, book and discount 5 -> 25; circle 0 with a book (10) and discount 15 -> 1. (Taken over from the deleted
  legacy draft training_costs_draft.md, package 16 A10; every other number of that draft was already here or in
  skills.md / weapons.md / progression.md.)
- Attention option 2: attention_to_training(n): per attention, training as if spending comfort = (Dex mod + attention
  course) / 2, min 1, tenths; training = floor(comfort * comfort rate) (Q114). Dex 16 -> 1.5 * 10 = 15.
- Attention option 4: attention_to_base_points(n): per attention max(0.4, 0.2 * (Int mod + attention course)) base
  points, kept in tenths (Character.base_points_tenths, never lost); every whole point is +1 base slot. 5 attention at
  the minimum -> 2.0 -> base slots 5 -> 7. (Closes Q110.)

#### Purchase and progression commands [package 15]
Every command validates, spends training (a non-training source spends nothing), refuses with a reason, is journaled,
and never refunds. Prices are the constants of wp/core/training.py (data, not scattered literals).
- level_up(hp_roll): needs and spends 1000 experience (progression.md "Level up", package 33), level +1, training
  +100 * the NEW level, the hit-die roll of the new level (at most the die, a roll below 1 counts 1; set_hp_roll edits
  it later). Refused above the die and below 1000 experience. RULES give no level cap (Q103). The
  current HP are not raised (Q111).
- exchange_comfort(n): n comfort -> n * (level + 1) * 5 training. Refused above the comfort the character has. An
  item / class bonus to the rate has no field yet (Q107).
- buy_attention_course: +1 for 200; it adds to the stat bonus of EVERY attention conversion (OV, OT removal, RL raise:
  assumption Q102).
- buy_reaction: 200 * the new number of reactions (1 -> 2 costs 400, 2 -> 3 costs 600). Character.reactions starts at 1.
- buy_seed(name): 200, a new seed (id from the name); sprout_seed(seed_id): 200, refused twice (the quirk itself is
  narrative).
- make_language_native(lid): first native free, 50 while natives < Int mod, else 100; refused when already native.
- promote_skill(name, to_tier): normal -> advanced 40 + 20 * other advanced or specialized; advanced -> specialized
  200 + 50 * other specialized; normal -> specialized pays both; refused for the same or a lower tier (skills.md).
- buy_professionalism(skills, class_skill_points): 300; class skill points 2+ / 4+ / 6+ / 8+ -> exactly 1 / 2 / 3 / 4
  chosen skills become specialized; refused below 2 points, for a wrong number of skills, for an already specialized
  skill, and a second time (assumption Q105). "Only classes without their own professionalism" and "skills from the
  class list" cannot be checked yet: there is no class data (Q104).
- learn_spell(name, circle, discount): 20 + 10 * circle^2, half with discount (a class with a book, or learning from a
  teacher or a scroll); circle 0..9. A minimal spell record (id, name, circle, source, cost, upgrades).
- buy_spell_upgrade(spid, name, metamagic): 25 * (1 + circle^2) per upgrade; three slots per spell; an upgrade takes 1
  slot, the second identical one 2 (each further identical one 1 more: Q106); a metamagic takes slots = its circles;
  refused when the slots do not fit.
- buy_combat_basics(wid): 50 / 100 / 150 for scale 1 / 2 / 3, once per node, refused for Basic/simple (weapons.md).
- buy_maneuver(name, ...): 250, an entry in the maneuver list (edit its tags and numbers with edit_maneuver). Its
  `source` parameter is the purchase source, so the maneuver's own source label is set with edit_maneuver (Q112).
- buy_item_qualification(iid): 50 * N (N = Item.qualification_n); refused without N or twice. What the qualification
  unlocks: the hidden properties (package 25 D note below; Q109 closed).
- Tests: package 15 (test_pkg15.py), every price with the numbers above.
- [package 25 D, closes Q109] Qualification unlocks the hidden properties of the item: each property has a
  minimum qualification level; below it the item shows "???", at or above it the text and its effects act (in the
  tab it belongs to: base = not activated, or activated). The purchase stays 50 * N for qualification N at once.

#### Catalog trainings [OWNER, package 37, decision 2]
- New kinds of training are catalog entries (kind trainings): name, module, price per unit in training points (a
  number or a formula), repeatable, limit (optional), the effect of one unit (N units = N times, one source row), and
  what unlocks it (an ability, a race, a quirk, an item tag, or nothing = everyone).
- The Training tab lists the built-in trainings and the catalog ones the character can use; locked ones only with
  "show locked", with the reason. Buying spends training points; no refund. First user: Ragmal mana, 200 per unit:
  3 units = 600 training, mana +3.
- Level offsets: a source may count the character one level higher for the comfort exchange or for Attention only
  (const:training.comfort_exchange_level_offset, const:attention.level_offset). Lomit Adaptation: at level 2 the
  exchange gives 5 + 5 x 3 = 20 instead of 15; Attention 1 + 3 / 3 = 2 instead of 1.

## File: crafting.md

### Recipes and crafting [OWNER]

#### Recipe (new entity, tab "Recipes/Crafting")
- Name, linked SKILL (which skill is used, its bonus), cost in OV (time points), money and/or resources.
- A recipe can create: narrative bonuses, buffs (consumables), items, or something for the base.
- Rolls are made OUTSIDE the app. The app only records a crafting attempt: player taps the recipe (spends OV, money, resources);
  optional button "-4 DC for OV": each extra 1 OV gives cumulative -4 to the DC.
- OV also pay for the narrative side. Unspent OV burn at "end of cycle" (also the start of a new one).

#### Unusual items (first six categories only)
Categories of items: Weapons, Armor and Shields, Slotted items, Extra equipment, Knowledge, Consumables (+ others, see doll.md).
- Needs a feature blueprint and an unusual material of level X (ilvl) and a craft check DC 15 + X.
- Without unusual material: DC rises to 15 + 3X.
- Example: X = 2: DC 17 with material, 21 without. With 2 extra OV spent: 17 - 8 = 9 (cumulative -4 per OV).

#### Item level
- Every item has ILVL (item level), recorded and used (e.g. material ilvl X above).

## File: doll.md

### Character doll (slots) [OWNER]
Owner's slot list (22): Hands, Armor/clothes, Belt, Body, Chest, Eyes, Hands (gloves), Head, Neck, Fingers, Back, Shoulders, Legs, Feet,
Belt pouch (unload), Combat companion/squire, Pet/familiar, Modifier, Craft tools, Camp tools, Magic components, Worship item.

Each slot holds ONE item that gives a bonus; items can be swapped for the situation.
- Hands (2 hands total): weapon, shield, voodoo dolls, staves, combat tools, other items. Used in combat, gives parry and light.
  Items needing more than 2 hands cannot be equipped together.
- Armor (or clothes).
- Slotted gear: Belt (belts, straps), Body (robe, vestment), Chest (shirt, vest), Eyes (lenses, glasses), Hands (gloves, shackles),
  Head (helm, hat, hood), Neck (necklace, collar, brooch), Fingers (ring, hidden claw), Back (bag, quiver),
  Shoulders (cloak, pauldrons), Legs (trousers, scabbard), Feet (boots, shoes).
- Belt pouch / unload (consumables): base 10 L slots (gear.md).
- Combat companion / squire (squire, mount, combat pet). Pet / familiar (parrot, rat).
- Modifier (earrings, amulets).
- Craft tools (smithing etc.). Camp tools (tents, dishes).
- Magic components. Worship item (holy symbol etc.).
- Item level ILVL is stored on every item.

- [OWNER, package 16 E] The slot list is data (wp/catalog/data/doll_slots.json; ids hands, armor, belt, body, chest,
  eyes, gloves, head, neck, fingers, back, shoulders, legs, feet, belt_pouch, companion, pet, modifier, craft_tools,
  camp_tools, magic_components, worship_item). Item.slot names its slot. equip_item into an occupied slot is refused
  (reason slot_occupied); equip_item(swap=True) takes the other item off (it stays in the bag). The hands slot is
  equip_hands (2 hands). An item without a slot is worn without a slot check (as before). Bonuses count only while
  worn / held.
- [OWNER, package 24 A, C] The two hands are two positions, left and right. equip_hands takes an optional side
  (default: a shield goes to the left hand, another item to the first free hand: right, then left); a two-handed
  item takes both. move_hand_item moves an item to the other hand (a taken hand is refused; swap=True swaps).
  A file without stored sides gets them by the order of the held items when read. The main hand of an attack record
  is the right hand by default (set_main_hand); a weapon in the other hand is the off hand.
- [package 24 C] Doll layout = data of the layout profile (coordinates relative to the body picture; SAMPLE values):
  views "basic" (only the two hands) and "body" (every slot on a human figure). Commands equip_to_slot, unequip_slot,
  swap_slots; an item fits only its own slot (Item.slot).

## File: races.md

### Races [OWNER, package 36]

Source texts of the owner: Wp_claude/RACES_SOURCE.md (12 races of two game modules). Nothing about a race, class,
weapon group or module is written in code: a race is catalog data (kind races), every entry names its module.

#### What a race stores [OWNER, decision 1]
- Only what affects the character: name, stat changes, HP, speed, abilities (name, text, effects, price, charges,
  triggers), languages, type tags. NO general description.
- A feat "whose prerequisites you meet" is plain text on the ability; prerequisites are never checked (decision 2).
- Narrative abilities with no mechanics are text only (decision 5), e.g. "does not lower morale from crits and pain".

#### Taking and changing a race [OWNER, decision 15]
- Taking a race copies its entries into the character, each with the source "race:<id>". Stat changes and HP are
  EFFECTS of the race, never edits of base values.
- Changing a race: the list of everything with the old race source (quirks the race gave and paid race traits
  included) is shown and must be confirmed; it is removed and the new race entries are added. One command, one
  journal line, one undo step. No training refund.
- A catalog change never changes the copies already taken.

#### Paid traits and chains [OWNER, decision 9]
- A paid race trait (fly for 600 training, then good flight for 300; swim; a drawback buy-out) is an ordinary ability
  of the race with a price in training, taken by the normal purchase. A chain = two abilities, the second needs the
  first. Training spent is never refunded automatically (the owner adds training by hand in the editor if needed).
- Mordon histories (6 types by d20) are six separate abilities; the player takes the one the roll gave; the d20 table
  is in the hint text. The program never rolls (decision 11).

#### Languages [OWNER, decision 16]
- A race gives known languages: the first is the native one (free), the others are known, not native
  (training.md "Languages").

#### Movement [OWNER, decision 10]
- The speed cell shows the land speed; the other modes (fly with a quality text, swim, climb) come from abilities /
  effects (move:<mode>, feet) and are listed on hover. Feet only.

#### Combat pressure [OWNER, decision 4]
- Combat pressure IS the morale scale -10..+10 of the core.

#### Tests
- Every race of RACES_SOURCE.md: a character with the race, hand numbers of the stats, HP at level 1, speed and two or
  three key effects (tests/model/test_races36.py).

#### Package 37 [OWNER, decisions 2-6]
- Narrative abilities (resurrect, prophecy, possession ...) are only text on the ability.
- Copying (White maiden) and Universality (humans) are abilities WITHOUT effects: the player takes any feat / racial
  ability from the catalog as usual and links it to them with "held by".
- BP spent by an ability with "restore only by the long rest" (Ankalian Adrenaline) stay missing after a short rest.
- Ragmal mana training is a catalog training (see training.md).
- Package 37 P2 (the 12 races done properly):
  - A charged racial status (Dance with blades, Shadow of Santerra, Eradication of filth) follows its race ability:
    Dance comes back at every combat start, Shadow and Eradication after the long rest. Test: Dance 1 -> 0 -> 1 at
    the next combat; Shadow 2 -> 1, the short rest keeps 1, the long rest -> 2.
  - Heavy swing (Ragmal): 2 temporary HP until the next zero-initiative tick. Dragon tail (Rahim): -2 AC until the
    next zero-initiative tick (the natural tail attack is parked).
  - Hunt for incarnations (Ragmal): every use costs 4 mana and adds +1 fire or acid damage (cumulative) until the end
    of combat. Test: mana 9 -> 5 -> 1, damage +1 then +2, 0 after the combat.
  - Mordon type 5: -4 on the first five attacks of each combat = 5 charges of the history, one spent per attack,
    refilled at the combat start; the buy-out removes the -4. Type 2: no wound penalty = no pain penalty.
  - Lomit Adaptation: one level higher for the comfort exchange and Attention (level 2: 20 instead of 15, Attention 2).
  - Ulstanger Rage: +1 damage per pain on melee attacks only. Northerner: Endurance and Toughness are placeholder
    feats (the owner's text is needed) - replaced by "Package 38": real feats.
  - Races with "two city languages": the text "choose two languages of the region" (added by hand).

#### Package 38 [OWNER, decisions 1-6]
- Mordon type 2 Wall of Bones: "no wound penalty" = no penalty from pain (pain and OT still accrue). It gets the feat
  Toughness for free, held by the ability. Drawbacks, bought out for 300 training: -4 CMD; bleeding hits x2 (NOT
  computed: the player sets the bleeding; the program shows the reminder "bleeding x2" while a bleeding status is
  active); comfort per fight 1 less and at most 3 (resources.md "Comfort per fight").
- Ulstanger Northerner: takes the real feats Endurance and Toughness (catalog.md "Feats") and links them (held by).
- Mordon type 5: the reroll once per long rest is its own charge (1, refilled by the long rest), separate from the
  -4 counter of 5 charges (buffs.md "Rerolls").

## Appendix: ac_zones.md (DRAFT, not built; review optional)

### AC zones (AC by direction) [OWNER, package 13 H] - DRAFT, NOT IMPLEMENTED

This is a DRAFT of the owner's future AC-by-direction scheme. Nothing here is built yet; the current AC modes
(front, flank, flat-footed, parry, touch, shield side; defense.md) stay in force until the owner gives the full table.

#### Cells
```
[1][2][3]
[4][5][6]
[7][8][9]
```
- Cell 5 is the character; he faces UP (towards 1, 2, 3).
- Cells 1, 2, 3 (front): full AC, or parry.
- Cell 8 (back): no Dex bonus and no dodge, unless a feature says otherwise.

#### Shield coverage (shield in the LEFT hand)
| Shield | Cells with the shield bonus |
|---|---|
| buckler | 1, 2, 4 |
| light shield | 1, 2, 3, 4, 7 (package 15, Q93; was 1, 2, 3, 4) |
| heavy shield | 1, 2, 3, 4, 7 |
| tower shield | 1, 2, 3, 4, 7 |
- Shield in the RIGHT hand: mirror the cells: 1<->3, 4<->6, 7<->9.
- Cells 6, 8, 9 never get the shield bonus (for a left-hand shield).
- A tower shield itself gives NO parry bonus: the +2 parry comes from the tower shield proficiency rank (Q28).

#### Features change cells
- Any feature, ability or status may change the rules of any cell (for example: give dodge in cell 8).
- The block effects (buffs.md "Block effects") must later be able to take a CELL as a scope.

#### Requirement for the implementation
- It must be DATA: a table of cells with flags (Dex / dodge allowed, shield coverage by shield type, parry allowed),
  read by the AC code, NOT new hard-coded conditions per cell.

#### Values per cell [OWNER, package 14, closes Q92]
- Every cell shows BOTH values: Full and Parry (parrying is the player's choice and may be done with an empty hand).
- The current flank / flat-footed / shield-side modes later become PRESETS of cells.

#### Parry and shields [OWNER, package 15, closes Q93]
- Parry is possible with anything held: a weapon, a stick, a torch, an improvised weapon ("junk": the Contact group
  bonuses apply to improvised weapons), or unarmed with the Unarmed combat / Contact bonuses. Parry cells: 1, 2, 3.
- There is NO special "side with no weapon".
- A shield gives its bonus only in the cells it covers (shield in the LEFT hand; mirror for the right hand: 1<->3,
  4<->6, 7<->9): buckler 1, 2, 4; every other shield (light, heavy, tower) 1, 2, 3, 4, 7. Cells 6, 8, 9 never get a
  shield bonus. (The light-shield row of the table above was changed accordingly.)
- The cell logic is NOT implemented yet (a later, data-driven package).

#### Variants and settings (package 24) [OWNER, package 24 B; built]
- Built as data: cells and variants in wp/rules_data/ac_zones.json; the cell rules are rule constants of group
  ac_zones (constants.json), changeable per character (set_rule_setting) and by effects. The draft above stays as written.
- Every cell returns a LIST of variants {id, label, ac, applies_when (melee | ranged), chance}:
  - melee = the full AC; melee_parry = with parry, only in the parry cells; ranged = parry does NOT work against
    ranged attacks (constant ac_zones.ranged_ignores_parry = 1), the shield counts where it covers
    (ac_zones.ranged_keeps_shield = 1).
  - A chance: in a cell that loses Dex / dodge, a cancel chance > 0 (ac_zones.dex_loss_chance_pct + effects, 0..100)
    gives every variant a second value WITH Dex and dodge and that chance ("AC without Dex / AC with Dex"). The app
    never rolls.
- Settings (defaults): parry cells 1, 2, 3; Dex / dodge lost only in cell 8; shield cells of a LEFT-hand shield:
  buckler 1, 2, 4, every other shield 1, 2, 3, 4, 7 (right hand: mirror); the default shield hand: left.
- Effects (feat, class trait, status, item): parry_cells, shield_cells, dex_loss_cells (effect cells added with
  value >= 0, removed with value < 0); dex_loss_chance_pct (a number); any AC bonus (also the shield type) and the
  parry layer may carry cells = the cells it counts in (empty = every cell). Stacking per cell by the typed rules.
- Hands have sides (gear.md, doll.md): a shield covers the cells of ITS hand; two shields (one per hand): per cell the
  larger shield bonus (one bonus type, the larger wins).
- Display (app settings): the primary variant (big number in the centre of the cell), the secondary (small number
  bottom right), the slash list "A / B / C" (order and visible variants).
- The old modes are presets: cell 2 = front and parry, cell 6 = flank, cell 8 = flat-footed (touch = cell 2).

#### Flank with the shield in either hand (package 27) [OWNER, review 5 F15; built]
- Flank = the cell of the side WITHOUT a shield: cell 6 with the shield in the left hand (or no shield), its mirror
  cell 4 when every held shield is in the right hand. The screen shows one number: the old modes front, flank and
  flat-footed are the melee numbers of their cells, parry the parry number of cell 2 (touch keeps its own ladder).
- Example: heavy shield 2, deflection +3 only in cell 6. Shield left: cell 6 = 13, flank 13. Shield right: cell 6 =
  10 + 2 + 3 = 15, cell 4 = 10, flank = 10.

## Data tables with rule numbers

### Rule constants (wp/rules_data/constants.json)
Every number can be changed per character (rules_settings). Values as shipped.

| id | value | unit | meaning |
|---|---|---|---|
| training.start | 1000 | training | training points of a new character |
| training.ability_step | 150 | training | +1 ability = step * max(1, new modifier) |
| training.shield_grade_cost | 100 | training | next shield proficiency grade |
| training.armor_grade_cost | 250 | training | next armor proficiency grade |
| training.base_slot_cost | 100 | training | one base slot |
| training.hp_point_cost | 50 | training | max HP +1 (hit-die HP) |
| training.base_start | 5 | slots | base slots of a new character |
| training.language_non_native | 30 | training | non-native language, per project step |
| training.language_native_cheap | 50 | training | native language while natives < Int mod |
| training.language_native_expensive | 100 | training | native language above that |
| exp.level_cost | 1000 | xp | level_up needs and spends this much experience (package 33) |
| exp.max_banked | 1999 | xp | experience never above this: no two banked level-ups (package 33) |
| training.level_up_per_level | 100 | training | training at level-up = this * new level |
| training.reaction_step | 200 | training | +1 reaction = this * the new number |
| training.seed_cost | 200 | training | new seed |
| training.sprout_cost | 200 | training | sprout a seed |
| training.attention_course_cost | 200 | training | attention course +1 |
| training.maneuver_cost | 250 | training | new combat maneuver |
| training.qualification_step | 50 | training | item qualification = this * N |
| training.professionalism_cost | 300 | training | professionalism option |
| training.professionalism_skills | [[8, 4], [6, 3], [4, 2], [2, 1]] | pairs | class skill points -> specialized skills |
| training.spell_base | 20 | training | new spell = base + per_circle_sq * circle^2 |
| training.spell_per_circle_sq | 10 | training | new spell: per circle squared |
| training.spell_discount_divisor | 2 |  | spellbook / teacher / scroll: price divided by |
| training.mastery_base | 25 | training | spell upgrade = base * (1 + circle^2) |
| training.mastery_slots | 3 | slots | upgrade slots per spell |
| training.base_point_tenths_per_int | 2 | tenths | attention option 4: per Int mod |
| training.base_point_tenths_min | 4 | tenths | attention option 4: minimum per attention |
| training.spell_min_price | 1 | training | a new spell costs at least this |
| training.base_max_per_level | 10 | slots | max base slots = this * level |
| training.comfort_max_base | 5 | comfort | comfort max = base + per_level * level |
| training.comfort_max_per_level | 5 | comfort | comfort max per level |
| training.comfort_rate_base | 5 | training | 1 comfort = base + per_level * level training |
| training.comfort_rate_per_level | 5 | training | comfort rate per level |
| training.attention_comfort_min | 1.0 | comfort | attention option 2: at least this |
| comfort.fight_cap | 5 | scale | comfort per fight: the largest absolute morale of a combat counts at most this (package 38) |
| comfort.fight_minus | 1 | comfort | comfort per fight = that morale minus this, never below 0 (package 38) |
| comfort.fight_max | 4 | comfort | comfort per fight at most this (package 38) |
| training.attention_comfort_divisor | 2.0 |  | attention option 2: Dex mod divided by |
| training.tenths_per_point | 10 | tenths | tenths in one base point |
| weapons.max_level | 12 | grade | highest weapon proficiency grade |
| weapons.expert_level | 8 | grade | first expert grade (grade cost X counts groups at this or above) |
| weapons.specialist_slots | [5, 6, 7] | grades | grades that open a specialist pick |
| weapons.expert_slots | [8, 9, 10, 11] | grades | grades that open an expert pick |
| weapons.master_slot | 12 | grade | grade that opens the master pick |
| weapons.qualified_penalty | 0 | to-hit | penalty when qualified |
| weapons.one_below_penalty | -2 | to-hit | one grade below the qualification |
| weapons.not_qualified_penalty | -4 | to-hit | further below the qualification |
| weapons.lucky_base | 20 | d20 | lucky attack threshold |
| weapons.lucky_mastery_max | 3 | picks | mastery picks that lower the lucky threshold |
| weapons.min_threshold | 2 | d20 | crit / lucky threshold never below |
| weapons.basics_cost | [50, 100, 150] | training | combat basics for scale 1 / 2 / 3 |
| weapons.basics_raise_base | 5 | grades | combat basics raise = this - difficulty |
| weapons.grade_cost_base | 30 | training | grade cost = (base + per_expert * X) * difficulty * scale |
| weapons.grade_cost_per_expert | 5 | training | grade cost per OTHER group at expert+ |
| weapons.repeat_second | 2 | ordinal | second pick of the same bonus |
| weapons.repeat_third | 3 | ordinal | third pick of the same bonus |
| weapons.damage_pick | 3 | damage | damage per 'damage +3' pick |
| weapons.range_pick_ft | 10 | ft | range per 'range +10 ft' pick |
| weapons.durability_specialist_pct | 30 | percent | hardness per specialist pick |
| weapons.durability_expert_pct | 70 | percent | hardness per expert pick |
| dice.d20_faces | 20 | faces | the d20 (crit base range 20+) |
| weapons.keen_multiplier | 2 |  | keen multiplies the BASE crit range |
| load.light_max_l | 59 | L | light load up to this (5.9 B) |
| load.heavy_max_l | 109 | L | heavy load up to this (10.9 B) |
| load.l_per_b | 10 | L | L in one B; thresholds shift by Str mod * this |
| morale.scale_min | -10 | scale | morale scale lowest |
| morale.scale_max | 10 | scale | morale scale highest |
| pain.hp_step | 3 | HP | 1 pain per this many HP below 0 |
| size.attack_ac | {"small": 1, "medium": 0, "large": -1} | map | size to attack and AC |
| size.cmb_cmd | {"small": -1, "medium": 0, "large": 1} | map | size to CMB and CMD |
| speed.base_ft | 20 | ft | default race speed |
| speed.encumbrance_ft | -10 | ft | speed change while encumbered (weight) |
| ability.mod_base | 10 | score | modifier = (score - base) // divisor |
| ability.mod_divisor | 2 |  | modifier divisor |
| bp.cap_divisor | 4 | HP | BP cap = ceil(max HP / this) |
| morale.divisor | 2 |  | morale bonus = trunc(scale / this) |
| ac.base | 10 | AC | AC base before layers |
| ac.encumbrance_dodge_cap | 2 | AC | encumbered: Dex + dodge at most |
| ac.armor_grade_parry | {"none": 0, "light": 2, "medium": 4, "heavy": 6} | map | parry by armor proficiency grade |
| ac.tower_grade_parry | 2 | AC | parry of the tower shield proficiency grade |
| ac.odd_level_step | 2 | levels | parry +1 per this many levels from level 3 |
| injuries.severity | {"light": [2, 3], "medium": [5, 2], "heavy": [12, 1]} | map | severity -> (OT removed, base healing rating) |
| injuries.comfort_ot | 3 | OT | 1 comfort removes this much OT |
| injuries.attention_min | 2 |  | attention value = max(this, Str mod) |
| magic.circle_mana | [0, 1, 3, 5, 7, 9, 11, 13, 15, 17] | mana | mana cost by circle 0..9 |
| magic.concentration_base | 10 | DC | concentration DC = base + per_ot * OT |
| magic.concentration_per_ot | 2 | DC | concentration DC per OT gained |
| actions.standard | 2 | actions | a standard action (shift 1, move 1, full-round 3) |
| magic.slot_overload_mult | 2 |  | slot casters and cantrips: overload = this * actions |
| pain.death_cap | 8 | pain | pain count that kills |
| rest.short_rest_costs | {"heal": 1, "charges": 2, "spirit": 2, "stat": 1, "pain": 1, "mana": 1, "divine": 1} | BP | short rest option prices |
| rest.free_heal_base | 2 | HP | free heal of the short rest = this + level |
| skills.advanced_roll_bonus | 3 | roll | bonus of an advanced / specialized skill |
| skills.rank_price | {"normal": 20, "advanced": 15, "specialized": 10} | map | +1 rank = price * new rank, by tier |
| skills.promote_base | 40 | training | make advanced = base + per_other * others |
| skills.promote_per_other | 20 | training | per OTHER advanced or specialized skill |
| skills.specialize_base | 200 | training | make specialized = base + per_other * others |
| skills.specialize_per_other | 50 | training | per OTHER specialized skill |
| dying.action_slots | 3 | actions | action slots in a turn |
| dying.concentration_dc | 20 | DC | concentration DC to act while dying |
| dying.pain_per_painful_action | 1 | pain | pain per painful action |
| dying.hp_loss | {"dying": 2, "resting": 1, "stabilized": 0} | map | HP lost per tick by state |
| dying.clean_actions | 1 | actions | clean actions while dying |
| dying.diehard_clean_actions | 2 | actions | clean actions while dying with Diehard |
| proficiency.shield_rank | {"none": 0, "light": 1, "heavy": 2, "tower": 3} | map | shield proficiency grade -> rank |
| proficiency.shield_need | {"": 1, "light": 1, "heavy": 2, "tower": 3} | map | shield type -> rank needed |
| proficiency.armor_rank | {"none": 0, "light": 1, "medium": 2, "heavy": 3} | map | armor proficiency grade -> rank |
| proficiency.armor_need | {"": 1, "light": 1, "medium": 2, "heavy": 3} | map | armor type -> rank needed |
| spirit.base | 5 | spirit | spirit max = base + per_cha * Cha mod |
| spirit.per_cha | 5 | spirit | spirit per Cha modifier |
| attention.drive_level | 4 | level | a drive at this level or above gives +1 attention |
| items.broken_defense_divisor | 2 |  | a broken armor / shield bonus is divided by this |
| attention.level_offset | 0 | levels | levels added for the Attention per cycle only (package 37: a source changes it through const:attention.level_offset) |
| training.comfort_exchange_level_offset | 0 | levels | levels added for the comfort exchange rate only (package 37: const:training.comfort_exchange_level_offset) |
| attention.level_step | 3 | levels | attention per cycle +1 per this many levels |
| items.broken_weapon_penalty | -2 | to-hit | a broken weapon: attack and damage |
| items.masterwork_attack | 1 | to-hit | masterwork weapon attack bonus |
| items.masterwork_penalty_relief | 1 | skill | masterwork armor: skill penalty smaller by |
| items.broken_at_fraction | 2 |  | broken at max HP / this and below |
| items.broken_skill_mult | 2 |  | a broken armor's skill penalty is multiplied by |
| items.hardness_per_enchant | 2 | hardness | hardness + this * enchantment N |
| twf.base_penalties | [-6, -10] | to-hit | two-weapon penalties (primary, off hand) |
| twf.light_relief | 2 | to-hit | a light off-hand weapon: each penalty smaller by |
| twf.feat_relief | [2, 6] | to-hit | the feat: penalties smaller by (primary, off hand) |
| twf.weapons_needed | 2 | weapons | weapons in the hands for a two-weapon combination |
| attack.default_crit_mult | 2 |  | crit multiplier without a weapon card |
| attack.grip_factor | {"one": [1, 1], "off": [1, 2], "two": [3, 2]} | fraction | Str to damage by grip (numerator, denominator) |
| attack.crit_hint | {"2": "+0", "3": "+4", "4": "+8"} | text | house-rule crit confirmation hint by multiplier (tooltip only) |
| attack.max_primary | 2 | records | primary attack records at most |
| cmd.base | 10 | CMD | CMD = base + BAB + Str + Dex + size |
| narrative.drive_max | 5 | level | highest drive level |
| narrative.lens_start | 1 |  | a new lens starts at this value |
| hands.max | 2 | hands | hands of all held items add up to at most this |
| hands.two_handed | 2 | hands | an item needing this many hands is two-handed |
| attention.ov_min | 2 | OV | 1 attention gives max(this, Con mod) OV |
| progression.hit_die_min | 1 | HP | a level_up roll below this counts this (package 33) |
| progression.hit_die_default | 1 | HP | level_up without a roll takes this die value (Q111) |
| training.feat_default_cost | 200 | training | feat price when the author gives none |
| new.hit_die | 8 | HP | hit die of a new character (and its level-1 HP) |
| new.reactions | 1 | reactions | reactions of a new character |
| tick.max_order_items | 6 | items | all orders of the tick's balance items are tried up to this many (then greedy) |
| hands.default_shield_side | "left" | hand | a shield taken up without a side goes to this hand (ac_zones.md: shield in the LEFT hand) |
| hands.default_weapon_sides | ["right", "left"] | hands | an item other than a shield goes to the first free hand of this list (assumption Q160) |
| hands.main_default | "right" | hand | the main hand of an attack record without its own main hand (package 24 A3) |
| ac_zones.parry_cells | [1, 2, 3] | cells | cells where parry works (ac_zones.md; Q155) |
| ac_zones.dex_loss_cells | [8] | cells | cells where Dex and dodge are lost (ac_zones.md; Q154) |
| ac_zones.shield_cells | {"buckler": [1, 2, 4], "light": [1, 2, 3, 4, 7], "heavy": [1, 2, 3, 4, 7], "tower": [1, 2, 3, 4, 7], "": [1, 2, 3, 4, 7]} | cells | cells a shield in the LEFT hand covers, by shield type (ac_zones.md); the right hand mirrors |
| ac_zones.ranged_ignores_parry | 1 | flag | 1 = parry does not work against ranged attacks (package 24 B1) |
| ac_zones.ranged_keeps_shield | 1 | flag | 1 = the shield bonus counts against ranged attacks in covered cells (package 24 B1) |
| ac_zones.dex_loss_chance_pct | 0 | percent | chance that the Dex loss is cancelled in a Dex-loss cell; effects add (package 24 B1) |
| class.bab_factor | {"good": 1.0, "medium": 0.75, "poor": 0.5} | factor | ASSUMPTION (PF-like, Q167): BAB = level * factor, rounded down |
| class.save_good_base | 2 | points | ASSUMPTION (ROADMAP): good save = base + level / divisor, rounded down |
| class.save_good_divisor | 2 | levels | ASSUMPTION (ROADMAP): good save divisor |
| class.save_poor_divisor | 3 | levels | ASSUMPTION (ROADMAP): poor save = level / divisor, rounded down |
| narrative.principle_min_level | 2 | level | a drive at this level or higher expects a principle (reminder only) |
| spells.areas | ["single", "cone", "line", "burst", "other"] | ids | area ids of spell damage components (package 25 F) |
| actions.base | 3 | actions | actions per turn before effects actions_max (owner, package 26 A) |
| actions.cost_presets | {"shift": 1, "move": 1, "standard": 2, "full_round": 3, "complete_round": 4} | actions | action costs (combat.md Actions): presets for cost_actions |
| drives.start_points | 12 | points | drive points of a new character (a hint only: nothing is blocked) |
| drives.buy_up_cost | 3 | comfort | comfort for +1 drive level |
| drives.buy_down_cost | 2 | comfort | comfort for -1 drive level |
| drives.quest_allowed_level | 3 | level | a drive at this level may take a quest |
| drives.quest_mandatory_level | 4 | level | a drive at this level must have a quest (reminder only) |
| drives.spirit_bonus | {"2": 1, "3": 2, "4": 3, "5": 4} | bonus | spirit roll bonus by drive level while the drive is under threat (a hint, spirit is spent by hand) |

### Damage types (damage_types.json)

| type | physical (DR works) |
|---|---|
| piercing | yes |
| slashing | yes |
| bludgeoning | yes |
| fire |  |
| cold |  |
| lightning |  |
| acid |  |
| sound |  |
| force |  |
| positive |  |
| negative |  |
| pure |  |

### Doll slots (doll_slots.json)

| slot id | name |
|---|---|
| hands | Hands |
| armor | Armor / clothes |
| belt | Belt |
| body | Body |
| chest | Chest |
| eyes | Eyes |
| gloves | Hands (gloves) |
| head | Head |
| neck | Neck |
| fingers | Fingers |
| back | Back |
| shoulders | Shoulders |
| legs | Legs |
| feet | Feet |
| belt_pouch | Belt pouch (unload) |
| companion | Combat companion / squire |
| pet | Pet / familiar |
| modifier | Modifier |
| craft_tools | Craft tools |
| camp_tools | Camp tools |
| magic_components | Magic components |
| worship_item | Worship item |

### Weapon qualification levels (weapons.json)

| owner word | grade |
|---|---|
| Новичок | 1 |
| Ученик | 2 |
| Любитель | 3 |
| Опытный | 4 |
| Специалист 1 | 5 |
| Специалист 2 | 6 |
| Специалист 3 | 7 |
| Эксперт 1 | 8 |
| Эксперт 2 | 9 |
| Эксперт 3 | 10 |
| Эксперт 4 | 11 |
| Мастер | 12 |

### Effect targets of sheet numbers (sheet_targets.json)

| target | meaning |
|---|---|
| absorber: | a damage absorber (absorber:mana, absorber:pool:<id>): note = the damage types it takes, comma list ('' = all); after temp HP, before HP (package 36) |
| actions_max | actions per turn (package 26 A): added to the base 3 |
| armor_skill_penalty | added to the armor skill penalty (positive = smaller penalty, never above 0) |
| attack_melee | the general melee attack number of the sheet (package 34: its manual source rows) |
| attack_ranged | the general ranged attack number of the sheet (package 34: its manual source rows) |
| attention_per_cycle | attention at the end of a cycle |
| balance_max | balance max (also inside the start-of-combat snapshot) |
| balance_regen | balance regen per tick |
| base_slots | base slots |
| bp_max | max BP |
| check: | an ability check (check:con): situational texts only, the sheet has no check number (package 38, Endurance) |
| comfort_max | max comfort |
| comfort_rate_bonus | training per comfort point in exchange_comfort |
| const: | any numeric rule constant (const:<id> of wp/rules_data/constants.json): the value is added, or replaces it with the note 'replace' (package 37, owner decision 1) |
| crit_mult | crit multiplier (weapon id = that weapon only) |
| damage_per_pain | damage bonus per pain point (race rule) |
| dex_loss_cells | AC cells losing Dex and dodge: cells added (value >= 0) or removed (value < 0) (package 24 B2) |
| dex_loss_chance_pct | percent chance that the Dex loss is cancelled in a Dex-loss cell (package 24 B2) |
| dr | damage reduction vs physical damage; Effect.note = the bypass text (narrative only); Effect.stacks: total = the largest non-stacking entry + all stacking entries |
| exp_percent | experience received changed by this percent (-25 = a quarter less; package 36, rule switch) |
| extra_hit_dice | one extra hit die per effect; the value is the HP of that die; it counts max(1, value + current Con mod) like every die |
| heal_percent | healing by the Heal button changed by this percent (-50 = half; package 36, rule switch) |
| hp_max | max HP |
| item_hardness | hardness of items (Effect.weapon = one item id; none = every item); never below 0 |
| item_hp | max HP of items (Effect.weapon = one item id; none = every item); not from item tabs |
| iterative_penalty | makes every step of the iterative penalty smaller (a step never goes above 0) |
| load_mod | added to the Str modifier used for the load thresholds |
| mana_level | the most one spell may cost in mana (level + this) |
| mana_max | max mana |
| max_dex | Dex cap of the worn armor (only when a cap exists) |
| morale_scale | count the morale scale X higher (defense.md; the scale stays -10..10) |
| move: | a movement mode (move:fly, move:swim, move:climb): value in feet, note = the quality text (package 36) |
| natural_regen_percent | the HP a rest gives changed by this percent (100 = double; package 36, rule switch) |
| pain_cap | pain count at which the character dies (default 8) |
| pain_penalty_per_pain | roll penalty per pain point (default 1; -1 makes 0, never below 0) |
| pain_reduction | the effective pain lowered by N, never below 0 (package 36, rule switch) |
| parry | parry layer |
| parry_cells | AC cells where parry works: effect cells added (value >= 0) or removed (value < 0) (package 24 B2) |
| percent: | signed percent damage modifier of one type (percent:fire 50 = 50% more, -100 = immune) |
| pool_max: | max of one resource pool (pool_max:<pool id>) |
| reactions | reactions per round |
| reminder: | a standing reminder (reminder:<key>, text reminder.<key>): shown while the sum of its effects is above 0 (package 38: the Mordon bleeding x2, removed by the buy-out -1) |
| resist: | flat resistance to one damage type (resist:fire ...); never stacks, the larger wins |
| shield_cells | AC cells a held shield covers: cells added (value >= 0) or removed (value < 0) (package 24 B2) |
| short_rest_bp | extra BP gained by the short rest |
| short_rest_heal | added to the free heal of the short rest (after the 'larger of' rule) |
| slots: | max spell slots of one circle (slots:1 ... slots:9, slots:0 = cantrips) |
| spell_cost | mana cost of every circle 1+ spell (never below 0) |
| spell_overload | overload gained by every cast (never below 0) |
| spell_price_discount | training subtracted from a new spell's price after the spellbook half; minimum 1 |
| spell_resistance | spell resistance (shown only, not a damage step) |
| spirit_max | max spirit |
| stat: | ability score (stat:str ... stat:cha): typed bonuses stack by the normal rules; the modifier and everything built on it follow |
| switch: | a choice rule switch (switch:at_negative_hp): the effect note is the value (package 36, switches.json) |
| temp_hp | own temp HP of the character (manual source rows, own feats / items; package 35, owner Q229): added on read, spent by damage after the 'by button' pool and before buff temp HP (counted in temp_hp_spent), cleared by the short rest; temp HP from an external effect is a status (temp_hp_left) |
