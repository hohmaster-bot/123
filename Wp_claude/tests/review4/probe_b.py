"""Review 4 probes, part B: rest, injuries, stats, gear, training, skills, weapons, progression, narrative,
magic, robustness (see probe_rules.py)."""
import os
import sys
from dataclasses import replace  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_common import *  # noqa: E402,F401,F403
from probe_common import Pick, Weapon  # noqa: E402,F401

# ============================================================ rest.md
@case("rest.md:6", "BP cap 11->3, 15->4, 19->5, 20->5, 21->6", (3, 4, 5, 5, 6))
def _():
    return tuple(dv.bp_max(hero(hp_rolls=(h,), hit_die=h)) for h in (11, 15, 19, 20, 21))


@case("rest.md:9", "4 max HP -> BP 1; leather 2; race +3 -> balance max 6", 6)
def _():
    c = hero(hp_rolls=(4,), hit_die=4, bp_current=1, balance_bonus=3, items=(Item("l", "leather", equipped=True, armor=2),))
    return dv.balance_max(c)


@case("rest.md:17", "overcap: 5/5 short rest -> 5; keep -> 6; long rest 7/5 -> 5; end of cycle 7/5 -> 5", (5, 6, 5, 5))
def _():
    return (run(hero(), ("short_rest", {})).bp_current, run(hero(), ("short_rest", {"keep_overcap": True})).bp_current,
            run(hero(bp_current=7), ("long_rest", {})).bp_current, run(hero(bp_current=7), ("end_cycle", {})).bp_current)


@case("rest.md:27-34", "long rest: OT, comfort, temp HP untouched; overload 0; balance to max; HP full",
      (7, 3, 4, 0, 10, 20))
def _():
    c = run(hero(hp_current=2, trauma=7, comfort_current=3, temp_hp=4, overload=3, balance_current=1), ("long_rest", {}))
    return (c.trauma, c.comfort_current, c.temp_hp, c.overload, c.balance_current, c.hp_current)


@case("rest.md:55", "level 3, HP 1/20: free +5 HP; a second heal costs 1 BP", (6, 11, 5))
def _():
    a = run(hero(level=3, hp_current=1, bp_current=5), ("short_rest", {}))
    b = run(hero(level=3, hp_current=1, bp_current=5), ("short_rest", {"spends": [(rs.OPT_HEAL, {})]}))
    return (a.hp_current, b.hp_current, b.bp_current)


@case("rest.md:44 / buffs.md:83", "short rest 'restore charges' (2 BP): rage 0/3 -> 3/3", 3)
def _():
    c = hero(statuses=(ef.Status("rage", sid="rage", charges=Pool(0, 3), active=False),))
    return run(c, ("short_rest", {"spends": [(rs.OPT_CHARGES, {})]})).statuses[0].charges.current


# ============================================================ injuries.md / stats.md
@case("injuries.md:7", "injury light/medium/heavy removes 2/5/12 OT", (10, 7, 0))
def _():
    return tuple(run(hero(trauma=12), ("add_injury", {"severity": s})).trauma for s in ("light", "medium", "heavy"))


@case("injuries.md:12", "1 comfort removes 3 OT; 1 attention removes max(2, Str mod) OT (Str 16 -> 3)", (4, 4))
def _():
    a = run(hero(trauma=7, comfort_current=2), ("remove_ot_comfort", {"n": 1})).trauma
    b = run(hero(trauma=7, attention=1, abilities=abil(str=16)), ("remove_ot_attention", {"n": 1})).trauma
    return (a, b)


@case("injuries.md:32", "after removing cut_3 a new cut is cut_4", "cut_4")
def _():
    c = hero(trauma=20)
    for _ in range(3):
        c = run(c, ("add_injury", {"severity": "light", "name": "cut"}))
    c = run(c, ("remove_injury", {"injury_id": "cut_3"}), ("add_injury", {"severity": "light", "name": "cut"}))
    return c.injuries[-1].jid


@case("injuries.md:38-39", "base RL light 3; 1 attention raises RL by max(2, Str mod) -> 5", 5)
def _():
    c = run(hero(attention=1, trauma=2), ("add_injury", {"severity": "light", "name": "cut"}))
    c = run(c, ("raise_heal_rating", {"injury_id": c.injuries[0].jid}))
    return c.injuries[0].heal_rating


