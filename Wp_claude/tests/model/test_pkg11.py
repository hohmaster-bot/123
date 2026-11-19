"""Package 11: status container, stat-mod effect values, race size and speed, feat effects.
Run: python Wp_claude/tests/model/test_pkg11.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.injuries import Injury  # noqa: E402
from wp.model import container_view as cv  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.catalog import skills_catalog as sc  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import stats_view as stv  # noqa: E402
from wp.core import skills as sk  # noqa: E402
from wp.catalog import feats_catalog as fc  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character, Feat, Item  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg11")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def refused(ch, name, **kw):
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return "refused: " + str(e).split(":")[0]
    return "allowed"


def hero(**kw):
    base = dict(hp_rolls=(20,), hp_current=20, spirit_current=5, balance_current=5, bp_current=5)
    base.update(kw)
    return Character(**base)


ATK2 = (Effect(bo.ATTACK, 2),)


def rage(cur=2, mx=3, **kw):
    return Status("Rage", sid="rage", effects=ATK2, duration=ef.TICKS, full_ticks=5, charges=Pool(cur, mx), **kw)


def haste(**kw):
    return Status("Haste", sid="haste", effects=ATK2, duration=ef.TICKS, full_ticks=3, **kw)


def st(ch, sid):
    return next(s for s in ch.statuses if s.sid == sid)


def added(*statuses, **kw):
    ch = hero(**kw)
    for s in statuses:
        ch = run(ch, ("add_status", {"status": s}))
    return ch


# ---- A: container ----
S.case("a-add-inactive", "buffs.md [OWNER pkg 11 A]: a new entry starts inactive: no charge spent, no bonus",
       (False, 2, 0))(
    lambda: (lambda c: (st(c, "rage").active, st(c, "rage").charges.current, dv.total(c, bo.ATTACK)))(added(rage())))
S.case("a-activate-charges", "buffs.md: activate with charges: one spent, full duration per charge, bonus +2",
       (True, 1, 5, 2))(
    lambda: (lambda c: (st(c, "rage").active, st(c, "rage").charges.current, st(c, "rage").remaining,
                        dv.total(c, bo.ATTACK)))(run(added(rage()), ("activate_status", {"sid": "rage"}))))
S.case("a-activate-no-charges", "buffs.md: an entry without charges just becomes active (full duration 3)", (True, 3))(
    lambda: (lambda s: (s.active, s.remaining))(st(run(added(haste()), ("activate_status", {"sid": "haste"})), "haste")))
S.case("a-add-active", "buffs.md: add with active=True starts it at once (charge spent)", (True, 1))(
    lambda: (lambda s: (s.active, s.charges.current))(
        st(run(hero(), ("add_status", {"status": rage(), "active": True})), "rage")))
S.case("a-refuse-no-charge", "buffs.md: no charge left -> refused", "refused: no charges left")(
    lambda: refused(added(rage(cur=0)), "activate_status", sid="rage"))
S.case("a-refuse-active", "buffs.md: already active -> refused", "refused: status Haste is already active")(
    lambda: refused(run(added(haste()), ("activate_status", {"sid": "haste"})), "activate_status", sid="haste"))
S.case("a-refuse-cost", "buffs.md: the cost cannot be paid (2 spirit, have 1) -> refused",
       "refused: cannot pay 2 spirit for Haste (have 1)")(
    lambda: refused(added(haste(cost_resource="spirit", cost_amount=2), spirit_current=1), "activate_status", sid="haste"))
S.case("a-cost-paid", "buffs.md: activation pays the cost (spirit 5 -> 3)", 3)(
    lambda: run(added(haste(cost_resource="spirit", cost_amount=2)), ("activate_status", {"sid": "haste"})).spirit_current)
S.case("a-remove-early", "buffs.md: remove_status ends it now: inactive, time cleared, entry stays, bonus gone",
       (False, 0, 1, 0))(
    lambda: (lambda c: (st(c, "haste").active, st(c, "haste").remaining, len(c.statuses), dv.total(c, bo.ATTACK)))(
        run(added(haste()), ("activate_status", {"sid": "haste"}), ("remove_status", {"sid": "haste"}))))
S.case("a-remove-inactive", "buffs.md: removing an inactive status is refused", "refused: status Haste is not active")(
    lambda: refused(added(haste()), "remove_status", sid="haste"))


def _run_ticks(ch, n):
    out = []
    for _ in range(n):
        ch = run(ch, ("tick", {}))
        out.append((st(ch, "haste").active, dv.total(ch, bo.ATTACK)))
    return out


S.case("a-full-duration", "buffs.md: 3 ticks: bonus while active, inactive after the 3rd tick, entry stays",
       [(True, 2), (True, 2), (False, 0), (False, 0)])(
    lambda: _run_ticks(run(added(haste()), ("activate_status", {"sid": "haste"})), 4))
S.case("a-inactive-no-tick", "buffs.md: an inactive status does not tick and gives nothing (remaining 4 stays)", (4, 0))(
    lambda: (lambda c: (st(c, "haste").remaining, dv.total(c, bo.ATTACK)))(
        run(hero(statuses=(haste(active=False, remaining=4),)), ("tick", {}))))
S.case("a-hidden", "buffs.md: hidden is display only: still gives the bonus and ticks (3 -> 2)", (True, 2, 2))(
    lambda: (lambda c: (st(c, "haste").hidden, dv.total(c, bo.ATTACK), st(c, "haste").remaining))(
        run(added(haste()), ("activate_status", {"sid": "haste"}), ("set_status_hidden", {"sid": "haste", "value": True}),
            ("tick", {}))))
S.case("a-favorite", "buffs.md: favorite flag -> container favorites list", ("haste",))(
    lambda: cv.container_view(run(added(haste(), rage()), ("set_status_favorite", {"sid": "haste"}))).favorites)
S.case("a-delete", "buffs.md: delete_status removes the entry from the container", ("rage",))(
    lambda: tuple(s.sid for s in run(added(haste(), rage()), ("delete_status", {"sid": "haste"})).statuses))
S.case("a-charges-long-rest", "rest.md (unchanged): the long rest restores status charges (1/3 -> 3/3)", 3)(
    lambda: st(run(added(rage()), ("activate_status", {"sid": "rage"}), ("long_rest", {})), "rage").charges.current)
S.case("a-charges-short-rest", "rest.md (unchanged): the short rest does not restore status charges (1 stays)", 1)(
    lambda: st(run(added(rage()), ("activate_status", {"sid": "rage"}), ("short_rest", {})), "rage").charges.current)
S.case("a-container-kinds", "buffs.md: the container lists statuses, injuries and item effects",
       (("status", "rage", True), ("injury", "injury:0", False), ("item", "ring", False)))(
    lambda: tuple((e.kind, e.eid, e.manageable) for e in cv.container_view(hero(
        statuses=(rage(),), injuries=(Injury("cut", "light", 2),),
        items=(Item("ring", "ring", equipped=True, effects_off=ATK2),))).entries))
S.case("a-temp-hp-ends", "resources.md: temp HP of a status go when it ends early (5 -> 0, stored 0)", (5, 0, 0))(
    lambda: (lambda c: (dv.temp_hp_total(c), dv.temp_hp_total(run(c, ("remove_status", {"sid": "aid"}))),
                        st(run(c, ("remove_status", {"sid": "aid"})), "aid").temp_hp_left))(
        run(hero(), ("add_status", {"active": True, "status": Status(
            "aid", sid="aid", one_shot=(ef.OneShot(ef.TEMP_HP, 5),), duration=ef.TICKS, full_ticks=3)}))))


def _old_save():
    """A save written before package 11: statuses without the new fields still load."""
    d = json.loads(cio.dumps(hero(statuses=(haste(),))))
    for s in d["character"]["statuses"]:
        for k in ("full_ticks", "cost_resource", "cost_amount", "hidden", "favorite"):
            s.pop(k, None)
    return cio.loads(json.dumps(d)).statuses[0].full_ticks


S.case("a-old-save", "D11: an old save without the new status fields loads (defaults)", 0)(_old_save)


# ---- B: stat-mod as an effect value (Q65) ----
def abil(**scores):
    return {a: Ability(base=scores.get(a, 10)) for a in ABILITIES}


def with_status(effects, **scores):
    cat = sc.load_default()
    return hero(abilities=abil(**scores), skills=(sc.make_skill(cat, "intimidate"),),
                statuses=(Status("x", sid="x", effects=effects),))


STR_INTIM = (Effect(bo.skill_target("intimidate"), stat_mod="str"),)


def intim(ch):
    return dv.skill_bonus(ch, "intimidate")


S.case("b-str-to-intimidate", "buffs.md [OWNER Q65]: +Str mod to Intimidation (Cha 12 +1, Str 16 +3) = 4; without 1",
       (4, 1))(
    lambda: (intim(with_status(STR_INTIM, str=16, cha=12)), intim(with_status((), str=16, cha=12))))


def _sword_dmg(effects, **scores):
    ch = with_status(effects, **scores)
    ch = Character(**{**ch.__dict__, "items": (Item("sw", "sword", kind="weapon", hands=1, in_hands=True,
                                                     groups=("blades",)),)})
    ch = dispatch(ch, "add_attack", iid="sw", group="blades").state
    return av.by_record(ch, ch.attacks[0].rid).damage


S.case("b-dex-to-damage", "buffs.md: +Dex mod to damage (Dex 18 +4, Str 10): damage 4", 4)(
    lambda: _sword_dmg((Effect(bo.DAMAGE, stat_mod="dex"),), dex=18))


def _str_damaged():
    ch = with_status(STR_INTIM, str=16, cha=12)
    a = dict(ch.abilities)
    a["str"] = Ability(base=16, damage=4)             # stat damage: Str 16 -> 12 (+1)
    return intim(Character(**{**ch.__dict__, "abilities": a}))


S.case("b-stat-damage", "buffs.md: read on the CURRENT modifier: Str 16 damaged by 4 -> +1, total 2", 2)(_str_damaged)
S.case("b-negative-mod", "buffs.md: a negative modifier gives a negative value (Str 6 -> -2): Cha 12 +1 - 2 = -1", -1)(
    lambda: intim(with_status(STR_INTIM, str=6, cha=12)))
S.case("b-stacks-flat", "defense.md stacking: untyped stat-mod +3 and untyped +1 add up -> attack 4", 4)(
    lambda: dv.total(with_status((Effect(bo.ATTACK, stat_mod="str"), Effect(bo.ATTACK, 1)), str=16), bo.ATTACK))
S.case("b-typed-no-stack", "defense.md stacking: competence stat-mod +3 and competence +2 -> the larger, 3", 3)(
    lambda: dv.total(with_status((Effect(bo.ATTACK, btype="competence", stat_mod="str"),
                                  Effect(bo.ATTACK, 2, "competence")), str=16), bo.ATTACK))
S.case("b-multiplier", "buffs.md: multiplier 2 -> Str +3 * 2 = 6 to attack", 6)(
    lambda: dv.total(with_status((Effect(bo.ATTACK, stat_mod="str", multiplier=2),), str=16), bo.ATTACK))
S.case("b-ac-layer", "defense_layers.md: a dodge effect of +Wis mod (Wis 14 +2) raises the dodge layer -> AC 12", 12)(
    lambda: dv.ac(with_status((Effect(bo.AC, btype=bo.DODGE, stat_mod="wis"),), wis=14)))


# ---- C: race size and speed ----
def sized(size):
    return hero(size=size, bab=2, abilities=abil(str=12, dex=12))


S.case("c-sizes", "combat.md [OWNER pkg 11 C]: BAB 2, Str/Dex 12: (attack, AC, CMB, CMD) small (+1,12,2,13) medium (0,11,3,14) large (-1,10,4,15)",
       ((1, 12, 2, 13), (0, 11, 3, 14), (-1, 10, 4, 15)))(
    lambda: tuple((dv.size_mod(c), dv.ac(c), stv.cmb(c).total, stv.cmd(c).total)
                  for c in (sized(z) for z in ("small", "medium", "large"))))
S.case("c-size-in-attack", "combat.md: the unarmed attack of a small character gets +1 (BAB 2 + Str 1 + size 1 = 4)", 4)(
    lambda: next(a for a in av.all_attacks(sized("small"))).to_hit)
S.case("c-base-speed", "combat.md: base speed default 20 ft; a race with 30", (20, 30))(
    lambda: (dv.speed(hero()), dv.speed(hero(base_speed=30))))
S.case("c-speed-item", "combat.md: +10 ft from a worn item (target speed)", 30)(
    lambda: dv.speed(hero(items=(Item("b", "boots", equipped=True, effects_off=(Effect(bo.SPEED, 10, "enhancement"),)),))))
S.case("c-speed-status", "combat.md: a status -5 ft (slowed), only while active", (15, 20))(
    lambda: (dv.speed(hero(statuses=(Status("slow", sid="s", effects=(Effect(bo.SPEED, -5),)),))),
             dv.speed(hero(statuses=(Status("slow", sid="s", effects=(Effect(bo.SPEED, -5),), active=False),)))))
S.case("c-speed-overload", "gear.md: overload -10 ft (20 -> 10)", (True, 10))(
    lambda: (lambda c: (dv.overloaded(c), dv.speed(c)))(hero(items=(Item("rock", "rock", weight_l=300),))))
S.case("c-speed-no-morale", "combat.md: speed is not a roll: morale and pain do not change it", 20)(
    lambda: dv.speed(hero(in_combat=True, morale_scale=6)))
S.case("c-set-size-refused", "combat.md: size is small / medium / large only", "refused: size must be one of small, medium, large")(
    lambda: refused(hero(), "set_size", size="huge"))
S.case("c-set-size", "set_size / set_base_speed commands", ("large", 30))(
    lambda: (lambda c: (c.size, c.base_speed))(run(hero(), ("set_size", {"size": "large"}), ("set_base_speed", {"feet": 30}))))


def _old_size_save():
    d = json.loads(cio.dumps(hero()))
    d["character"]["size_cmb"] = 1
    d["character"]["size_mod"] = -1
    c = cio.loads(json.dumps(d))
    return (c.size, dv.size_mod(c))


S.case("c-old-save", "D1/D11: an old file with size_mod / size_cmb loads; the fields are dropped (size medium)", ("medium", 0))(
    _old_size_save)


# ---- D: feats with effects (Q68) ----
def with_feat(*effects, **kw):
    cat = sc.load_default()
    base = dict(abilities=abil(str=16, dex=14), skills=(sc.make_skill(cat, "intimidate"),),
                items=(Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("blades",)),),
                feats=(Feat("ft", title="Feat", effects=effects),))
    base.update(kw)
    ch = dispatch(hero(**base), "add_attack", iid="sw", group="blades").state
    return ch


def _atk11(ch):
    return av.by_record(ch, ch.attacks[0].rid)


S.case("d-attack-damage", "training.md [OWNER pkg 11 D]: feat +1 attack, +2 damage reach the attack view (Str 16: 4 / 5)",
       (4, 5))(
    lambda: (lambda a: (a.to_hit, a.damage))(_atk11(with_feat(Effect(bo.ATTACK, 1), Effect(bo.DAMAGE, 2)))))
S.case("d-skill-statmod", "pkg 11 D + B: feat +Str mod to Intimidation (Str 16 -> +3)", 3)(
    lambda: dv.skill_bonus(with_feat(Effect(bo.skill_target("intimidate"), stat_mod="str")), "intimidate"))
S.case("d-speed", "pkg 11 D: feat +10 ft speed -> 30", 30)(
    lambda: dv.speed(with_feat(Effect(bo.SPEED, 10))))
S.case("d-remove-feat", "pkg 11 D: removing the feat removes its effect (attack 4 -> 3)", (4, 3))(
    lambda: (lambda c: (_atk11(c).to_hit, _atk11(run(c, ("remove_feat", {"fid": "ft"}))).to_hit))(
        with_feat(Effect(bo.ATTACK, 1))))


def _catalog_feat():
    cat = fc.parse(json.dumps({"format": "wipefinder.feats", "version": 1, "feats": [
        {"fid": "brute", "name": "Brute", "cost": 200, "granted_maneuvers": ["shove"],
         "effects": [{"target": "attack", "value": 1}, {"target": "skill:intimidate", "stat_mod": "str"}]}]}))
    ch = run(with_feat(), ("remove_feat", {"fid": "ft"}), ("add_feat", {"catalog": cat, "fid": "brute"}))
    f = ch.feats[0]
    return (len(f.effects), f.granted_maneuvers, _atk11(ch).to_hit, dv.skill_bonus(ch, "intimidate"))


S.case("d-catalog", "catalog.md: a catalog feat carries effects and granted_maneuvers to the sheet", (2, ("shove",), 4, 3))(
    _catalog_feat)
S.case("d-feat-save-load", "D11: feat effects and granted_maneuvers survive save/load", True)(
    lambda: (lambda c: cio.loads(cio.dumps(c)) == c)(hero(feats=(Feat("ft", effects=(Effect(bo.ATTACK, stat_mod="str"),),
                                                                    granted_maneuvers=("trip",)),))))


# ---- owner answers recorded in RULES ----
S.case("q56-initiative-morale", "defense.md [OWNER Q56]: Dex 14 +2 competence = 4; morale scale 2 in combat 5, out of combat 4",
       (5, 4))(
    lambda: tuple(stv.initiative(hero(abilities=abil(dex=14), morale_scale=2, in_combat=c,
                                      statuses=(Status("c", sid="c", effects=(Effect(bo.INITIATIVE, 2, "competence"),)),))).total
                  for c in (True, False)))


def _adv(new_rank, level):
    try:
        return sk.rank_step_cost(sk.ADVANCED, new_rank, level)
    except ValueError:
        return "refused"


S.case("q64-advanced-cap", "skills.md [OWNER Q64]: level 2, advanced rank 2 -> 3 refused; 1 -> 2 costs 30", ("refused", 30))(
    lambda: (_adv(3, 2), _adv(2, 2)))
S.case("q55-save-stats", "defense.md [OWNER Q55]: Fort Con, Ref Dex, Will Wis", {"fort": "con", "ref": "dex", "will": "wis"})(
    lambda: dict(Character().save_stats))

if __name__ == "__main__":
    sys.exit(S.run())
