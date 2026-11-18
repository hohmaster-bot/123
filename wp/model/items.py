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
"""
from dataclasses import replace

from wp.core import weapons as wpn

OK = "ok"
BROKEN = "broken"
NOT_WORKING = "not_working"
DESTROYED = "destroyed"
BROKEN_PENALTY = -2            # weapon: attack and damage with it


def item_active(it):
    """Activated AND activatable (Q30); a destroyed item is never active."""
    return it.activated and not it.destroyed and (it.activation_day > 0 or it.activation_decade > 0)


def enchant(it):
    """Enchantment level N, only while the item is activated (Q30)."""
    return it.enchant if item_active(it) else 0


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
    if 2 * cur <= mx:
        return BROKEN
    return OK


def works(it):
    return state(it) not in (NOT_WORKING, DESTROYED)


def defensive(it):
    """Armor or shield: at HP 0 it cannot be put on and a worn one counts as taken off (pkg 7)."""
    return it.armor > 0 or it.shield > 0 or it.kind == "shield" or bool(it.shield_type)


def broken(it):
    return state(it) == BROKEN


def tab(it):
    """The one acting tab (D17): "activated" while active, else "not activated"; nothing at HP 0."""
    if not works(it):
        return ()
    return it.effects_on if item_active(it) else it.effects_off


def durability(it, picks=()):
    """Final hardness: base with weapon mastery percent, then +2N while activated (assumption)."""
    return wpn.final_durability(it.durability, picks) + 2 * enchant(it)


def scale_off(cur, old_max, new_max):
    """Current HP when the maximum drops: cur * new / old, rounded to nearest (half up);
    a positive value never becomes 0."""
    if old_max <= 0 or cur <= 0:
        return cur
    v = (2 * cur * new_max + old_max) // (2 * old_max)
    return max(1, v)


def switch(it, on):
    """The item with `activated` = on and its current HP adjusted (gear.md, package 6)."""
    new = replace(it, activated=on, active_until=it.active_until if on else "")
    if it.hp_current is None or not it.enchant:
        return new
    if on:
        return replace(new, hp_current=it.hp_current + it.enchant)
    return replace(new, hp_current=scale_off(it.hp_current, hp_max(it, active=True), hp_max(it, active=False)))


def with_hp(it, value):
    """Item with current HP = value; below 0 -> destroyed for good (and switched off)."""
    value = int(value)
    if value < 0:
        return replace(it, hp_current=value, destroyed=True, activated=False, active_until="")
    return replace(it, hp_current=value)


def damaged(it, amount):
    return with_hp(it, hp_current(it) - int(amount))
