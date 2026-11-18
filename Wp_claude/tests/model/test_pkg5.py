"""Package 5: owner answers (dodge/Dex, enhancement layer, shields, ids, shield attacks, enchantment).
Run: python Wp_claude/tests/model/test_pkg5.py"""
import os
import sys
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.core import ac as acm  # noqa: E402
from wp.core import ac_layers as L  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import ids  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.model.character import SHIELD, Character, Item  # noqa: E402

S = Suite("test_pkg5")


def layers(mode=acm.FRONT, **kw):
    return dict(acm.parts(acm.AcInput(**kw), mode))


def dodge(v):
    return bo.Bonus(v, bo.DODGE, bo.AC)


def pick(p, *keys):
    return tuple(p[k] for k in keys)


# ---- A: dodge layer = dodge bonuses + Dex mod ----
S.case("a-dex-2-dodge+1", "defense_layers.md [OWNER pkg 5]: Dex -2, dodge +1 -> sum -1: base 9, dodge 0, flat 0",
       (0, 0, 9))(
    lambda: (lambda p: (p["dodge"], p["flat"], L.base(tuple(p.items()))))(layers(dex_mod=-2, bonuses=(dodge(1),))))
S.case("a-dex-2-dodge+1-ff", "defense_layers.md: Dex -2, dodge +1, flat-footed -> base 8", (0, 8))(
    lambda: (lambda p: (p["dodge"], L.base(tuple(p.items()))))(
        layers(acm.FLAT_FOOTED, dex_mod=-2, bonuses=(dodge(1),))))
# Owner example: Dex -2, armor 8: base 8, position 1-7, armor 8-15, exact 16, hit 17+; flat-footed the same.
_EX = (("position", None, 7), ("armor", 8, 15), ("exact", 16, 16), ("hit", 17, None))
S.case("a-example-ladder", "defense_layers.md Example [OWNER pkg 5]: Dex -2, armor 8 (front and flat-footed)",
       (_EX, _EX))(
    lambda: tuple(tuple((r.layer, r.lo, r.hi) for r in L.ladder(acm.parts(acm.AcInput(dex_mod=-2, armor=8), m)))
                  for m in (acm.FRONT, acm.FLAT_FOOTED)))
S.case("a-example-rolls", "defense_layers.md: rolls 7 position, 8 armor, 16 exact, 17 hit", ("position", "armor", "exact", "hit"))(
    lambda: tuple(L.layer_for_roll(acm.parts(acm.AcInput(dex_mod=-2, armor=8)), r)[0] for r in (7, 8, 16, 17)))
S.case("a-untyped-split", "defense_layers.md: untyped +3 to flat, untyped -1 lowers the base", (3, -1))(
    lambda: pick(layers(bonuses=(bo.Bonus(3, bo.FLAT, bo.AC), bo.Bonus(-1, bo.FLAT, bo.AC))), "flat", "penalty"))
S.case("a-dex+2-dodge+1", "defense_layers.md: Dex +2, dodge +1 -> dodge 3", (3, 0))(
    lambda: pick(layers(dex_mod=2, bonuses=(dodge(1),)), "dodge", "flat"))
S.case("a-dex+2-dodge+1-ff", "defense_layers.md: Dex +2, dodge +1, flat-footed -> 0", (0, 0))(
    lambda: pick(layers(acm.FLAT_FOOTED, dex_mod=2, bonuses=(dodge(1),)), "dodge", "flat"))
S.case("a-real-ac", "defense_layers.md: real AC = 10 + sum of layers (Dex -2, dodge +1, armor 3: 12; ff 11)",
       (12, 12, 11, 11))(
    lambda: (lambda i: (acm.ac(i), L.ac_total(acm.parts(i)), acm.ac(i, acm.FLAT_FOOTED),
                        L.ac_total(acm.parts(i, acm.FLAT_FOOTED))))(
        acm.AcInput(dex_mod=-2, armor=3, bonuses=(dodge(1),))))

