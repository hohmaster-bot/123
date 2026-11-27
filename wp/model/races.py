"""A race in the character (package 36 P3; owner decisions 1, 9, 15, 16; RULES/races.md).

A race entry of the catalog (kind races) holds only what affects the character: effects (stats, HP, ...), speed,
abilities (id, name, text, price in training, needs, effects, triggers, charges, tags, held_by), statuses, pools,
quirks, languages, type tags. copies(entry, ch) builds the records the character gets, each with the source
"race:<id>": the race's own effects are one feat "race_<id>" (stat changes and HP are EFFECTS, never edits of base
values); every ability WITHOUT a price is a feat at once; a priced ability is bought later (buy_race_ability). The
entry is kept as a snapshot (Character.race_info, JSON text): a catalog change never changes the taken copy.
of_race(ch, rid) lists everything with the source race:<rid> (the change-race confirmation list).
"""
import json
from dataclasses import replace

from wp.catalog import convert
from wp.core import rerolls as rr
from wp.core.damage import Pool
from wp.core.effects import OneShot, Status
from wp.core.triggers import Trigger
from wp.model import race_languages as rl
from wp.model.character import Feat, ResourcePool, Usage
from wp.model.notebook import Quirk

SOURCE = "race:"
COLLECTIONS = (("feats", "fid"), ("statuses", "sid"), ("pools", "pid"), ("quirks", "kid"), ("languages", "lid"))


def source_of(rid):
    return SOURCE + rid


def snapshot(ch):
    """The taken race entry (a dict) or {}."""
    return json.loads(ch.race_info) if ch.race_info else {}


def _triggers(d):
    return tuple(Trigger(**{k: (dict(v) if k == "params" else v) for k, v in dict(t).items()})
                 for t in d.get("triggers", ()))


def _effects(d):
    return tuple(convert.effect(e) for e in d.get("effects", ()))


def auto(a):
    """An ability taken with the race: no price and not marked "auto": false (a Mordon history is taken by choice)."""
    return bool(a.get("auto", not int(a.get("price", 0))))


STATUS_FIELDS = ("per_tick_hp", "charge_source", "charge_per_round", "full_ticks", "source_ref", "temp_hp_stacks")


def _usage(a):
    """The charges of an ability and their recharge rule (package 37 P2.1): {"charges": N, "recharge": rule}."""
    u = a.get("usage")
    if not u:
        return None
    n = int(u.get("charges", 0))
    return Usage(charges_max=n, charges_current=n, recharge=u.get("recharge", "manual"))


def ability_feat(rid, a):
    return Feat(fid=a["id"], title=a.get("name", a["id"]), source=source_of(rid), cost=int(a.get("price", 0)),
                effects=_effects(a), triggers=_triggers(a), text=a.get("text", ""), needs=a.get("needs", ""),
                held_by=a.get("held_by", ""), usage=_usage(a), rerolls=rr.from_data(a.get("rerolls")))


def _status(rid, d):
    charges = d.get("charges")
    extra = {k: d[k] for k in STATUS_FIELDS if k in d}
    if "one_shot" in d:                # e.g. 2 temp HP for one tick (Heavy swing, package 37)
        extra["one_shot"] = tuple(OneShot(o["resource"], int(o["amount"])) for o in d["one_shot"])
    return Status(name=d.get("name", d["id"]), sid=d["id"], effects=_effects(d), active=False, source=source_of(rid),
                  duration=d.get("duration", "infinite"), note=d.get("text", ""), triggers=_triggers(d),
                  charges=Pool(int(charges), int(charges)) if charges else None,
                  rerolls=rr.from_data(d.get("rerolls")), **extra)


