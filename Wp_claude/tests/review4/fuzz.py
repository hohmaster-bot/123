"""Review 4: seeded fuzz of random VALID command sequences on a rich character, with invariants after every step.
Run: python Wp_claude/tests/review4/fuzz.py [sequences] [steps] [first_seed]
Prints every distinct violation once (kind, seed, step, command) with the shortest sequence found by a greedy
minimizer. A CommandError is a normal refusal, never a violation; any other exception is.
"""
import os
import random
import sys
from dataclasses import fields, replace

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

from wp.commands import CHANGED, CommandError, dispatch  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import magic as mg  # noqa: E402
from wp.core import rest as rs  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.skills import Skill  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import active_list as al  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import container_view as cv  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import maneuver_view as mv  # noqa: E402
from wp.model import pool_view as pv  # noqa: E402
from wp.model import spell_view as sv  # noqa: E402
from wp.model import stats_view as stv  # noqa: E402
from wp.model import twf  # noqa: E402
from wp.model.character import (Ability, AttackRecord, Character, Feat, Item, Maneuver, ResourcePool, Usage,  # noqa: E402
                                WeaponEntry)
from wp.storage import character_io as cio  # noqa: E402


def rich():
    ab = {a: Ability(base=b) for a, b in zip(("str", "dex", "con", "int", "wis", "cha"), (14, 13, 12, 14, 10, 12))}
    items = (
        Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("blades",), hp=10, durability=5, enchant=2,
             activation_day=1, activation_decade=5, weight_l=10, masterwork=True),
        Item("sh", "shield", kind="shield", hands=1, in_hands=True, shield=2, shield_type="heavy", hp=8, durability=5,
             skill_penalty=-1, weight_l=10),
        Item("ar", "mail", equipped=True, armor=4, armor_type="medium", hp=12, durability=6, skill_penalty=-2,
             spell_penalty_mana=1, spell_failure_pct=10, weight_l=30),
        Item("pot", "potion", consumable=True, quantity=3, weight_l=1, on_use_status="heal"),
        Item("ring", "ring", equipped=True, usage=Usage(charges_max=2, charges_current=2, recharge="long_rest",
                                                          cooldown_rounds=1)),
        Item("dg", "dagger", kind="weapon", hands=1, groups=("blades",), crit_range=19, hp=4, durability=10, weight_l=1),
    )
    statuses = (
        ef.Status("rage", sid="rage", effects=(ef.Effect(bo.ATTACK, 2, bo.MORALE),), duration=ef.TICKS, full_ticks=3,
                  charges=Pool(2, 2), active=False),
        ef.Status("aura", sid="aura", effects=(ef.Effect(bo.AC, 1, "luck"),), duration=ef.TICKS, full_ticks=3,
                  charge_source="ki", charge_per_round=1, active=False),
        ef.Status("bleed", sid="bleed", per_tick_hp=-2, duration=ef.TICKS, full_ticks=2, active=False),
        ef.Status("heal", sid="heal", per_tick_hp=2, duration=ef.TICKS, full_ticks=2, active=False),
        ef.Status("guard", sid="guard", duration=ef.END_OF_COMBAT, one_shot=(ef.OneShot(ef.TEMP_HP, 4),), active=False),
        ef.Status("calm", sid="calm", per_tick_restore={"spirit": 1}, duration=ef.TICKS, full_ticks=2, active=False),
    )
    feats = (Feat("stance", title="stance", is_stance=True, effects=(ef.Effect(bo.AC, 2, bo.DODGE),)),
             Feat("power", title="power", usage=Usage(charges_max=1, charges_current=1, recharge="short_rest")))
    return Character(level=5, bab=4, abilities=ab, hp_rolls=(10, 6, 6, 6, 6), hit_die=10, hp_current=39, bp_current=10,
                     balance_current=10, balance_bonus=2, spirit_current=8, caster=mg.MAGE, mana=Pool(12, 12),
                     mana_enabled=True, slots={0: Pool(2, 2)}, comfort_current=5, attention=3, trauma=6,
                     items=items, statuses=statuses, feats=feats, armor_grade="medium", shield_grade="heavy",
                     weapons=(WeaponEntry(Weapon("blades", grades=8), picks=(Pick(5, "durability_30"), Pick(6, "crit_1"),
                                                                            Pick(7, "attack_1"), Pick(8, "hp_1"))),),
                     attacks=(AttackRecord("r", "sw", "blades", primary=True), AttackRecord("d", "dg", "blades")),
                     maneuvers=(Maneuver("trip", "trip", required_tags=("blades",), to_hit=1, cost_balance=2),),
                     pools=(ResourcePool("ki", "ki", 4, 4, "short_rest"), ResourcePool("fp", "fp", "con_mod + level", 6,
                                                                                       "long_rest")),
                     skills=(Skill("climb", "str", armor_penalty_applies=True), Skill("lore", "int", "advanced", 2)))


