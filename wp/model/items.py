"""Item activation, enchantment and item HP (RULES/gear.md, weapons.md). Computed on read (D6).

- Enchantment N counts only while the item is activated; an item with no activation price is
  an ordinary item, always off (Q30).
- Item HP is stored as the CURRENT number (`Item.hp_current`; None = at max). Max = base HP
  + weapon mastery HP + N (enchantment, only while activated).
- Switching ON an enchanted item: current HP +N (flat). Switching OFF: current * new max / old max,
  rounded to nearest; a positive value never rounds to 0.
- States: "ok"; "broken" = 0 < HP <= 50% of max; "not_working" = HP 0 (gives nothing);
  "destroyed" = HP went below 0 (stored flag, cannot be activated or healed).
- An item without HP (max 0, no stored current) is not tracked: always "ok".
- HP 0 (or destroyed): the item gives NOTHING, also no enchantment (+N attack/damage/lucky,
  armor/shield +N, hardness +2N) and no tabs (package 8, R2).
- `picks` = weapon mastery picks of the group the item is used with (records.item_picks):
  "weapon HP +1" raises max HP, "durability +30% / +70%" raises hardness (package 8, R3).
- Masterwork (flag): weapon +1 to attack as an ENHANCEMENT bonus, but it is OFF while the weapon's
  enchantment +1 or higher is active (masterwork_state gives the reason id); armor/shield skill
  penalty -1 smaller (never above 0) always, applied before the broken doubling (package 9 D).
- Order of item numbers (package 9 F): own base, then enchantment N (only while activated), then
  the mastery picks. Hardness = (base + 2N) * (100 + mastery percent) / 100, rounded down;
  "+30%" and "+70%" add up (both = +100%, x2). Max HP = base + N + "HP +1" picks.
- Notches (package 9 G): 1 notch = 1 item HP; notches = floor(damage / final hardness); a durable
  item (default: armor and shields) loses at most 1 per attack; hardness 0 = no automatic notches.
"""
from dataclasses import replace

from wp.core import weapons as wpn
from wp.rules_data import rules as rd

# rule numbers that were inline literals (package 20: data, wp/rules_data/constants.json)
BROKEN_AT = rd.ref("items.broken_at_fraction")   # broken at max HP / this and below
BROKEN_SKILL_MULT = rd.ref("items.broken_skill_mult")   # a broken armor's skill penalty is multiplied by
HARDNESS_PER_ENCHANT = rd.ref("items.hardness_per_enchant")   # hardness + this * enchantment N

OK = "ok"
BROKEN = "broken"
NOT_WORKING = "not_working"
DESTROYED = "destroyed"
BROKEN_PENALTY = rd.ref("items.broken_weapon_penalty")  # weapon: attack and damage with it
MASTERWORK_ATTACK = rd.ref("items.masterwork_attack")  # masterwork weapon: +1 attack, type enhancement
MASTERWORK_PENALTY_RELIEF = rd.ref("items.masterwork_penalty_relief")  # masterwork armor/shield: skill penalty 1 smaller
# masterwork_state reason ids (data for the UI, no text)
MW_NOT_MASTERWORK = "not_masterwork"
MW_NOT_WORKING = "not_working"
MW_ENCHANT_ACTIVE = "enchant_active"


def spent(it):
    """A consumable at quantity 0: stays in the list, greyed, weighs 0 (gear.md, package 13 D)."""
    return it.consumable and it.quantity <= 0


def weight_l(it):
    """Weight of the item stack = unit weight * quantity (0 when spent)."""
    return 0 if spent(it) else it.weight_l * max(0, it.quantity)


def item_active(it):
    """Activated AND activatable (Q30); a destroyed item is never active."""
    return it.activated and not it.destroyed and (it.activation_day > 0 or it.activation_decade > 0)


def enchant(it, picks=()):
    """Enchantment level N, only while the item is activated (Q30) AND works (HP > 0, R2)."""
    return it.enchant if item_active(it) and works(it, picks) else 0


def hp_max(it, picks=(), active=None):
    """Base HP + expert picks + N while activated. `active` overrides the item's own state."""
    on = item_active(it) if active is None else active
    return wpn.final_hp(it.hp, picks) + (it.enchant if on else 0)


def hp_current(it, picks=()):
    return hp_max(it, picks) if it.hp_current is None else it.hp_current


def tracked(it):
    return it.hp_current is not None or wpn.final_hp(it.hp, ()) > 0


def state(it, picks=()):
    if it.destroyed:
        return DESTROYED
    if not tracked(it):
        return OK
    cur, mx = hp_current(it, picks), hp_max(it, picks)
    if cur <= 0:
        return NOT_WORKING
    if BROKEN_AT * cur <= mx:
        return BROKEN
    return OK


