"""Sheet numbers with effect targets (package 16 A2) and the base contents (gear.md "Base", package 16 G7).
Split out of derived_view (module size); derived_view re-exports these names."""
from wp.core.damage import Pool
from wp.model import items as itm
from wp.model import sheet_targets as stg
from wp.model.derived_view import works
from wp.rules_data import rules as rd



def mana_max(ch):
    return max(0, ch.mana.max + stg.value(ch, "mana_max"))


def mana_pool(ch):
    """Mana with the effect "mana_max"; the stored Pool keeps the base max (bridge writes back the current only)."""
    return Pool(ch.mana.current, mana_max(ch))


def slot_pool(ch, circle):
    p = ch.slots.get(circle)
    if p is None:
        return None
    return Pool(p.current, max(0, p.max + stg.value(ch, stg.SLOTS + str(circle))))


def slot_pools(ch):
    return {c: slot_pool(ch, c) for c in ch.slots}


def reactions(ch):
    return max(0, ch.reactions + stg.value(ch, "reactions"))


def base_slots(ch):
    """Base slots: bought / start slots + whole base points of attention option 4 (tenths kept) + effects."""
    return max(0, ch.base_slots + ch.base_points_tenths // rd.const("training.tenths_per_point", ch) + stg.value(ch, "base_slots"))


def comfort_rate_bonus(ch):
    return stg.value(ch, "comfort_rate_bonus")


# ---------------------------------------------------------- base contents (gear.md "Base", package 16 G7)

def at_base(ch):
    """Items left at the base (not carried, not worn, not held) that still work: their acting tab gives its effects
    ("Strong" +2 Str, gear.md)."""
    return [it for it in ch.items if not it.carried and not it.equipped and not it.in_hands and works(ch, it)
            and not itm.spent(it)]


def base_used(ch):
    """Base slots taken: Item.base_slot_cost of every item at the base; grey items (spent, destroyed) take 0."""
    return sum(max(0, it.base_slot_cost) for it in ch.items
               if not it.carried and not it.equipped and not it.in_hands and not itm.spent(it) and not it.destroyed)


def base_view(ch):
    """(used, max, over): over the limit is shown red, never refused (gear.md)."""
    used, mx = base_used(ch), base_slots(ch)
    return used, mx, used > mx