@case("stats.md:9", "Str 18 drain 1 -> 17/18; short rest stat option -> 18/18", ((17, 18), (18, 18)))
def _():
    c = hero(abilities={**abil(), "str": Ability(base=18, damage=1)})
    a = (dv.ability_current(c, "str"), c.ability("str").score_max)
    b = run(c, ("short_rest", {"spends": [(rs.OPT_STAT, {"stat": "str"})]}))
    return (a, (dv.ability_current(b, "str"), b.ability("str").score_max))


# ============================================================ gear.md
@case("gear.md:25", "bag 30 + sword 20 + armor 50 + axe 15 = 115 L; flag on -> 85", (115, 85))
def _():
    items = (Item("bp", "rope", weight_l=30), Item("sw", "sword", kind="weapon", hands=1, in_hands=True, weight_l=20),
             Item("ar", "mail", equipped=True, weight_l=50), Item("ax", "axe", kind="weapon", weight_l=15))
    return (dv.carried_weight_l(hero(items=items)), dv.carried_weight_l(hero(items=items, ignore_bag_weight=True)))


@case("gear.md:30", "load thresholds Str +2: light up to 79 L, heavy up to 129 L", ("light", "heavy", "overload"))
def _():
    return tuple(dv.load_status(hero(abilities=abil(str=14), items=(Item("x", "x", weight_l=w),))) for w in (79, 129, 130))


@case("gear.md:38", "armor slowdown worn 5 ft -> 15; reduction 3 -> 18; with overload -> 5", (15, 18, 5))
def _():
    ar = Item("ar", "mail", equipped=True, armor=4, speed_penalty_ft=5)
    red = ef.Status("r", sid="r", effects=(ef.Effect(bo.SLOWDOWN_REDUCTION, 3),))
    return (dv.speed(hero(items=(ar,))), dv.speed(hero(items=(ar,), statuses=(red,))),
            dv.speed(hero(items=(ar, Item("rock", "rock", weight_l=200)))))


@case("gear.md:126", "item HP: base 10, +3, 13/13, damage 6 -> 7; off -> 5; on -> 8", (13, 7, 5, 8))
def _():
    sw = sword(hp=10, enchant=3, activation_day=1)
    c = run(hero(items=(sw,)), ("activate_item", {"iid": "sw"}))
    a = dv.item_view(c, "sw").hp_current
    c = run(c, ("damage_item", {"iid": "sw", "amount": 6}))
    b = dv.item_view(c, "sw").hp_current
    c = run(c, ("deactivate_item", {"iid": "sw"}))
    d = dv.item_view(c, "sw").hp_current
    c = run(c, ("activate_item", {"iid": "sw"}))
    return (a, b, d, dv.item_view(c, "sw").hp_current)


@case("gear.md:118", "hardness 5, +2 activated, +30% -> 11", 11)
def _():
    sw = sword(durability=5, hp=10, enchant=2, activation_day=1)
    c = hero(items=(sw,), attacks=(AttackRecord("r", "sw", "blades"),),
             weapons=(WeaponEntry(Weapon("blades", grades=12), picks=(Pick(5, "durability_30"),)),))
    return dv.item_view(run(c, ("activate_item", {"iid": "sw"})), "sw").durability


@case("gear.md:147", "notches hardness 5: 4/5/9/10 -> 0/1/1/2", (0, 1, 1, 2))
def _():
    return tuple(dispatch(hero(items=(sword(durability=5, hp=10),)), "hit_item", iid="sw", damage=d).info["notches"]
                 for d in (4, 5, 9, 10))


@case("gear.md:193", "3 potions of 5 L -> 15 L; after one use 10; at 0 spent, weight 0, still listed",
      (15, 10, (0, True, 1)))
def _():
    p = Item("p", "potion", weight_l=5, quantity=3, consumable=True)
    c = hero(items=(p,))
    a = dv.carried_weight_l(c)
    c = run(c, ("use_consumable", {"iid": "p"}))
    b = dv.carried_weight_l(c)
    c = run(c, ("use_consumable", {"iid": "p", "n": 2}))
    return (a, b, (dv.carried_weight_l(c), dv.item_view(c, "p").spent, len(c.items)))


