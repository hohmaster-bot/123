# Classes and magic

## Class editor, 3 tabs [OWNER]
1. Basics: name, HP die (player picks), BAB progression, good saves (Fort/Ref/Will), as in current program.
   Checkboxes: has mana (has spellbook?), has slots, special resource 1, 2, 3 (name entered right here).
2. Abilities: same as race/feats: name + effect. E.g. rage, school of magic. Effects = generic effect system.
3. Maximums per level: slots max, mana max, ki/darkness/etc max; a formula may be used. Editable.
   Current mana/slots displayed elsewhere. Specific prepared spells live in the Spells tab.

## Restore [OWNER]
- Slots: full rest, some narrative situations, short rest. On short rest slots may or may not return despite resource spent.
- Mana [OWNER, package 22 A1], two separate things:
  1. Rest regeneration (rest.md): the short rest option "Restore mana by regen" (free once, then 1 BP; the amount X is
     typed in, decided by the GM, no formula); the long rest restores all mana.
  2. Manual restore: command restore_mana(amount): a GM narrative effect or an ability gives mana at any time; up to
     the max (an over-max value is kept, never raised); refused while a block_restore covers mana; journaled.
  Tests: 2/10 + 5 -> 7; + 20 -> 10; 12/10 stays 12; blocked -> refused.
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

## Racial damage absorbers [OWNER]
- Absorption is 1:1; absorbed part does not hit balance (like temp HP). Other traits/classes/races may add other absorbers.
- Some races redirect damage: after temp HP, before HP, damage hits MANA and acts like temp HP.
  Model damage as an ordered list of absorbers (temp HP -> race pool -> HP), configurable per character.

- [OWNER, package 16 B] Circles 0-9 ONLY: no circle 10 or above anywhere (rules, data, code). cast_spell and
  learn_spell refuse any other circle with a reason.
