"""Records of package 25 (stored on the Character; registered in wp/storage/character_io.py).

ClassInfo: the snapshot of a class catalog entry (kind "classes") taken by set_class (like add_feat copies a feat):
the character file keeps working without the catalog; set_class again picks up catalog edits (assumption Q168).
HiddenProperty: an item property shown as "???" until the item's qualification reaches min_qualification (Q109).
SpellDamage: one damage component of a spell (no dice rolled by the app).
"""
from dataclasses import dataclass, field
from typing import Dict, Tuple

from wp.core.effects import Effect
from wp.core.frozen import freeze_fields

GOOD = "good"
MEDIUM = "medium"
POOR = "poor"
SAVES = ("fort", "ref", "will")


@dataclass(frozen=True)
class ClassInfo:
    cid: str
    name: str = ""
    hit_die: int = 0                   # 0 = keep Character.hit_die
    bab_growth: str = MEDIUM           # good / medium / poor (factor table: constant class.bab_factor)
    saves: Dict[str, str] = field(default_factory=lambda: {"fort": POOR, "ref": POOR, "will": POOR})
    class_skills: Tuple[str, ...] = ()     # skill ids (professionalism picks must be among them)
    spellbook: bool = False            # spells at half price by default (learn_spell)
    divine: bool = False               # divine caster: spell failure mode default zero_balance
    spell_failure_mode: str = ""       # "" = by the divine flag
    own_professionalism: bool = False  # the class has its own professionalism: the 300 option is refused
    notes: str = ""

    def __post_init__(self):
        freeze_fields(self, ("saves",))


@dataclass(frozen=True)
class HiddenProperty:
    hid: str
    text: str = ""
    effects: Tuple[Effect, ...] = ()
    min_qualification: int = 1
    tab: str = "base"                  # base = the "not activated" tab, activated = the "activated" tab (Q169)


@dataclass(frozen=True)
class SpellDamage:
    dice_count: str = "0"              # formula (wp/core/formula.py), may use level, e.g. "level / 2"
    die_size: int = 6
    flat: str = "0"                    # formula
    damage_type: str = ""              # one of the 12 damage types (catalog damage_types)
    area: str = "single"               # an id of the constant spells.areas
    range: str = ""                    # feet as text ("100") or a text ("touch")
    save: str = "none"                 # fort / ref / will / none
    save_effect: str = ""
