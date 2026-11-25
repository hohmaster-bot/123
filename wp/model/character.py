"""Character sheet as frozen data. Only BASE values are stored (D6, D18);
everything derived (HP max, BP max, balance max, AC, load, pain total...) is
computed on read in derived_view.py. Every entity has a stable id (D7).

Changes go only through wp.commands (D5): they return a NEW Character.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from wp.core.damage import Pool
from wp.core.effects import Effect, Status
from wp.core.frozen import freeze_fields
from wp.core.injuries import Injury
from wp.core.pain import PainEntry, PainProfile
from wp.core.rest import Charge
from wp.core.skills import Skill
from wp.core.statuses import NegativeTraits
from wp.core.weapons import Pick, Weapon
from wp.model.class_types import ClassInfo, HiddenProperty, SpellDamage
from wp.model.experience import LevelRecord, XpEntry
from wp.model.notebook import Court, Drive, Lens, Quest, Quirk, Story
from wp.model.template import Template
from wp.rules_data import rules as rd

ABILITIES = ("str", "dex", "con", "int", "wis", "cha")
DICT_FIELDS = ("abilities", "slots", "resources", "save_base", "save_stats", "char_settings", "save_override",
               "attack_sources")


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
class Usage:
    """Charges and cooldown of a usable thing (item, feat, attack record, maneuver; gear.md, package 14 B)."""
    charges_max: int = 0
    charges_current: int = 0
    recharge: str = "manual"           # short_rest / long_rest / combat_start / manual
    cooldown_rounds: int = 0           # spending starts this cooldown
    cooldown_current: int = 0          # rounds left; the tick lowers it by 1


@dataclass(frozen=True)
class Item:
    iid: str                           # stable id
    name: str
    kind: str = ""                     # WEAPON / SHIELD / MISC / AMMO / "" (worn gear, bag item)
    equipped: bool = False             # worn on the doll (armor, ring, belt...)
    in_hands: bool = False             # held in the hands slot (weapon, shield, special item)
    hands: int = 0                     # hands needed in the hands slot: 0, 1 or 2 (gear.md)
    hand: str = ""                     # chosen hand while held: "left" / "right" ("" = by order, model/hands.py)
    carried: bool = True               # False = left at the base (no weight)
    armor: int = 0                     # worn armor bonus
    shield: int = 0                    # shield bonus to AC: only while in hands (gear.md)
    shield_type: str = ""              # shield card: "light" / "heavy" / "tower" ("" = not a shield)
    natural: int = 0
    max_dex: Optional[int] = None
    skill_penalty: int = 0             # armor penalty to Str/Dex skills (gear.md "Armor"), e.g. -2
    armor_type: str = ""               # armor category: "light" / "medium" / "heavy" (proficiency rank 1/2/3)
    touch_bonus: int = 0               # armor bonus to TOUCH AC only (catalog column "touch AC"), worn armor
    spell_penalty_mana: int = 0        # extra mana cost of every mana spell while worn / held (>= 0)
    spell_failure_pct: int = 0         # spell failure chance while worn / held, 0..100
    speed_penalty_ft: int = 0          # armor slowdown in ft (body_view.armor_slowdown, gear.md)
    durable: Optional[bool] = None     # loses at most 1 HP per attack; None = default (armor/shield yes)
    condition_tag: str = "none"        # display only: none / combat_only / out_of_combat_only
    weight_l: int = 0
    quantity: int = 1                  # how many (weight = unit weight * quantity; gear.md "Consumables", pkg 13 D)
    consumable: bool = False           # used up by use_consumable; at quantity 0 "spent" (grey, weight 0)
    on_use_status: str = ""            # status id activated when the consumable is used
    usage: Optional[Usage] = None      # charges and cooldown of the item (package 14 B, Q94)
    effects_off: Tuple[Effect, ...] = ()   # tab "not activated" (D17)
    effects_on: Tuple[Effect, ...] = ()    # tab "activated" (D17)
    activated: bool = False
    activation_day: int = 0            # spirit price for "day" (until the short rest); 0 = not set
    activation_decade: int = 0         # spirit price for "decade" (until the long rest); 0 = not set
    active_until: str = ""             # state while activated: "short" / "long"
    # weapon card (owner's table)
    groups: Tuple[str, ...] = ()       # weapon groups this weapon belongs to (any number)
    wkind: str = ""                    # weapon kind id = the catalog card id (a maneuver tag, package 12 B)
    required_level: int = 0            # qualification level (weapons.md), from the card's qualification
    qualification: str = ""            # qualification as written in the owner's table
    qualification_n: int = 0           # item qualification "Qualification N" (gear.md); 0 = none needed
    qualified: bool = False            # bought for 50 * N (package 15); level = qualification_n when bought
    hidden_properties: Tuple[HiddenProperty, ...] = ()   # unlocked by the qualification (package 25 D, Q109)
    finesse: bool = False              # column "F." of the table: finesse AND light (one flag, owner)
    price_sp: int = 0                  # price in silver (1 gp = 10 sp)
    damage_small: str = ""             # dice, small size
    damage_medium: str = ""            # dice, medium size
    crit_range: int = 20               # lowest d20 that threatens
    crit_mult: int = 2
    keen: bool = False                 # property "keen": doubles the BASE crit range (combat.md)
    range_ft: int = 0
    dmg_type: str = ""                 # P / S / B
    durability: int = 0                # hardness (HD) typed by the author (base)
    hp: int = 0                        # item HP typed by the author (base)
    masterwork: bool = False           # masterwork (any item, activated or not): weapon +1 attack
                                       # (enhancement), armor/shield skill penalty -1 smaller (items.py)
    enchant: int = 0                   # enchantment level N (gear.md): weapon +N attack/damage/lucky,
                                       # armor/shield +N bonus; all: hardness +2N, item HP +N
    hp_current: Optional[int] = None   # CURRENT item HP (None = at max); see wp/model/items.py
    destroyed: bool = False            # HP went below 0: destroyed for good (grey, cannot be activated)
    damage_small2: str = ""            # double weapon: second row (the other end)
    damage_medium2: str = ""
    double: bool = False               # double weapon (quarterstaff): two damage rows, one per end
    no_parry: bool = False             # cannot parry with it (spiked gauntlets = parry with an empty hand)
    damage_text: str = ""              # damage as written in the table when it is not a simple small/medium pair
    variable: Tuple[str, ...] = ()     # fields the table gives as "Vary." (left empty on purpose)
    attack_kind: str = "melee"         # weapon card: melee / ranged / thrown (package 17, attack_kind.py)
    slot: str = ""                     # doll slot id (wp/catalog/data/doll_slots.json); "" = no slot (package 16 E)
    ilvl: Optional[int] = None         # item level ILVL (doll.md); None = not given (package 21, Q133)
    base_slot_cost: int = 1            # base slots taken while left at the base (gear.md "Base"; grey items 0)
    source: str = ""                   # where it came from (loot, shop, template:<id>...), a label


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
    main_hand: str = ""                # left / right: the hand this record is the MAIN hand for ("" = hands.main_default)
    usage: Optional[Usage] = None      # charges and cooldown (package 14 B)
    iterative_step: Optional[int] = None   # own iterative step (e.g. -3); None = rules_settings (package 16 C)
    cost_reactions: int = 0            # reactions spent by use_attack (attack of opportunity...; package 22 A2)
    cost_actions: int = 0              # shown only: the player presses spend_actions (package 26 A)
    kind: str = ""                     # melee / ranged / thrown; "" = the weapon card's attack_kind (package 17)
    damage_stat: Optional[str] = None  # "none" or a stat id; None = the kind's default (stat = the attack stat)
    damage_mult: Any = None            # multiplier of the damage stat; None = the kind's default / the grip


@dataclass(frozen=True)
class Maneuver:
    """Character-level maneuver (combat.md "Maneuver list", package 12 B). Costs are RECORD ONLY:
    nothing is spent automatically. extra keeps unknown future keys on save/load, never read."""
    mid: str                           # stable id (made from the name)
    name: str
    description: str = ""
    required_tags: Tuple[str, ...] = ()   # weapon group ids, weapon kind ids, the special tag "unarmed"
    tag_mode: str = "any"              # "any" (default) / "all"
    to_hit: int = 0                    # added to the weapon's main attack, this maneuver only
    damage: int = 0
    effects: Tuple[Effect, ...] = ()   # typed effects on this maneuver's attack only
    cost_actions: int = 0
    cost_balance: int = 0
    cost_spirit: int = 0
    cost_reactions: int = 0            # record + availability check (package 22 A2)
    required_feat: str = ""            # feat id; unavailable unless the feat is owned
    condition_tag: str = "none"        # display only
    favorite: bool = False
    source: str = ""                   # free label: style / class / feat
    notes: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)
    usage: Optional[Usage] = None      # charges and cooldown (package 14 B)

    def __post_init__(self):
        freeze_fields(self, ("extra",))


@dataclass(frozen=True)
class RulesSettings:
    """Rule switches as DATA (RULES/resources.md "Rule switches", package 14 G). Every NEW rule constant or
    switch goes here instead of code (owner goal: full control over bonuses and rules through settings)."""
    ignore_pain: bool = False          # pain gives no penalties (the pain count itself stays)
    ignore_negative_morale: bool = False   # a negative morale scale counts as 0
    speed_multiplier: Any = 1          # derived speed = floor(speed * multiplier)
    rest_regen_multiplier: Any = 1     # HP regenerated by a rest: floor(gain * multiplier) + bonus
    rest_regen_bonus: int = 0
    hp_regen_per_tick: int = 0         # HP healed every zero-initiative tick
    overload_enabled: bool = True      # False: the overload counter is never applied and never blocks regen
    log_limit: int = 0                 # journal: keep the last N entries (0 = unlimited, package 14 H)
    iterative_step: int = -5           # iterative attack penalty per step (combat.md, package 16 C)
    ranged_attack_stat: str = "dex"    # attack kinds (combat.md, package 17): defaults per kind
    ranged_damage_stat: str = "none"
    ranged_damage_mult: Any = 1
    thrown_attack_stat: str = "dex"
    thrown_damage_stat: str = "str"
    thrown_damage_mult: Any = 1
    damage_order: Tuple[str, ...] = ("percent", "flat", "modifier")   # damage steps (defense.md, package 17)
    constants: Dict[str, Any] = field(default_factory=dict)   # rule constant overrides {id: value} (package 20, D23)

    def __post_init__(self):
        freeze_fields(self, ("constants",))


@dataclass(frozen=True)
class ResourcePool:
    """Character-level resource pool (Ki-like; resources.md "Resource pools", package 13 C)."""
    pid: str                           # stable id (made from the name)
    name: str
    max: Any = 0                       # a number or a formula string (buffs.md "Formulas", package 14 C)
    current: int = 0                   # stored and shown as is (above the max allowed, package 16 A6)
    restore: str = "manual"            # short_rest / long_rest / combat_start / manual: restores to max
    source: str = ""                   # "template:<id>" when a template added it (package 16 G6)


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
class Seed:
    """A seed in the Quirks tab (training.md "Seeds"): bought for 200, sprouted for 200 (package 15)."""
    sid: str
    name: str
    sprouted: bool = False


@dataclass(frozen=True)
class SpellUpgrade:
    """One spell mastery upgrade (progression.md "Spell mastery"): slots it takes, metamagic circles (0 = none)."""
    name: str
    slots: int = 1
    metamagic: int = 0


@dataclass(frozen=True)
class Spell:
    """A learned spell (package 15; a minimal record: the spell list itself is a later package)."""
    spid: str
    name: str
    circle: int = 0
    source: str = "training"
    cost: int = 0
    upgrades: Tuple[SpellUpgrade, ...] = ()
    damage: Tuple[SpellDamage, ...] = ()   # damage components (package 25 F)
    cost_actions: int = 0              # shown only (package 26 A)


@dataclass(frozen=True)
class Feat:
    fid: str                           # catalog template id (stable)
    title: str = ""
    flags: Tuple[str, ...] = ()        # copied from the template, e.g. ("finesse",)
    source: str = "training"
    cost: int = 0
    condition_tag: str = "none"        # display only: none / combat_only / out_of_combat_only
    effects: Tuple[Effect, ...] = ()   # permanent while the feat is owned (same structure as statuses)
    usage: Optional[Usage] = None      # charges and cooldown (package 14 B)
    granted_maneuvers: Tuple[str, ...] = ()   # maneuver ids (used from package 12)
    is_stance: bool = False            # a stance: its effects apply only while it is the active stance (Q74)
    cost_reactions: int = 0            # reactions the feat's use costs: a record (package 22 A2)


@dataclass(frozen=True)
class LogEntry:
    """Journal entry (package 14 H): ids and numbers only, no texts."""
    seq: int = 0                       # order counter (Character.log_seq)
    command: str = ""                  # command id
    kind: str = ""                     # item / spell / damage / heal / status / charges / rest / injury / stance / combat / other
    params: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    round: int = 0                     # combat round (0 = not in combat)
    at: str = ""                       # time stamp of the Session clock (package 27 E; "" without a Session)

    def __post_init__(self):
        freeze_fields(self, ("params", "result"))


@dataclass(frozen=True)
class Character:
    level: int = 1
    bab: int = 0                       # base attack bonus (base value, class progression by hand)
    abilities: Dict[str, Ability] = field(default_factory=lambda: {a: Ability() for a in ABILITIES})
    # HP: hit die results entered by hand (progression.md)
    hp_rolls: Tuple[int, ...] = (rd.default("new.hit_die"),)   # hit-die HP per level: level 1 = the die max
    hit_die: int = rd.default("new.hit_die")   # class hit die (cap for each roll and for training HP)
    hp_race: int = 0                   # race bonus to max HP (may be 0)
    hp_bonus: int = 0                  # other bonuses to max HP (feats, class, quirks, items)
    hp_current: int = rd.default("new.hit_die")
    temp_hp: int = 0
    # balance / BP (maxima derived)
    balance_current: int = 0
    balance_bonus: int = 0             # race, class, other
    balance_regen_bonus: int = 0
    bp_current: int = 0                # may be above max: "overcap" (narrative BP...), package 8 C
    bp_bonus: int = 0
    # spirit: max derived (5 + 5 * Cha mod, min 0, + bonuses by source)
    spirit_current: int = 0
    spirit_bonuses: Tuple[Tuple[str, int], ...] = ()
    # pools with a max typed by hand (class tables)
    mana: Pool = Pool(0, 0)
    mana_enabled: bool = False
    caster: Optional[str] = None       # magic.MAGE / magic.SLOTS / None
    divine_slots: bool = False         # slots are divine casts (short rest option "divine casts")
    spell_failure_mode: str = ""       # "cancel" / "zero_balance"; "" = default (divine: zero_balance)
    slots: Dict[int, Pool] = field(default_factory=dict)
    resources: Dict[str, Pool] = field(default_factory=dict)
    charges: Tuple[Charge, ...] = ()
    comfort_current: int = 0
    comfort_bonus: int = 0
    attention: int = 0                 # no maximum (narrative.md)
    attention_course: int = 0          # +1 per 200 training: adds to every attention conversion (package 15)
    drives: Tuple[Drive, ...] = ()     # narrative drives, level 0..5 (package 16 F)
    quests: Tuple[Quest, ...] = ()
    stories: Tuple[Story, ...] = ()
    courts: Tuple[Court, ...] = ()
    quirks: Tuple[Quirk, ...] = ()
    lenses: Tuple[Lens, ...] = ()
    templates: Tuple[Template, ...] = ()   # ability sources with effects, dice, feats, pools, statuses (pkg 16 G6)
    base_points_tenths: int = 0        # fractional base points from attention option 4, in tenths (10 = 1 slot)
    # pain, trauma, overload
    pain: Tuple[PainEntry, ...] = ()
    pain_profile: PainProfile = PainProfile()
    trauma: int = 0
    overload: int = 0
    absorbers: Tuple[str, ...] = ()    # temp-HP analogs in order, e.g. ("mana",)
    # states
    statuses: Tuple[Status, ...] = ()
    injuries: Tuple[Injury, ...] = ()
    injury_counter: int = 0            # last number used in an injury id; never goes down (Q75)
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
    maneuvers: Tuple[Maneuver, ...] = ()
    pools: Tuple[ResourcePool, ...] = ()   # resource pools (package 13 C)
    rules_settings: RulesSettings = RulesSettings()   # rule switches as data (package 14 G)
    char_settings: Dict[str, Any] = field(default_factory=dict)   # character-bound settings (package 19, D13)
    balance_cap_hits: int = 0          # hits this combat that lowered the balance cap (homerule)
    balance_cap_start: Optional[int] = None   # balance cap taken at start_combat (snapshot); None = live
    ov: int = 0                        # time points (OV), no cap
    languages: Tuple[Language, ...] = ()
    reactions: int = rd.default("new.reactions")   # +1 reaction for 200 * the new number (package 15)
    reactions_current: Optional[int] = None   # reactions left this round; None = all (package 22 A2)
    actions_current: Optional[int] = None     # actions left this turn; None = all (package 26 A)
    seeds: Tuple[Seed, ...] = ()
    spells: Tuple[Spell, ...] = ()
    professionalism_bought: bool = False   # the 300-point professionalism option (package 15, Q29)
    shield_grade: str = "none"
    armor_grade: str = "none"
    training: int = rd.default("training.start")
    base_slots: int = rd.default("training.base_start")
    size: str = "medium"               # race size: small / medium / large (mods derived, combat.md)
    base_speed: int = rd.default("speed.base_ft")   # race base speed in feet (derived = base + bonuses)
    save_base: Dict[str, int] = field(default_factory=lambda: {"fort": 0, "ref": 0, "will": 0})  # class table, by hand
    save_stats: Dict[str, str] = field(default_factory=lambda: {"fort": "con", "ref": "dex", "will": "wis"})
    active_stance: Optional[str] = None   # feat id of the active stance (combat.md "Stances", Q74)
    ignore_bag_weight: bool = False    # bag weight not counted (gear.md "drop bag" button, package 8 E)
    log: Tuple[LogEntry, ...] = ()
    log_seq: int = 0                   # last journal order number (package 14 H)
    combat_round: int = 0              # 1 at start_combat, +1 per tick in combat, 0 out of combat
    iterative_count: int = 0           # attacks used in this round's series (package 16 C); tick / end_combat: 0
    class_id: str = ""                 # one class (package 25 B); "" = no class: BAB / saves typed by hand as before
    class_info: Optional[ClassInfo] = None   # snapshot of the class catalog entry (set_class)
    bab_override: Optional[int] = None # with a class: a hand-typed BAB wins over the class value
    save_override: Dict[str, int] = field(default_factory=dict)   # with a class: hand-typed base saves win
    attack_sources: Dict[str, str] = field(default_factory=dict)  # melee / ranged -> stat id or "record:<rid>" (pkg 30)
    favorites: Tuple[str, ...] = ()    # favourite abilities "kind:id" (feat / item / attack / maneuver / spell, pkg 30)
    xp_log: Tuple[XpEntry, ...] = ()   # experience entries (package 26 C); the total is derived
    xp_counter: int = 0                # last experience / level history id number (never reused)
    level_history: Tuple[LevelRecord, ...] = ()   # written by level_up

    def __post_init__(self):
        # dict fields are read-only mappings (package 16 A7): no in-place change without a command
        freeze_fields(self, DICT_FIELDS)

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