def works(it, picks=()):
    return state(it, picks) not in (NOT_WORKING, DESTROYED)


def defensive(it):
    """Armor or shield: at HP 0 it cannot be put on and a worn one counts as taken off (pkg 7)."""
    return it.armor > 0 or it.shield > 0 or it.kind == "shield" or bool(it.shield_type)


def broken(it, picks=()):
    return state(it, picks) == BROKEN


def masterwork_state(it, picks=()):
    """(active, reason id). Armor/shield: active whenever it works. Weapon: OFF while its
    enchantment +1 or more is active (package 9 D); an activated tab without enchantment N
    (an active ability like fire d6) does not switch it off."""
    if not it.masterwork:
        return False, MW_NOT_MASTERWORK
    if not works(it, picks):
        return False, MW_NOT_WORKING
    if not defensive(it) and enchant(it, picks) >= 1:
        return False, MW_ENCHANT_ACTIVE
    return True, ""


def masterwork_attack(it, picks=()):
    """Masterwork weapon (not a shield): +1 attack (enhancement) while masterwork is active."""
    if defensive(it) or not masterwork_state(it, picks)[0]:
        return 0
    return MASTERWORK_ATTACK


def skill_penalty(it, picks=()):
    """Str/Dex skill penalty of armor or a shield: masterwork -1 smaller (not above 0), then doubled
    while broken (gear.md); 0 at HP 0 (the item counts as taken off)."""
    if not works(it, picks):
        return 0
    p = min(0, it.skill_penalty)
    if it.masterwork:
        p = min(0, p + MASTERWORK_PENALTY_RELIEF)
    return BROKEN_SKILL_MULT * p if broken(it, picks) else p


def tab(it, picks=()):
    """The one acting tab (D17): "activated" while active, else "not activated"; nothing at HP 0. Unlocked hidden
    properties (package 25 D) add their effects to the tab they belong to (base = not activated)."""
    if not works(it, picks):
        return ()
    on = item_active(it)
    hidden = tuple(e for h in it.hidden_properties if unlocked(it, h) and (h.tab == ACTIVATED) == on for e in h.effects)
    return (it.effects_on if on else it.effects_off) + hidden


ACTIVATED = "activated"
LOCKED_TEXT = "???"


def qualification_level(it):
    """The item's qualification level: its N once bought (buy_item_qualification, 50 * N), else 0 (Q109)."""
    return it.qualification_n if it.qualified else 0


def unlocked(it, h):
    return qualification_level(it) >= h.min_qualification


def hidden_view(it):
    """((id, text or "???", locked, tab, min_qualification), ...) for the item view."""
    return tuple((h.hid, h.text if unlocked(it, h) else LOCKED_TEXT, not unlocked(it, h), h.tab, h.min_qualification)
                 for h in it.hidden_properties)


def durability(it, picks=()):
    """Final hardness: (base + 2N while activated) * (100 + mastery percent) / 100, down (package 9 F)."""
    return wpn.final_durability(it.durability + HARDNESS_PER_ENCHANT * enchant(it, picks), picks)


def is_durable(it):
    """Durable = at most 1 notch per attack; default: armor and shields yes, others no (package 9 G)."""
    return defensive(it) if it.durable is None else bool(it.durable)


def notches(it, damage, picks=()):
    """Item HP lost to one attack: floor(damage / final hardness), at most 1 if durable;
    None when the hardness is 0 or not set (no automatic notches: use damage_item)."""
    h = durability(it, picks)
    if h <= 0:
        return None
    n = max(0, int(damage)) // h
    return min(1, n) if is_durable(it) else n


def scale_off(cur, old_max, new_max):
    """Current HP when the maximum drops: cur * new / old, rounded to nearest (half up);
    a positive value never becomes 0."""
    if old_max <= 0 or cur <= 0:
        return cur
    v = (2 * cur * new_max + old_max) // (2 * old_max)
    return max(1, v)


def switch(it, on, picks=()):
    """The item with `activated` = on and its current HP adjusted (gear.md, package 6)."""
    new = replace(it, activated=on, active_until=it.active_until if on else "")
    if it.hp_current is None or not it.enchant:
        return new
    if on:
        return replace(new, hp_current=it.hp_current + it.enchant)
    return replace(new, hp_current=scale_off(it.hp_current, hp_max(it, picks, active=True),
                                             hp_max(it, picks, active=False)))


def with_hp(it, value):
    """Item with current HP = value; below 0 -> destroyed for good (and switched off)."""
    value = int(value)
    if value < 0:
        return replace(it, hp_current=value, destroyed=True, activated=False, active_until="")
    return replace(it, hp_current=value)


def damaged(it, amount, picks=()):
    return with_hp(it, hp_current(it, picks) - int(amount))
