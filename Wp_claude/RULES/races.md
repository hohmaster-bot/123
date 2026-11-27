# Races [OWNER, package 36]

Source texts of the owner: Wp_claude/RACES_SOURCE.md (12 races of two game modules). Nothing about a race, class,
weapon group or module is written in code: a race is catalog data (kind races), every entry names its module.

## What a race stores [OWNER, decision 1]
- Only what affects the character: name, stat changes, HP, speed, abilities (name, text, effects, price, charges,
  triggers), languages, type tags. NO general description.
- A feat "whose prerequisites you meet" is plain text on the ability; prerequisites are never checked (decision 2).
- Narrative abilities with no mechanics are text only (decision 5), e.g. "does not lower morale from crits and pain".

## Taking and changing a race [OWNER, decision 15]
- Taking a race copies its entries into the character, each with the source "race:<id>". Stat changes and HP are
  EFFECTS of the race, never edits of base values.
- Changing a race: the list of everything with the old race source (quirks the race gave and paid race traits
  included) is shown and must be confirmed; it is removed and the new race entries are added. One command, one
  journal line, one undo step. No training refund.
- A catalog change never changes the copies already taken.

## Paid traits and chains [OWNER, decision 9]
- A paid race trait (fly for 600 training, then good flight for 300; swim; a drawback buy-out) is an ordinary ability
  of the race with a price in training, taken by the normal purchase. A chain = two abilities, the second needs the
  first. Training spent is never refunded automatically (the owner adds training by hand in the editor if needed).
- Mordon histories (6 types by d20) are six separate abilities; the player takes the one the roll gave; the d20 table
  is in the hint text. The program never rolls (decision 11).

## Languages [OWNER, decision 16]
- A race gives known languages: the first is the native one (free), the others are known, not native
  (training.md "Languages").

## Movement [OWNER, decision 10]
- The speed cell shows the land speed; the other modes (fly with a quality text, swim, climb) come from abilities /
  effects (move:<mode>, feet) and are listed on hover. Feet only.

## Combat pressure [OWNER, decision 4]
- Combat pressure IS the morale scale -10..+10 of the core.

## Tests
- Every race of RACES_SOURCE.md: a character with the race, hand numbers of the stats, HP at level 1, speed and two or
  three key effects (tests/model/test_races36.py).

## Package 37 [OWNER, decisions 2-6]
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
    feats (the owner's text is needed).
  - Races with "two city languages": the text "choose two languages of the region" (added by hand).
