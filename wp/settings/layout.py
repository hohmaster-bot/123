"""Cells, colour rules and actions of layout profiles against a real character (package 19). Read only, except
run_action / run_quick, which run EXISTING character commands through dispatch (no new engine).

A cell / element "source" is a reference resolved by the model:
  resource:<hp|balance|bp|spirit|comfort|mana>  -> {"current", "max"}
  ability:<str..cha>                            -> {"score", "mod"}
  status:<status id>                            -> {"active", "remaining", "charges", "charges_max"}
  pool:<pool id>                                -> {"current", "max"}
  skill:<skill id>                              -> {"bonus"}
  value:<Character field>                       -> {"value"}      (a plain stored number / text)
  stat:<fort|ref|will|initiative|cmb|cmd|attack_melee|attack_ranged> -> {"value"}  (package 30)
  counter:<ot|pain|morale|speed|attention|ov|overload|load>          -> {"value"}  (package 30)
The list of every source of a character: wp/model/screen_view.py cell_sources.
An unknown or broken reference gives (None, warning id) and never raises.
Colour rules: a list [{"below": n, "color": "#..."} | {"above": n, "color": "#..."}]; the FIRST rule that matches wins
(assumption Q140); the number compared is current / score / bonus / value.
"""
from wp.commands import CommandError, dispatch
from wp.model import derived_view as dv
from wp.model import pool_view as pv

RESOURCES = {"hp": dv.hp_pool, "balance": dv.balance_pool, "bp": dv.bp_pool, "spirit": dv.spirit_pool,
             "comfort": dv.comfort_pool, "mana": dv.mana_pool}
UNKNOWN_SOURCE = "unknown_source"


def resolve(ch, source):
    kind, _, oid = str(source).partition(":")
    try:
        if kind == "resource" and oid in RESOURCES:
            p = RESOURCES[oid](ch)
            return {"current": p.current, "max": p.max}, None
        if kind == "ability" and oid in ch.abilities:
            return {"score": dv.ability_current(ch, oid), "mod": dv.ability_mod(ch, oid)}, None
        if kind == "status":
            s = next((x for x in ch.statuses if x.sid == oid), None)
            if s is not None:
                return {"active": s.active, "remaining": s.remaining,
                        "charges": s.charges.current if s.charges else None,
                        "charges_max": s.charges.max if s.charges else None}, None
        if kind == "pool":
            p = next((x for x in ch.pools if x.pid == oid), None)
            if p is not None:
                return {"current": pv.current(ch, p), "max": pv.max_of(ch, p)}, None
        if kind == "skill":
            return {"bonus": dv.skill_bonus(ch, oid)}, None
        if kind in ("stat", "counter"):
            from wp.model import screen_view as scr
            if (kind == "stat" and oid in scr.STAT_SOURCES) or (kind == "counter" and oid in scr.COUNTERS):
                return {"value": (scr.stat_value if kind == "stat" else scr.counter_value)(ch, oid)}, None
        if kind == "value" and oid and hasattr(ch, oid) and isinstance(getattr(ch, oid), (int, str, bool)):
            return {"value": getattr(ch, oid)}, None
    except (KeyError, ValueError):
        pass
    return None, UNKNOWN_SOURCE


def number(resolved):
    if not resolved:
        return None
    for k in ("current", "score", "bonus", "value", "charges"):
        if k in resolved and isinstance(resolved[k], (int, float)) and not isinstance(resolved[k], bool):
            return resolved[k]
    return None


def color(rules, value):
    if value is None:
        return None
    for r in rules or ():
        if "below" in r and value < r["below"]:
            return r.get("color")
        if "above" in r and value > r["above"]:
            return r.get("color")
    return None


def cell_view(ch, cell):
    """(resolved value, colour, warning) of one cell or element."""
    res, warn = resolve(ch, cell.get("source", ""))
    return res, color(cell.get("color_rules"), number(res)), warn


def run_action(ch, action):
    """One action {"command": id, "params": {...}} through the character dispatch (refusals as usual)."""
    return dispatch(ch, action["command"], **dict(action.get("params", {}))).state


def run_quick(ch, button):
    """A quick button: its action, or its macro (a plain list of commands) run in order. All or nothing: if one
    command is refused, the refusal is raised and the character stays as it was (assumption Q141)."""
    steps = list(button.get("macro") or ()) or [button["action"]]
    new = ch
    for i, step in enumerate(steps):
        try:
            new = run_action(new, step)
        except CommandError as e:
            raise CommandError("step %d (%s) refused: %s" % (i + 1, step.get("command"), e), e.reason,
                               step=i + 1, **e.params)
    return new
