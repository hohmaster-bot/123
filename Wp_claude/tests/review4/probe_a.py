"""Review 4 probes, part A: resources, buffs, combat, defense (see probe_rules.py)."""
import os
import sys
from dataclasses import replace  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_common import *  # noqa: E402,F401,F403
from probe_common import Pick, Weapon  # noqa: E402,F401

# ============================================================ resources.md
@case("resources.md:7", "3 temp HP, 7 damage -> temp 0, HP -4, balance -4", (0, 16, 6))
def _():
    c = run(hero(temp_hp=3), ("take_damage", {"amount": 7}))
    return (dv.temp_hp_total(c), c.hp_current, c.balance_current)


@case("resources.md:28", "10 damage, 25% -> 7.5 -> 8 (round up)", 12)
def _():
    return run(hero(), ("take_damage", {"amount": 10, "reductions": dm.Reductions(percent={dm.PHYSICAL: 25})})).hp_current


@case("resources.md:29", "10 fire, 50% -> 5, flat 2 -> 3: HP -3, balance -3", (17, 7))
def _():
    r = dm.Reductions(percent={"fire": 50}, flat={"fire": 2})
    c = run(hero(), ("take_damage", {"amount": 10, "dtype": "fire", "reductions": r}))
    return (c.hp_current, c.balance_current)


@case("resources.md:39-40", "balance 1, hit 10 -> HP -10, bal 0, OT 9, pain 1; then 1 and 1 -> HP -12, pain 3, OT 11",
      ((10, 0, 9, 1), (8, 0, 11, 3)))
def _():
    c = run(hero(balance_current=1), ("take_damage", {"amount": 10}))
    a = (c.hp_current, c.balance_current, c.trauma, dv.pain_total(c))
    c = run(c, ("take_damage", {"amount": 1}), ("take_damage", {"amount": 1}))
    # pain total includes temp pain from HP only when HP < 0 (HP stays >= 0 here)
    return (a, (c.hp_current, c.balance_current, c.trauma, sum(p.amount for p in c.pain)))


@case("resources.md:48", "cap snapshot: armor 2 + BP 5 = 7; spend 2 BP -> 7; hit -> 6; end -> 3+2=5 (BP 3, armor kept)",
      (7, 7, 6, 5))
def _():
    c = hero(balance_bonus=0, balance_current=7, items=(Item("ar", "mail", equipped=True, armor=2),))
    c = run(c, ("start_combat", {}))
    a = dv.balance_max(c)
    c = run(c, ("spend_bp", {"n": 2}))
    b = dv.balance_max(c)
    c = run(c, ("take_damage", {"amount": 1}))
    d = dv.balance_max(c)
    return (a, b, d, dv.balance_max(run(c, ("end_combat", {}))))


@case("resources.md:54", "balance 6/6, hit 5 -> 1/6, then cap 5 -> 1/5", ((1, 5)))
def _():
    c = run(hero(balance_bonus=1, balance_current=6), ("start_combat", {}), ("take_damage", {"amount": 5}))
    return (c.balance_current, dv.balance_max(c))


@case("resources.md:61", "pay_hp_cost: balance 7 cost 9 -> 0, HP same, OT +2, pain +1, cap unchanged", (0, 20, 2, 1, 7))
def _():
    c = run(hero(balance_bonus=2, balance_current=7), ("start_combat", {}), ("pay_hp_cost", {"amount": 9}))
    return (c.balance_current, c.hp_current, c.trauma, dv.pain_total(c), dv.balance_max(c))


@case("resources.md:67", "damage_to_balance: 6 - 4 -> 2; 2 - 5 -> 0, OT 3, pain 1, HP same", ((2, 20), (0, 3, 1, 20)))
def _():
    a = run(hero(balance_current=6), ("damage_to_balance", {"amount": 4}))
    b = run(hero(balance_current=2), ("damage_to_balance", {"amount": 5}))
    return ((a.balance_current, a.hp_current), (b.balance_current, b.trauma, dv.pain_total(b), b.hp_current))


@case("resources.md:84", "temp pain from HP: 0, -2, -5, -7, -12 -> 0, 0, 1, 2, 4", (0, 0, 1, 2, 4))
def _():
    return tuple(dv.pain_total(hero(hp_current=h)) for h in (0, -2, -5, -7, -12))


