"""A heavy character for the performance budgets (package 23 B): 100 items, 60 statuses with effects, 40 skills,
20 weapon nodes with records and maneuvers, 30 pools, 15 injuries, 10 feats, a 5000-line journal. Deterministic."""
from wp.core.damage import Pool
from wp.core.effects import Effect, Status
from wp.core.injuries import Injury
from wp.core.skills import Skill
from wp.core.weapons import Weapon
from wp.model.character import (ABILITIES, Ability, AttackRecord, Character, Feat, Item, LogEntry, Maneuver,
                                ResourcePool, WeaponEntry)

TYPES = ("enhancement", "morale", "competence", "luck", "insight", "flat")
TARGETS = ("attack", "damage", "ac", "save", "skill", "initiative", "stat:str", "stat:dex", "hp_max", "dr")


def effect(i):
    return Effect(TARGETS[i % len(TARGETS)], 1 + i % 3, "dodge" if TARGETS[i % len(TARGETS)] == "ac" and i % 2 else
                  TYPES[i % len(TYPES)])


def heavy():
    groups = tuple("g%d" % i for i in range(20))
    weapons = tuple(WeaponEntry(Weapon(g, grades=6)) for g in groups)
    items = []
    for i in range(100):
        g = groups[i % 20]
        if i < 20:
            items.append(Item("w%d" % i, "weapon %d" % i, kind="weapon", hands=1, in_hands=i < 2, groups=(g,), hp=10,
                              durability=5, effects_off=(effect(i), effect(i + 1))))
        elif i < 25:
            items.append(Item("a%d" % i, "armor %d" % i, armor=2 + i % 3, equipped=i == 20, hp=20, durability=8,
                              effects_off=(effect(i),)))
        else:
            items.append(Item("m%d" % i, "misc %d" % i, equipped=i % 4 == 0, weight_l=i % 7, effects_off=(effect(i),)))
    attacks = tuple(AttackRecord("r%d" % i, "w%d" % i, groups[i % 20]) for i in range(20))
    maneuvers = tuple(Maneuver("m%d" % i, "maneuver %d" % i, required_tags=(groups[i % 20],), to_hit=1) for i in range(20))
    statuses = tuple(Status("status %d" % i, sid="s%d" % i, effects=(effect(i), effect(i + 3)), active=True,
                            charges=Pool(1, 3) if i % 5 == 0 else None) for i in range(60))
    skills = tuple(Skill("skill%d" % i, ABILITIES[i % 6], ranks=i % 5) for i in range(40))
    pools = tuple(ResourcePool("p%d" % i, "pool %d" % i, "con_mod + level" if i % 3 == 0 else 5, 3) for i in range(30))
    injuries = tuple(Injury("cut", "light", 3, jid="cut_%d" % i, effects=(Effect("skill", -1),)) for i in range(15))
    feats = tuple(Feat("f%d" % i, title="feat %d" % i, effects=(effect(i),)) for i in range(10))
    log = tuple(LogEntry(seq=i + 1, command="tick", kind="combat", params={}, result={"n": i}) for i in range(5000))
    return Character(level=10, hp_rolls=(8,) * 10, hp_current=60, bab=10, abilities={a: Ability(base=14) for a in ABILITIES},
                     items=tuple(items), attacks=attacks, maneuvers=maneuvers, weapons=weapons, statuses=statuses,
                     skills=skills, pools=pools, injuries=injuries, injury_counter=15, feats=feats, log=log,
                     log_seq=5000, balance_current=5, bp_current=5, training=5000)
