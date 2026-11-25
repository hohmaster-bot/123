"""Break registry: package 26 (actions, flask bars, experience)."""
T = ("model/test_pkg26.py",)

ENTRIES = [
    dict(id="p26-actions-effect", file="wp/commands/action_cmds.py",
         old="    return max(0, int(rd.const(\"actions.base\", ch)) + stg.value(ch, TARGET))",
         new="    return max(0, int(rd.const(\"actions.base\", ch)))", suites=T, rule="pkg 26 A: effects add actions"),
    dict(id="p26-actions-refused", file="wp/commands/action_cmds.py", old="    if have < n:\n", new="    if False:\n",
         suites=T, rule="pkg 26 A: not enough actions -> refused"),
    dict(id="p26-actions-tick", file="wp/commands/combat_cmds.py",
         old="    new = replace(new, actions_current=None)                   # and the actions (package 26 A)",
         new="    new = new", suites=T, rule="pkg 26 A: the tick restores the actions"),
    dict(id="p26-actions-end", file="wp/commands/gear_cmds.py", old="iterative_count=0, reactions_current=None,\n                  actions_current=None)",
         new="iterative_count=0, reactions_current=None)", suites=T, rule="pkg 26 A: end_combat restores the actions"),
    dict(id="p26-flask-rest", file="wp/model/flask.py", old="    if maximum % size:\n        out.append(maximum % size)",
         new="    pass", suites=T, rule="pkg 26 B: the last partial segment"),
    dict(id="p26-flask-fill", file="wp/model/flask.py", old="        out.append(min(seg, left))", new="        out.append(seg)",
         suites=T, rule="pkg 26 B: fills follow the current value"),
    dict(id="p26-xp-total", file="wp/model/experience.py", old="    return sum(int(e.amount) for e in ch.xp_log)",
         new="    return sum(max(0, int(e.amount)) for e in ch.xp_log)", suites=T, rule="pkg 26 C: a negative entry counts"),
    dict(id="p26-xp-id", file="wp/commands/xp_cmds.py", old="    n = ch.xp_counter + 1", new="    n = len(ch.xp_log) + 1",
         suites=T, rule="pkg 26 C: ids are never reused"),
    dict(id="p26-history", file="wp/commands/progression_cmds.py", old="    new = xp_cmds.add_history(new, level, roll, note, at)",
         new="    new = new", suites=T, rule="pkg 26 C: level_up writes the level history"),
    dict(id="p26-progress", file="wp/model/experience.py", old="    return max(0, min(PCT, total(ch) * PCT // int(ch.next_level_at)))",
         new="    return total(ch)", suites=T, rule="pkg 26 C: progress percent of the goal"),
    dict(id="p26-stamp", file="wp/app/session.py", old="            params = dict(params, at=at)",
         new="            params = params", suites=T, rule="pkg 26 C: entries carry the Session time stamp"),
]