# ---- B: enhancement goes to the armor layer; other unlisted types go to flat ----
S.case("b-enhancement-armor", "defense_layers.md [OWNER Q26]: enhancement +2 raises the armor layer (4 -> 6)", (6, 0))(
    lambda: pick(layers(armor=4, bonuses=(bo.Bonus(2, bo.ENHANCEMENT, bo.AC),)), "armor", "flat"))
S.case("b-sacred-flat", "defense_layers.md: sacred +2 is not a layer; in AC it goes to flat (assumption)", (0, 2, 12))(
    lambda: (lambda p: (p["armor"], p["flat"], 10 + sum(p.values())))(
        layers(bonuses=(bo.Bonus(2, "sacred", bo.AC),))))
S.case("b-enhancement-touch", "defense.md: touch ignores armor, so its enhancement too", 0)(
    lambda: layers(acm.TOUCH, armor=4, bonuses=(bo.Bonus(2, bo.ENHANCEMENT, bo.AC),))["armor"])


# ---- C: shields: type on the card, heavy/tower add the shield bonus to balance max while in a hand ----
def shield_char(stype, in_hands=True, bonus=2, grade="tower"):
    """Package 8 D1: the balance bonus needs the shield grade; "tower" grade covers every type."""
    sh = Item("sh", "shield", kind=SHIELD, hands=1, in_hands=in_hands, shield=bonus, shield_type=stype)
    return Character(hp_rolls=(8,), hp_current=8, bp_current=2, items=(sh,), shield_grade=grade)


S.case("c-heavy-in-hand", "training.md [OWNER Q28]: heavy shield +2 in hand -> balance max +2", 2)(
    lambda: dv.balance_max(shield_char("heavy")) - dv.balance_max(shield_char("")))
S.case("c-heavy-in-bag", "training.md: heavy shield in the bag -> no balance bonus", 0)(
    lambda: dv.balance_max(shield_char("heavy", in_hands=False)) - dv.balance_max(shield_char("")))
S.case("c-tower-light", "training.md: tower +3 -> +3; light shield -> +0", (3, 0))(
    lambda: (dv.shield_balance_bonus(shield_char("tower", bonus=3)), dv.shield_balance_bonus(shield_char("light"))))


# ---- F: parry from proficiency: armor 0/2/4/6, tower shields grade +2 ----
def parry_of(level, shield_grade):
    return dv.ac_input(Character(level=level, armor_grade="heavy", shield_grade=shield_grade)).parry


S.case("f-parry-proficiency", "training.md / defense.md [OWNER pkg 5]: heavy + tower grade: L1 8, L3 9; no shield 6",
       (8, 9, 6, 6))(
    lambda: (parry_of(1, "tower"), parry_of(3, "tower"), parry_of(1, "none"), parry_of(1, "heavy")))
S.case("f-tower-item-no-parry", "defense.md: a tower shield ITEM without the grade gives no parry", 6)(
    lambda: dv.ac_input(Character(level=1, armor_grade="heavy", items=(
        Item("t", "tower", kind=SHIELD, hands=1, in_hands=True, shield=4, shield_type="tower"),))).parry)


# ---- E: ids are made by the program (D7) ----
_RU_ELF = "".join(chr(c) for c in (1069, 1083, 1100, 1092, 1080, 1081, 1089, 1082, 1080, 1081))   # Elfiyskiy


def _two_langs():
    ch = Character(training=500)
    ch = dispatch(ch, "buy_language", title=_RU_ELF).state
    ch = dispatch(ch, "buy_language", title=_RU_ELF).state
    return tuple(lang.lid for lang in ch.languages)


S.case("e-language-no-id", "ARCH D7 [OWNER pkg 5]: language without id is bought; same name -> another id",
       ("elfiyskiy", "elfiyskiy_2"))(_two_langs)
