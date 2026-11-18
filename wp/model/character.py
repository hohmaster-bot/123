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


WEAPON = "weapon"
SHIELD = "shield"
MISC = "misc"
AMMO = "ammo"


@dataclass(frozen=True)
class Item:
    iid: str                           # stable id
    name: str
    kind: str = ""                     # WEAPON / SHIELD / MISC / AMMO / "" (worn gear, bag item)
    equipped: bool = False             # worn on the doll (armor, ring, belt...)
    in_hands: bool = False             # held in the hands slot (weapon, shield, special item)
    hands: int = 0                     # hands needed in the hands slot: 0, 1 or 2 (gear.md)
    carried: bool = True               # False = left at the base (no weight)
    armor: int = 0                     # worn armor bonus
    shield: int = 0                    # shield bonus to AC: only while in hands (gear.md)
    shield_type: str = ""              # shield card: "light" / "heavy" / "tower" ("" = not a shield)
    natural: int = 0
    max_dex: Optional[int] = None
    skill_penalty: int = 0             # armor penalty to Str/Dex skills (gear.md "Armor"), e.g. -2
    weight_l: int = 0
    count: int = 1                     # pieces (ammo: bolts...)
    effects_off: Tuple[Effect, ...] = ()   # tab "not activated" (D17)
    effects_on: Tuple[Effect, ...] = ()    # tab "activated" (D17)
    activated: bool = False
    activation_day: int = 0            # spirit price for "day" (until the short rest); 0 = not set
    activation_decade: int = 0         # spirit price for "decade" (until the long rest); 0 = not set
    active_until: str = ""             # state while activated: "short" / "long"
    # weapon card (owner's table)
    groups: Tuple[str, ...] = ()       # weapon groups this weapon belongs to (any number)
    required_level: int = 0            # qualification level (weapons.md), from the card's qualification
    qualification: str = ""            # qualification as written in the owner's table
    finesse: bool = False              # column "F." of the table: finesse AND light (one flag, owner)
    price_sp: int = 0                  # price in silver (1 gp = 10 sp)
    damage_small: str = ""             # dice, small size
    damage_medium: str = ""            # dice, medium size
    crit_range: int = 20               # lowest d20 that threatens
    crit_mult: int = 2
    range_ft: int = 0
    dmg_type: str = ""                 # P / S / B
    durability: int = 0                # hardness (HD) typed by the author (base)
    hp: int = 0                        # item HP typed by the author (base)
    enchant: int = 0                   # enchantment level N (gear.md): weapon +N attack/damage/lucky,
                                       # armor/shield +N bonus; all: hardness +2N, item HP +N
    hp_damage: int = 0                 # damage the item took; current item HP = max - damage
    damage_small2: str = ""            # double weapon: second row (the other end)
    damage_medium2: str = ""
    double: bool = False               # double weapon (quarterstaff): two damage rows, one per end
    no_parry: bool = False             # cannot parry with it (spiked gauntlets = parry with an empty hand)
    damage_text: str = ""              # damage as written in the table when it is not a simple small/medium pair
    variable: Tuple[str, ...] = ()     # fields the table gives as "Vary." (left empty on purpose)


@dataclass(frozen=True)
class AttackRecord:
    """Attack record = weapon + chosen weapon group + grip + attack stat (owner)."""
    rid: str                           # stable id
    item: str                          # item iid, or "unarmed"
    group: str                         # weapon group (mastery node id) giving the bonuses
    grip: str = "one"                  # "one" / "off" / "two"
    stat: str = ""                     # attack stat; "" = default (Str, Finesse rules)
    primary: bool = False
    twf: bool = False                  # "combination of two attacks" toggle (two-weapon fighting)
    twf_off: str = ""                  # off-hand record id; "" = the other end of a double weapon


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
class Feat:
    fid: str                           # catalog template id (stable)
    title: str = ""
    flags: Tuple[str, ...] = ()        # copied from the template, e.g. ("finesse",)
    source: str = "training"
    cost: int = 0


@dataclass(frozen=True)
class LogEntry:
    command: str
    summary: str


@dataclass(frozen=True)
class Character:
    level: int = 1
    bab: int = 0                       # base attack bonus (base value, class progression by hand)
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
    feats: Tuple[Feat, ...] = ()
    attacks: Tuple[AttackRecord, ...] = ()
    balance_cap_hits: int = 0          # hits this combat that lowered the balance cap (homerule)
    ov: int = 0                        # time points (OV), no cap
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