@case("resources.md:86-87", "state at HP < 0 cleared at HP >= 0 (healing)", None)
def _():
    from wp.core import statuses as stt
    c = run(hero(hp_current=-3, negative_state=stt.DYING), ("restore", {"resource": "hp", "amount": 5}))
    return c.negative_state


@case("resources.md:93", "dying: -2 HP per tick (balance first, then HP; balance 0 -> HP -2)", -5)
def _():
    from wp.core import statuses as stt
    c = run(hero(hp_current=-3, negative_state=stt.DYING, balance_current=0, balance_bonus=-5, bp_current=0),
            ("tick", {}))
    return c.hp_current


@case("resources.md:109", "bleed 3 rounds hits exactly 3 times", (17, 14, 11, 11))
def _():
    st = ef.Status("bleed", sid="b", per_tick_hp=-3, duration=ef.TICKS, full_ticks=3)
    c = run(hero(balance_current=0, balance_bonus=-5, bp_current=0), ("add_status", {"status": st, "active": True}))
    out = []
    for _ in range(4):
        c = run(c, ("tick", {}))
        out.append(c.hp_current)
    return tuple(out)


@case("resources.md:111-112", "overload 1: no regen this tick; regen next tick", ((0, 0), (1, 0)))
def _():
    c = hero(balance_current=0, overload=1, level=1)
    a = run(c, ("tick", {}))
    b = run(a, ("tick", {}))
    return ((a.balance_current, a.overload), (min(b.balance_current, 1), b.overload))


@case("resources.md:120-122", "spirit: Cha +2 -> 15; -1 -> 0; +2 with +3 -> 18; Cha 8 with -2 -> 0", (15, 0, 18, 0))
def _():
    return (dv.spirit_max(hero(abilities=abil(cha=14))), dv.spirit_max(hero(abilities=abil(cha=8))),
            dv.spirit_max(hero(abilities=abil(cha=14), spirit_bonuses=(("r", 3),))),
            dv.spirit_max(hero(abilities=abil(cha=8), spirit_bonuses=(("c", -2),))))


@case("resources.md:129", "mage 3-mana standard: mana -3, balance -3, overload +2 (level 3: mana level allows 3)",
      (7, 7, 2))
def _():
    c = run(hero(level=3, caster=mg.MAGE, mana=Pool(10, 10)), ("cast_spell", {"circle": 2, "mana_cost": 3}))
    return (c.mana.current, c.balance_current, c.overload)


@case("resources.md:130", "non-mage same spell: slot spent, balance unchanged, overload +4", (0, 10, 4))
def _():
    c = run(hero(caster=mg.SLOTS, slots={2: Pool(1, 1)}), ("cast_spell", {"circle": 2}))
    return (c.slots[2].current, c.balance_current, c.overload)


@case("resources.md:157", "long rest restores short_rest AND long_rest pools; manual not", (3, 4, 0))
def _():
    c = hero(pools=(ResourcePool("a", "a", 3, 0, "short_rest"), ResourcePool("b", "b", 4, 0, "long_rest"),
                    ResourcePool("m", "m", 2, 0, "manual")))
    c = run(c, ("long_rest", {}))
    return tuple(pv.current(c, p) for p in c.pools)


@case("resources.md:172", "rule switch ignore_pain: pain 2 -> attack 0, count 2", (0, 2))
def _():
    c = hero(pain=(PainEntry(2),), rules_settings=RulesSettings(ignore_pain=True))
    return (av.all_attacks(c)[0].to_hit, dv.pain_total(c))


@case("resources.md:180", "journal: a command that changes nothing is NOT logged (resolve_spell_failure failed=False)", 0,
      "ambiguous")
def _():
    c = run(hero(caster=mg.MAGE, mana=Pool(10, 10)), ("resolve_spell_failure", {"failed": False}))
    return len(c.log)


@case("resources.md:180", "journal: spend_balance(0) changes nothing -> not logged", 0, "ambiguous")
def _():
    return len(run(hero(), ("spend_balance", {"n": 0})).log)


@case("resources.md:180", "journal: take_damage 0 changes nothing -> not logged", 0, "ambiguous")
def _():
    return len(run(hero(), ("take_damage", {"amount": 0})).log)


