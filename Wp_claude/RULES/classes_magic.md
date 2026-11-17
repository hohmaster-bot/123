# Classes and magic

## Class editor, 3 tabs [OWNER]
1. Basics: name, HP die (player picks), BAB progression, good saves (Fort/Ref/Will), as in current program.
   Checkboxes: has mana (has spellbook?), has slots, special resource 1, 2, 3 (name entered right here).
2. Abilities: same as race/feats: name + effect. E.g. rage, school of magic. Effects = generic effect system.
3. Maximums per level: slots max, mana max, ki/darkness/etc max; a formula may be used. Editable.
   Current mana/slots displayed elsewhere. Specific prepared spells live in the Spells tab.

## Restore [OWNER]
- Slots: full rest, some narrative situations, short rest. On short rest slots may or may not return despite resource spent.
- Mana: short rest gives X; X is decided by the GM (manual input, no formula). Full rest restores all.
- Slots on short rest: the GM decides whether they return (manual).
- Other per-class pools: full restore on long rest (see rest.md).

## Where abilities live [OWNER]
- Abilities paid with mana or slots belong to SPELLS.
- Abilities paid with ki, adrenaline or other special class pools live in class tab 2, tagged "ability" (RU: "sposobnost").
- Spells vs abilities are separate lists; no overlap in cost types.

## Mana source [OWNER]
- Each class has its OWN mana table, entered by hand per level. Race/feats/abilities can add mana too.
  Example: race gives 6, class level 1 gives 2 (or put 2 in class and 6 in a racial ability).

## Spell cost [OWNER, confirmed]
- Circles 0-9 as in Pathfinder. Mana cost per spell is whatever the spell says (1, 3, 5 ... by circle); entered per spell.
- Mage (mana user): balance cost = mana cost (0 mana -> 0 balance). Overload = duration in rounds
  (4 rounds -> 4; instant cast -> 0).
- Non-mana caster: spends a slot of that circle, no balance loss, overload 2X.
- Cantrips (circle 0): characters with a circle-0 slot spend it, EVEN mana users have slots for circle 0 only.
  Characters who can cast cantrips but have no circle-0 slot at all: unlimited. Cantrip overload 2X for everyone.
- Examples: mage, circle 2 (3 mana), 4 rounds: mana -3, balance -3, overload +4. Instant 3-mana spell: mana -3, balance -3, overload 0.
  Non-mage circle 1, 3 rounds: slot -1, overload +6.

## Racial damage absorbers [OWNER]
- Absorption is 1:1; absorbed part does not hit balance (like temp HP). Other traits/classes/races may add other absorbers.
- Some races redirect damage: after temp HP, before HP, damage hits MANA and acts like temp HP.
  Model damage as an ordered list of absorbers (temp HP -> race pool -> HP), configurable per character.
