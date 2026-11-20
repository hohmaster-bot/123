"""Hands slot and attack records (RULES/gear.md "Doll", weapons.md, combat.md).

Hands: one shared slot for everything that needs hands (weapon, shield, special item);
the item's `hands` (0, 1, 2) add up to at most 2. Attack records: weapon + one
chosen group + grip + stat; up to 2 primary records.
"""
from dataclasses import replace

from wp.catalog.weapons_catalog import CONTACT, UNARMED_COMBAT
from wp.commands.base import CommandError, command, commit
from wp.commands.item_cmds import check_wearable
from wp.model import derived_view as dv
from wp.model import ids
from wp.model import iterative as itv
from wp.model import records as rec
from wp.model.character import AttackRecord

MAX_HANDS = 2
GRIPS = ("one", "off", "two")
UNARMED_GROUPS = (UNARMED_COMBAT, CONTACT)


def _set_item(ch, iid, **changes):
    ch.item(iid)
    return replace(ch, items=tuple(replace(it, **changes) if it.iid == iid else it for it in ch.items))


@command
def equip_hands(ch, iid=""):
    """Put an item into the hands slot; the hands of all held items add up to at most 2."""
    it = ch.item(iid)
    if it.in_hands:
        raise CommandError("%s is already in the hands" % it.name, "already_hands", values=(it.name,))
    if it.hands <= 0:
        raise CommandError("%s needs no hands" % it.name, "needs_no_hands", values=(it.name,))
    check_wearable(ch, it)             # a shield at HP 0 cannot be taken up; a weapon at HP 0 can
    if dv.hands_used(ch) + it.hands > MAX_HANDS:
        raise CommandError("not enough free hands for %s (%d of %d used)" % (it.name, dv.hands_used(ch), MAX_HANDS), "not_enough_free_hands", values=(it.name, dv.hands_used(ch), MAX_HANDS))
    return commit(_set_item(ch, iid, in_hands=True), "equip_hands", "%s in hands" % it.name)


@command
def unequip_hands(ch, iid=""):
    it = ch.item(iid)
    if not it.in_hands:
        raise CommandError("%s is not in the hands" % it.name, "not_hands", values=(it.name,))
    return commit(_set_item(ch, iid, in_hands=False), "unequip_hands", "%s out of hands" % it.name)


@command
def add_attack(ch, iid="", group="", grip="one", stat="", rid=""):
    """New attack record. Weapon: the group must be one of the weapon's groups.
    Unarmed: Unarmed combat (or Contact). Every record is a main attack record (package 12 B);
    maneuvers live in the character's maneuver list (maneuver_cmds)."""
    if grip not in GRIPS:
        raise CommandError("grip must be one, off or two", "grip_must_one_off")
    if iid == rec.UNARMED:
        if group not in UNARMED_GROUPS:
            raise CommandError("unarmed attacks use Unarmed combat or Contact", "unarmed_attacks_use_unarmed")
        card = next((i for i in ch.items if i.iid == rec.UNARMED), None)
        if card is not None and card.finesse and grip == "two":
            raise CommandError("a finesse weapon is held in one hand or the off-hand only (owner)", "finesse_weapon_held_one")
    else:
        it = ch.item(iid)
        groups = rec.attack_groups(it)     # a shield attacks as an improvised weapon (Contact) by default
        if not groups:
            raise CommandError("%s is not a weapon" % it.name, "not_weapon", values=(it.name,))
        group = group or groups[0]
        if group not in groups:
            raise CommandError("%s is not in group %r" % (it.name, group), "not_group", values=(it.name, group))
        if it.hands == 2 and grip != "two":
            raise CommandError("%s is two-handed" % it.name, "two_handed", values=(it.name,))
        if grip == "off" and it.hands == 2:
            raise CommandError("a two-handed weapon cannot be off-hand", "two_handed_weapon_cannot")
        if grip == "two" and it.finesse:
            raise CommandError("a finesse weapon is held in one hand or the off-hand only (owner)", "finesse_weapon_held_one")
    if not rid:                        # made by the program (D7); a number is added on a collision
        rid = ids.unique("%s:%s:%s" % (iid, group, grip), (r.rid for r in ch.attacks))
    if any(r.rid == rid for r in ch.attacks):
        raise CommandError("attack record already exists: %s" % rid, "attack_record_already_exists", values=(rid,))
    record = AttackRecord(rid=rid, item=iid, group=group, grip=grip, stat=stat)
    return commit(replace(ch, attacks=ch.attacks + (record,)), "add_attack", "attack %s" % rid)


