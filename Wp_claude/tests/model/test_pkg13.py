"""Package 13: block effects, resource pools and per-round statuses, consumables, active list, injuries.
Run: python Wp_claude/tests/model/test_pkg13.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.catalog import skills_catalog as sc  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import rest as rs  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.model import active_list as al  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import blocks as blk  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import stats_view as stv  # noqa: E402
from wp.model.character import (ABILITIES, SHIELD, Ability, AttackRecord, Character, Feat, Item,  # noqa: E402
                                ResourcePool)
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg13")


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
    base = dict(hp_rolls=(20,), hp_current=20, spirit_current=5, balance_current=5, bp_current=5)
    base.update(kw)
    return Character(**base)


def st(sid, *effects, **kw):
    return Status(sid, sid=sid, effects=tuple(effects), **kw)


def block(btype, *scope):
    return Effect(bo.BLOCK_BONUS, block_type=btype, block_scope=tuple(scope) or ("all",))


# ---- B1: block_balance_regen ----
def _regen(*statuses, overload=0):
    c = hero(balance_current=0, overload=overload, statuses=statuses)
    return (run(c, ("tick", {})).balance_current, blk.regen_block_reasons(c))


S.case("b1-regen-free", "resources.md: no block -> the balance regenerates (0 -> 1)", (1, ()))(lambda: _regen())
S.case("b1-regen-blocked", "buffs.md [OWNER pkg 13 B1]: block_balance_regen -> no regen; reason = the source id",
       (0, ("tired",)))(lambda: _regen(st("tired", Effect(bo.BLOCK_REGEN))))
S.case("b1-regen-overload", "buffs.md: overload keeps working; both reasons listed", (0, ("overload", "tired")))(
    lambda: _regen(st("tired", Effect(bo.BLOCK_REGEN)), overload=2))
S.case("b1-regen-inactive", "buffs.md: an inactive source blocks nothing (0 -> 1)", (1, ()))(
    lambda: _regen(st("tired", Effect(bo.BLOCK_REGEN), active=False)))


# ---- B2: block_bonus ----
def fight(*statuses, **kw):
    base = dict(in_combat=True, morale_scale=4, statuses=statuses)
    base.update(kw)
    return hero(**base)


S.case("b2-morale-all", "buffs.md [OWNER pkg 13 B2]: no morale bonus at all: attack +2 -> 0, save +2 -> 0", ((2, 2), (0, 0)))(
    lambda: tuple((dv.total(c, bo.ATTACK), stv.save(c, "will").total) for c in (fight(), fight(st("x", block(bo.MORALE))))))
S.case("b2-morale-penalty-stays", "buffs.md: penalties are never blocked: morale scale -4 -> -2 stays", -2)(
    lambda: dv.total(fight(st("x", block(bo.MORALE)), morale_scale=-4), bo.ATTACK))
SACRED = st("blessed", Effect(bo.ATTACK, 2, "sacred"), Effect(bo.AC, 2, "sacred"))
S.case("b2-sacred-attack-only", "buffs.md: no sacred bonus to attacks only: attack 0, AC still 12", ((2, 12), (0, 12)))(
    lambda: tuple((dv.total(c, bo.ATTACK), dv.ac(c)) for c in (hero(statuses=(SACRED,)),
                                                              hero(statuses=(SACRED, st("x", block("sacred", "attack")))))))
S.case("b2-luck", "buffs.md: no luck bonus: luck +1 to saves -> 0 (Fort 1 -> 0)", (1, 0))(
    lambda: tuple(stv.save(hero(statuses=s), "fort").total for s in (
        (st("l", Effect(bo.SAVE, 1, "luck")),), (st("l", Effect(bo.SAVE, 1, "luck")), st("x", block("luck"))))))
DODGE1 = st("d", Effect(bo.AC, 1, bo.DODGE))
S.case("b2-dodge-ac", "defense_layers.md: no dodge to AC drops the positive Dex part too: Dex 14 + dodge 1 -> AC 13 -> 10",
       (13, 10))(
    lambda: tuple(dv.ac(hero(abilities=abil(dex=14), statuses=s)) for s in ((DODGE1,), (DODGE1, st("x", block(bo.DODGE, "ac"))))))
S.case("b2-dodge-dex-penalty", "defense_layers.md: Dex 8 (-1) + dodge 1 = AC 10; blocked: the Dex penalty stays -> 9",
       (10, 9))(
    lambda: tuple(dv.ac(hero(abilities=abil(dex=8), statuses=s)) for s in ((DODGE1,), (DODGE1, st("x", block(bo.DODGE, "ac"))))))


def _skills(*statuses):
    cat = sc.load_default()
    c = hero(skills=(sc.make_skill(cat, "stealth"), sc.make_skill(cat, "athletics")),
             statuses=(st("c", Effect(bo.SKILL, 2, "competence")),) + statuses)
    return (dv.skill_bonus(c, "stealth"), dv.skill_bonus(c, "athletics"))


S.case("b2-skill-scope", "buffs.md: block competence on skill:stealth only: stealth 2 -> 0, athletics keeps 2", ((2, 2), (0, 2)))(
    lambda: (_skills(), _skills(st("x", block("competence", "skill:stealth")))))
S.case("b2-two-sources", "buffs.md: blocks from two sources (status: morale, feat: luck) both work -> 0",
       (3, 0))(
    lambda: tuple(dv.total(c, bo.ATTACK) for c in (
        fight(st("l", Effect(bo.ATTACK, 1, "luck"))),
        fight(st("l", Effect(bo.ATTACK, 1, "luck")), st("x", block(bo.MORALE)), feats=(Feat("ft", effects=(block("luck"),)),)))))
S.case("b2-inactive-source", "buffs.md: an inactive status blocks nothing (attack stays 2)", 2)(
    lambda: dv.total(fight(Status("x", sid="x", effects=(block(bo.MORALE),), active=False)), bo.ATTACK))


def _sword_attack(*statuses, **kw):
    c = hero(abilities=abil(str=16), statuses=statuses,
             items=(Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("blades",)),),
             attacks=(AttackRecord("r", "sw", "blades"),), **kw)
    a = av.by_record(c, "r")
    return (a.to_hit, a.damage)


S.case("b2-attack-view", "buffs.md: the attack view drops blocked bonuses too (Str 16 +3, morale +2 -> 5/5; blocked 3/3)",
       ((5, 5), (3, 3)))(
    lambda: (_sword_attack(in_combat=True, morale_scale=4), _sword_attack(st("x", block(bo.MORALE)), in_combat=True, morale_scale=4)))


# ---- B3: block_stat_bonus ----
def stat_block(*stats):
    return st("x", Effect(bo.BLOCK_STAT, block_stats=tuple(stats)))


S.case("b3-dex", "buffs.md [OWNER pkg 13 B3]: Dex 14: AC 12 -> 10, Reflex 2 -> 0", ((12, 2), (10, 0)))(
    lambda: tuple((dv.ac(c), stv.save(c, "ref").total) for c in (
        hero(abilities=abil(dex=14)), hero(abilities=abil(dex=14), statuses=(stat_block("dex"),)))))
S.case("b3-str", "buffs.md: Str 16 blocked: attack and damage +3 -> 0", (0, 0))(
    lambda: _sword_attack(stat_block("str")))
S.case("b3-negative-stays", "buffs.md: a negative modifier stays: Str 6 blocked -> attack -2", (-2, -2))(
    lambda: (lambda c: (lambda a: (a.to_hit, a.damage))(av.by_record(c, "r")))(
        hero(abilities=abil(str=6), statuses=(stat_block("str"),),
             items=(Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("blades",)),),
             attacks=(AttackRecord("r", "sw", "blades"),))))
S.case("b3-all", "buffs.md: \"all\" blocks every positive stat modifier (Dex 14, Wis 14: AC 10, Will 0)", (10, 0))(
    lambda: (lambda c: (dv.ac(c), stv.save(c, "will").total))(hero(abilities=abil(dex=14, wis=14), statuses=(stat_block("all"),))))
S.case("b3-other-stat-free", "buffs.md: blocking Str leaves Dex (AC 12)", 12)(
    lambda: dv.ac(hero(abilities=abil(dex=14), statuses=(stat_block("str"),))))


# ---- B4: cannot_be_flanked ----
SHIELD2 = Item("sh", "shield", kind=SHIELD, hands=1, in_hands=True, shield=2)
S.case("b4-flank", "buffs.md [OWNER pkg 13 B4]: flank drops the shield (12 -> 10); cannot_be_flanked: flank = front 12",
       ((12, 10), (12, 12)))(
    lambda: tuple((dv.ac(c), dv.ac(c, acm.FLANK)) for c in (
        hero(items=(SHIELD2,)), hero(items=(SHIELD2,), statuses=(st("x", Effect(bo.NO_FLANK)),)))))


def _liquescit(active):
    me = Feat("me_liquescit", title="Me Liquescit", is_stance=True,
              effects=(block(bo.DODGE, "ac"), Effect(bo.NO_FLANK)))
    return hero(abilities=abil(dex=14), statuses=(DODGE1,), items=(SHIELD2,), feats=(me,),
                active_stance="me_liquescit" if active else None)


S.case("b-me-liquescit", "combat.md stance \"Me Liquescit\" (no dodge bonus to AC, cannot be flanked): Dex 14 + dodge 1 + "
       "shield 2: off -> front 15, flank 13; on -> front 12, flank 12", ((15, 13), (12, 12)))(
    lambda: tuple((dv.ac(c), dv.ac(c, acm.FLANK)) for c in (_liquescit(False), _liquescit(True))))


# ---- C: resource pools and per-round statuses ----
def ki_char(pool_cur=3, **st_kw):
    status = Status("Ki mode", sid="ki_mode", effects=(Effect(bo.ATTACK, 1),), charge_source="ki", charge_per_round=1,
                    active=False, **st_kw)
    return hero(pools=(ResourcePool("ki", "Ki", max=3, current=pool_cur, restore="short_rest"),), statuses=(status,))


def _ki_ticks(ch, n):
    out = []
    for _ in range(n):
        ch = run(ch, ("tick", {}))
        out.append((ch.statuses[0].active, ch.pools[0].current))
    return out


S.case("c-ki-3-ticks", "buffs.md [OWNER pkg 14 A, Q83]: pool 3, 1 per round: activation pays round 1 (2 left), ticks pay "
       "rounds 2 and 3, the 3rd tick cannot pay -> exactly 3 rounds",
       (2, [(True, 1), (True, 0), (False, 0)]))(
    lambda: (lambda c: (c.pools[0].current, _ki_ticks(c, 3)))(run(ki_char(), ("activate_status", {"sid": "ki_mode"}))))
S.case("c-ki-manual-end", "buffs.md: removed by hand after 1 tick (3 -> 2 -> 1): inactive, the pool stays 1, no more payment",
       (False, 1))(
    lambda: (lambda c: (c.statuses[0].active, c.pools[0].current))(
        run(ki_char(), ("activate_status", {"sid": "ki_mode"}), ("tick", {}), ("remove_status", {"sid": "ki_mode"}),
            ("tick", {}))))
S.case("c-duration-first", "buffs.md: duration 2, pool 3: activation 2; tick 1 pays (1), tick 2 pays (0) and the duration "
       "ends (payment before the duration step, Q95); tick 3 pays nothing", [(True, 1), (False, 0), (False, 0)])(
    lambda: _ki_ticks(run(ki_char(duration=ef.TICKS, full_ticks=2), ("activate_status", {"sid": "ki_mode"})), 3))
S.case("c-own-charges", "buffs.md [OWNER pkg 14 A, Q91]: source own, 2 per round, charges 4/4: activation spends 2 (not 1 + 2) "
       "-> 2; tick pays 2 -> 0; the next tick ends it", (2, [(True, 0), (False, 0)]))(
    lambda: (lambda c: (c.statuses[0].charges.current,
                        [(x.statuses[0].active, x.statuses[0].charges.current)
                         for x in (run(c, ("tick", {})), run(c, ("tick", {}), ("tick", {})))]))(
        run(hero(statuses=(Status("burst", sid="b", charges=Pool(4, 4), charge_per_round=2, active=False),)),
            ("activate_status", {"sid": "b"}))))
S.case("c-refuse-empty-pool", "buffs.md: activation with a pool below one round's payment is refused",
       "refused: not enough Ki for Ki mode: need 1 per round, have 0")(
    lambda: refused(ki_char(pool_cur=0), "activate_status", sid="ki_mode"))
S.case("c-refuse-no-pool", "buffs.md: a pool that does not exist -> refused",
       "refused: status Ki mode pays from pool 'ki', which does not exist")(
    lambda: refused(hero(statuses=ki_char().statuses), "activate_status", sid="ki_mode"))


def _pools():
    return hero(pools=(ResourcePool("a", "A", 3, 0, "short_rest"), ResourcePool("b", "B", 3, 0, "long_rest"),
                       ResourcePool("c", "C", 3, 0, "combat_start"), ResourcePool("d", "D", 3, 0, "manual")))


S.case("c-restore-rules", "resources.md [OWNER pkg 13 C, pkg 14 Q88]: short rest restores A, long rest A and B, start_combat C, "
       "manual D never", ((3, 0, 0, 0), (3, 3, 0, 0), (0, 0, 3, 0)))(
    lambda: tuple(tuple(p.current for p in run(_pools(), step).pools) for step in (
        ("short_rest", {}), ("long_rest", {}), ("start_combat", {}))))
S.case("c-pool-commands", "resources.md: add_pool (current = max), spend 2, restore -> (3, 1, 3)", (3, 1, 3))(
    lambda: (lambda c: (c.pools[0].current, run(c, ("spend_pool", {"pid": "ki", "n": 2})).pools[0].current,
                        run(c, ("spend_pool", {"pid": "ki", "n": 2}), ("restore_pool", {"pid": "ki"})).pools[0].current))(
        run(hero(), ("add_pool", {"name": "Ki", "max": 3, "restore": "short_rest"}))))
S.case("c-spend-below-zero", "resources.md: spending below 0 is refused", "refused: not enough Ki: need 4, have 3")(
    lambda: refused(ki_char(), "spend_pool", pid="ki", n=4))
S.case("c-bad-restore", "resources.md: restore must be one of the four rules",
       "refused: restore must be one of short_rest, long_rest, combat_start, manual")(
    lambda: refused(hero(), "add_pool", name="X", max=1, restore="dawn"))
S.case("c-edit-remove", "resources.md: edit_pool sets max 5; remove_pool removes it", (5, ()))(
    lambda: (lambda c: (c.pools[0].max, run(c, ("remove_pool", {"pid": "ki"})).pools))(
        run(ki_char(), ("edit_pool", {"pid": "ki", "max": 5}))))
S.case("c-unpaid-does-not-act", "buffs.md (assumption Q84): a status that cannot pay ends at once and does not heal this tick",
       (False, 10))(
    lambda: (lambda c: (c.statuses[0].active, c.hp_current))(run(
        hero(hp_current=10, pools=(ResourcePool("ki", "Ki", 3, 0),),
             statuses=(Status("regen", sid="r", per_tick_hp=2, charge_source="ki", charge_per_round=1),)), ("tick", {}))))
S.case("c-save-load", "D11: pools and the per-round fields survive save/load", True)(
    lambda: (lambda c: cio.loads(cio.dumps(c)) == c)(ki_char()))


# ---- D: consumables ----
POTION = Item("pot", "potion", consumable=True, quantity=3, weight_l=5, on_use_status="heal")
HEAL = Status("heal", sid="heal", per_tick_hp=2, duration=ef.TICKS, full_ticks=3, active=False)


def _w(c):
    return dv.carried_weight_l(c)


S.case("d-weight", "gear.md [OWNER pkg 13 D]: weight = unit weight * quantity (5 * 3 = 15); after one use 10", (15, 10))(
    lambda: (_w(hero(items=(POTION,), statuses=(HEAL,))),
             _w(run(hero(items=(POTION,), statuses=(HEAL,)), ("use_consumable", {"iid": "pot"})))))
S.case("d-spent", "gear.md: at quantity 0 the item stays, spent (grey) and weighs 0", (1, 0, True, 0))(
    lambda: (lambda c: (len(c.items), c.items[0].quantity, dv.item_view(c, "pot").spent, _w(c)))(
        run(hero(items=(POTION,), statuses=(HEAL,)), ("use_consumable", {"iid": "pot", "n": 1}),
            ("remove_status", {"sid": "heal"}), ("use_consumable", {"iid": "pot", "n": 1}),
            ("remove_status", {"sid": "heal"}), ("use_consumable", {"iid": "pot", "n": 1}))))
S.case("d-refuse", "gear.md: using more than there is -> refused", "refused: not enough potion: have 3, use 4")(
    lambda: refused(hero(items=(POTION,), statuses=(HEAL,)), "use_consumable", iid="pot", n=4))
S.case("d-refuse-not-consumable", "gear.md: a non-consumable cannot be used", "refused: ring is not a consumable")(
    lambda: refused(hero(items=(Item("ring", "ring"),)), "use_consumable", iid="ring"))
S.case("d-on-use-status", "gear.md: using the potion activates its status (heal, 3 ticks)", (True, 3))(
    lambda: (lambda s: (s.active, s.remaining))(run(hero(items=(POTION,), statuses=(HEAL,)),
                                                   ("use_consumable", {"iid": "pot"})).statuses[0]))
S.case("d-remove-item", "gear.md: only remove_item deletes a spent consumable", ())(
    lambda: run(hero(items=(Item("pot", "potion", consumable=True, quantity=0),)), ("remove_item", {"iid": "pot"})).items)


# ---- E: active list ----
def _mixed():
    sword = Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("blades",))
    ring = Item("ring", "ring", equipped=True, activated=True, activation_day=1, effects_on=(Effect(bo.ATTACK, 1),))
    axe = Item("ax", "axe", kind="weapon", hands=1, groups=("axes",))          # in the bag: its record is not available
    return hero(items=(sword, ring, POTION, axe), attacks=(AttackRecord("r", "sw", "blades"), AttackRecord("a", "ax", "axes")),
                charges=(rs.Charge("wand", rs.ITEM, Pool(2, 5)), rs.Charge("rage", rs.ABILITY, Pool(1, 3))),
                statuses=(st("bless", Effect(bo.ATTACK, 1), hidden=True), st("off", active=False)))


S.case("e-active-list", "pkg 13 E: attacks, activated items, item charges, active statuses (hidden flag), consumables",
       (("r", "unarmed"), ("ring",), (("wand", 2, 5),), (("bless", True),), (("pot", 3, False),)))(
    lambda: (lambda v: (tuple(a.record for a in v.attacks), v.activated_items,
                        tuple((c.name, c.current, c.max) for c in v.item_charges),
                        tuple((s.sid, s.hidden) for s in v.statuses),
                        tuple((x.iid, x.quantity, x.spent) for x in v.consumables)))(al.active_list(_mixed())))


# ---- F: injuries ----
def _three():
    return run(hero(trauma=30), *[("add_injury", {"severity": "light", "name": n}) for n in ("cut", "bruise", "cut")])


S.case("f-remove", "injuries.md [OWNER pkg 13 F]: remove_injury by id; the others keep their ids",
       ("cut_1", "cut_3"))(lambda: tuple(j.jid for j in run(_three(), ("remove_injury", {"injury_id": "bruise_2"})).injuries))
S.case("f-never-reused", "injuries.md (Q75): after removing cut_3 a new cut gets cut_4, not cut_3", ("cut_1", "bruise_2", "cut_4"))(
    lambda: tuple(j.jid for j in run(_three(), ("remove_injury", {"injury_id": "cut_3"}),
                                     ("add_injury", {"severity": "light", "name": "cut"})).injuries))
S.case("f-refuse", "injuries.md: an unknown id is refused", "refused: no injury with id 'nope'")(
    lambda: refused(_three(), "remove_injury", injury_id="nope"))
S.case("f-counter-saved", "D11: the injury counter survives save/load (3)", 3)(
    lambda: cio.loads(cio.dumps(_three())).injury_counter)

if __name__ == "__main__":
    sys.exit(S.run())
