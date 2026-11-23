"""AC cells of a character (package 23 D): every cell with Full and Parry (RULES/ac_zones.md). The shield type is
the held shield's shield_type ("" = no type: covers like light / heavy / tower); the hand is the left one until the
sheet stores which hand holds the shield (assumption Q156)."""
from wp.core import ac_zones as acz
from wp.model import derived_view as dv
from wp.model import records as rec


def shield_type(ch):
    return next((it.shield_type for it in ch.items if it.in_hands and rec.is_shield(it)), "")


def cells(ch, shield_enabled=True, hand=acz.LEFT):
    return acz.all_cells(dv.ac_input(ch, shield_enabled=shield_enabled), shield_type(ch), hand)
