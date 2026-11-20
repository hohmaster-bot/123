"""Review 4, section 8: behavior questions answered by running the real commands.
Run: python Wp_claude/tests/review4/behavior.py   (prints what happens; no pass / fail)
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.model import active_list as al  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import maneuver_view as mv  # noqa: E402
from wp.model import twf  # noqa: E402
from wp.model.character import AttackRecord, Character, Feat, Item, Maneuver, ResourcePool, Usage  # noqa: E402


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def show(title, value):
    print("- %s: %r" % (title, value))


def hero(**kw):
    base = dict(hp_rolls=(20,), hit_die=20, hp_current=20, bp_current=5, balance_current=5, spirit_current=10)
    base.update(kw)
    return Character(**base)


def statuses(ch):
    return tuple((s.sid, s.active, s.remaining, s.charges.current if s.charges else None) for s in ch.statuses)


RAGE = ef.Status("rage", sid="rage", duration=ef.TICKS, full_ticks=3, charges=Pool(1, 3), active=False,
                 effects=(ef.Effect(bo.ATTACK, 2, bo.MORALE),))
EOC = ef.Status("guard", sid="guard", duration=ef.END_OF_COMBAT, active=False, one_shot=(ef.OneShot(ef.TEMP_HP, 4),))
PLAIN = ef.Status("blessed", sid="blessed", charges=Pool(0, 2), active=False)   # no source
FEAT = Feat("power", usage=Usage(charges_max=2, charges_current=0, recharge="long_rest"))

print("## Statuses and charges on long rest / end_combat / level_up")
c = run(hero(statuses=(RAGE, EOC, PLAIN), feats=(FEAT,), in_combat=True, combat_round=1),
        ("activate_status", {"sid": "rage"}), ("activate_status", {"sid": "guard"}))
show("in combat after activating rage and guard", statuses(c))
e = run(c, ("end_combat", {}))
show("end_combat (rage keeps running, guard ends)", statuses(e))
lr = run(c, ("long_rest", {}))
show("long rest during combat: statuses (active ones keep running; charges of rage AND of the plain buff restored)",
     statuses(lr))
show("long rest: feat usage charges", lr.feats[0].usage.charges_current)
lu = run(c, ("level_up", {"hp_roll": 5}))
show("level_up: statuses unchanged", statuses(lu) == statuses(c))

print("## A status of duration 1 activated in a round")
one = ef.Status("flash", sid="flash", duration=ef.TICKS, full_ticks=1, active=False, effects=(ef.Effect(bo.ATTACK, 3),),
                per_tick_hp=-1)
c = run(hero(statuses=(one,), balance_current=0, balance_bonus=-5, bp_current=0), ("start_combat", {}),
        ("activate_status", {"sid": "flash"}))
show("same round: active, attack bonus", (c.statuses[0].active, av.all_attacks(c)[0].to_hit))
t = run(c, ("tick", {}))
show("after the first tick: active, HP (the DoT part acted once)", (t.statuses[0].active, t.hp_current))

print("## Removing an item that has charges or an active status")
potion = Item("pot", "potion", consumable=True, quantity=2, on_use_status="heal",
              usage=Usage(charges_max=2, charges_current=2))
heal = ef.Status("heal", sid="heal", per_tick_hp=2, duration=ef.TICKS, full_ticks=2, active=False)
c = run(hero(items=(potion,), statuses=(heal,)), ("use_consumable", {"iid": "pot"}))
c2 = run(c, ("remove_item", {"iid": "pot"}))
show("status started by the removed item stays active", statuses(c2))
ring = Item("ring", "ring", equipped=True, effects_off=(ef.Effect(bo.AC, 1, "deflection"),),
            usage=Usage(charges_max=3, charges_current=1))
c = run(hero(items=(ring,)), ("remove_item", {"iid": "ring"}))
show("ring with charges removed: items, active list charges", (len(c.items), al.active_list(c).item_charges))
a = Item("a", "sword A", kind="weapon", hands=1, in_hands=True, groups=("blades",))
b = Item("b", "dagger B", kind="weapon", hands=1, in_hands=True, groups=("blades",))
c = hero(items=(a, b), attacks=(AttackRecord("ra", "a", "blades", twf=True, twf_off="rb"),
                                AttackRecord("rb", "b", "blades", grip="off")))
c = run(c, ("remove_item", {"iid": "b"}))
show("TWF record whose off-hand weapon was removed: twf_off left dangling", (c.attacks[0].twf, c.attacks[0].twf_off))
try:
    twf.combination(c, "ra")
    show("twf.combination on it", "works")
except Exception as ex:  # noqa: BLE001
    show("twf.combination on it raises", "%s: %s" % (type(ex).__name__, ex))
show("all_attacks on it", tuple((v.record, v.available, v.missing) for v in av.all_attacks(c)))

print("## Stance feat removed while active")
st = Feat("stance", is_stance=True, effects=(ef.Effect(bo.AC, 2, bo.DODGE),))
c = run(hero(feats=(st,)), ("set_active_stance", {"fid": "stance"}), ("remove_feat", {"fid": "stance"}))
show("active_stance after removing the feat", c.active_stance)

print("## Maneuver whose required feat is removed")
f = Feat("trip_feat")
m = Maneuver("trip", "trip", required_tags=("blades",), required_feat="trip_feat")
c = hero(feats=(f,), maneuvers=(m,), items=(a,), attacks=(AttackRecord("ra", "a", "blades"),))
show("with the feat", (mv.maneuver_view(c)[0].available, mv.maneuver_view(c)[0].reasons))
c = run(c, ("remove_feat", {"fid": "trip_feat"}))
show("feat removed: kept, unavailable, reasons", (len(c.maneuvers), mv.maneuver_view(c)[0].available,
                                                  mv.maneuver_view(c)[0].reasons))

print("## Extra checks")
pool_status = ef.Status("aura", sid="aura", duration=ef.TICKS, full_ticks=3, charge_source="ki", charge_per_round=1,
                        active=False)
c = run(hero(statuses=(pool_status,), pools=(ResourcePool("ki", "ki", 5, 5),)), ("activate_status", {"sid": "aura"}),
        ("remove_pool", {"pid": "ki"}), ("tick", {}))
show("pool removed under an active per-round status, after a tick", statuses(c))
try:
    run(hero(items=(Item("pot", "potion", consumable=True, quantity=1, on_use_status="gone"),)),
        ("use_consumable", {"iid": "pot"}))
except CommandError as ex:
    show("consumable whose status was deleted", "refused: %s" % ex)
c = run(hero(statuses=(ef.Status("x", sid="x", duration=ef.TICKS, full_ticks=2, active=False),)),
        ("activate_status", {"sid": "x"}), ("tick", {}), ("tick", {}), ("activate_status", {"sid": "x"}))
show("a finished status can be activated again (no charges)", statuses(c))