def copies(entry, ch):
    """{collection: records to add, "base_speed": feet, "languages": records} for the race entry."""
    rid = entry["id"]
    base = Feat(fid="race_" + rid, title=entry.get("name", rid), source=source_of(rid), cost=0,
                effects=_effects(entry), text=entry.get("text", ""))
    feats = (base,) + tuple(ability_feat(rid, a) for a in entry.get("abilities", ()) if auto(a))
    statuses = tuple(_status(rid, d) for d in entry.get("statuses", ()))
    pools = tuple(ResourcePool(p["id"], p.get("name", p["id"]), p.get("max", 0), int(p.get("current", 0)),
                               p.get("restore", "manual"), source_of(rid)) for p in entry.get("pools", ()))
    quirks = tuple(Quirk(q["id"], q.get("name", q["id"]), text=q.get("text", ""), effects=_effects(q),
                         source=source_of(rid), rerolls=rr.from_data(q.get("rerolls")))
                   for q in entry.get("quirks", ()))
    langs = rl.languages(entry.get("languages", ()), ch.languages)
    return {"feats": feats, "statuses": statuses, "pools": pools, "quirks": quirks, "languages": langs,
            "base_speed": entry.get("speed")}


def of_race(ch, rid):
    """((collection, id, name), ...) of everything with the source race:<rid> (+ the languages the race gave)."""
    src, out = source_of(rid), []
    for coll, key in COLLECTIONS[:-1]:
        for r in getattr(ch, coll):
            if getattr(r, "source", "") == src:
                out.append((coll, getattr(r, key), getattr(r, "title", "") or getattr(r, "name", "")))
    given = snapshot(ch).get("_languages_given", ())
    out += [("languages", lg.lid, lg.name) for lg in ch.languages if lg.lid in given]
    return tuple(out)


def without(ch, rid):
    """The character without the race's entries."""
    gone = {(c, i) for c, i, _ in of_race(ch, rid)}
    fields = {}
    for coll, key in COLLECTIONS:
        fields[coll] = tuple(r for r in getattr(ch, coll) if (coll, getattr(r, key)) not in gone)
    return replace(ch, **fields)


def with_race(ch, entry, default_speed):
    c = copies(entry, ch)
    snap = dict(entry)
    snap["_languages_given"] = [lg.lid for lg in c["languages"]]
    taken = {f.fid for f in ch.feats}
    return replace(ch, feats=ch.feats + tuple(f for f in c["feats"] if f.fid not in taken),
                   statuses=ch.statuses + c["statuses"], pools=ch.pools + c["pools"], quirks=ch.quirks + c["quirks"],
                   languages=ch.languages + c["languages"], race_id=entry["id"],
                   race_info=json.dumps(snap, ensure_ascii=False, sort_keys=True),
                   base_speed=int(c["base_speed"]) if c["base_speed"] is not None else int(default_speed))


def ability(ch, aid):
    return next((a for a in snapshot(ch).get("abilities", ()) if a["id"] == aid), None)


def view(ch):
    """The race view: id, name, module, type tags, speed, the race effects, the abilities (id, name, text, price,
    needs, taken) and the languages."""
    snap = snapshot(ch)
    if not snap:
        return {"race_id": "", "name": "", "module": "", "abilities": (), "effects": (), "languages": (),
                "type_tags": (), "speed": None}
    taken = {f.fid for f in ch.feats}
    base = next((f for f in ch.feats if f.fid == "race_" + snap["id"]), None)
    return {"race_id": snap["id"], "name": snap.get("name", snap["id"]), "module": snap.get("module", ""),
            "type_tags": tuple(snap.get("type_tags", ())), "speed": snap.get("speed"),
            "effects": tuple((e.target, e.value, e.note) for e in (base.effects if base else ())),
            "abilities": tuple((a["id"], a.get("name", a["id"]), a.get("text", ""), int(a.get("price", 0)),
                                a.get("needs", ""), a["id"] in taken) for a in snap.get("abilities", ())),
            "module_name": snap.get("name_en", ""),
            "languages": tuple((lg.name, lg.native) for lg in ch.languages
                               if lg.lid in snap.get("_languages_given", ()))}
