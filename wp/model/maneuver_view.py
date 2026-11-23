"""Maneuver list view (RULES/combat.md "Maneuver list", package 12 B). Computed on read (D6).

- Weapon tags = all groups of the weapon (a shield without groups: Contact) + its weapon kind id
  (Item.wkind, the catalog card). The special tag "unarmed" matches the unarmed attack while it is
  possible: no weapon (an item with weapon groups) in the hands.
- tag_mode "any": one required tag is enough; "all": every required tag. No required tags: any
  weapon in the hands or the unarmed attack (assumption Q79).
- One entry PER matching weapon in the hands (numbers differ per weapon): that weapon's main attack
  record (records.main_record) with the maneuver's to-hit / damage (untyped) and its effects added to
  this attack only, by the usual stacking rules. A matching weapon without any attack record gives no
  numbers (reason "no_attack_record", assumption Q78).
- required_feat not owned -> unavailable ("feat_missing"). Losing a weapon never deletes a maneuver:
  it is only unavailable. Costs are shown, never spent. Reasons are ids for the UI.
"""
from dataclasses import dataclass
from typing import Tuple

from wp.core import bonuses as bo
from wp.model import attack_view as av
from wp.model import derived_view as dv
from wp.model import records as rec

UNARMED_TAG = "unarmed"
NO_MATCH = "no_matching_weapon"
FEAT_MISSING = "feat_missing"
NO_REACTIONS = "not_enough_reactions"     # package 22 A2
UNARMED_NOT_POSSIBLE = "unarmed_not_possible"
NO_RECORD = "no_attack_record"


@dataclass(frozen=True)
class ManeuverWeapon:
    item: str                          # item iid, or "unarmed"
    record: str                        # the main attack record used ("" = none)
    to_hit: int = 0
    damage: int = 0
    cmb: int = 0


@dataclass(frozen=True)
class ManeuverView:
    mid: str
    name: str
    available: bool
    weapons: Tuple[ManeuverWeapon, ...]
    reasons: Tuple[str, ...]           # ids: no_matching_weapon / feat_missing / unarmed_not_possible / no_attack_record
    cost: Tuple[int, int, int]         # (actions, balance, spirit): record only
    favorite: bool = False
    condition_tag: str = "none"
    granted_by: Tuple[str, ...] = ()   # feats whose granted_maneuvers list this maneuver


def weapon_tags(item):
    return set(rec.attack_groups(item)) | ({item.wkind} if item.wkind else set())


def matches(m, tags):
    req = set(m.required_tags)
    if not req:
        return True
    return req <= tags if m.tag_mode == "all" else bool(req & tags)


def _held_weapons(ch):
    return [it for it in ch.items if it.in_hands and rec.attack_groups(it)]


def unarmed_possible(ch):
    """No weapon (an item with weapon groups) in the hands."""
    return not any(it.groups for it in ch.items if it.in_hands)


def _extra(ch, m):
    ctx = dv.context(ch)
    out = [bo.Bonus(m.to_hit, bo.FLAT, bo.ATTACK, source=m.name), bo.Bonus(m.damage, bo.FLAT, bo.DAMAGE, source=m.name)]
    return out + [e.as_bonus(m.name, ctx) for e in m.effects]


def _numbers(ch, m, item_id, record):
    a = av.attack(ch, record, _extra(ch, m))
    return ManeuverWeapon(item=item_id, record=record.rid, to_hit=a.to_hit, damage=a.damage, cmb=a.cmb)


def _unarmed_record(ch):
    return next((r for r in ch.attacks if r.item == rec.UNARMED), None) or rec.default_unarmed()


def view_one(ch, m):
    reasons = []
    entries = []
    for it in _held_weapons(ch):
        if not matches(m, weapon_tags(it)):
            continue
        r = rec.main_record(ch, it.iid)
        if r is None:
            reasons.append(NO_RECORD)
            continue
        entries.append(_numbers(ch, m, it.iid, r))
    if matches(m, {UNARMED_TAG}) and (UNARMED_TAG in m.required_tags or not m.required_tags):
        if unarmed_possible(ch):
            entries.append(_numbers(ch, m, rec.UNARMED, _unarmed_record(ch)))
        elif UNARMED_TAG in m.required_tags and not entries:
            reasons.append(UNARMED_NOT_POSSIBLE)
    if not entries and NO_RECORD not in reasons and UNARMED_NOT_POSSIBLE not in reasons:
        reasons.append(NO_MATCH)
    if m.required_feat and not any(f.fid == m.required_feat for f in ch.feats):
        reasons.append(FEAT_MISSING)
    if m.cost_reactions:
        from wp.commands import reaction_cmds
        if reaction_cmds.reactions_current(ch) < m.cost_reactions:
            reasons.append(NO_REACTIONS)
    ok = bool(entries) and FEAT_MISSING not in reasons and NO_REACTIONS not in reasons
    return ManeuverView(mid=m.mid, name=m.name, available=ok, weapons=tuple(entries), reasons=tuple(reasons),
                        cost=(m.cost_actions, m.cost_balance, m.cost_spirit), favorite=m.favorite,
                        condition_tag=m.condition_tag,
                        granted_by=tuple(f.fid for f in ch.feats if m.mid in f.granted_maneuvers))


def maneuver_view(ch):
    return tuple(view_one(ch, m) for m in ch.maneuvers)
