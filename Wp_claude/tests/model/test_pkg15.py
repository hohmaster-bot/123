"""Package 15: Q95 per-round payment, the missing purchase / progression commands.
Expected numbers are computed by hand from RULES (training.md, progression.md, injuries.md, skills.md, weapons.md).
Run: python Wp_claude/tests/model/test_pkg15.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.catalog import skills_catalog as sc  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import skills as sk  # noqa: E402
from wp.core import weapons as wpn  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.injuries import Injury  # noqa: E402
from wp.core.weapons import Weapon  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import (ABILITIES, Ability, Character, Item, Language, ResourcePool,  # noqa: E402
                                WeaponEntry)
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg15")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def refused(ch, name, /, **kw):
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return "refused: " + str(e)
    return "allowed"


def abil(**scores):
    return {a: Ability(base=scores.get(a, 10)) for a in ABILITIES}


def hero(**kw):
    base = dict(hp_rolls=(8,), hp_current=8, spirit_current=5, balance_current=5, bp_current=2, training=1000)
    base.update(kw)
    return Character(**base)


def spent(ch, *steps):
    return ch.training - run(ch, *steps).training


# ================================================================ A. Q95
def aura(duration, full):
    st = Status("aura", sid="aura", effects=(Effect(bo.ATTACK, 2),), per_tick_hp=1, charge_source="ki",
                charge_per_round=1, duration=duration, full_ticks=full, active=False)
    return run(hero(hp_current=4, pools=(ResourcePool("ki", "Ki", 5, 5),), statuses=(st,)), ("activate_status", {"sid": "aura"}))


def _rounds(c, n):
    out = []
    for _ in range(n):
        c = run(c, ("tick", {}))
        out.append((c.statuses[0].active, c.pools[0].current, c.hp_current))
    return out


S.case("a-aura-3", "buffs.md [OWNER pkg 15, Q95]: aura 3 rounds at 1 Ki costs exactly 3 (5 -> 4 at activation, 3, 2, "
       "the 3rd tick ends it without paying); it heals on ticks 1-3", (4, [(True, 3, 5), (True, 2, 6), (False, 2, 7)]))(
    lambda: (lambda c: (c.pools[0].current, _rounds(c, 3)))(aura(ef.TICKS, 3)))
S.case("a-aura-1", "buffs.md: duration 1 costs 1 at activation; it acts in its round (+2 attack now) and ends at the first "
       "tick without paying (it still heals once)", (4, 2, [(False, 4, 5)]))(
    lambda: (lambda c: (c.pools[0].current, dv.total(c, bo.ATTACK), _rounds(c, 1)))(aura(ef.TICKS, 1)))
S.case("a-infinite-pays", "buffs.md: without a duration every tick pays (5 -> 4 -> 3 -> 2)", [(True, 3, 5), (True, 2, 6)])(
    lambda: _rounds(aura(ef.INFINITE, 0), 2))

# ================================================================ B1 level_up
S.case("b1-level-up", "progression.md: level 1 -> 2: training +100 * 2 = 200 (1000 -> 1200), roll 5 added (8, 5)",
       (2, 1200, (8, 5)))(lambda: (lambda c: (c.level, c.training, c.hp_rolls))(run(hero(), ("level_up", {"hp_roll": 5}))))
S.case("b1-level-up-3", "progression.md: level 2 -> 3 gives +300", 300)(
    lambda: -spent(hero(level=2, hp_rolls=(8, 5)), ("level_up", {"hp_roll": 4})))
S.case("b1-refusals", "progression.md: the roll is needed and must be 1..die (d8)",
       ("refused: give the hit-die roll for the new level (1..8)", "refused: hit-die roll must be 1..8",
        "refused: hit-die roll must be 1..8"))(
    lambda: (refused(hero(), "level_up"), refused(hero(), "level_up", hp_roll=0), refused(hero(), "level_up", hp_roll=9)))

# ================================================================ B2 comfort exchange
S.case("b2-exchange", "training.md: level 2, 2 comfort -> 2 * (2 + 1) * 5 = 30 training; comfort 3 -> 1", (30, 1))(
    lambda: (lambda c: (c.training - 1000, c.comfort_current))(
        run(hero(level=2, comfort_current=3), ("exchange_comfort", {"n": 2}))))
S.case("b2-refuse", "training.md: more comfort than there is -> refused", "refused: not enough comfort: have 1, exchange 2")(
    lambda: refused(hero(comfort_current=1), "exchange_comfort", n=2))

# ================================================================ B3 OT removal, RL
S.case("b3-ot-comfort", "injuries.md: 2 comfort -> -6 OT (7 -> 1); OT 2 with 1 comfort -> 0 (never below 0)", (1, 0))(
    lambda: (run(hero(trauma=7, comfort_current=2), ("remove_ot_comfort", {"n": 2})).trauma,
             run(hero(trauma=2, comfort_current=1), ("remove_ot_comfort", {})).trauma))
S.case("b3-ot-comfort-refuse", "injuries.md: no OT -> refused; not enough comfort -> refused",
       ("refused: no OT to remove", "refused: not enough comfort: have 1, spend 2"))(
    lambda: (refused(hero(comfort_current=1), "remove_ot_comfort"),
             refused(hero(trauma=5, comfort_current=1), "remove_ot_comfort", n=2)))
S.case("b3-ot-attention", "injuries.md: 1 attention -> -max(2, Str mod): Str 16 (+3) 10 -> 7; Str 10 (+0) 10 -> 8", (7, 8))(
    lambda: (run(hero(trauma=10, attention=1, abilities=abil(str=16)), ("remove_ot_attention", {})).trauma,
             run(hero(trauma=10, attention=1), ("remove_ot_attention", {})).trauma))
CUT = Injury("cut", "light", 3, jid="cut_1")
S.case("b3-rl", "injuries.md: 1 attention raises RL by max(2, Str mod): light RL 3 -> 5 (Str 10); attention 1 -> 0", (5, 0))(
    lambda: (lambda c: (c.injuries[0].heal_rating, c.attention))(
        run(hero(attention=1, injuries=(CUT,)), ("raise_heal_rating", {"injury_id": "cut_1"}))))
S.case("b3-rl-refuse", "injuries.md: no attention / unknown injury -> refused", ("refused: no attention", "refused: no injury with id 'x'"))(
    lambda: (refused(hero(injuries=(CUT,)), "raise_heal_rating", injury_id="cut_1"),
             refused(hero(attention=1), "raise_heal_rating", injury_id="x")))
S.case("b3-injury-ot", "injuries.md: taking a light / medium / heavy injury removes 2 / 5 / 12 OT (existing add_injury)",
       (10, 7, 0))(
    lambda: tuple(run(hero(trauma=12), ("add_injury", {"severity": s})).trauma for s in ("light", "medium", "heavy")))

# ================================================================ B8 attention course
S.case("b8-course", "training.md: attention course 200; then 1 attention -> Con mod 0: max(2, 0) + 1 = 3 OV; OT 10 -> 7; RL 3 -> 6",
       (200, 3, 7, 6))(
    lambda: (lambda c: (1000 - c.training, run(c, ("convert_attention", {})).ov,
                        run(c, ("remove_ot_attention", {})).trauma,
                        run(c, ("raise_heal_rating", {"injury_id": "cut_1"})).injuries[0].heal_rating))(
        run(hero(attention=3, trauma=10, injuries=(CUT,)), ("buy_attention_course", {}))))

# ================================================================ B4 skills
def skilled():
    cat = sc.load_default()
    ath = sc.make_skill(cat, "athletics")
    st = sc.make_skill(cat, "stealth")
    pe = sc.make_skill(cat, "perception")
    from dataclasses import replace
    return hero(level=3, skills=(ath, replace(st, tier=sk.ADVANCED), replace(pe, tier=sk.SPECIALIZED)))


S.case("b4-advanced", "skills.md: athletics normal -> advanced: 40 + 20 * 2 others (advanced stealth + specialized perception) = 80",
       (80, sk.ADVANCED))(
    lambda: (lambda c: (1000 - c.training, next(s for s in c.skills if s.name == "athletics").tier))(
        run(skilled(), ("promote_skill", {"name": "athletics", "to_tier": sk.ADVANCED}))))
S.case("b4-specialized", "skills.md: stealth advanced -> specialized: 200 + 50 * 1 other specialized = 250", 250)(
    lambda: spent(skilled(), ("promote_skill", {"name": "stealth", "to_tier": sk.SPECIALIZED})))
S.case("b4-both", "skills.md: athletics normal -> specialized pays both: 80 + 250 = 330", 330)(
    lambda: spent(skilled(), ("promote_skill", {"name": "athletics", "to_tier": sk.SPECIALIZED})))
S.case("b4-refuse", "skills.md: the same or a lower tier is refused", "refused: stealth is already advanced")(
    lambda: refused(skilled(), "promote_skill", name="stealth", to_tier=sk.ADVANCED))
S.case("b4-cap-stays", "skills.md (Q64): after promotion the advanced rank cap stays the level (level 3: rank 4 refused)",
       "refused: normal/advanced skill ranks cannot exceed character level")(
    lambda: refused(run(skilled(), ("promote_skill", {"name": "athletics", "to_tier": sk.ADVANCED})),
                    "buy_skill_rank", name="athletics", target=4))

# ================================================================ B5 professionalism
S.case("b5-prof", "training.md: professionalism 300, class with 4 skill points -> 2 skills become specialized",
       (300, (sk.SPECIALIZED, sk.SPECIALIZED)))(
    lambda: (lambda c: (1000 - c.training, tuple(s.tier for s in c.skills if s.name in ("athletics", "stealth"))))(
        run(skilled(), ("buy_professionalism", {"skills": ("athletics", "stealth"), "class_skill_points": 4}))))
S.case("b5-counts", "training.md: 2+ / 4+ / 6+ / 8+ skill points -> 1 / 2 / 3 / 4 skills; 1 -> 0", (0, 1, 2, 3, 4))(
    lambda: tuple(__import__("wp.core.training", fromlist=["x"]).professionalism_skills(p) for p in (1, 2, 5, 6, 9)))
S.case("b5-refusals", "training.md: wrong count, too few skill points, bought twice -> refused",
       ("refused: choose exactly 2 different skills (class skill points 4)",
        "refused: professionalism needs a class with at least 2 skill points", "refused: professionalism is already bought"))(
    lambda: (refused(skilled(), "buy_professionalism", skills=("athletics",), class_skill_points=4),
             refused(skilled(), "buy_professionalism", skills=("athletics",), class_skill_points=1),
             refused(run(skilled(), ("buy_professionalism", {"skills": ("athletics",), "class_skill_points": 2})),
                     "buy_professionalism", skills=("stealth",), class_skill_points=2)))

# ================================================================ B6 spells
S.case("b6-learn", "training.md: new spell 20 + 10 * circle^2: circle 2 -> 60, with a book 30; circle 0 -> 20; circle 3 -> 110",
       (60, 30, 20, 110))(
    lambda: tuple(spent(hero(), ("learn_spell", {"name": "x", "circle": c, "discount": d}))
                  for c, d in ((2, False), (2, True), (0, False), (3, False))))
S.case("b6-learn-refuse", "classes_magic.md: circles 0..9", "refused: circle must be 0..9")(
    lambda: refused(hero(), "learn_spell", name="x", circle=10))


def _spell():
    return run(hero(training=2000), ("learn_spell", {"name": "Fire bolt", "circle": 2}))


S.case("b6-mastery", "progression.md: upgrade 25 * (1 + 4) = 125; range then range again = 1 + 2 slots (full); a third refused",
       (125, (1, 2), "refused: not enough slots: fire_bolt uses 3 of 3, the upgrade needs 3"))(
    lambda: (lambda c: (_spell().training - run(_spell(), ("buy_spell_upgrade", {"spid": "fire_bolt", "name": "range"})).training,
                        tuple(u.slots for u in c.spells[0].upgrades),
                        refused(c, "buy_spell_upgrade", spid="fire_bolt", name="range")))(
        run(_spell(), ("buy_spell_upgrade", {"spid": "fire_bolt", "name": "range"}),
            ("buy_spell_upgrade", {"spid": "fire_bolt", "name": "range"}))))
S.case("b6-metamagic", "progression.md: a metamagic of +2 circles takes 2 slots; then 1 more upgrade fits, a +2 metamagic does not",
       ((2, 1), "refused: not enough slots: fire_bolt uses 3 of 3, the upgrade needs 2"))(
    lambda: (lambda c: (tuple(u.slots for u in c.spells[0].upgrades),
                        refused(c, "buy_spell_upgrade", spid="fire_bolt", name="quicken", metamagic=2)))(
        run(_spell(), ("buy_spell_upgrade", {"spid": "fire_bolt", "name": "empower", "metamagic": 2}),
            ("buy_spell_upgrade", {"spid": "fire_bolt", "name": "range"}))))

# ================================================================ B7 combat
def _weapons(**kw):
    node = Weapon("long_swords", scale=2, difficulty=1, **kw)
    return hero(weapons=(WeaponEntry(node), WeaponEntry(Weapon("basic_simple", basic=True))))


S.case("b7-basics", "weapons.md: combat basics, scale 2 -> 100; +(5 - difficulty 1) = +4 grades (level 0 -> 4)", (100, 4))(
    lambda: (lambda c: (1000 - c.training, wpn.level(c.weapon_catalog(), "long_swords")))(
        run(_weapons(), ("buy_combat_basics", {"wid": "long_swords"}))))
S.case("b7-basics-refuse", "weapons.md: once per node; Basic/simple cannot be trained",
       ("refused: long_swords already has combat basics", "refused: group Basic/simple cannot be trained"))(
    lambda: (refused(run(_weapons(), ("buy_combat_basics", {"wid": "long_swords"})), "buy_combat_basics", wid="long_swords"),
             refused(_weapons(), "buy_combat_basics", wid="basic_simple")))
S.case("b7-maneuver", "training.md: a new maneuver costs 250 and appears in the maneuver list", (250, ("feint",)))(
    lambda: (lambda c: (1000 - c.training, tuple(m.mid for m in c.maneuvers)))(run(hero(), ("buy_maneuver", {"name": "Feint"}))))
S.case("b7-qualification", "training.md: item qualification 50 * N: N 3 -> 150, the item is qualified", (150, True))(
    lambda: (lambda c: (1000 - c.training, c.items[0].qualified))(
        run(hero(items=(Item("rod", "rod", qualification_n=3),)), ("buy_item_qualification", {"iid": "rod"}))))
S.case("b7-qualification-refuse", "training.md: no N -> refused; twice -> refused",
       ("refused: ring needs no qualification", "refused: already qualified with rod"))(
    lambda: (refused(hero(items=(Item("ring", "ring"),)), "buy_item_qualification", iid="ring"),
             refused(hero(items=(Item("rod", "rod", qualification_n=3, qualified=True),)), "buy_item_qualification", iid="rod")))

# ================================================================ B8 reactions, seeds, languages
S.case("b8-reactions", "training.md: 1 reaction -> the 2nd costs 400; the 3rd 600", (400, 600, 3))(
    lambda: (spent(hero(), ("buy_reaction", {})), spent(hero(reactions=2), ("buy_reaction", {})),
             run(hero(reactions=2), ("buy_reaction", {})).reactions))
S.case("b8-seeds", "training.md: a seed 200, sprouting 200; sprouting twice refused",
       (200, 400, True, "refused: seed seed_of_fire has already sprouted"))(
    lambda: (lambda c: (spent(hero(), ("buy_seed", {"name": "Seed of fire"})), 1000 - c.training, c.seeds[0].sprouted,
                        refused(c, "sprout_seed", seed_id="seed_of_fire")))(
        run(hero(), ("buy_seed", {"name": "Seed of fire"}), ("sprout_seed", {"seed_id": "seed_of_fire"}))))
S.case("b8-native", "training.md: Int 14 (+2): natives 1 -> 50; natives 2 -> 100; no native yet -> free (0)", (50, 100, 0))(
    lambda: (spent(hero(abilities=abil(int=14), languages=(Language("a", "a", True), Language("b", "b"))),
                   ("make_language_native", {"lid": "b"})),
             spent(hero(abilities=abil(int=14), languages=(Language("a", "a", True), Language("c", "c", True),
                                                          Language("b", "b"))), ("make_language_native", {"lid": "b"})),
             spent(hero(languages=(Language("b", "b"),)), ("make_language_native", {"lid": "b"}))))
S.case("b8-native-refuse", "training.md: an already native language -> refused", "refused: a is already native")(
    lambda: refused(hero(languages=(Language("a", "a", True),)), "make_language_native", lid="a"))
S.case("b-free-source", "training.md: a non-training source spends nothing (reaction from race: 1000 stays)", 1000)(
    lambda: run(hero(), ("buy_reaction", {"source": "race"})).training)
S.case("b-not-enough", "training.md: not enough training -> refused", "refused: not enough training: need 400, have 100")(
    lambda: refused(hero(training=100), "buy_reaction"))
S.case("b-journal", "resources.md: purchases are logged with kind purchase / progression / ot",
       ("progression", "purchase", "ot"))(
    lambda: tuple(e.kind for e in run(hero(trauma=5, comfort_current=1), ("level_up", {"hp_roll": 3}), ("buy_reaction", {}),
                                      ("remove_ot_comfort", {})).log))
S.case("b-save-load", "D11: spells, upgrades, seeds, reactions, attention course, qualification survive save/load", True)(
    lambda: (lambda c: cio.loads(cio.dumps(c)) == c)(run(
        hero(training=3000, items=(Item("rod", "rod", qualification_n=1),)),
        ("learn_spell", {"name": "Fire bolt", "circle": 2}), ("buy_spell_upgrade", {"spid": "fire_bolt", "name": "range"}),
        ("buy_seed", {"name": "s"}), ("buy_reaction", {}), ("buy_attention_course", {}),
        ("buy_item_qualification", {"iid": "rod"}))))

if __name__ == "__main__":
    sys.exit(S.run())
