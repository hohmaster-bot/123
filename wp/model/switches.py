"""Rule switches (package 36, P2.4): a declared list in data (wp/rules_data/switches.json: id, kind, allowed, default)
read through ONE function, value(ch, sid). A choice switch is set by an effect with the target switch:<id> whose note
is the value (the last active one wins; else the default); a target switch is the stacked number of its sheet target
(heal_percent, exp_percent, pain_reduction, natural_regen_percent, pain_cap); an action switch has no value (it is a
trigger action). percent(n, pct) = floor(n * (100 + pct) / 100), never below 0.
"""
import io
import json
import math
import os

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rules_data", "switches.json")
PREFIX = "switch:"
PCT = 100                              # a percent (not a rule)


def _load(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        return {s["id"]: s for s in json.load(f)["switches"]}


SWITCHES = _load()


def value(ch, sid):
    spec = SWITCHES[sid]
    if spec["kind"] == "choice":
        from wp.model import blocks as blk
        got = [e.note for _src, e in blk.active_effects(ch) if e.target == PREFIX + sid and e.note]
        return got[-1] if got else spec["default"]
    if spec["kind"] == "target":
        from wp.model import sheet_targets as stg
        return int(spec["default"]) + stg.value(ch, spec["target"])
    return spec["default"]


def percent(n, pct):
    return max(0, int(math.floor(int(n) * (PCT + int(pct)) / float(PCT))))


def view(ch):
    """{switch id: its value} (the combat / sheet views show them)."""
    return {sid: value(ch, sid) for sid in SWITCHES if SWITCHES[sid]["kind"] != "action"}
