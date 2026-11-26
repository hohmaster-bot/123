"""The bottom strip and the journal tab without Qt (package 35 P2, ROADMAP step 6; UI_WISHES "Classic screen v2"
point 10). Pure functions over the views, tested without PySide6.

strips(profile, data) -> the cell rows: the main strip (data "bottom_strip") and the profile's own strips (profile
    field "strips": a list of cell lists; empty by default = no second strip).
cell(nid, res, combat, sheet, items, totals) -> (value text or (key, values), note key or "", style) of one cell: ot,
    pain, morale (the scale: its sources total, totals["morale"], so it equals the Sources dialog), speed, load ("X of max" + the category and the limits); None when the cell is hidden (morale
    outside combat).
number_of(nid) -> the sources number the cell opens (the Sources dialog).
journal_lines(log, kind, text) -> the journal entries newest first, filtered by kind ("" = all) and a text (in the
    command id, the kind or the params / result values; case-insensitive).
line_text(entry) -> "seq round command params -> result" (ids and numbers only: the journal stores no texts).
"""
from wp.ui import params_logic as pl

MORALE = "morale"
OTHER = ("", "", "")                    # any other sheet number: the block shows its sources total
OTHER_OK = ("temp_hp", "attention", "initiative", "cmb", "cmd", "fort", "ref", "will", "attack_melee", "attack_ranged",
            "hp_max", "balance_max", "spirit_max", "mana_max")
SOURCES = {"ot": "ot", "pain": "pain", "morale": "morale", "speed": "speed", "load": "load"}


def strips(profile, data):
    out = [list(data["bottom_strip"])]
    out += [list(s) for s in (profile or {}).get("strips") or () if s]
    return out


def cell(nid, res, combat, sheet, items, totals=None):
    if nid == "ot":
        return str(int(res["ot"])), "", ""
    if nid == "pain":
        return str(int(res["pain"])), "", ""
    if nid == MORALE:
        if not combat["in_combat"]:
            return None
        return pl.signed((totals or {}).get(MORALE, combat["morale_scale"])), "", ""
    if nid == "speed":
        return str(int(sheet["speed"])), "", ""
    if nid == "load":
        ld = items["load"]
        cat = pl.load_category(ld["carried_l"], ld["light_max_l"], ld["heavy_max_l"])
        return (("load.of", (ld["carried_l"], ld["heavy_max_l"])), ("load.limits", (ld["light_max_l"], ld["heavy_max_l"]),
                "load." + cat), (pl.OVER if cat == pl.OVER else ""))
    return None if nid not in OTHER_OK else OTHER


def number_of(nid):
    return SOURCES.get(nid, nid)


def _hay(e):
    return " ".join([e.command, e.kind] + ["%s=%s" % kv for kv in sorted(dict(e.params).items())] +
                    ["%s=%s" % kv for kv in sorted(dict(e.result).items())]).lower()


def journal_lines(log, kind="", text=""):
    t = str(text or "").strip().lower()
    return [e for e in reversed(tuple(log)) if (not kind or e.kind == kind) and (not t or t in _hay(e))]


def line_text(e):
    params = ", ".join("%s=%s" % kv for kv in sorted(dict(e.params).items()))
    result = ", ".join("%s=%s" % kv for kv in sorted(dict(e.result).items()))
    return "%d. %s%s%s" % (e.seq, e.command, (" (%s)" % params) if params else "", (" -> %s" % result) if result else "")
