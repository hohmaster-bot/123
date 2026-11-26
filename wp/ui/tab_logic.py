"""The content tabs of the right column without Qt (package 35 P4; UI_WISHES "Classic screen v2" point 9). Pure
functions over the views: each gives the rows of one tab's table (tuples of texts / numbers) and its summary values.
No game number is computed here: every number comes from a view (the core); the tables only arrange them.
Game-module neutrality (package 35): no class, race, weapon group or country name is written here; catalogs are
listed by their data.
"""
HEAVY = ("skills", "inventory", "training", "catalogs")     # UI_WISHES 9: an "expand to full screen" button


def injury_rows(view):
    """(id, name, severity, heal rating, permanent, charges "cur/max")."""
    return [(j.jid, j.name, j.severity, j.heal_rating, j.permanent, "%d/%d" % (j.charges.current, j.charges.max))
            for j in view["injuries"]]


def drive_rows(view):
    """(id, name, type, level, principle, quest state, comfort received, reminder flags)."""
    return [(d["did"], d["name"], d["type"], d["level"], d["principle"], d["quest_state"], d["comfort_received"],
             d["principle_missing"] or d["quest_missing"]) for d in view["drives"]]


def drive_summary(view):
    s = view["drive_summary"]
    return s["distributed"], s["start_points"], tuple(s["reminders"])


def item_rows(ch_items, views):
    """(id, name, weight L, quantity, worn, in hands, state) of every item: the record from the character, the
    state from the items view (dv.item_view)."""
    by_id = {v.iid: v for v in views}
    return [(it.iid, it.name, it.weight_l, by_id[it.iid].quantity, it.equipped, it.in_hands, by_id[it.iid].state)
            for it in ch_items]


def training_summary(view):
    """(training points, level, base slots, reactions, comfort "cur/max", attention)."""
    c = view["comfort"]
    return (view["training"], view["level"], view["base_slots"], view["reactions"],
            "%d/%d" % (c["current"], c["max"]), view["attention"])


def qualification_rows(ch_items):
    """(id, name, N, bought) of the items that need a qualification (gear.md "Qualification N": 50 x N training)."""
    return [(it.iid, it.name, it.qualification_n, it.qualified) for it in ch_items if it.qualification_n]


def rest_rows(view):
    """(option id, BP cost) of the short rest options that have something to restore."""
    return [(o, int(c)) for o, c in view["options"]]


def skill_rows(view):
    """(name, tier, ranks, bonus)."""
    return [(n, t, r, b) for n, t, r, b in view]


def feat_rows(sheet):
    """(id, title, charges, cooldown) of the character's feats."""
    return [(fid, title, ch, cd) for fid, title, ch, cd in sheet["feats"]]


def narrative_rows(ch, kind):
    """(id, name, state, text) of the quests / courts / stories / quirks (RULES/narrative.md); state: quests open /
    done, quirks active / burned, courts "level x tier y"; a court quest names its court (the giver)."""
    if kind == "quest":
        courts = {c.cid: c.name for c in ch.courts}
        return [(q.qid, q.name + ((" (" + courts.get(q.giver, q.giver) + ")") if q.giver else ""),
                 "done" if q.done else "open", q.text) for q in ch.quests]
    if kind == "court":
        return [(c.cid, c.label(), "", c.note) for c in ch.courts]
    if kind == "story":
        return [(x.stid, x.name, "", x.text) for x in ch.stories]
    if kind == "quirk":
        return [(k.kid, k.name, "burned" if k.burned else "active", k.text) for k in ch.quirks]
    return []
