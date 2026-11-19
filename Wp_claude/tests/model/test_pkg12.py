"""Package 12: status has no cost, armor slowdown, injury ids, stances, maneuvers by tags, CMB per record.
Run: python Wp_claude/tests/model/test_pkg12.py"""
import json
import os
import sys
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.model import container_view as cv  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import stance_view as stv  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character, Feat, Item  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg12")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def refused(ch, name, **kw):
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return "refused: " + str(e)
    return "allowed"


def abil(**scores):
    return {a: Ability(base=scores.get(a, 10)) for a in ABILITIES}


def hero(**kw):
    base = dict(hp_rolls=(20,), hp_current=20, spirit_current=5, balance_current=5, bp_current=5, trauma=20)
    base.update(kw)
    return Character(**base)


# ---- A1: a status has no cost (Q69) ----
def _old_cost_save():
    d = json.loads(cio.dumps(hero(statuses=(Status("Haste", sid="haste", duration=ef.TICKS, full_ticks=3, active=False),))))
    d["character"]["statuses"][0]["cost_resource"] = "spirit"
    d["character"]["statuses"][0]["cost_amount"] = 2
    c = cio.loads(json.dumps(d))
    return (c.statuses[0].sid, run(c, ("activate_status", {"sid": "haste"})).spirit_current)


S.case("a1-old-cost-save", "buffs.md [OWNER pkg 12, Q69]: an old status with a cost loads; activation spends nothing",
       ("haste", 5))(_old_cost_save)


# ---- A2: armor slowdown (Q72) ----
def armor(**kw):
    base = dict(equipped=True, armor=4, hp=20, speed_penalty_ft=5)
    base.update(kw)
    return Item("ar", "chain", **base)


def red(value):
    return Feat("ft", title="ft", effects=(Effect(bo.SLOWDOWN_REDUCTION, value),))


S.case("a2-worn-bag", "gear.md [OWNER pkg 12, Q72]: worn armor -5 ft (20 -> 15); in the bag no slowdown (20)", (15, 20))(
    lambda: (dv.speed(hero(items=(armor(),))), dv.speed(hero(items=(armor(equipped=False),)))))
S.case("a2-broken-zero", "gear.md: broken armor still slows (15); armor at 0 HP counts as taken off (20)", (15, 20))(
    lambda: (dv.speed(hero(items=(armor(hp_current=8),))), dv.speed(hero(items=(armor(hp_current=0),)))))
S.case("a2-reduction", "gear.md: reduction 3 -> slowdown 2 (18); reduction 10 -> 0, never a bonus (20)", (18, 20))(
    lambda: (dv.speed(hero(items=(armor(),), feats=(red(3),))), dv.speed(hero(items=(armor(),), feats=(red(10),)))))
S.case("a2-all", "gear.md: reduction \"all\" ignores the slowdown completely (armor 10 ft -> 20)", 20)(
    lambda: dv.speed(hero(items=(armor(speed_penalty_ft=10),), feats=(red(ef.ALL),))))
S.case("a2-overload", "gear.md: overload -10 ft stacks with the armor slowdown -5 ft (20 -> 5)", (True, 5))(
    lambda: (lambda c: (dv.overloaded(c), dv.speed(c)))(hero(items=(armor(), Item("rock", "rock", weight_l=300)))))
S.case("a2-status-source", "gear.md: an active status may reduce it too (reduction 5 -> 20)", 20)(
    lambda: dv.speed(hero(items=(armor(),), statuses=(Status("s", sid="s", effects=(Effect(bo.SLOWDOWN_REDUCTION, 5),)),))))


# ---- A3: injury ids (Q70) ----
def _two_cuts():
    return run(hero(), ("add_injury", {"severity": "light", "name": "cut"}), ("add_injury", {"severity": "light", "name": "cut"}))


S.case("a3-unique", "injuries.md [OWNER pkg 12, Q70]: two injuries with the same name get different ids", ("cut", "cut_2"))(
    lambda: tuple(j.jid for j in _two_cuts().injuries))
