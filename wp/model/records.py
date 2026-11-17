"""Attack records and weapon-group bonuses (RULES/weapons.md, combat.md, gear.md).

- An attack record = weapon + ONE chosen weapon group + grip + attack stat.
  Bonuses come ONLY from the chosen group; never from two groups at once; parent
  groups add no bonuses (levels and basics still follow D16).
- Attacks are shown only for weapons held in the hands, plus the unarmed attack (always).
- Up to two records are marked primary; a single visible weapon record is primary
  automatically. Passive group bonuses (balance regen +1, parry...) come from the
  primary records' groups; "Unarmed combat" bonuses always work, even when armed.
"""
from wp.catalog.weapons_catalog import BASIC, UNARMED_COMBAT
from wp.core import bonuses as bo
from wp.core import weapons as wpn
from wp.model.character import AttackRecord

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


def in_hands_ids(ch):
    return {it.iid for it in ch.items if it.in_hands}


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