# ============================================================ buffs.md
@case("buffs.md:6-7", "'+4 Str for 8 rounds' (effect target str) raises the Str modifier: Str 10 -> mod +2", 2)
def _():
    st = ef.Status("bull", sid="b", effects=(ef.Effect("str", 4, "enhancement"),), duration=ef.TICKS, full_ticks=8)
    c = run(hero(), ("add_status", {"status": st, "active": True}))
    return dv.ability_mod(c, "str")


@case("buffs.md:5", "effect on max HP (target hp_max) from a status +5 -> max HP 25", 25)
def _():
    st = ef.Status("toughness", sid="t", effects=(ef.Effect("hp_max", 5),))
    return dv.hp_max(run(hero(), ("add_status", {"status": st, "active": True})))


@case("buffs.md:5", "effect on balance regen (target balance_regen) +2 -> regen 1+0+2 = 3", 3)
def _():
    st = ef.Status("calm", sid="c", effects=(ef.Effect("balance_regen", 2),))
    return dv.balance_regen(run(hero(), ("add_status", {"status": st, "active": True})))


@case("buffs.md:36", "+Str mod to Intimidation (Str 16, Cha 12) -> 4", 4)
def _():
    st = ef.Status("x", sid="x", effects=(ef.Effect(bo.skill_target("intim"), stat_mod="str"),))
    c = run(hero(abilities=abil(str=16, cha=12), skills=(Skill("intim", "cha"),)), ("add_status", {"status": st, "active": True}))
    return dv.skill_bonus(c, "intim")


@case("buffs.md:74-75", "3-tick status: bonus during 2 ticks, inactive after the 3rd", ((1, 1, 0), (True, True, False)))
def _():
    st = ef.Status("b", sid="b", effects=(ef.Effect(bo.ATTACK, 1),), duration=ef.TICKS, full_ticks=3)
    c = run(hero(), ("add_status", {"status": st, "active": True}))
    hits, act = [], []
    for _ in range(3):
        c = run(c, ("tick", {}))
        hits.append(av.all_attacks(c)[0].to_hit)
        act.append(c.statuses[0].active)
    return (tuple(hits), tuple(act))


@case("buffs.md:61", "activate_status refusals: no charge / already active", ("refused", "refused"))
def _():
    a = hero(statuses=(ef.Status("r", sid="r", charges=Pool(0, 3), active=False),))
    b = hero(statuses=(ef.Status("r", sid="r", active=True),))
    return (refused(lambda: dispatch(a, "activate_status", sid="r")), refused(lambda: dispatch(b, "activate_status", sid="r")))


@case("buffs.md:130", "aura 3 rounds at 1 Ki costs 3 Ki; duration 1 costs 1 and ends at the first tick",
      ((2, 1, 0, 0, 0), (2, False)))
def _():
    aura = ef.Status("aura", sid="a", duration=ef.TICKS, full_ticks=3, charge_source="ki", charge_per_round=1)
    c = run(hero(pools=(ResourcePool("ki", "ki", 5, 5),)), ("add_status", {"status": aura, "active": True}))
    # pool 5: activation pays round 1 (4), tick 1 pays round 2 (3), tick 2 pays round 3 (2), tick 3 ends: 3 Ki in all
    seq = [pv.current(c, c.pools[0]) - 2]
    for _ in range(4):
        c = run(c, ("tick", {}))
        seq.append(pv.current(c, c.pools[0]) - 2)
    one = ef.Status("one", sid="o", duration=ef.TICKS, full_ticks=1, charge_source="ki", charge_per_round=1)
    d = run(hero(pools=(ResourcePool("ki", "ki", 3, 3),)), ("add_status", {"status": one, "active": True}), ("tick", {}))
    return (tuple(seq), (pv.current(d, d.pools[0]), d.statuses[0].active))


@case("buffs.md:154", "rage pool max con_mod + 2*(level+1), Con mod 3, level 4 -> 13; Con mod 1 -> 11", (13, 11))
def _():
    p = ResourcePool("rage", "rage", "con_mod + 2*(level+1)", 13)
    a = hero(level=4, abilities=abil(con=16), pools=(p,))
    b = hero(level=4, abilities=abil(con=12), pools=(p,))
    return (pv.max_of(a, p), pv.current(b, p))