S.case("e-status-no-id", "D7: two statuses 'Rage' without sid get rage and rage_2", ("rage", "rage_2"))(
    lambda: (lambda c: tuple(s.sid for s in c.statuses))(
        dispatch(dispatch(Character(), "add_status", status=Status("Rage"), ticks=3).state,
                 "add_status", status=Status("Rage"), ticks=3).state))


@S.case("e-language-no-name", "D7: a language with neither id nor name is refused", "rejected")
def _noname():
    try:
        dispatch(Character(training=500), "buy_language")
    except CommandError:
        return "rejected"
    return "accepted"


S.case("e-slug", "ids.py: punctuation and spaces -> one underscore; empty -> 'id'", ("long_sword_2", "id"))(
    lambda: (ids.slug("  Long-Sword (2) "), ids.slug("!!")))


# ---- G: a shield in the hand can attack (improvised, group Contact by default) ----
def _sword_and_shield():
    sw = Item("sw", "sword", kind="weapon", hands=1, groups=("blades",), damage_medium="1d8")
    sh = Item("sh", "shield", kind=SHIELD, hands=1, shield=2, shield_type="heavy")
    ch = Character(items=(sw, sh), bab=1)
    for iid in ("sw", "sh"):
        ch = dispatch(ch, "equip_hands", iid=iid).state
    ch = dispatch(ch, "add_attack", iid="sw", group="blades").state
    return dispatch(ch, "add_attack", iid="sh").state


S.case("g-shield-attack", "owner pkg 5: shield + sword in hands; shield has a record (Contact), AC keeps the shield, hands 2",
       (("sh", "contact"), 12, 2))(
    lambda: (lambda c: (tuple((r.item, r.group) for r in c.attacks if r.item == "sh")[0], dv.ac(c), dv.hands_used(c)))(
        _sword_and_shield()))
S.case("g-shield-visible", "owner: the shield record is shown as an attack while the shield is in a hand", True)(
    lambda: any(a.weapon == "sh" for a in av.all_attacks(_sword_and_shield())))


@S.case("g-misc-no-attack", "a non-weapon, non-shield item still cannot attack", "rejected")
def _misc():
    ch = Character(items=(Item("t", "torch", kind="misc", hands=1),))
    ch = dispatch(ch, "equip_hands", iid="t").state
    try:
        dispatch(ch, "add_attack", iid="t")
    except CommandError:
        return "rejected"
    return "accepted"


# ---- H + Q30: enchantment N counts ONLY while the item is activated ----
ON = dict(activated=True, active_until="short", activation_day=1)      # activated "day" item
PRICED = dict(activation_day=1)                                         # activatable, switched off
MWK = (Effect(bo.ATTACK, 1),)                                           # "not activated" tab: masterwork +1
FIRE = (Effect(bo.DAMAGE, dice="1d6", note="fire"),)                    # "activated" tab: fire d6


def _sword(n, state=PRICED, off=(), on=()):
    return Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("blades",), durability=10, hp=5,
                enchant=n, effects_off=off, effects_on=on, **state)


def _ch(item, **kw):
    ch = Character(items=(item,), bab=0, spirit_current=5, **kw)
    return dispatch(ch, "add_attack", iid=item.iid, group=item.groups[0] if item.groups else "").state


def _atk(ch):
    return av.by_record(ch, ch.attacks[0].rid)


S.case("q30-sword5-off", "gear.md [OWNER Q30]: +5 sword not activated: attack +1 (masterwork tab), damage +0, lucky 20",
       (1, 0, 20))(lambda: (lambda a: (a.to_hit, a.damage, a.lucky))(_atk(_ch(_sword(5, off=MWK)))))
S.case("q30-sword5-on", "gear.md [OWNER Q30]: +5 sword activated: attack +5, damage +5, lucky 15", (5, 5, 15))(
    lambda: (lambda a: (a.to_hit, a.damage, a.lucky))(_atk(_ch(_sword(5, ON, off=MWK)))))