ITEMS = ("sw", "sh", "ar", "pot", "ring", "dg")
EXTENDED = False
STATUSES = ("rage", "aura", "bleed", "heal", "guard", "calm")


def random_step(r, ch):
    """(command, params) chosen at random; params are in their valid ranges (refusals are fine)."""
    it = r.choice(ITEMS)
    st = r.choice(STATUSES)
    menu = [
        ("take_damage", {"amount": r.randint(0, 14), "dtype": r.choice(("physical", "fire"))}),
        ("damage_to_balance", {"amount": r.randint(0, 8)}),
        ("pay_hp_cost", {"amount": r.randint(0, 8)}),
        ("spend_balance", {"n": r.randint(0, 5)}),
        ("restore", {"resource": r.choice(("hp", "balance", "spirit", "bp", "comfort")), "amount": r.randint(0, 9)}),
        ("spend_bp", {"n": r.randint(0, 3)}),
        ("short_rest", {"spends": r.choice(([], [(rs.OPT_HEAL, {})], [(rs.OPT_PAIN, {})], [(rs.OPT_SPIRIT, {})],
                                             [(rs.OPT_CHARGES, {})])), "keep_overcap": r.random() < 0.3}),
        ("long_rest", {}),
        ("tick", {}), ("tick", {}), ("tick", {}),
        ("start_combat", {}), ("end_combat", {}),
        ("cast_spell", {"circle": r.randint(0, 3), "penalty_balance": r.randint(0, 1)}),
        ("activate_status", {"sid": st}), ("activate_status", {"sid": st}),
        ("remove_status", {"sid": st}),
        ("set_status_duration", {"sid": st, "remaining": r.randint(0, 4)}),
        ("use_consumable", {"iid": "pot"}),
        ("activate_item", {"iid": it, "kind": r.choice((None, "day", "decade"))}),
        ("deactivate_item", {"iid": it}),
        ("damage_item", {"iid": it, "amount": r.randint(0, 6)}),
        ("hit_item", {"iid": it, "damage": r.randint(0, 25)}),
        ("equip_item", {"iid": it}), ("unequip_item", {"iid": it}),
        ("equip_hands", {"iid": it}), ("unequip_hands", {"iid": it}),
        ("spend_charge", {"owner_kind": r.choice(("item", "feat", "status")),
                          "owner_id": r.choice(("ring", "power", "rage"))}),
        ("spend_pool", {"pid": r.choice(("ki", "fp")), "n": r.randint(0, 3)}),
        ("restore_pool", {"pid": r.choice(("ki", "fp"))}),
        ("set_active_stance", {"fid": r.choice((None, "stance", "power"))}),
        ("add_injury", {"severity": r.choice(("light", "medium")), "name": "cut"}),
        ("remove_ot_comfort", {"n": 1}),
        ("exchange_comfort", {"n": 1}),
        ("convert_attention", {}),
        ("end_cycle", {}),
        ("set_temp_hp", {"value": r.randint(0, 5)}),
        ("level_up", {"hp_roll": r.randint(1, 10)}),
        ("buy_skill_rank", {"name": r.choice(("climb", "lore"))}),
    ]
    if EXTENDED:       # destructive commands (run with a 4th argument "x")
        menu += [("remove_item", {"iid": it}), ("delete_status", {"sid": st}), ("remove_feat", {"fid": "stance"}),
                 ("set_twf", {"rid": "r", "off": "d", "on": True}), ("remove_attack", {"rid": r.choice(("r", "d"))}),
                 ("add_attack", {"iid": it}), ("remove_pool", {"pid": "ki"})]
    return menu[r.randrange(len(menu))]


def views(ch):
    """Every derived view must work on any reachable state."""
    for m in (acm.FRONT, acm.FLANK, acm.FLAT_FOOTED, acm.PARRY, acm.TOUCH):
        dv.ac(ch, m)
    for r in ch.attacks:
        if r.twf:
            twf.combination(ch, r.rid)
    av.all_records(ch)
    av.all_attacks(ch)
    stv.view(ch)
    sv.view(ch)
    mv.maneuver_view(ch)
    cv.container_view(ch)
    al.active_list(ch)
    dv.weight_view(ch)
    for it in ch.items:
        dv.item_view(ch, it.iid)
    for s in ch.skills:
        dv.skill_bonus(ch, s.name)
    dv.speed(ch)
    dv.balance_regen(ch)


def _no_log(ch):
    return replace(ch, log=(), log_seq=0)