@case("buffs.md:115", "block dodge on AC: Dex 14 + dodge 1: 13 -> 10; Dex 8: 10 -> 9", (13, 10, 10, 9))
def _():
    dodge = ef.Status("d", sid="d", effects=(ef.Effect(bo.AC, 1, bo.DODGE),))
    blk_ = ef.Status("no", sid="n", effects=(ef.Effect(bo.BLOCK_BONUS, block_type=bo.DODGE, block_scope=(bo.AC,)),))
    hi, lo = hero(abilities=abil(dex=14), statuses=(dodge,)), hero(abilities=abil(dex=8), statuses=(dodge,))
    return (dv.ac(hi), dv.ac(replace(hi, statuses=(dodge, blk_))), dv.ac(lo), dv.ac(replace(lo, statuses=(dodge, blk_))))


# ============================================================ combat.md
@case("combat.md:8", "iterative: 2nd attack-tagged option -5, 3rd -10 (attack view / any command exposes it)",
      "exposed", "missing feature")
def _():
    fields = av.AttackView.__dataclass_fields__
    return "exposed" if any("iter" in f for f in fields) else "no field in AttackView, only wp/core/combat.py"


@case("combat.md:18", "crit: dagger 19+ -> 19; pick crit+1 -> 18; keen -> 17", (19, 18, 17))
def _():
    d = sword(crit_range=19)
    a = hero(items=(d,), attacks=(AttackRecord("r", "sw", "blades"),))
    b = replace(a, weapons=(WeaponEntry(Weapon("blades", grades=12), picks=(Pick(5, "crit_1"),)),))
    c = replace(a, items=(replace(d, keen=True),))
    return (rec_view(a).crit_range, rec_view(b).crit_range, rec_view(c).crit_range)


@case("combat.md:14", "'Weapon mastery can widen range by 2 (20 -> 18)' vs one pick crit +1 (20 -> 19)", 18, "ambiguous")
def _():
    a = hero(items=(sword(),), attacks=(AttackRecord("r", "sw", "blades"),),
             weapons=(WeaponEntry(Weapon("blades", grades=12), picks=(Pick(5, "crit_1"),)),))
    return rec_view(a).crit_range


@case("combat.md:42-43", "Str 16 (+3): one 3, two hands 4, off 1; Str 6 (-2): -2 with any grip",
      ((3, 4, 1), (-2, -2, -2)))
def _():
    def dmg(st, grip):
        it = sword(hands=1)
        c = hero(abilities=abil(str=st), items=(it,), attacks=(AttackRecord("r", "sw", "blades", grip=grip),))
        return rec_view(c).damage
    return (tuple(dmg(16, g) for g in ("one", "two", "off")), tuple(dmg(6, g) for g in ("one", "two", "off")))


@case("combat.md:50-53", "TWF table: normal -6/-10, light -4/-8, feat -4/-4, light+feat -2/-2",
      ((-6, -10), (-4, -8), (-4, -4), (-2, -2)))
def _():
    from wp.model import twf
    return tuple(twf.penalties(l, f) for l, f in ((False, False), (True, False), (False, True), (True, True)))


@case("combat.md:135", "size small/medium/large with BAB 2, Str/Dex 12: (attack, AC, CMB, CMD)",
      ((4, 12, 2, 13), (3, 11, 3, 14), (2, 10, 4, 15)))
def _():
    out = []
    for size in ("small", "medium", "large"):
        c = hero(bab=2, abilities=abil(str=12, dex=12), size=size)
        # attack = BAB 2 + Str 1 + size (+1 / 0 / -1); the RULES line lists only the size part
        out.append((av.all_attacks(c)[0].to_hit, dv.ac(c), stv.cmb(c).total, stv.cmd(c).total))
    return tuple(out)


@case("combat.md:136", "speed: base 20; +10 ft item -> 30; overload -> 10", (20, 30, 10))
def _():
    a = hero()
    b = hero(items=(Item("b", "boots", equipped=True, effects_off=(ef.Effect(bo.SPEED, 10),)),))
    c = hero(items=(Item("rock", "rock", weight_l=200),))
    return (dv.speed(a), dv.speed(b), dv.speed(c))