@case("gear.md:201", "spend_charge with cooldown 2: second spend refused until 2 ticks pass", ("refused", "allowed"))
def _():
    f = Feat("f", usage=Usage(charges_max=3, charges_current=3, cooldown_rounds=2))
    c = run(hero(feats=(f,)), ("spend_charge", {"owner_kind": "feat", "owner_id": "f"}))
    a = refused(lambda: dispatch(c, "spend_charge", owner_kind="feat", owner_id="f"))
    c = run(c, ("tick", {}), ("tick", {}))
    return (a, refused(lambda: dispatch(c, "spend_charge", owner_kind="feat", owner_id="f")))


@case("doll.md:5", "each doll slot holds ONE item: a second armor can be worn at the same time (no slot model)",
      "refused", "missing feature")
def _():
    c = hero(items=(Item("a1", "mail", armor=4), Item("a2", "plate", armor=8)))
    return refused(lambda: run(c, ("equip_item", {"iid": "a1"}), ("equip_item", {"iid": "a2"})))


# ============================================================ training.md / skills.md / weapons.md / progression
@case("training.md:27", "ability 15->16 = 450 (base 13 + race 2); 17->18 = 600", (450, 600))
def _():
    a = run(hero(abilities={**abil(), "str": Ability(base=13, race=2)}), ("buy_ability", {"name": "str"}))
    b = run(hero(abilities={**abil(), "str": Ability(base=15, race=2)}), ("buy_ability", {"name": "str"}))
    return (1000 - a.training, 1000 - b.training)


@case("training.md:31", "comfort exchange: 1 comfort = 10 / 15 / 20 training at level 1 / 2 / 3", (10, 15, 20))
def _():
    return tuple(run(hero(level=l, comfort_current=1), ("exchange_comfort", {"n": 1})).training - 1000 for l in (1, 2, 3))


@case("training.md:69,73", "languages: 3 projects -> 90; Int mod 2, natives 1 -> next native 50", (90, 50))
def _():
    from wp.model.character import Language
    a = run(hero(), ("buy_language", {"title": "elvish", "projects": 3}))
    b = run(hero(abilities=abil(int=14), languages=(Language("c", "common", True),)),
            ("buy_language", {"title": "dwarf", "native": True}))
    return (1000 - a.training, 1000 - b.training)


@case("training.md:87", "reaction: 1 -> 2 costs 400", 400)
def _():
    return 1000 - run(hero(), ("buy_reaction", {})).training


@case("training.md:92", "new spell circle 2 -> 60; with a book 30", (60, 30))
def _():
    return (1000 - run(hero(), ("learn_spell", {"name": "x", "circle": 2})).training,
            1000 - run(hero(), ("learn_spell", {"name": "y", "circle": 2, "discount": True})).training)


@case("progression.md:23", "spell upgrade circle 2 = 25*(1+4) = 125", 125)
def _():
    c = run(hero(training=2000), ("learn_spell", {"name": "x", "circle": 2}))
    t = c.training
    return t - run(c, ("buy_spell_upgrade", {"spid": c.spells[0].spid, "name": "range"})).training


@case("skills.md:63", "normal 0->1 = 20, 2->3 = 60; advanced 0->1 = 15; specialized level 5, 5->6 = 60", (20, 60, 15, 60))
def _():
    def cost(skill, level=20):
        c = hero(level=level, skills=(skill,))
        return 1000 - run(c, ("buy_skill_rank", {"name": skill.name})).training
    return (cost(Skill("a", "dex")), cost(Skill("a", "dex", ranks=2)), cost(Skill("a", "dex", sk.ADVANCED)),
            cost(Skill("a", "dex", sk.SPECIALIZED, ranks=5), 5))


@case("skills.md:43", "level 2, advanced rank 2 -> 3 refused", "refused")
def _():
    return refused(lambda: dispatch(hero(level=2, skills=(Skill("a", "dex", sk.ADVANCED, ranks=2),)), "buy_skill_rank", name="a"))


