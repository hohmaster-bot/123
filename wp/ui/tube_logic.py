"""The resources block without Qt (package 33): pure functions, tested without PySide6.

parse_edit(text) -> ("add", n) for "+N" / "-N", ("set", n) for a plain number; bad text -> EditError (i18n key).
edit_command(resource, kind, n, current) -> (command, params) for Session.dispatch: "add" = adjust_value(resource, n);
    "set" = set_value(resource, n), for a class pool adjust_value(resource, n - current) (set_value has no pools).
fill(current, maximum) -> 0.0 .. 1.0 (the liquid); over_max(current, maximum); ticks(maximum, step) -> the tick
    positions 0 < x < 1 every `step` points; temp_fill(temp, maximum) -> the temp HP strip 0.0 .. 1.0.
pick_mode(height, autoswitch, modes) -> "big" | "medium" | "thin" (the auto-switch; without it always "big").
split_pools(pools, order, large, count) -> (large, compact): pool_order first, then the rest; the large ones are the
    pools_large ids (when set) or the first `count`.
These are display numbers and text parsing, never game rules (the core checks every value: D25).
"""
import re

ADD, SET = "add", "set"
POOL = "pool"
_EDIT = re.compile(r"^\s*([+-]?)\s*(\d+)\s*$")
BAD_EDIT = "resources.bad_edit"
LARGE = 3                              # pools drawn large by default (UI_WISHES 6; data: resources.json large_pools)


class EditError(ValueError):
    def __init__(self, text):
        super().__init__(text)
        self.key = BAD_EDIT
        self.text = text


def parse_edit(text):
    m = _EDIT.match(str(text or ""))
    if not m:
        raise EditError(text)
    sign, n = m.groups()
    n = int(n)
    if sign == "+":
        return ADD, n
    if sign == "-":
        return ADD, -n
    return SET, n


def is_pool(resource):
    return resource == POOL or str(resource).startswith(POOL + ":")


def edit_command(resource, kind, n, current):
    if kind == ADD:
        return "adjust_value", {"resource": resource, "delta": int(n)}
    if is_pool(resource):
        return "adjust_value", {"resource": resource, "delta": int(n) - int(current)}
    return "set_value", {"resource": resource, "value": int(n)}


def fill(current, maximum):
    if maximum is None or int(maximum) <= 0:
        return 0.0
    return max(0.0, min(1.0, float(current) / float(maximum)))


def over_max(current, maximum):
    return maximum is not None and int(current) > int(maximum)


def ticks(maximum, step):
    """Positions of the segment ticks: every `step` points, strictly inside the tube."""
    if not maximum or int(maximum) <= 0 or not step or int(step) <= 0:
        return ()
    m, s = int(maximum), int(step)
    return tuple(k * s / float(m) for k in range(1, (m - 1) // s + 1))


def temp_fill(temp, maximum):
    return fill(temp, maximum)


def pick_mode(height, autoswitch, modes):
    """modes = {"big": min height, "medium": min height} (data); below medium -> the thin bar with the number."""
    if not autoswitch:
        return "big"
    h = float(height)
    if h >= float(modes["big"]):
        return "big"
    if h >= float(modes["medium"]):
        return "medium"
    return "thin"


def split_pools(pools, order=(), large=(), count=LARGE):
    """pools = ((pid, name, {current, max}), ...) of the resources view."""
    pos = {pid: i for i, pid in enumerate(order or ())}
    ordered = sorted(pools, key=lambda p: (pos.get(p[0], len(pos)), list(pools).index(p)))
    if large:
        big = [p for p in ordered if p[0] in set(large)][:count]
    else:
        big = ordered[:count]
    ids = {p[0] for p in big}
    return tuple(big), tuple(p for p in ordered if p[0] not in ids)