@command
def remove_attack(ch, rid=""):
    left = tuple(r for r in ch.attacks if r.rid != rid)
    if len(left) == len(ch.attacks):
        raise CommandError("no attack record %r" % (rid,), "no_attack_record", values=(rid,))
    return commit(replace(ch, attacks=left), "remove_attack", "attack %s removed" % rid)


@command
def set_twf(ch, rid="", off="", on=True):
    """Two-weapon combination on a record (main hand). off = off-hand record id, or "" for the other
    end of a double weapon. Allowed only with two weapons in the hands or a double weapon."""
    from wp.model import twf
    rec_ = next((r for r in ch.attacks if r.rid == rid), None)
    if rec_ is None:
        raise CommandError("no attack record %r" % (rid,), "no_attack_record", values=(rid,))
    if on:
        if not twf.available(ch, rec_, off):
            raise CommandError("two-weapon combination needs two weapons in the hands or a double weapon", "two_weapon_combination_needs")
        if off:
            other = next((r for r in ch.attacks if r.rid == off), None)
            if other is None or other.item == rec_.item:
                raise CommandError("the off-hand record must be another weapon", "off_hand_record_must")
        elif not (rec_.item != rec.UNARMED and ch.item(rec_.item).double):
            raise CommandError("without an off-hand record the weapon must be a double weapon", "without_off_hand_record")
    attacks = tuple(replace(r, twf=bool(on), twf_off=off if on else "") if r.rid == rid else r for r in ch.attacks)
    return commit(replace(ch, attacks=attacks), "set_twf", "%s two-weapon %s" % (rid, "on" if on else "off"))


@command
def set_primary_attack(ch, rid="", on=True):
    """Mark a record primary (at most 2) or not."""
    if not any(r.rid == rid for r in ch.attacks):
        raise CommandError("no attack record %r" % (rid,), "no_attack_record", values=(rid,))
    if on and sum(1 for r in ch.attacks if r.primary and r.rid != rid) >= rec.MAX_PRIMARY:
        raise CommandError("at most %d primary attack records" % rec.MAX_PRIMARY, "most_primary_attack_records", values=(rec.MAX_PRIMARY,))
    attacks = tuple(replace(r, primary=bool(on)) if r.rid == rid else r for r in ch.attacks)
    return commit(replace(ch, attacks=attacks), "set_primary_attack",
                  "%s primary %s" % (rid, "on" if on else "off"))


@command
def use_attack(ch, rid=""):
    """The "attack" button (package 16 C): one use of an attack record. The iterative counter +1; the view shows the
    penalty of the NEXT attack. Refused for an unknown or unavailable record."""
    record = next((r for r in ch.attacks if r.rid == rid), None)
    if record is None:
        raise CommandError("no attack record %r" % (rid,), "no_attack_record", values=(rid,))
    ok, why = rec.attack_available(ch, record)
    if not ok:
        raise CommandError("attack %s is not available: take %s in hand" % (rid, ", ".join(why["missing"]) or "?"),
                           "attack_not_available", values=(rid,), missing=tuple(why["missing"]))
    pen = itv.penalty(ch, record)
    return commit(replace(ch, iterative_count=ch.iterative_count + 1), "use_attack",
                  "attack %s, iterative %d" % (rid, pen), {"iterative": pen, "count": ch.iterative_count + 1})


@command
def set_iterative_count(ch, n=0):
    """Set the current iterative series by hand (package 16 C)."""
    n = int(n)
    if n < 0:
        raise CommandError("the iterative count cannot be negative", "iterative_count_negative", values=(n,))
    return commit(replace(ch, iterative_count=n), "set_iterative_count", "iterative count %d" % n)
