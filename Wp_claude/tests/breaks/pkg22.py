"""Break registry: package 22 (mana restore, reactions, balance cap in combat, best tick order, paired attack)."""
T = ("model/test_pkg22.py",)

ENTRIES = [
    dict(id="p22-mana-block", file="wp/commands/reaction_cmds.py", old="    if blk.restore_blocked(ch, \"mana\"):",
         new="    if False:", suites=T, rule="pkg 22 A1: a block_restore mana refuses restore_mana"),
    dict(id="p22-mana-over-max", file="wp/commands/reaction_cmds.py", old="    after = dm.restore(before, amount)",
         new="    after = dm.Pool(min(before.max, before.current + amount), before.max)", suites=T,
         rule="resources.md Over max: an over-max value is kept"),
    dict(id="p22-reaction-refusal", file="wp/commands/reaction_cmds.py", old="    if have < n:\n", new="    if False:\n",
         suites=T, rule="pkg 22 A2: no reaction left -> refused"),
    dict(id="p22-reaction-tick", file="wp/commands/combat_cmds.py",
         old="    new = replace(new, reactions_current=None)                 # a new round", new="    new = new  # a new round",
         suites=T, rule="pkg 22 A2: the tick restores reactions"),
    dict(id="p22-reaction-attack", file="wp/commands/attack_cmds.py", old="    if record.cost_reactions:          # an attack",
         new="    if False:          # an attack", suites=T, rule="pkg 22 A2: an attack with a reaction cost spends it"),
    dict(id="p22-maneuver-reactions", file="wp/model/maneuver_view.py",
         old="        if reaction_cmds.reactions_current(ch) < m.cost_reactions:", new="        if False:", suites=T,
         rule="pkg 22 A2: a maneuver needs its reactions"),
    dict(id="p22-cap-clamp", file="wp/commands/base.py", old="        if ch.balance_current > cap:", new="        if False:",
         suites=T, rule="pkg 22 A3: balance never above the cap in combat"),
    dict(id="p22-tick-fixed-order", file="wp/core/tick.py", old="    for order in _orders(items):", new="    for order in [tuple(items)]:",
         suites=T, rule="pkg 22 A4: the most favourable tick order"),
    dict(id="p22-tick-balance-first", file="wp/core/tick.py", old="    return (v.trauma, v.pain, -v.balance.current)",
         new="    return (-v.balance.current, v.trauma, v.pain)", suites=T, rule="Q150: overflow first, then balance"),
    dict(id="p22-tick-greedy", file="wp/core/tick.py", old="    return [tuple(dmg[:k] + regen + dmg[k:]) for k in range(len(dmg) + 1)]",
         new="    return [tuple(dmg + regen)]", suites=T, rule="pkg 22 A4: greedy tries the regen at every place"),
]
