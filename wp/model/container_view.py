"""Status container view (RULES/buffs.md "Status container", package 11 A). Computed on read (D6).

One list of every status-like entry of the character, ready for the UI:
  - kind "status": entries of Character.statuses (managed by activate_status / remove_status /
    delete_status / set_status_hidden / set_status_favorite / add_status);
  - kind "injury": injuries (read only here: they work as injuries.md says, Q1);
  - kind "item": effects of a worn / held item's acting tab (read only: tied to item activation, Q2).
favorites = ids of status entries marked favorite. "hidden" is display only.
"""
from dataclasses import dataclass
from typing import Optional, Tuple

from wp.core.effects import Effect
from wp.model import derived_view as dv
from wp.model import ids

STATUS = "status"
INJURY = "injury"
ITEM = "item"


@dataclass(frozen=True)
class Entry:
    kind: str
    eid: str                           # status sid / "injury:<n>" / item iid
    name: str
    source: str
    active: bool
    duration: str = ""
    remaining: int = 0
    full_ticks: int = 0
    charges: Optional[Tuple[int, int]] = None    # (current, max)
    hidden: bool = False
    favorite: bool = False
    condition_tag: str = "none"
    manageable: bool = False           # True only for kind "status" (the status commands act on it)
    effects: Tuple[Effect, ...] = ()   # the entry's effects (statuses, injuries: package 14 D)


@dataclass(frozen=True)
class ContainerView:
    entries: Tuple[Entry, ...]
    favorites: Tuple[str, ...]


def _status_entry(s):
    return Entry(kind=STATUS, eid=s.sid, name=s.name, source=s.source, active=s.active, duration=s.duration,
                 remaining=s.remaining, full_ticks=s.full_ticks,
                 charges=(s.charges.current, s.charges.max) if s.charges is not None else None,
                 hidden=s.hidden, favorite=s.favorite, condition_tag=s.condition_tag, manageable=True,
                 effects=s.effects)


def _injury_entries(ch):
    # stable injury ids (package 12, Q70); an injury built by hand without an id gets one here for the view
    return tuple(Entry(kind=INJURY, eid=j.jid, name=j.name or j.severity, source="injury",
                       active=True, charges=(j.charges.current, j.charges.max) if j.charges.max else None,
                       effects=j.effects)
                 for j in ids.with_injury_ids(ch.injuries, ch.injury_counter)[0])


def _item_entries(ch):
    out = []
    for it in ch.items:
        if not (it.equipped or it.in_hands):
            continue
        tab = dv.item_tab(it, dv.picks(ch, it))
        if tab:
            out.append(Entry(kind=ITEM, eid=it.iid, name=it.name, source="item", active=True,
                             condition_tag=it.condition_tag))
    return tuple(out)


def container_view(ch):
    statuses = tuple(_status_entry(s) for s in ch.statuses)
    return ContainerView(entries=statuses + _injury_entries(ch) + _item_entries(ch),
                         favorites=tuple(e.eid for e in statuses if e.favorite))
