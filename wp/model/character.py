"""Character sheet as frozen data. Only BASE values are stored (D6, D18);
everything derived (HP max, BP max, balance max, AC, load, pain total...) is
computed on read in derived_view.py. Every entity has a stable id (D7).

Changes go only through wp.commands (D5): they return a NEW Character.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from wp.core.damage import Pool
from wp.core.effects import Effect, Status
from wp.core.injuries import Injury
from wp.core.pain import PainEntry, PainProfile
from wp.core.rest import Charge
from wp.core.skills import Skill
from wp.core.statuses import NegativeTraits
from wp.core.weapons import Pick, Weapon

ABILITIES = ("str", "dex", "con", "int", "wis", "cha")


@dataclass(frozen=True)
class Ability:
    """Score = base + race + other bonuses (by source). Damage lowers the current
    value, permanent damage lowers the max (stats.md). Price uses base + race."""
    base: int = 10
    race: int = 0
    bonuses: Tuple[Tuple[str, int], ...] = ()   # (source, value): items, quirks...
    damage: int = 0
    permanent: int = 0

    @property
    def score_max(self):
        return self.base + self.race + sum(v for _, v in self.bonuses) - self.permanent

    @property
    def current(self):
        return self.score_max - self.damage


@dataclass(frozen=True)
class Item:
    iid: str                           # stable id
    name: str
    equipped: bool = False
    carried: bool = True               # False = left at the base (no weight)
    armor: int = 0                     # worn armor bonus
    shield: int = 0
    natural: int = 0
    max_dex: Optional[int] = None
    weight_l: int = 0
    effects_off: Tuple[Effect, ...] = ()   # tab "not activated" (D17)
    effects_on: Tuple[Effect, ...] = ()    # tab "activated" (D17)
    activated: bool = False
    activation_cost: int = 0           # spirit to activate (0 = not activatable)
    activation_until: str = ""         # card field "active until": "short" (day) / "long" (decade);
                                       # "" = default by cost (1 -> short, 5 -> long)
    active_until: str = ""             # state while activated: which rest switches it off
    weapon_id: Optional[str] = None    # link to the weapon catalog
    durability: int = 0                # value typed by the author (base)
    hp: int = 0


@dataclass(frozen=True)
class WeaponEntry:
    """Weapon proficiency node. weapon.name is the STABLE ID (parents use ids)."""
    weapon: Weapon
    title: str = ""                    # display name
    picks: Tuple[Pick, ...] = ()


@dataclass(frozen=True)
class Language:
    lid: str                           # stable id
    name: str
    native: bool = False


@dataclass(frozen=True)
class LogEntry:
    command: str
    summary: str


@dataclass(frozen=True)
class Character:
    level: int = 1
    abilities: Dict[str, Ability] = field(default_factory=lambda: {a: Ability() for a in ABILITIES})
    # HP: hit die results entered by hand (progression.md)
    hp_rolls: Tuple[int, ...] = (8,)
    hp_bonus: int = 0
    hp_current: int = 8
    temp_hp: int = 0
    # balance / BP (maxima derived)
    balance_current: int = 0
    balance_bonus: int = 0             # race, class, other
    balance_regen_bonus: int = 0
    bp_current: int = 0
    temp_bp: int = 0
    bp_bonus: int = 0
    # spirit: max derived (5 + 5 * Cha mod, min 0, + bonuses by source)
    spirit_current: int = 0
    spirit_bonuses: Tuple[Tuple[str, int], ...] = ()
    # pools with a max typed by hand (class tables)
    mana: Pool = Pool(0, 0)
    mana_enabled: bool = False
    caster: Optional[str] = None       # magic.MAGE / magic.SLOTS / None
    slots: Dict[int, Pool] = field(default_factory=dict)
    resources: Dict[str, Pool] = field(default_factory=dict)
    charges: Tuple[Charge, ...] = ()
    comfort_current: int = 0
    comfort_bonus: int = 0
    attention: int = 0                 # no maximum (narrative.md)
    drives: Dict[str, int] = field(default_factory=dict)   # drive id -> level
    # pain, trauma, overload
    pain: Tuple[PainEntry, ...] = ()
    pain_profile: PainProfile = PainProfile()
    trauma: int = 0
    overload: int = 0
    absorbers: Tuple[str, ...] = ()    # temp-HP analogs in order, e.g. ("mana",)
    # states
    statuses: Tuple[Status, ...] = ()
    injuries: Tuple[Injury, ...] = ()
    negative_state: Optional[str] = None
    traits: NegativeTraits = NegativeTraits()
    in_combat: bool = False
    morale_scale: int = 0
    # gear, mastery, skills, training
    items: Tuple[Item, ...] = ()
    weapons: Tuple[WeaponEntry, ...] = ()
    skills: Tuple[Skill, ...] = ()
    languages: Tuple[Language, ...] = ()
    shield_grade: str = "none"
    armor_grade: str = "none"
    training: int = 1000
    base_slots: int = 5
    size_mod: int = 0
    log: Tuple[LogEntry, ...] = ()

    def ability(self, name):
        return self.abilities[name]

    def item(self, iid):
        for it in self.items:
            if it.iid == iid:
                return it
        raise KeyError("no item with id %r" % (iid,))

    def weapon_catalog(self):
        """{stable id: core Weapon} for wp.core.weapons functions."""
        return {e.weapon.name: e.weapon for e in self.weapons}
