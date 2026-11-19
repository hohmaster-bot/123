"""Stances (RULES/combat.md "Stances", package 12, Q74). Computed on read (D6).

A stance is a FEAT with is_stance = True. The character has one active stance (Character.active_stance:
a feat id or None). A stance feat's effects apply ONLY while it is the active stance; ordinary feats
always apply (derived_view.feat_bonuses). No lock and no combat rule: the player switches it with
set_active_stance; end_combat does not change it. Stances are NOT statuses in the container.
"""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class StanceEntry:
    fid: str
    title: str
    active: bool


@dataclass(frozen=True)
class StanceView:
    stances: Tuple[StanceEntry, ...]
    active: Optional[str]


def feat_applies(ch, feat):
    """Ordinary feat: always. Stance feat: only while it is the active stance."""
    return not feat.is_stance or ch.active_stance == feat.fid


def stance_view(ch):
    active = ch.active_stance if any(f.fid == ch.active_stance and f.is_stance for f in ch.feats) else None
    return StanceView(stances=tuple(StanceEntry(f.fid, f.title or f.fid, f.fid == active)
                                    for f in ch.feats if f.is_stance),
                      active=active)
