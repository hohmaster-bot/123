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
from wp.model import attack_view as av  # noqa: E402
from wp.model import maneuver_view as mv  # noqa: E402
from wp.model import stats_view as stats  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model.character import ABILITIES, Ability, AttackRecord, Character, Feat, Item, WeaponEntry  # noqa: E402
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


S.case("a3-unique", "injuries.md [OWNER pkg 12-13, Q70/Q75]: two injuries with the same name get different ids", ("cut_1", "cut_2"))(
    lambda: tuple(j.jid for j in _two_cuts().injuries))
S.case("a3-stable", "injuries.md: removing another injury keeps the ids (cut_2 stays cut_2); a freed id is never "
       "reused (pkg 13, Q75: counter) -> cut_3", ("cut_2", "cut_3"))(
    lambda: tuple(j.jid for j in run(replace(_two_cuts(), injuries=_two_cuts().injuries[1:]),
                                     ("add_injury", {"severity": "light", "name": "cut"})).injuries))


def _old_injury_save():
    from wp.core.injuries import Injury
    d = json.loads(cio.dumps(hero(injuries=(Injury("bruise", "light", 2),))))
    d["character"]["injuries"][0].pop("jid")
    return cio.loads(json.dumps(d)).injuries[0].jid


S.case("a3-old-file", "injuries.md: an old file without injury ids loads; the program gives the id", "bruise_1")(_old_injury_save)
S.case("a3-container", "buffs.md: the container view uses the injury id", ("cut_1", "cut_2"))(
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

# ---- B: maneuvers by tags ----
def longsword(**kw):
    base = dict(kind="weapon", hands=1, in_hands=True, groups=("long_swords", "heavy_weapons"), wkind="longsword")
    base.update(kw)
    return Item("ls", "long sword", **base)


def axe(**kw):
    base = dict(kind="weapon", hands=1, in_hands=True, groups=("axes",), wkind="handaxe")
    base.update(kw)
    return Item("ax", "hand axe", **base)


EXPERT = WeaponEntry(Weapon("long_swords", grades=8), picks=(Pick(5, "attack_1"), Pick(6, "attack_1"), Pick(7, "attack_1")))
RECS = (AttackRecord("r_ls", "ls", "long_swords"), AttackRecord("r_ax", "ax", "axes"))


def fighter(items=None, **kw):
    base = dict(bab=2, abilities=abil(str=14), items=items if items is not None else (longsword(),), attacks=RECS,
                weapons=(EXPERT,))
    base.update(kw)
    return hero(**base)


def man(ch, name, **fields):
    return run(ch, ("add_maneuver", dict(name=name, **fields)))


def view(ch, mid):
    return next(v for v in mv.maneuver_view(ch) if v.mid == mid)


S.case("b-tag-any", "combat.md [OWNER pkg 12 B]: tag_mode any: heavy_weapons OR polearms -> the long sword fits", True)(
    lambda: view(man(fighter(), "Cleave", required_tags=("heavy_weapons", "polearms")), "cleave").available)
S.case("b-tag-all", "combat.md: tag_mode all: long_swords AND heavy_weapons fits; long_swords AND axes does not",
       (True, False))(
    lambda: (view(man(fighter(), "A", required_tags=("long_swords", "heavy_weapons"), tag_mode="all"), "a").available,
             view(man(fighter(), "B", required_tags=("long_swords", "axes"), tag_mode="all"), "b").available))
S.case("b-two-groups", "combat.md: one weapon in two groups brings the maneuvers of both groups", (True, True))(
    lambda: (lambda c: (view(c, "lunge").available, view(c, "smash").available))(
        man(man(fighter(), "Lunge", required_tags=("long_swords",)), "Smash", required_tags=("heavy_weapons",))))
S.case("b-kind-tag", "combat.md: the weapon kind id (catalog card) is a tag too", True)(
    lambda: view(man(fighter(), "Half-sword", required_tags=("longsword",)), "half_sword").available)


def _two():
    c = man(fighter(items=(longsword(), axe())), "Feint", required_tags=("long_swords", "axes"))
    return view(c, "feint")


S.case("b-two-weapons", "combat.md: two matching weapons in hands -> two entries; the expert sword +3 higher",
       (("ls", "ax"), 3))(
    lambda: (lambda v: (tuple(w.item for w in v.weapons), v.weapons[0].to_hit - v.weapons[1].to_hit))(_two()))
S.case("b-numbers", "combat.md: entry = the weapon's main attack + maneuver modifiers (+2 hit, -1 damage)", (2, -1))(
    lambda: (lambda c: (view(c, "power").weapons[0].to_hit - av.by_record(c, "r_ls").to_hit,
                        view(c, "power").weapons[0].damage - av.by_record(c, "r_ls").damage))(
        man(fighter(), "Power", required_tags=("long_swords",), to_hit=2, damage=-1)))
S.case("b-effects-stack", "combat.md: maneuver effects competence +2 (a competence +3 status wins) and insight +1 -> +4", 4)(
    lambda: (lambda c: view(c, "aim").weapons[0].to_hit - av.by_record(replace(c, statuses=()), "r_ls").to_hit)(
        man(fighter(statuses=(Status("s", sid="s", effects=(Effect(bo.ATTACK, 3, "competence"),)),)), "Aim",
            required_tags=("long_swords",), effects=(Effect(bo.ATTACK, 2, "competence"), Effect(bo.ATTACK, 1, "insight")))))
S.case("b-unarmed", "combat.md: tag unarmed fits with empty hands; with a sword in hand -> unarmed_not_possible",
       ((True, "unarmed"), (False, ("unarmed_not_possible",))))(
    lambda: (lambda vs: ((vs[0].available, vs[0].weapons[0].item), (vs[1].available, vs[1].reasons)))(
        (view(man(fighter(items=()), "Jab", required_tags=("unarmed",)), "jab"),
         view(man(fighter(), "Jab", required_tags=("unarmed",)), "jab"))))
S.case("b-required-feat", "combat.md: required_feat missing -> unavailable (feat_missing); owned -> available",
       ((False, ("feat_missing",)), (True, ())))(
    lambda: tuple((v.available, v.reasons) for v in (
        view(man(fighter(), "Riposte", required_tags=("long_swords",), required_feat="duelist"), "riposte"),
        view(man(fighter(feats=(Feat("duelist", granted_maneuvers=("riposte",)),)), "Riposte",
                 required_tags=("long_swords",), required_feat="duelist"), "riposte"))))
S.case("b-granted-by", "training.md: a feat's granted_maneuvers id shows on the maneuver (granted_by)", ("duelist",))(
    lambda: view(man(fighter(feats=(Feat("duelist", granted_maneuvers=("riposte",)),)), "Riposte"), "riposte").granted_by)
S.case("b-weapon-gone", "combat.md: weapon put away -> unavailable (no_matching_weapon) but kept",
       (False, ("no_matching_weapon",), 1))(
    lambda: (lambda c: (view(c, "lunge").available, view(c, "lunge").reasons, len(c.maneuvers)))(
        run(man(fighter(), "Lunge", required_tags=("long_swords",)), ("unequip_hands", {"iid": "ls"}))))
S.case("b-cost-record-only", "combat.md: costs are shown, nothing is spent (balance 5, spirit 5 stay)", ((1, 2, 3), 5, 5))(
    lambda: (lambda c: (view(c, "x").cost, c.balance_current, c.spirit_current))(
        man(fighter(), "X", required_tags=("long_swords",), cost_actions=1, cost_balance=2, cost_spirit=3)))
S.case("b-edit-remove", "combat.md: edit_maneuver sets fields; remove_maneuver removes it", (("axes",), "all", ()))(
    lambda: (lambda c: (c.maneuvers[0].required_tags, c.maneuvers[0].tag_mode,
                        run(c, ("remove_maneuver", {"mid": "x"})).maneuvers))(
        run(man(fighter(), "X"), ("edit_maneuver", {"mid": "x", "required_tags": ["axes"], "tag_mode": "all"}))))
S.case("b-edit-unknown", "combat.md: an unknown field is refused (future keys go into extra)",
       "refused: unknown maneuver fields: spark (put future keys into extra)")(
    lambda: refused(man(fighter(), "X"), "edit_maneuver", mid="x", spark=3))
S.case("b-save-load", "D11: maneuvers with the extra dict survive save/load", True)(
    lambda: (lambda c: cio.loads(cio.dumps(c)) == c)(
        man(fighter(), "Spark strike", required_tags=("long_swords",), extra={"spark": 2, "steps": (1, 2)},
            effects=(Effect(bo.ATTACK, stat_mod="str"),))))


def _old_maneuver_record():
    d = json.loads(cio.dumps(fighter()))
    recs = d["character"]["attacks"]
    first = dict(recs[0])
    first.update(rid="old_m", kind="maneuver", base_record="r_ls")
    recs.append(first)
    recs[0]["kind"] = "main"
    recs[0]["base_record"] = ""
    return tuple(r.rid for r in cio.loads(json.dumps(d)).attacks)


S.case("b-old-records", "D1: an old item-bound maneuver record is dropped on load; main records stay",
       ("r_ls", "r_ax"))(_old_maneuver_record)


# ---- C: CMB per attack record (Q58) ----
def _cmbs(**kw):
    c = fighter(items=(longsword(), axe()), **kw)
    return (av.by_record(c, "r_ls").cmb, av.by_record(c, "r_ax").cmb, stats.cmb(c).total)


S.case("c-cmb-two-swords", "combat.md [OWNER pkg 12 C, Q58]: expert record CMB +3 vs the other; sheet CMB unchanged "
       "(BAB 2 + Str 2 = 4)", (7, 4, 4))(lambda: _cmbs())
S.case("c-cmb-pain-morale", "combat.md: pain 1 and morale scale 4 in combat (+2) as the sheet CMB rule -> 8, 5, 5",
       (8, 5, 5))(lambda: _cmbs(pain=(PainEntry(1),), morale_scale=4, in_combat=True))
S.case("c-cmb-in-maneuver", "combat.md: a maneuver view shows the CMB of the matching weapon (7 / 4)", (7, 4))(
    lambda: tuple(w.cmb for w in _two().weapons))

if __name__ == "__main__":
    sys.exit(S.run())
