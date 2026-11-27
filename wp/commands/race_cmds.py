"""Race commands (package 36 P3; owner decision 15; RULES/races.md).

take_race(race): the character has no race: the race entry (from the catalog, given by the Session / UI) is copied in,
    every record with the source race:<id>; the entry is kept as a snapshot.
change_race(race, confirm): everything with the old race source (quirks the race gave and paid race traits included)
    is removed and the new race entries are added: one command, one journal line, one undo step, no training refund.
    Without confirm=True it is refused with the list of what would be removed (reason race_change_confirm).
buy_race_ability(aid, source, feats): a priced ability of the taken race (the snapshot), paid in training like every
    purchase (training.md); an ability that needs another one is refused until that one is taken. Package 38: an
    ability with "grants_feats" adds those catalog feats for free, linked "held by" the ability (the Mordon Wall of
    Bones gets Toughness); feats = their catalog entries (given by the Session / UI like the race entry).
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import training as tr
from wp.model import races
from wp.model.character import Feat
from wp.rules_data import rules as rd


def _entry(race):
    if not race or not isinstance(race, dict) or not race.get("id"):
        raise CommandError("no race entry given", "no_race_given")
    return race


@command
def take_race(ch, race=None):
    entry = _entry(race)
    if ch.race_id:
        raise CommandError("the character already has the race %s: change it" % ch.race_id, "race_taken",
                           values=(ch.race_id,))
    new = races.with_race(ch, entry, rd.const("speed.base_ft", ch))
    return commit(new, "take_race", "race %s" % entry["id"], {"race": entry["id"]})


@command
def change_race(ch, race=None, confirm=False):
    entry = _entry(race)
    if not ch.race_id:
        return take_race(ch, race=entry)
    gone = races.of_race(ch, ch.race_id)
    if not confirm:
        raise CommandError("changing the race removes %d entries: confirm" % len(gone), "race_change_confirm",
                           values=(", ".join(name or oid for _c, oid, name in gone),), removed=tuple(gone))
    old = ch.race_id
    new = races.with_race(replace(races.without(ch, old), race_id="", race_info=""), entry,
                          rd.const("speed.base_ft", ch))
    return commit(new, "change_race", "race %s -> %s" % (old, entry["id"]),
                  {"race": entry["id"], "removed": tuple(oid for _c, oid, _n in gone)})


def _granted(ch, a, entries):
    """The free feats an ability grants (package 38): catalog copies, cost 0, held by the ability."""
    from wp.catalog import feats_catalog as fcat
    have, out = {f.fid for f in ch.feats}, []
    for fid in a.get("grants_feats", ()):
        if fid in have:
            continue
        e = next((x for x in entries or () if isinstance(x, dict) and x.get("id") == fid), None)
        if e is None:
            raise CommandError("the feat %s of %s is not given" % (fid, a["id"]), "grant_entry_needed",
                               values=(fid, a["id"]))
        t = fcat.from_entries([e]).templates[0]
        out.append(Feat(fid=fid, title=t.name, flags=t.flags, source=races.source_of(ch.race_id), cost=0,
                        effects=t.effects, granted_maneuvers=t.granted_maneuvers, is_stance=t.is_stance,
                        rerolls=t.rerolls,
                        held_by="feat:" + a["id"]))
    return tuple(out)


@command
def buy_race_ability(ch, aid="", source=tr.TRAINING, feats=()):
    a = races.ability(ch, aid)
    if a is None:
        raise CommandError("the race has no ability %r" % (aid,), "not_found", values=("race abilities", aid))
    if any(f.fid == aid for f in ch.feats):
        raise CommandError("already taken: %s" % aid, "feat_already_sheet", values=(aid,))
    need = a.get("needs", "")
    if need and not any(f.fid == need for f in ch.feats):
        raise CommandError("%s needs %s first" % (aid, need), "needs_ability", values=(aid, need))
    price = int(a.get("price", 0))
    try:
        left = tr.pay(ch.training, price, source)
    except ValueError as e:
        raise CommandError(str(e), "rule_refused")
    feat = races.ability_feat(ch.race_id, a)
    granted = _granted(ch, a, feats)
    return commit(replace(ch, feats=ch.feats + (feat,) + granted, training=left), "buy_race_ability",
                  "race ability %s for %d" % (aid, price), {"cost": price})
