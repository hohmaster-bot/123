"""Read-only data of the Classic screen v2 (package 30; UI_WISHES.md "Classic screen v2", ARCH/ui_gaps.md).

- attack_number(ch, kind): the general MELEE / RANGED attack (owner, package 30): BAB + the modifier of the source
  stat (defaults: melee str, ranged dex; Character.attack_sources, set_attack_source) + pain (always) + morale (only
  in combat, morale_bonus is 0 outside). A source "record:<rid>" takes that attack record's to-hit and names its
  weapon. RULES/combat.md "General attack numbers".
- load(ch): the carried weight, the category key (light / heavy / overload; shown as light / load / overloaded,
  i18n load.*), both limits in L and the text "<carried> of <heavy limit>" (RULES/gear.md "Weight").
- squares(current, max): the numbered squares ((1, spent), (2, spent), ...): spending takes the SMALLEST numbers first,
  so 1 .. max - current are spent.
- shield_side(ch), cell_lines(ch): the held shield side (left / right / both / "") and the layer parts per AC cell.
- reminders(ch): every standing reminder (drives; see the function), favorites(ch), cell_sources(ch).
"""
from dataclasses import replace

from wp.core import pain as pn
from wp.model import attack_view as av
from wp.model import classes as klass
from wp.model import derived_view as dv
from wp.model import hands as hd
from wp.model import load_view as lv

MELEE = "melee"
RANGED = "ranged"
KINDS = (MELEE, RANGED)
DEFAULT_STAT = {MELEE: "str", RANGED: "dex"}
RECORD = "record:"
COUNTERS = ("ot", "pain", "morale", "speed", "attention", "ov", "overload", "load")
STAT_SOURCES = ("fort", "ref", "will", "initiative", "cmb", "cmd", "attack_melee", "attack_ranged")


def attack_source(ch, kind):
    return ch.attack_sources.get(kind, DEFAULT_STAT[kind])


def _general(ch, kind):
    """Effects aimed at the general number itself (targets attack_melee / attack_ranged, package 34)."""
    from wp.model import sheet_targets as stg
    return stg.value(ch, "attack_" + kind)


def attack_number(ch, kind):
    """{"total", "lines": ((label, value), ...), "source", "weapon"}."""
    src = attack_source(ch, kind)
    if src.startswith(RECORD):
        rec = next((r for r in ch.attacks if r.rid == src[len(RECORD):]), None)
        if rec is not None:
            v = av.attack(ch, rec)
            item = next((it for it in ch.items if it.iid == rec.item), None)
            lines = tuple((x.label, x.value) for x in v.to_hit_lines) + (("bonuses", _general(ch, kind)),)
            return {"total": v.to_hit + _general(ch, kind), "lines": lines, "source": src,
                    "weapon": item.name if item is not None else rec.item}
        src = DEFAULT_STAT[kind]                        # the record was removed: back to the default stat
    pain = pn.penalty_bonus(dv.pain_total(ch), dv.pain_profile(ch)).value
    lines = (("bab", klass.bab(ch)), ("stat:" + src, dv.ability_mod(ch, src)), ("pain", pain),
             ("morale", dv.morale_bonus(ch)), ("bonuses", _general(ch, kind)))
    return {"total": sum(v for _, v in lines), "lines": lines, "source": src, "weapon": ""}


def load(ch):
    from wp.core import derived as cdv
    from wp.model import sheet_targets as stg
    light, heavy = cdv.load_thresholds_l(dv.ability_mod(ch, "str") + stg.value(ch, "load_mod"))
    carried = lv.carried_weight_l(ch)
    cat = lv.load_status(ch)
    return {"carried_l": carried, "light_max_l": light, "heavy_max_l": heavy, "category": cat,
            "label": "load." + cat, "text": ("load.of", (carried, heavy))}


def squares(current, maximum):
    spent = max(0, int(maximum) - int(current))
    return tuple((n, n <= spent) for n in range(1, int(maximum) + 1))


def shield_side(ch):
    from wp.model import records as rec
    sides = hd.sides(ch)
    held = [sides.get(it.iid, "") for it in ch.items if it.in_hands and (rec.is_shield(it) or it.shield)]
    if not held:
        return ""
    return held[0] if len(set(held)) == 1 else hd.BOTH


def cell_lines(ch):
    """{cell: ((layer, value), ...)} of the melee variant of every AC cell (the number's sources)."""
    from wp.core import ac as acm
    from wp.core import ac_zones as acz
    from wp.model import ac_zones_view as zv
    inp = dv.ac_input(ch)
    rules = zv.rules(ch)
    shields = zv.shields(ch)
    out = {}
    for c in acz.CELLS:
        cinp = replace(inp, shield=acz.shield_value(c, shields, rules))
        on = acz._shield_on(cinp, c, shields, rules)
        out[c] = tuple(acm.layer_parts(cinp, use_shield=on, lose_dex=c in rules.dex_loss_cells, cell=c))
    return out


def reminders(ch):
    """Standing reminders ((text key, values), ...): the drive reminders (principle missing, quest missing) and the
    open drive quests (their penalty text). One-shot reminders (level_up) stay in the command result."""
    from wp.commands import drive_cmds
    from wp.model import links
    return drive_cmds.reminders(ch) + drive_cmds.open_quests(ch) + links.reminders(ch)   # + not backed (pkg 36)


def favorites(ch):
    """The favourite statuses (Status.favorite) and the favourite abilities (Character.favorites, "kind:id")."""
    return {"statuses": tuple(s.sid for s in ch.statuses if s.favorite), "abilities": tuple(ch.favorites)}


def cell_sources(ch):
    """Every source a cell may show (wp/settings/layout.py resolve): (source id, i18n label key)."""
    from wp.settings import layout
    out = [("resource:" + r, "resource." + r) for r in layout.RESOURCES]
    out += [("ability:" + a, "stat." + a) for a in ch.abilities]
    out += [("stat:" + s, "param." + s) for s in STAT_SOURCES]
    out += [("counter:" + c, "counter." + c) for c in COUNTERS]
    out += [("pool:" + p.pid, p.name) for p in ch.pools]
    out += [("status:" + s.sid, s.name) for s in ch.statuses]
    out += [("skill:" + s.name, "skill." + s.name) for s in ch.skills]
    return tuple(out)


def stat_value(ch, name):
    from wp.model import stats_view as stats
    if name == "attack_melee":
        return attack_number(ch, MELEE)["total"]
    if name == "attack_ranged":
        return attack_number(ch, RANGED)["total"]
    return stats.view(ch)[name].total


def counter_value(ch, name):
    if name == "load":
        return load(ch)["carried_l"]
    values = {"ot": ch.trauma, "pain": dv.pain_total(ch), "morale": dv.morale_bonus(ch), "speed": dv.speed(ch),
              "attention": ch.attention, "ov": ch.ov, "overload": ch.overload}
    return values[name]