@case("combat.md:142-143", "CMB per record: two swords, one with mastery +3 -> 7 and 4, general 4", (7, 4, 4))
def _():
    a = sword()
    b = Item("ax", "axe", kind="weapon", hands=1, in_hands=True, groups=("axes",))
    w = (WeaponEntry(Weapon("blades", grades=12), picks=(Pick(5, "attack_1"), Pick(8, "attack_1"), Pick(12, "attack_1"))),
         WeaponEntry(Weapon("axes", grades=0)))
    c = hero(bab=3, abilities=abil(str=12), items=(a, b), weapons=w,
             attacks=(AttackRecord("r", "sw", "blades"), AttackRecord("q", "ax", "axes")))
    return (rec_view(c, "r").cmb, rec_view(c, "q").cmb, stv.cmb(c).total)


@case("combat.md:165", "Me Liquescit: Dex 14, dodge +1, shield 2: off front 15 / flank 13; on 12 / 12", ((15, 13), (12, 12)))
def _():
    stance = Feat("ml", is_stance=True, effects=(ef.Effect(bo.BLOCK_BONUS, block_type=bo.DODGE, block_scope=(bo.AC,)),
                                                 ef.Effect(bo.NO_FLANK)))
    dodge = ef.Status("d", sid="d", effects=(ef.Effect(bo.AC, 1, bo.DODGE),))
    sh = Item("sh", "shield", kind="shield", hands=1, in_hands=True, shield=2)
    c = hero(abilities=abil(dex=14), statuses=(dodge,), items=(sh,), feats=(stance,))
    on = run(c, ("set_active_stance", {"fid": "ml"}))
    return ((dv.ac(c), dv.ac(c, acm.FLANK)), (dv.ac(on), dv.ac(on, acm.FLANK)))


@case("combat.md:84", "maneuver 'unarmed' with a sword in hand -> unavailable (unarmed_not_possible)", False)
def _():
    m = Maneuver("kick", "kick", required_tags=("unarmed",))
    c = hero(items=(sword(),), attacks=(AttackRecord("r", "sw", "blades"),), maneuvers=(m,))
    return mv.maneuver_view(c)[0].available


# ============================================================ defense.md / layers
@case("defense.md:11", "Dex -2 (6): front AC 8, flat-footed 8", (8, 8))
def _():
    c = hero(abilities=abil(dex=6))
    return (dv.ac(c), dv.ac(c, acm.FLAT_FOOTED))


@case("defense.md:37-38", "saves base 3/1/2, Con 14, Dex 12, Wis 8 -> 5/2/1", (5, 2, 1))
def _():
    c = hero(abilities=abil(con=14, dex=12, wis=8), save_base={"fort": 3, "ref": 1, "will": 2})
    return tuple(stv.save(c, k).total for k in ("fort", "ref", "will"))


@case("defense.md:41-42", "initiative Dex 14 + 2 competence -> 4; scale 2 in combat -> 5; same out of combat -> 4", (4, 5, 4))
def _():
    st = ef.Status("c", sid="c", effects=(ef.Effect(bo.INITIATIVE, 2, "competence"),))
    c = hero(abilities=abil(dex=14), statuses=(st,))
    return (stv.initiative(c).total, stv.initiative(replace(c, in_combat=True, morale_scale=2)).total,
            stv.initiative(replace(c, morale_scale=2)).total)


@case("defense.md:53", "morale: scale 3 -> +1, -4 -> -2, 1 -> 0 (attack in combat)", (1, -2, 0))
def _():
    return tuple(av.all_attacks(hero(in_combat=True, morale_scale=s))[0].to_hit for s in (3, -4, 1))


@case("defense_layers.md:28", "Dex -2, armor 8: base 8; hit just barely 16", (8, 16))
def _():
    c = hero(abilities=abil(dex=6), items=(Item("ar", "plate", equipped=True, armor=8),))
    parts = acm.parts(dv.ac_input(c))
    return (acl.base(parts), acl.ac_total(parts))


@case("defense.md:12-15", "parry: level 1 heavy armor + tower grade -> 8; level 3 -> 9; no shield grade -> 6", (8, 9, 6))
def _():
    def p(level, sg):
        return dv.ac_input(hero(level=level, armor_grade="heavy", shield_grade=sg)).parry
    return (p(1, "tower"), p(3, "tower"), p(1, "none"))


