# Gear

## Doll [OWNER]
- Doll = worn or ready items. Two hands: items in hands needing > 2 hands total cannot be equipped. Rest of doll is worn.
- Hands [OWNER]: there is no separate shield slot. The two hands are one shared slot for everything that needs hands:
  weapon, shield, any special item (misc). An item has a field "hands" (0, 1 or 2); the hands of items held in the hands
  add up to at most 2 (a two-handed weapon takes both; shield + two-handed is impossible). Allowed: shield + weapon,
  weapon + weapon, two-handed weapon, special item + weapon. The shield bonus to AC (type shield) works only while the
  shield is held in a hand, not while it lies in the bag.
- Armor, helm, glasses, etc. Character slots: see doll.md.
- Magic items may need activation: 1 spirit/day or 5 until the end of the cycle; cost may scale or have an alternative.
- Requirements: "Qualification N" or Court level X.

## Qualification
- Tied to a specific item; does not work for other items (training.md). In levels, each level costs 50 training. Unlocks hidden properties of unusual items.

## Belt (unload) [OWNER]
- Consumables slots (potions, scrolls). Base 10 L. Activation usually 1 spirit, can differ.
- Special slot, buffs or injuries can add bonus belt slots.

## Bag
- Everything not worn and not a weapon. Button "drop bag" excludes its weight until picked up again.

## Weight [OWNER]
- Unit "balk" B: 5.9 B = 59 L. Stored as L.
- Load thresholds [OWNER confirmed]: base light 0-5.9 B, heavy to 10.9 B, above = overload.
  Both thresholds shift by Str MODIFIER (in B). Examples: +2 -> 7.9 / 12.9; -2 -> 3.9 / 8.9; +3 -> 8.9 / 13.9; -1 -> 4.9 / 9.9.
  Above heavy: drag only or drop something (overload icon).
- Overload effect: dodge bonus to AC capped at +2; Dex gives dodge; speed -10 ft.
- Abilities may ignore slowdown from armor/overload (editor/settings/doll section).

## Base (resource for strengthening) [OWNER]
- Blessings, immaterial and material things at player's home. Start 5 slots, max 10*level.
- Item = 1 slot normally, some items/buffs more. "Grey" items take 0 slots.
- Example: item "Strong" gives +2 Str and takes 10 slots.
- Base can temporarily exceed limit: player must carry something away or drop; show red indicator (like overload).
- Buffs from base give abilities, permanent parameters, or improve modifiers.

## Armor [OWNER]
- Skill penalty (Str/Dex skills), arcane spell failure chance (slot magic & mana, NOT ki-like abilities).
- Weight, armor bonus. May slow. Mwk/special may reduce penalty (rarely give bonus).

## Enchantment [OWNER, package 5]
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
  activated" tab (e.g. masterwork +1 to attack; a special non-magic material writes its non-magic bonus there).
- An item with no activation price is an ordinary item: always off, it cannot be activated (soft refusal), and its
  enchantment never counts.
- Extra weapon effects (fire d6 and the like) go into the "activated" tab and work only while activated.
- Deactivation (the short rest for "day" items, the long rest for all) removes the enchantment bonuses.
- Assumption (OPEN_QUESTIONS): hardness = base with the weapon mastery percent, then +2N, only while activated.

## Item HP [OWNER, package 6, closes Q31]
- Item HP is stored as the CURRENT number (not as "damage taken"; no migrations, D1).
  Max = base max + HP from weapon mastery + N from enchantment (enchantment only while the item is activated).
- Switching an enchanted item ON: current HP +N (the enchantment bonus, flat, not proportional).
  Switching OFF: current HP * (new max / old max), rounded to nearest; a positive value is never rounded to 0
  (switching off never breaks the item by itself).
  Example: base 10, enchantment +3, active 13/13, damage 6 -> 7; off -> 7*10/13 = 5; on -> 8.
- Broken = item HP <= 50% of max (and > 0).
  Weapon: -2 to attack and damage with this weapon.
  Armor and shield (a shield counts as armor): the AC bonus is halved, rounded down; the armor skill penalty doubles.
- Item HP 0: the item does not work, no bonuses at all (no base values, no enchantment, no tabs).
- Item HP below 0: destroyed for good (state "destroyed": cannot be activated, cannot be healed; stays in the list,
  grey, removed only by hand).
- Commands: damage_item(iid, amount), set_item_hp(iid, value) (manual, edit mode).
- Repair and restoring item HP: the rules do not say (OPEN_QUESTIONS Q32).
- Tests: the example above; a positive HP is not rounded to 0 when switching off; broken at exactly 50% and below,
  not at 51%; broken sword -2 attack and damage; broken armor 5 -> 2, armor penalty x2; shield like armor; HP 0 gives
  nothing; HP -1 destroyed and cannot be activated; a broken weapon shows -2 in the attack table.
- An item without HP (no base HP and no current HP entered, e.g. a ring) is not tracked: always working.
- Tests: +5 sword not activated: attack +1 (masterwork tab), damage +0; activated: +5; no price -> cannot be
  activated, no enchantment; +2 armor not activated -> base armor only; fire d6 only while activated; the short rest
  switches a "day" item off and the enchantment is gone.

## Item codes / sharing [OWNER]
- Any item/ability/etc -> code copied to clipboard. Code -> import as item (catalog import wanted, not built).
- Whole character copy, PDF export. UI must not block copy.

## Enabled / disabled (activation) [OWNER]
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
  inactive it is only a masterwork sword giving +1 attack, nothing else.
- Item activation data [OWNER, simplified]: item has two tabs: "not activated" and "activated". Either one set of effects or the other, never both.
  (An additive item just repeats the base effects in the activated tab.) No mode flag.
