# Character doll (slots) [OWNER]
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
