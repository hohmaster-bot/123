"""Flask bars (package 26 B): a resource drawn as a flask with a tick every N units.

App settings: resource_display[resource] (number | bar | both | percent | flask) and resource_segments[resource]
(N; 0 = no ticks; a class pool reads "pool:<id>", else "pool"). segments(12, 5) = [5, 5, 2]; fills(7, 12, 5) =
[5, 2, 0] (a value over the max fills every segment). Balance also gets the cap marker (the current cap), the max
before cap hits and the restore amount per tick.
"""
from wp.app import limits
from wp.commands import reaction_cmds
from wp.model import derived_view as dv
from wp.model import pool_view as pv

POOL = "pool"


def segments(maximum, size):
    maximum, size = max(0, int(maximum)), int(size)
    if size <= 0 or maximum == 0 or maximum // max(1, size) > limits.get("flask_segments_max"):
        return [maximum] if maximum else []    # more ticks than the limit (package 27): one segment, no ticks
    out = [size] * (maximum // size)
    if maximum % size:
        out.append(maximum % size)
    return out


def fills(current, maximum, size):
    left = max(0, min(int(current), int(maximum)))
    out = []
    for seg in segments(maximum, size):
        out.append(min(seg, left))
        left -= out[-1]
    return out


def _setting(app, key):
    from wp.settings import store as st
    from wp.settings import schema as sch
    return dict(st.get(app, key) if app is not None else sch.KEYS[key]["default"])


def bar(current, maximum, size, style):
    return {"current": int(current), "max": int(maximum), "style": style, "segment_size": int(size),
            "segments": segments(maximum, size), "fills": fills(current, maximum, size)}


def view(ch, app=None):
    styles, sizes = _setting(app, "resource_display"), _setting(app, "resource_segments")
    pools = {"hp": dv.hp_pool(ch), "balance": dv.balance_pool(ch), "bp": dv.bp_pool(ch), "spirit": dv.spirit_pool(ch),
             "mana": dv.mana_pool(ch), "comfort": dv.comfort_pool(ch)}
    out = {k: bar(p.current, p.max, sizes.get(k, 0), styles.get(k, "number")) for k, p in pools.items()}
    out["balance"].update(cap=dv.balance_max(ch), base_max=dv.balance_max_base(ch), restore=dv.balance_regen(ch))
    for p in ch.pools:
        key = "%s:%s" % (POOL, p.pid)
        out[key] = bar(pv.current(ch, p), pv.max_of(ch, p), sizes.get(key, sizes.get(POOL, 0)),
                       styles.get(key, styles.get(POOL, "number")))
    r = reaction_cmds.reactions_pool(ch)
    out["reactions"] = bar(r.current, r.max, 0, styles.get("reactions", "number"))
    return out
