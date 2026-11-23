"""Package 20: rule constants as data. For every constant group a value is changed with set_rule_setting and the
result is checked with hand-computed numbers; defaults give the old results (all older suites prove that).
Run: python Wp_claude/tests/model/test_pkg20.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import magic as mg  # noqa: E402
from wp.core import weapons as wpn  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.pain import PainProfile  # noqa: E402
from wp.core.skills import Skill  # noqa: E402
from wp.core.statuses import DYING  # noqa: E402
from wp.core.weapons import Weapon  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import twf  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character, Item  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402
from wp.settings import settings_view as sv  # noqa: E402
from wp.settings.store import AppSettings  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg20")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def hero(**kw):
    base = dict(hp_rolls=(8,), hp_current=8, spirit_current=5, balance_current=5, bp_current=2, training=1000)
    base.update(kw)
    return Character(**base)


def with_k(ch, values):
    for k, v in values.items():
        ch = dispatch(ch, "set_rule_setting", key=k, value=v).state
    return ch


def spent(ch, name, /, **params):
    return ch.training - dispatch(ch, name, **params).state.training


def view(ch, fn):
    with rd.using(ch):
        return fn()


# ---------------------------------------------------------------- the accessor
S.case("a-defaults", "pkg 20: the table defaults are the old numbers (150, 30, 59, 10, 8)", (150, 30, 59, 10, 8))(
    lambda: tuple(rd.default(c) for c in ("training.ability_step", "weapons.grade_cost_base", "load.light_max_l", "ac.base",
                                          "pain.death_cap")))
S.case("a-const-override", "pkg 20: const(id, ch) reads the character's override, else the table", (100, 150))(
    lambda: (rd.const("training.ability_step", with_k(hero(), {"training.ability_step": 100})),
             rd.const("training.ability_step", hero())))
S.case("a-type-refused", "pkg 20: a constant has a type: 'x' for an int is refused", "wrong_type")(
    lambda: _reason(hero(), "set_rule_setting", key="training.ability_step", value="x"))
S.case("a-reset-view-save", "pkg 20: the view shows the override as changed; save / load keeps it; reset -> default",
       (True, 100, 150))(
    lambda: (lambda c: (sv.get(AppSettings(), c, "training.ability_step").changed,
                        cio.loads(cio.dumps(c)).rules_settings.constants["training.ability_step"],
                        rd.const("training.ability_step", dispatch(c, "reset_rule_setting", key="training.ability_step").state)))(
        with_k(hero(), {"training.ability_step": 100})))


def _reason(ch, name, **kw):
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return e.reason
    return "allowed"


# ---------------------------------------------------------------- one test per group
def str13(**kw):
    return hero(abilities={a: Ability(base=13 if a == "str" else 10) for a in ABILITIES}, **kw)


S.case("g-training", "training.md example: Str 13 -> 14 (new mod +2): 150 * 2 = 300; ability_step 100 -> 200", (300, 200))(
    lambda: (spent(str13(), "buy_ability", name="str"), spent(with_k(str13(), {"training.ability_step": 100}), "buy_ability", name="str")))
S.case("g-weapons", "weapons.md: grade cost (30 + 5X) * 1 * 1 = 30 with X 0; base 40 -> 40", (30, 40))(
    lambda: tuple(view(c, lambda: wpn.grade_cost({"g": Weapon("g")}, "g")) for c in (hero(), with_k(hero(), {"weapons.grade_cost_base": 40}))))
S.case("g-derived", "gear.md load: 65 L heavy with light max 59; light max 69 -> light", ("heavy", "light"))(
    lambda: tuple(view(c, lambda c=c: dv.load_status(c)) for c in (
        hero(items=(Item("bag", "sack", weight_l=65),)), with_k(hero(items=(Item("bag", "sack", weight_l=65),)), {"load.light_max_l": 69}))))
S.case("g-defense", "defense.md: AC base 10 -> 12 with ac.base 12", (10, 12))(
    lambda: tuple(view(c, lambda c=c: dv.ac(c)) for c in (hero(), with_k(hero(), {"ac.base": 12}))))
S.case("g-injuries", "injuries.md: 1 comfort removes 3 OT (10 -> 7); comfort_ot 4 -> 6", (7, 6))(
    lambda: tuple(run(c, ("remove_ot_comfort", {"n": 1})).trauma for c in (
        hero(trauma=10, comfort_current=2), with_k(hero(trauma=10, comfort_current=2), {"injuries.comfort_ot": 4}))))


def mage(**kw):
    return hero(level=5, hp_rolls=(8,) * 5, caster=mg.MAGE, mana=Pool(10, 10), mana_enabled=True, bp_current=6, **kw)


S.case("g-magic", "classes_magic.md: circle 2 costs 3 mana (10 -> 7); table 0,1,4,... -> 6", (7, 6))(
    lambda: tuple(run(c, ("cast_spell", {"circle": 2})).mana.current for c in (
        mage(), with_k(mage(), {"magic.circle_mana": [0, 1, 4, 5, 7, 9, 11, 13, 15, 17]}))))
S.case("g-pain", "resources.md: a NEW pain profile takes the table death cap 8 (the character's own cap is pain_profile.cap)", 8)(
    lambda: PainProfile().cap)
S.case("g-rest", "rest.md: free heal 2 + level 1 = 3: HP 2 -> 5; free_heal_base 3 -> 6", (5, 6))(
    lambda: tuple(run(c, ("short_rest", {})).hp_current for c in (hero(hp_current=2), with_k(hero(hp_current=2), {"rest.free_heal_base": 3}))))


def skilled():
    return hero(skills=(Skill("search", "int"),))


S.case("g-skills", "skills.md: make advanced = 40 with no others; promote_base 30 -> 30", (40, 30))(
    lambda: (spent(skilled(), "promote_skill", name="search"),
             spent(with_k(skilled(), {"skills.promote_base": 30}), "promote_skill", name="search")))
S.case("g-dying", "resources.md dying: -2 HP per tick (-3 -> -5); 3 per tick -> -6", (-5, -6))(
    lambda: tuple(run(c, ("tick", {})).hp_current for c in (
        hero(hp_current=-3, negative_state=DYING),
        with_k(hero(hp_current=-3, negative_state=DYING), {"dying.hp_loss": {"dying": 3, "resting": 1, "stabilized": 0}}))))
S.case("g-sheet", "resources.md: spirit 5 + 5 * Cha 0 = 5; spirit.base 6 -> 6", (5, 6))(
    lambda: tuple(view(c, lambda c=c: dv.spirit_max(c)) for c in (hero(), with_k(hero(), {"spirit.base": 6}))))


def enchanted():
    return hero(items=(Item("sw", "sword", durability=5, enchant=2, activated=True, activation_day=1, equipped=True),))


S.case("g-items", "gear.md: hardness (5 + 2 * N 2) = 9; hardness_per_enchant 3 -> 11", (9, 11))(
    lambda: tuple(view(c, lambda c=c: dv.item_view(c, "sw").durability) for c in (
        enchanted(), with_k(enchanted(), {"items.hardness_per_enchant": 3}))))
S.case("g-twf", "combat.md TWF table: -6 / -10; base penalties -4 / -8", ((-6, -10), (-4, -8)))(
    lambda: tuple(view(c, lambda: twf.penalties(False, False)) for c in (hero(), with_k(hero(), {"twf.base_penalties": [-4, -8]}))))


def three_items():
    return hero(items=tuple(Item("i%d" % n, "dagger", kind="weapon", hands=1, groups=("g",)) for n in range(3)))


S.case("g-attack", "gear.md: hands add up to 2: a third one-handed item refused; hands.max 3 -> allowed",
       ("not_enough_free_hands", "allowed"))(
    lambda: tuple(_reason(run(c, ("equip_hands", {"iid": "i0"}), ("equip_hands", {"iid": "i1"})), "equip_hands", iid="i2")
                  for c in (three_items(), with_k(three_items(), {"hands.max": 3}))))
S.case("g-narrative", "training.md option 3: 1 attention -> max(2, Con 0) = 2 OV; ov_min 3 -> 3", (2, 3))(
    lambda: tuple(run(c, ("convert_attention", {})).ov for c in (hero(attention=1), with_k(hero(attention=1), {"attention.ov_min": 3}))))
S.case("g-new-character", "progression.md: a new character has a d8 (8 HP) and 1 reaction from the table", (8, 8, 1))(
    lambda: (lambda c: (c.hit_die, c.hp_current, c.reactions))(Character()))

if __name__ == "__main__":
    sys.exit(S.run())