S.case("q30-activate-command", "gear.md: activate_item on the +5 sword -> attack +5", 5)(
    lambda: _atk(dispatch(_ch(_sword(5, off=MWK)), "activate_item", iid="sw").state).to_hit)


@S.case("q30-no-price", "gear.md [OWNER Q30]: no activation price -> soft refusal, always off, no enchantment",
        (True, False, 1, 0))
def _noprice():
    it = _sword(5, state={}, off=MWK)
    r = dispatch(_ch(it), "activate_item", iid="sw")
    stored_on = _ch(replace(it, activated=True))        # even if stored as activated: no price -> off
    return ("refused" in r.info, r.state.item("sw").activated, _atk(stored_on).to_hit, dv.enchant(stored_on.item("sw")))


def _armor(state):
    return Item("ar", "chain", equipped=True, armor=4, durability=10, hp=20, enchant=2, **state)


S.case("q30-armor-off", "gear.md [OWNER Q30]: +2 armor not activated -> only the base armor bonus 4", 4)(
    lambda: dict(acm.parts(dv.ac_input(Character(items=(_armor(PRICED),)))))["armor"])
S.case("h-armor-on", "gear.md: +2 armor activated -> armor layer 6, hardness +4 (14), HP +2 (22)", (6, 14, 22))(
    lambda: (lambda a: (dict(acm.parts(dv.ac_input(Character(items=(a,)))))["armor"], dv.item_durability(a),
                        dv.item_hp_max(a)))(_armor(ON)))
S.case("h-sword-hd-hp", "gear.md: +3 sword activated -> hardness +6, HP +3 (10/5 -> 16/8); off -> 10/5",
       (16, 8, 10, 5))(
    lambda: (dv.item_durability(_sword(3, ON)), dv.item_hp_max(_sword(3, ON)),
             dv.item_durability(_sword(3)), dv.item_hp_max(_sword(3))))
S.case("h-item-hp-current", "gear.md [pkg 6]: current item HP is stored; not set = at max (on 7, off 5)", (7, 5))(
    lambda: tuple(dv.item_hp_current(Item("x", "x", hp=5, enchant=2, **st)) for st in (ON, PRICED)))
S.case("h-shield", "gear.md: +1 shield activated -> shield bonus 3; off -> 2", (3, 2))(
    lambda: tuple(dv.shield_bonus(Character(items=(Item("sh", "shield", kind=SHIELD, hands=1, in_hands=True, shield=2,
                                                        enchant=1, **st),))) for st in (ON, PRICED)))
S.case("h-shield-no-attack-bonus", "gear.md: a shield's enchantment raises the shield bonus, not its attack", 0)(
    lambda: _atk(_ch(Item("sh", "shield", kind=SHIELD, hands=1, in_hands=True, shield=2, enchant=1, **ON))).to_hit)
S.case("q30-fire-only-on", "gear.md [OWNER Q30]: 'fire d6' (activated tab) shows only while activated",
       ((), (("1d6", "fire"),)))(
    lambda: (_atk(_ch(_sword(0, on=FIRE))).extra_dice, _atk(_ch(_sword(0, ON, on=FIRE))).extra_dice))
S.case("q30-short-rest-off", "gear.md: the short rest switches a 'day' item off -> enchantment gone (5 -> 1)", (5, 1))(
    lambda: (lambda c: (_atk(c).to_hit, _atk(dispatch(c, "short_rest").state).to_hit))(
        _ch(_sword(5, ON, off=MWK), hp_rolls=(8,), hp_current=8)))
S.case("h-save-load", "D11: enchant, item damage, shield type and effect dice survive save/load", True)(
    lambda: (lambda c: cio.loads(cio.dumps(c)) == c)(Character(items=(
        _sword(2, ON, on=FIRE), Item("sh", "shield", kind=SHIELD, shield=2, shield_type="tower", hp_current=1),))))

if __name__ == "__main__":
    sys.exit(S.run())
