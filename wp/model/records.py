"""Attack records and weapon-group bonuses (RULES/weapons.md, combat.md, gear.md).

- An attack record = weapon + ONE chosen weapon group + grip + attack stat.
  Bonuses come ONLY from the chosen group; never from two groups at once; parent
  groups add no bonuses (levels and basics still follow D16).
- Attacks are shown only for weapons held in the hands, plus the unarmed attack (always).
- Up to two records are marked primary; a single visible weapon record is primary
  automatically. Passive group bonuses (balance regen +1, parry...) come from the
  primary records' groups; "Unarmed combat" bonuses always work, even when armed.
"""
from wp.catalog.weapons_catalog import BASIC, CONTACT, UNARMED_COMBAT
from wp.core import bonuses as bo
from wp.core import weapons as wpn
from wp.model.character import SHIELD, AttackRecord

UNARMED = "unarmed"
MAX_PRIMARY = 2
PASSIVE_KEYS = ("parry", "balance_regen", "range_ft")


def node(ch, gid):
    for e in ch.weapons:
        if e.weapon.name == gid:
            return e
    return None


def is_basic(ch, gid):
    n = node(ch, gid)
    return gid == BASIC or (n is not None and n.weapon.basic)


def is_shield(item):
    return item.kind == SHIELD or bool(item.shield_type)


def attack_groups(item):
    """Groups an item can attack with: its weapon groups; a shield without groups attacks as an
    improvised weapon of group Contact (owner, package 5). Other items: none."""
    if item.groups:
        return tuple(item.groups)
    return (CONTACT,) if is_shield(item) else ()


def in_hands_ids(ch):
    return {it.iid for it in ch.items if it.in_hands}


def held_ids(ch):
    """Items in the hands, in list order (data for the UI: "in hands: sword A, shield A")."""
    return tuple(it.iid for it in ch.items if it.in_hands)


def required_items(ch, record):
    """Items an attack record needs in the hands: its weapon (a double weapon is one item), plus
    the off-hand weapon of a two-weapon record. Unarmed needs no item."""
    need = [record.item] if record.item != UNARMED else []
    if record.twf and record.twf_off:
        off = next((r for r in ch.attacks if r.rid == record.twf_off), None)
        if off is not None and off.item != UNARMED and off.item not in need:
            need.append(off.item)
    return tuple(need)


def _unarmed_off(ch, record):
    if not (record.twf and record.twf_off):
        return False
    off = next((r for r in ch.attacks if r.rid == record.twf_off), None)
    return off is not None and off.item == UNARMED


def attack_available(ch, record):
    """Can this attack record be used now (package 8 B)? Every weapon it needs must be in the hands
    (two-weapon: both, in any order; double weapon: the one weapon); an unarmed off-hand strike
    needs a free hand. Returns (bool, data) with ids, not text, so the UI can grey it out and say
    why: {"required": ids, "in_hands": ids, "missing": ids, "free_hand": bool}."""
    held = held_ids(ch)
    need = required_items(ch, record)
    missing = tuple(i for i in need if i not in held)
    used = sum(it.hands for it in ch.items if it.in_hands)
    free = used <= 1 if _unarmed_off(ch, record) else True
    ok = not missing and free
    return ok, {"required": need, "in_hands": held, "missing": missing, "free_hand": free}


def default_unarmed():
    return AttackRecord(rid=UNARMED, item=UNARMED, group=UNARMED_COMBAT)


def visible(ch):
    """Records of weapons in the hands, plus the unarmed record (explicit or default)."""
    held = in_hands_ids(ch) - {UNARMED}
    out = [r for r in ch.attacks if r.item != UNARMED and r.item in held]
    unarmed = [r for r in ch.attacks if r.item == UNARMED]
    out += unarmed or [default_unarmed()]
    return tuple(out)


def primary(ch):
    """Primary records among visible weapon records: the marked ones (max 2), or the
    single visible weapon record automatically."""
    weapon_recs = [r for r in visible(ch) if r.item != UNARMED]
    marked = [r for r in weapon_recs if r.primary][:MAX_PRIMARY]
    if marked:
        return tuple(marked)
    if len(weapon_recs) == 1:
        return tuple(weapon_recs)
    return ()


def _no_parry(ch, record):
    for it in ch.items:
        if it.iid == record.item:
            return it.no_parry
    return False


def group_picks(ch, gid):
    n = node(ch, gid)
    return n.picks if n is not None else ()


MAIN = "main"
MANEUVER = "maneuver"
KINDS = (MAIN, MANEUVER)


def main_record(ch, iid):
    """The item's MAIN attack record (kind "main", the plain weapon attack); None if it has none.
    Several main records (data built by hand): the primary one, else the first (package 9 F)."""
    recs = [r for r in ch.attacks if r.item == iid and r.kind == MAIN]
    marked = [r for r in recs if r.primary]
    return (marked or recs or [None])[0]


def item_record(ch, iid):
    """The record whose group and picks change the item's HP and hardness: its main record
    (package 9 F; maneuvers never count)."""
    return main_record(ch, iid)


def resolved(ch, record):
    """A maneuver inherits group and stat from its main record (package 9 F; its own modifiers come
    in a later package). A main record is returned as is."""
    if record.kind != MANEUVER:
        return record
    base = next((r for r in ch.attacks if r.rid == record.base_record), None)
    if base is None:
        return record
    return AttackRecord(rid=record.rid, item=record.item, group=base.group, grip=record.grip,
                        stat=base.stat, primary=record.primary, twf=record.twf, twf_off=record.twf_off,
                        kind=MANEUVER, base_record=record.base_record)


def item_picks(ch, item):
    """Mastery picks that change the item's HP and hardness (weapons.md "weapon HP +1",
    "durability +30% / +70%"): the picks of the group of item_record. A shield attacks through
    group Contact by default, so Contact picks reach a shield the same way (package 8, D2)."""
    r = item_record(ch, item.iid)
    return group_picks(ch, r.group) if r is not None else ()


def passive_groups(ch):
    """Groups whose passive bonuses apply: primary records' groups + Unarmed combat (always).
    Each group counts once."""
    seen = []
    for gid in [r.group for r in primary(ch)] + [UNARMED_COMBAT]:
        if gid not in seen:
            seen.append(gid)
    return tuple(seen)


def passive_bonuses(ch, key):
    """Passive group bonuses as FLAT bonuses (stacked by bonuses.py: flat adds)."""
    out = []
    no_parry = {r.group for r in primary(ch) if _no_parry(ch, r)}
    for gid in passive_groups(ch):
        if key == "parry" and gid in no_parry and gid != UNARMED_COMBAT:
            continue            # a weapon that cannot parry gives no parry from its group (empty hand instead)
        v = wpn.mastery_flat(group_picks(ch, gid)).get(key, 0)
        if v:
            out.append(bo.Bonus(v, bo.FLAT, bo.AC if key == "parry" else "passive", source=gid))
    return out


def passive(ch, key):
    """Total passive bonus of one kind (parry, balance_regen, range_ft)."""
    return bo.stack(passive_bonuses(ch, key))
