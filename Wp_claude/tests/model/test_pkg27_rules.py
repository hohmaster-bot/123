"""Package 27 F (review 5 F30, F15, F22): numeric tests for the 15 rules no content suite protected, the flank cell
with the shield in either hand, and the attention -> training tenths. Numbers by hand from RULES.
Run: python Wp_claude/tests/model/test_pkg27_rules.py"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import files  # noqa: E402
from wp.app import session as sm  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import damage as dm  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import cache  # noqa: E402
from wp.model import defense_view as dfv  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import iterative as itv  # noqa: E402
from wp.model import pick_flags  # noqa: E402
from wp.model import spell_damage as sd  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character, Item, WeaponEntry  # noqa: E402
from wp.model.class_types import SpellDamage  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_pkg27_rules")
TMP = tempfile.mkdtemp(prefix="wp_p27f_")


def buff(*effects):
    return (Status("b", sid="b", effects=tuple(effects)),)


def reason(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


# ---------------------------------------------------------------- damage (resources.md, defense.md)
def _dr_resist():
    ch = Character(hp_rolls=(10,), hp_current=10, balance_current=0, statuses=buff(Effect("dr", 3),
                                                                                    Effect("resist:slashing", 5)))
    return dispatch(ch, "take_damage", amount=10, dtype="slashing").state.hp_current


S.case("r-dr-resist-larger", "defense.md (one flat reduction, the larger): slashing 10 with DR 3 and resist 5 -> "
       "5 taken, HP 10 -> 5 (not 10 - 8 = 2)", 5)(_dr_resist)
S.case("r-modifier-core", "pkg 17: a percent modifier never below -100: 10 at -150% -> 0 (not -5)", 0)(
    lambda: dm.apply_modifier(10, -150))


def _modifier_view():
    ch = Character(statuses=buff(Effect("percent:fire", -150)))
    with rd.using(ch):
        return dfv.modifier(ch, "fire")


S.case("r-modifier-view", "pkg 17: the view of percent:fire -150 shows -100", -100)(_modifier_view)


def _mana_neg():
    from wp.core.damage import Pool
    ch = Character(mana=Pool(2, 10))
    return reason(lambda: dispatch(ch, "restore_mana", amount=-1)), ch.mana.current


S.case("r-mana-negative", "pkg 22: restore_mana -1 is refused (out_of_range), mana stays 2", ("out_of_range", 2))(
    _mana_neg)


# ---------------------------------------------------------------- spells (combat.md "Spells damage")
def _spell_dice():
    return sd.component(SpellDamage(dice_count="level - 5", die_size=6), 1)["dice_count"], \
        sd.component(SpellDamage(dice_count="level - 5", die_size=6), 7)["dice_count"]


S.case("r-spell-dice", "pkg 25 F: dice level - 5 at level 1 -> 0 dice (never below 0); at level 7 -> 2", (0, 2))(
    _spell_dice)


def _rollmod():
    ch = Character(in_combat=True, morale_scale=4)
    with rd.using(ch):
        return sd.roll_modifiers(ch)


S.case("r-spell-rollmod", "combat.md: the damage roll gets pain + morale: morale scale 4 in combat -> +2, no pain -> "
       "roll modifier +2", {"pain": 0, "morale": 2, "roll_modifier": 2})(_rollmod)


# ---------------------------------------------------------------- iterative (combat.md)
def _iter_cap():
    ch = Character(iterative_count=2, statuses=buff(Effect("iterative_penalty", 10)))
    with rd.using(ch):
        return itv.step(ch), itv.penalty(ch)


S.case("r-iter-cap", "pkg 16 C: step -5 + iterative_penalty 10 -> min(0, 5) = 0; 2 attacks used -> penalty 0",
       (0, 0))(_iter_cap)


# ---------------------------------------------------------------- weapon pick flags (weapons.md)
def _flags():
    ch = Character(weapons=(WeaponEntry(Weapon("blades", scale=3), "Blades", picks=(Pick(5, "no_attack_tag"),)),
                            WeaponEntry(Weapon("axes", scale=3), "Axes", picks=(Pick(5, "ignore_cover_20"),))))
    return tuple(f["bonus"] for f in pick_flags.abilities(ch, "blades")), len(pick_flags.abilities(ch))


S.case("r-pick-flags-group", "pkg 25 E: the blades record shows only the blades pick (no_attack_tag); the sheet shows "
       "both", (("no_attack_tag",), 2))(_flags)


# ---------------------------------------------------------------- files and session (ARCH/app_layer.md)
def _newest():
    d = tempfile.mkdtemp(dir=TMP)
    files.create(d, "hero", Character(level=1))
    files.save(d, "hero", Character(level=2), "backups", 5, 10.0)    # backup of level 1
    files.save(d, "hero", Character(level=3), "backups", 5, 20.0)    # backup of level 2 (the newest)
    with open(files.path_of(d, "hero"), "w") as f:
        f.write("{broken")
    return files.restore_backup(d, "hero", "backups").level


S.case("r-backup-newest", "pkg 23 A4: the restore takes the NEWEST valid backup: level 2 (not the older level 1)", 2)(
    _newest)


def _open_clears():
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "u"), lambda: 1000.0)
    s.new("hero", Character(bp_current=6))
    s.dispatch("spend_bp", n=1)
    before = s.can_undo()
    s.open("hero")
    return before, s.can_undo(), s.can_redo()


S.case("r-open-clears-undo", "pkg 25 A: opening a character clears both stacks", (True, False, False))(_open_clears)


# ---------------------------------------------------------------- the read cache (package 23 B)
def _scope():
    ch = Character(abilities={a: Ability(base=14 if a == "dex" else 10) for a in ABILITIES})
    c2 = dispatch(ch, "set_rule_setting", key="ability.mod_base", value=12).state
    with rd.using(c2):
        a = dv.ability_mod(c2, "dex")
    return a, dv.ability_mod(c2, "dex")


S.case("r-cache-scope", "pkg 23 B: Dex 14: (14 - 12) // 2 = 1 under the character's mod_base 12, (14 - 10) // 2 = 2 "
       "outside its scope (the cache key holds the scope)", (1, 2))(_scope)


@cache.cached
def _name_of(ch, obj):
    return obj.name


def _identity():
    ch = Character()
    a, b = Item("a", "first"), Item("b", "second")
    _name_of(ch, a)
    box = cache._STORE[id(ch)]
    key_a = next(k for k in box)
    key_b = (key_a[0], (cache._arg_key(b)[0],), key_a[2])
    box[key_b] = ((a,), "stale")       # an entry made for another object (an id reused after a free)
    return _name_of(ch, b)


S.case("r-cache-identity", "pkg 23 B: a cache entry whose kept object is not the argument is not used: 'second'",
       "second")(_identity)


def _cleared():
    ch = Character(hp_rolls=(10,), hp_current=10, balance_current=0)
    with rd.using(ch):
        dv.ability_mod(ch, "dex")
    box = cache._STORE.get(id(ch))
    dispatch(ch, "take_damage", amount=1)
    return box is not None, cache._STORE.get(id(ch)) is not box


S.case("r-cache-cleared", "pkg 23 B: a command drops the cache entries made before it (the command may make new ones)",
       (True, True))(_cleared)


# ---------------------------------------------------------------- F15 flank (owner, package 27)
SHIELD = Item("sh", "heavy shield", kind="shield", hands=1, shield=2, shield_type="heavy")


def _flank(side):
    from wp.app import views as vw
    ch = Character(items=(SHIELD,), statuses=buff(Effect("ac", 3, "deflection", cells=("6",))))
    ch = dispatch(ch, "equip_hands", iid="sh", side=side).state
    with rd.using(ch):
        d = vw.defense(ch)
    return d["modes"]["flank"], d["cells"]["4"]["full"], d["cells"]["6"]["full"]


S.case("f15-left", "F15 (owner): shield left (heavy 2 covers 1 2 3 4 7), deflection +3 only in cell 6: cell 4 = 12, "
       "cell 6 = 13, flank = cell 6 = 13", (13, 12, 13))(lambda: _flank("left"))
S.case("f15-right", "F15 (owner): shield right (mirror: covers 3 2 1 6 9): cell 4 = 10, cell 6 = 10 + 2 + 3 = 15; "
       "flank = the side without a shield = cell 4 = 10", (10, 10, 15))(lambda: _flank("right"))


# ---------------------------------------------------------------- F22 attention -> training (training.md)
def _attention():
    ch = Character(attention=1, abilities={a: Ability(base=16 if a == "dex" else 10) for a in ABILITIES})
    return dispatch(ch, "attention_to_training", n=1).state.training - ch.training


S.case("f22-tenths", "training.md: Dex 16 (mod 3) -> 1.5 comfort -> 15 tenths x comfort rate 10 / 10 = 15 training",
       15)(_attention)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