S.case("a3-stable", "injuries.md: removing another injury keeps the ids (cut_2 stays cut_2); a freed id may be reused "
       "by a new injury (assumption Q75)", ("cut_2", "cut"))(
    lambda: tuple(j.jid for j in run(replace(_two_cuts(), injuries=_two_cuts().injuries[1:]),
                                     ("add_injury", {"severity": "light", "name": "cut"})).injuries))


def _old_injury_save():
    from wp.core.injuries import Injury
    d = json.loads(cio.dumps(hero(injuries=(Injury("bruise", "light", 2),))))
    d["character"]["injuries"][0].pop("jid")
    return cio.loads(json.dumps(d)).injuries[0].jid


S.case("a3-old-file", "injuries.md: an old file without injury ids loads; the program gives the id", "bruise")(_old_injury_save)
S.case("a3-container", "buffs.md: the container view uses the injury id", ("cut", "cut_2"))(
    lambda: tuple(e.eid for e in cv.container_view(_two_cuts()).entries if e.kind == cv.INJURY))


# ---- A4: stances (Q74) ----
def stance(fid, value, **kw):
    return Feat(fid, title=fid, is_stance=True, effects=(Effect(bo.ATTACK, value),), **kw)


def stanced(active=None):
    return hero(feats=(stance("me_liquescit", 2), stance("iron", 1), Feat("power", title="power", effects=(Effect(bo.DAMAGE, 1),))),
                active_stance=active)


S.case("a4-only-active", "combat.md [OWNER pkg 12, Q74]: a stance's effect only while active (0 -> 2); ordinary feat always (1, 1)",
       ((0, 1), (2, 1)))(
    lambda: tuple((dv.total(c, bo.ATTACK), dv.total(c, bo.DAMAGE)) for c in (stanced(), stanced("me_liquescit"))))
S.case("a4-switch", "combat.md: switching stances: me_liquescit +2 -> iron +1 -> none 0", (2, 1, 0))(
    lambda: tuple(dv.total(run(stanced(), *steps), bo.ATTACK) for steps in (
        (("set_active_stance", {"fid": "me_liquescit"}),),
        (("set_active_stance", {"fid": "me_liquescit"}), ("set_active_stance", {"fid": "iron"})),
        (("set_active_stance", {"fid": "iron"}), ("set_active_stance", {"fid": None})))))
S.case("a4-refuse-not-owned", "combat.md: a stance the character does not own is refused",
       "refused: feat 'other' is not on the sheet")(lambda: refused(stanced(), "set_active_stance", fid="other"))
S.case("a4-refuse-not-stance", "combat.md: an ordinary feat is not a stance", "refused: feat power is not a stance")(
    lambda: refused(stanced(), "set_active_stance", fid="power"))
S.case("a4-remove-clears", "combat.md: removing the active stance feat clears active_stance (and its effect)", (None, 0))(
    lambda: (lambda c: (c.active_stance, dv.total(c, bo.ATTACK)))(run(stanced("iron"), ("remove_feat", {"fid": "iron"}))))
S.case("a4-end-combat-keeps", "combat.md: end_combat does not change the stance", "iron")(
    lambda: run(stanced("iron"), ("start_combat", {}), ("end_combat", {})).active_stance)
S.case("a4-view", "combat.md: the stance view lists the stances and the active one",
       ((("me_liquescit", False), ("iron", True)), "iron"))(
    lambda: (lambda v: (tuple((e.fid, e.active) for e in v.stances), v.active))(stv.stance_view(stanced("iron"))))
S.case("a4-not-in-container", "combat.md: stances are not statuses in the container", ())(
    lambda: tuple(e for e in cv.container_view(stanced("iron")).entries))
S.case("a4-save-load", "D11: is_stance and active_stance survive save/load", True)(
    lambda: (lambda c: cio.loads(cio.dumps(c)) == c)(stanced("iron")))

if __name__ == "__main__":
    sys.exit(S.run())
