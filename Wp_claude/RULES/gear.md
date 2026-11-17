# Gear

## Doll [OWNER]
- Doll = worn or ready items. Two hands: items in hands needing > 2 hands total cannot be equipped. Rest of doll is worn.
- Armor, helm, glasses, etc. Character slots: see doll.md.
- Magic items may need activation: 1 spirit/day or 5 until session end; cost may scale or have an alternative.
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

## Item codes / sharing [OWNER]
- Any item/ability/etc -> code copied to clipboard. Code -> import as item (catalog import wanted, not built).
- Whole character copy, PDF export. UI must not block copy.

## Enabled / disabled (activation) [OWNER]
- "Enabled/disabled" mainly means activation of enchanted/special items.
- Passive requirements: Qualification, skill X with Y ranks, Court X level Y.
- Activation cost: usually 1 spirit (active until end of SHORT rest), 5 spirit (until end of LONG rest), or X spirit.
  Short rest switches 1-spirit items off, long rest switches off all. Cost may also be stat damage, HP, etc.
- Consumables: usually 1 spirit to activate.
- Not activated items give fewer bonuses. Example: +5 magic sword (+5 attack, damage and lucky attack = enchant bonus):
  inactive it is only a masterwork sword giving +1 attack, nothing else.
- Item activation data [OWNER, simplified]: item has two tabs: "not activated" and "activated". Either one set of effects or the other, never both.
  (An additive item just repeats the base effects in the activated tab.) No mode flag.
