# Training, modes, purchases [OWNER]

Old beta had no real edit or training mode: just an "add X" button. The new app has three modes.

## Modes
- Play: normal use.
- Training: spend training points to buy things (feats, race/class abilities, skills, etc.). Needs resources.
- Edit: change anything with NO resources, up to HARD caps (e.g. HP not above level * max hit die value). Counts as fixing mistakes.
  New abilities/spells added in edit mode are treated as obtained at creation or similar.
- Each ability/feat/item stores its SOURCE (race, class, training, loot, quirk, template...) and separately the COST paid
  (editable, e.g. to change what a feat cost).
- Rule: only source = training spends training points. Other sources (race, class, loot, quirk) never spend them
  (old code wrongly spends for any source). Race and class abilities and feats can ALSO be bought with training.
- Price is editable on any purchase except feats (feat price is entered by its author, default 200 [beta behavior]).

## Ability score cost
- Score used for pricing = base + RACE bonus. Item and quirk bonuses do NOT raise the price; injuries usually do not lower it.
- Cost of +1 = 150 * max(1, new modifier).
- Example: base 13 + race 2 = 15. 15->16 = 150*3 = 450; 16->17 = 450; 17->18 = 150*4 = 600.
  If a race bonus is lost narratively, the price follows the new score.

## Comfort for training [OWNER]
- 1 comfort = 5 + 5 * level training (10, 15, 20 at levels 1, 2, 3). Item and class bonuses change it.

## Armor / shield grades
- Shield: 100 per grade: none -> light -> heavy -> tower.
- Armor: 250 per grade: none -> light -> medium -> heavy (from old code, owner did not object).

## Languages [OWNER confirmed]
- First native language free. Further native languages: buy with training or get narratively.
- CHEAP native purchase only while (number of native languages) < Int MODIFIER; otherwise the EXPENSIVE option.
  Int +2: 1 free + 1 cheap = 2 native. Int +3: 1 free + 2 cheap = 3 native. Int +1 or less: only the expensive option.
- Prices from old code (owner did not object): cheap 50, expensive 100; non-native language 30.
- Old code compared with the Int SCORE (not the modifier): bug.
- Tests: Int mod 2, natives 1 -> next native 50; natives 2 -> 100. Int mod 3, natives 2 -> 50; natives 3 -> 100. Int mod 1, natives 1 -> 100.

## Seeds, quirks, stories
- Seed ("new seed" (1), price 200): adds a seed entry to the Quirks tab (a separate tab, plain list).
- Sprout seed: narratively obtain a quirk.
- Stories are NOT listed separately in the sheet; a story is part of a quirk. Quirk fields: Seedling, Court, Focus, Story name.
- A quest, if any, is entered by hand.

## Qualification
- Always tied to a specific item; does not work for other items. 50 training per level.

## Professionalism [OWNER confirmed]
- A separate number (professionalism level), bought with training (old code: 300 for the feature).
- Cannot exceed character level.
- Class abilities (ONLY class abilities) may reference professionalism level instead of character level.
- Professionalism may also be a REQUIREMENT for activating items.
- Example: a wizard gets Mage Tower: gives professionalism x2 slots, spendable on narrative bonuses; effectively base bonuses.

## Attention course (spend 1 attention; Str/Dex/Con/Int/Wis/Cha = modifiers, never below 2 when converted into something useful)
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
