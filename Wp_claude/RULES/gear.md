# Gear

## Doll [OWNER]
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

## Qualification
- Tied to a specific item; does not work for other items (training.md). In levels, each level costs 50 training. Unlocks hidden properties of unusual items.

## Belt (unload) [OWNER]
- Consumables slots (potions, scrolls). Base 10 L. Activation usually 1 spirit, can differ.
- Special slot, buffs or injuries can add bonus belt slots.

## Bag
- Everything not worn and not a weapon. Button "drop bag" excludes its weight until picked up again.
- [OWNER, package 8] The button is the character flag ignore_bag_weight (default off, command set_ignore_bag_weight).
  While on, the bag weight (carried, not worn, not in the hands, not a weapon) is not counted in the carried weight;
  the weight view shows the flag. Tests: bag 30 + sword 20 + armor 50 + axe 15 = 115 L; flag on -> 85 L.

## Weight [OWNER]
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

## Base (resource for strengthening) [OWNER]
- Blessings, immaterial and material things at player's home. Start 5 slots, max 10*level.
- Item = 1 slot normally, some items/buffs more. "Grey" items take 0 slots.
- Example: item "Strong" gives +2 Str and takes 10 slots.
- Base can temporarily exceed limit: player must carry something away or drop; show red indicator (like encumbrance).
- [package 22 B7] 1 base point = 1 base slot; attention base points are kept in tenths, every whole point is +1 slot.
- Buffs from base give abilities, permanent parameters, or improve modifiers.

## Armor [OWNER]
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

## Masterwork [OWNER, package 8; package 9 closes Q39, Q40]
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

## Item codes / sharing [OWNER]
- Any item/ability/etc -> code copied to clipboard. Code -> import as item. [package 18] Built for catalog entries:
  store.export_entry / catalog_import_entry (catalog.md "Catalog files").
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
  inactive it is only a masterwork sword (flag) giving +1 attack, nothing else.
- Item activation data [OWNER, simplified]: item has two tabs: "not activated" and "activated". Either one set of effects or the other, never both.
  (An additive item just repeats the base effects in the activated tab.) No mode flag.

## Consumables [OWNER, package 13 D]
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

## Charges and cooldown [OWNER, package 14 B; closes Q94]
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

## Base contents [OWNER text above; built in package 16 G7]
- An item left at the base = not carried, not worn, not held. It takes Item.base_slot_cost slots (default 1; grey
  items: spent or destroyed, 0) and gives the effects of its acting tab ("Strong": +2 Str, 10 slots). base_view =
  (used, max, over); max = base slots (+ whole attention base points + effects "base_slots"); over the max is shown red,
  never refused. Tests: Strong at the base -> Str 12, 10 of 5 red; two items + a spent potion -> 2 of 5.

## Load display (package 30) [OWNER; closes Q197; the numbers do not change]
- From 0 to the light limit: "light". Above light up to the maximum (the heavy limit): "load" (the old "heavy" state,
  shown as "Нагрузка"). Above the maximum: overload, shown as "you are overloaded and can only drag" (red).
- The view gives the carried weight, the category key (light / heavy / overload), both limits and the text "40 of X"
  (X = the maximum). Example: Str 14 (+2): light up to 7.9 B = 79 L, maximum 12.9 B = 129 L.