@case("skills.md:67", "2nd advanced costs 60; 3rd specialization 300 (promote_skill)", (60, 300))
def _():
    a = hero(skills=(Skill("a", "dex", sk.ADVANCED), Skill("b", "dex")))
    b = hero(skills=(Skill("a", "dex", sk.SPECIALIZED), Skill("b", "dex", sk.SPECIALIZED), Skill("c", "dex", sk.ADVANCED)))
    return (1000 - run(a, ("promote_skill", {"name": "b"})).training,
            1000 - run(b, ("promote_skill", {"name": "c", "to_tier": sk.SPECIALIZED})).training)


@case("weapons.md:20", "grade cost X=0 diff 1 scale 2 -> 60", 60)
def _():
    c = hero(weapons=(WeaponEntry(Weapon("ls", scale=2)),))
    return 1000 - run(c, ("buy_weapon_grade", {"wid": "ls"})).training


@case("weapons.md:26", "basics on sword (1) + long swords (2) + heavy blades (3) -> level 4, not 12", 4)
def _():
    w = (WeaponEntry(Weapon("hb", scale=3, basics=True)), WeaponEntry(Weapon("ls", scale=2, basics=True, parents=("hb",))),
         WeaponEntry(Weapon("gs", scale=1, basics=True, parents=("ls",))))
    return dv.weapon_level(hero(weapons=w), "gs")


@case("weapons.md:6", "not qualified -4, one level below -2 (sword needs 2: level 0 -> -4, level 1 -> -2)", (-4, -2))
def _():
    def hit(grades):
        c = hero(items=(sword(required_level=2),), attacks=(AttackRecord("r", "sw", "blades"),),
                 weapons=(WeaponEntry(Weapon("blades", grades=grades)),))
        return rec_view(c).to_hit
    return (hit(0), hit(1))


@case("progression.md:9", "max HP rolls 10+6+6, Con 8, race 2, other 1 -> 22", 22)
def _():
    return dv.hp_max(hero(level=3, hp_rolls=(10, 6, 6), hit_die=10, abilities=abil(con=8), hp_race=2, hp_bonus=1))


@case("progression.md:13", "level up: training +100 * new level (1 -> 2: +200)", 1200)
def _():
    return run(hero(), ("level_up", {"hp_roll": 5})).training


@case("narrative.md:102", "end of cycle: level 7, two drives at 4+ -> attention +5", 5)
def _():
    return run(hero(level=7, drives={"a": 4, "b": 5}), ("end_cycle", {})).attention


@case("narrative.md:113-114", "lens counter 1/15, clamped 0..X (no model / command)", "exists", "missing feature")
def _():
    return "exists" if hasattr(Character(), "lenses") else "no lens field or command"


@case("classes_magic.md:133", "mage without circle-0 slots: cantrip unlimited, overload 2X = 4", (10, 4))
def _():
    c = run(hero(caster=mg.MAGE, mana=Pool(10, 10)), ("cast_spell", {"circle": 0}))
    return (c.mana.current, c.overload)


@case("classes_magic.md:138", "mage level 5, balance 2, cost 5 -> balance 0, OT 3, pain 1, DC 16", (0, 3, 1, 16))
def _():
    r = dispatch(hero(level=5, caster=mg.MAGE, mana=Pool(10, 10), balance_current=2), "cast_spell", circle=3, mana_cost=5)
    return (r.state.balance_current, r.state.trauma, dv.pain_total(r.state), r.info["result"].concentration_dc)


@case("robustness", "cast_spell circle 10 -> a clear CommandError (not an IndexError)", "refused")
def _():
    try:
        dispatch(hero(level=20, caster=mg.MAGE, mana=Pool(50, 50)), "cast_spell", circle=10)
    except CommandError:
        return "refused"
    return "allowed"


@case("robustness", "cast_spell circle -1 -> refused (not read as circle 9 cost 17)", "refused")
def _():
    try:
        dispatch(hero(level=20, caster=mg.MAGE, mana=Pool(50, 50)), "cast_spell", circle=-1)
    except CommandError:
        return "refused"
    return "allowed"


@case("resources.md:41-42", "DR / resistance come from the sheet's effects (an effect gives DR 3 vs physical)", 13,
      "missing feature")
def _():
    st = ef.Status("dr", sid="dr", effects=(ef.Effect("dr:physical", 3),))
    return run(hero(statuses=(st,)), ("take_damage", {"amount": 10})).hp_current