def invariants(before, after, result, cmd):
    """List of violation kinds."""
    out = []
    ch = after

    def need(cond, kind):
        if not cond:
            out.append(kind)
    need(ch.temp_hp >= 0 and all(s.temp_hp_left >= 0 for s in ch.statuses), "temp HP below 0")
    need(ch.balance_current >= 0, "balance below 0")
    need(ch.bp_current >= 0, "BP below 0")
    need(ch.trauma >= 0 and ch.overload >= 0 and ch.ov >= 0 and ch.attention >= 0, "counter below 0")
    need(ch.comfort_current >= 0 and ch.spirit_current >= 0 and ch.training >= 0, "resource below 0")
    need(ch.mana.current >= 0 and all(p.current >= 0 for p in ch.slots.values()), "mana or slot below 0")
    need(all(0 <= pv.current(ch, p) <= pv.max_of(ch, p) for p in ch.pools), "pool read out of bounds")
    need(all(s.charges is None or s.charges.current >= 0 for s in ch.statuses), "status charges below 0")
    need(all(it.quantity >= 0 for it in ch.items), "item quantity below 0")
    need(all(it.usage is None or 0 <= it.usage.charges_current <= max(it.usage.charges_max, it.usage.charges_current)
             for it in ch.items), "item charges out of bounds")
    need(not ch.in_combat or ch.combat_round >= 1, "combat round 0 in combat")
    need(ch.in_combat or (ch.combat_round == 0 and ch.balance_cap_start is None), "combat data left after combat")
    need(ch.negative_state is None or ch.hp_current < 0, "negative state at HP >= 0")
    need(dv.hands_used(ch) <= 2, "more than 2 hands used")
    need(not any(s.active and s.duration == ef.TICKS and s.remaining <= 0 for s in ch.statuses),
         "active N-ticks status with 0 ticks left")
    # heal-type commands never raise HP above max
    if cmd in ("restore", "tick", "short_rest", "long_rest") and before.hp_current <= dv.hp_max(before):
        need(ch.hp_current <= dv.hp_max(ch), "gameplay restore above max HP")
    # weight: unit weight * quantity of carried items, the bag skipped while ignored
    exp = sum(it.weight_l * it.quantity for it in ch.items if it.carried
              and not (ch.ignore_bag_weight and dv.in_bag(it)))
    need(dv.carried_weight_l(ch) == exp, "carried weight != sum of items")
    # save / load
    try:
        need(cio.loads(cio.dumps(ch)) == ch, "save/load round trip differs")
    except Exception as e:  # noqa: BLE001
        out.append("save/load raised %s" % type(e).__name__)
    # journal
    if CHANGED in result.events:
        need(len(ch.log) == len(before.log) + 1, "journal did not grow by 1 on a change")
        if _no_log(ch) == _no_log(before):
            out.append("journal entry for a command that changed nothing: %s" % cmd)
    else:
        need(ch.log == before.log, "journal changed on a soft refusal")
    try:
        views(ch)
    except Exception as e:  # noqa: BLE001
        out.append("derived view raised %s: %s" % (type(e).__name__, e))
    return out


def replay(steps):
    """(violations of the last step, error) for a fixed list of steps from the rich character."""
    ch = rich()
    last = []
    for cmd, params in steps:
        try:
            res = dispatch(ch, cmd, **params)
        except CommandError:
            last = []
            continue
        except Exception as e:  # noqa: BLE001
            return ["exception %s in %s: %s" % (type(e).__name__, cmd, e)]
        last = invariants(ch, res.state, res, cmd)
        ch = res.state
    return last


def minimize(steps, kind):
    """Greedy: drop steps one by one while the last step still shows the same violation kind."""
    steps = list(steps)
    i = 0
    while i < len(steps) - 1:
        trial = steps[:i] + steps[i + 1:]
        if any(k == kind for k in replay(trial)):
            steps = trial
        else:
            i += 1
    return steps


def main(n_seq=300, n_steps=50, first=1):
    seen = {}
    steps_run = refusals = 0
    for seed in range(first, first + n_seq):
        r = random.Random(seed)
        ch = rich()
        hist = []
        for i in range(n_steps):
            cmd, params = random_step(r, ch)
            hist.append((cmd, params))
            steps_run += 1
            try:
                res = dispatch(ch, cmd, **params)
            except CommandError:
                refusals += 1
                continue
            except Exception as e:  # noqa: BLE001
                kind = "exception %s in %s: %s" % (type(e).__name__, cmd, e)
                seen.setdefault(kind, (seed, i, list(hist)))
                break
            for kind in invariants(ch, res.state, res, cmd):
                seen.setdefault(kind, (seed, i, list(hist)))
            ch = res.state
    print("sequences %d, steps %d, refusals %d, distinct violations %d" % (n_seq, steps_run, refusals, len(seen)))
    for kind, (seed, i, hist) in sorted(seen.items()):
        short = minimize(hist, kind)
        print("- %s | seed %d step %d | shortest %d steps: %s" % (
            kind, seed, i, len(short), " ; ".join("%s%s" % (c, p if p else "") for c, p in short)))


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 3 and args[3] == "x":
        EXTENDED = True
    main(*[int(x) for x in args[:3]])
