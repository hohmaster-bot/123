"""Sources of every derived sheet number (package 34, owner: "every number has sources; the editor mode shows them
all and can change them"). One uniform view:

view(ch, number) -> {"number", "total", "rows": (row, ...), "target", "editable_target"}; a row is a dict
    id, name (an i18n key or a record name), kind (rule | stored | effect | manual), value, on, derived (computed from
    class / level / stats: shown with the rule that made it), manual (a SourceRow of the character), counted (whether
    the value is in the total: bonuses of one type do not stack), rule (the RULES file of a derived row).
The total is ALWAYS the real number of the sheet (the same function every other view uses), never stored; the rows
explain it: for every number the counted rows add up to the total (tests). Breakdowns that already exist are reused
(stats_view lines, screen_view.attack_number lines, screen_view.cell_lines); the "bonuses" line of them is opened up
into one row per effect source (statuses, feats, items, injuries, quirks, templates) and the manual rows.
Manual rows (Character.source_rows, commands source_add / source_edit / source_toggle / source_remove) are flat
effects on the number's effect target (source_row.TARGETS); a derived row is never written: the owner corrects it
with a manual row. Numbers: NUMBERS + "pool:<id>" + "ac:<cell>". No Qt here.
"""
from wp.core import bonuses as bo
from wp.model import blocks as blk
from wp.model import derived_view as dv
from wp.model import source_row as sr
from wp.rules_data import rules as rd

RULE, STORED, EFFECT, MANUAL = "rule", "stored", "effect", "manual"
NUMBERS = ("hp_max", "balance_max", "spirit_max", "mana_max", "temp_hp", "attack_melee", "attack_ranged",
           "initiative", "cmb", "cmd", "fort", "ref", "will", "speed", "load", "attention")
SAVES = ("fort", "ref", "will")
MANUAL_PREFIX = "source:"
STATUS = "status:"                     # package 34 part 2: the effects of one buff / status (read-only)


def known(ch, number):
    if number in NUMBERS:
        return True
    if number.startswith(sr.POOL):
        return any(p.pid == number[len(sr.POOL):] for p in ch.pools)
    if number.startswith(sr.AC):
        from wp.core import ac_zones as acz
        return number[len(sr.AC):] in acz.CELLS
    if number.startswith(STATUS):
        return any(s.sid == number[len(STATUS):] for s in ch.statuses)
    return False


def _row(rid, name, kind, value, on=True, derived=False, manual=False, counted=True, rule=""):
    return {"id": rid, "name": name, "kind": kind, "value": int(value), "on": bool(on), "derived": bool(derived),
            "manual": bool(manual), "counted": bool(counted and on), "rule": rule}


def rule_row(rid, value, rule):
    return _row(rid, "source." + rid, RULE, value, derived=True, rule=rule)


def stored_row(rid, value):
    return _row(rid, "source." + rid, STORED, value)


# ------------------------------------------------------------------ effect rows (one per source, with stacking)
def source_name(ch, src):
    for coll, key, title in (("statuses", "sid", "name"), ("feats", "fid", "title"), ("items", "iid", "name"),
                             ("injuries", "jid", "name"), ("quirks", "kid", "name"), ("templates", "tid", "name")):
        for r in getattr(ch, coll):
            if getattr(r, key, None) == src:
                return getattr(r, title, "") or src
    return "source." + (src or "unknown")     # morale, pain ... (i18n keys source.<id>)


def _counted(bonuses):
    """Which bonuses count (bonuses.stack): adding types all; per other type the winner (larger bonus vs larger
    penalty; equal -> none)."""
    flags = [b.btype in bo.ADDING_TYPES for b in bonuses]
    for t in {b.btype for b in bonuses if b.btype not in bo.ADDING_TYPES}:
        idx = [i for i, b in enumerate(bonuses) if b.btype == t]
        pos = max(idx, key=lambda i: int(bonuses[i].value), default=None)
        neg = min(idx, key=lambda i: int(bonuses[i].value), default=None)
        best = max(0, int(bonuses[pos].value))
        worst = min(0, int(bonuses[neg].value))
        win = bo.winner(best, worst)
        if win and win == best:
            flags[pos] = True
        elif win:
            flags[neg] = True
    return flags


def effect_rows(ch, bonuses):
    """Rows of a stacked bonus list: manual rows by their SourceRow, others by their record name."""
    bonuses = list(bonuses)
    flags = _counted(bonuses)
    rows = []
    manual = {r.sid: r for r in ch.source_rows}
    for b, on in zip(bonuses, flags):
        if b.source.startswith(MANUAL_PREFIX) and b.source[len(MANUAL_PREFIX):] in manual:
            r = manual[b.source[len(MANUAL_PREFIX):]]
            rows.append(_row(r.sid, r.name, MANUAL, b.value, manual=True, counted=on))
        else:
            rows.append(_row(b.source or b.btype, source_name(ch, b.source), EFFECT, b.value, counted=on))
    return rows


def off_rows(ch, number):
    """Manual rows switched off (they give no effect, so they are not among the bonuses)."""
    return [_row(r.sid, r.name, MANUAL, r.value, on=False, manual=True) for r in ch.source_rows
            if r.number == number and not r.on]


def target_bonuses(ch, target):
    """The bonuses of a sheet_targets.value target (same filter as sheet_targets.stack_of)."""
    from wp.model import sheet_targets as stg
    if not stg._has(ch, target):
        return []
    bs = [b for b in stg.sheet_bonuses(ch) if b.target == target and b.btype not in bo.AC_ONLY_TYPES and not b.cells]
    return blk.unblocked(ch, bs, target)


def typed_bonuses(ch, target, extra=None):
    """The bonuses of stats_view._typed (rolls and saves: morale and pain included where they apply)."""
    bs = [b for b in dv.all_bonuses(ch)
          if bo.applies(b, target) or (extra is not None and b.target == extra and b.btype not in bo.AC_ONLY_TYPES)]
    return blk.unblocked(ch, bs, target, extra)


def _target_rows(ch, number, target):
    return effect_rows(ch, target_bonuses(ch, target)) + off_rows(ch, number)


# ------------------------------------------------------------------ the numbers
def _hp(ch):
    con = dv.ability_mod(ch, "con")
    dice = sum(max(1, d + con) for d in dv.hit_dice(ch))
    rows = [rule_row("hit_dice", dice, "progression.md"), stored_row("hp_race", ch.hp_race),
            stored_row("hp_bonus", ch.hp_bonus)] + _target_rows(ch, "hp_max", "hp_max")
    return dv.hp_max(ch), rows


def _balance(ch):
    rows = [rule_row("armor", dv.armor_bonus(ch), "rest.md"), rule_row("bp_current", ch.bp_current, "rest.md"),
            stored_row("balance_bonus", ch.balance_bonus), rule_row("shield", dv.shield_balance_bonus(ch), "gear.md")]
    rows += _target_rows(ch, "balance_max", "balance_max")
    total = dv.balance_max(ch)
    if ch.in_combat:                   # the combat snapshot and the hits (resources.md)
        base = dv.balance_max_base(ch)
        rows.append(rule_row("combat_cap", total - base, "resources.md"))
    return total, rows


def _spirit(ch):
    from wp.model.derived_view import SPIRIT_BASE, SPIRIT_PER_CHA
    base = max(0, SPIRIT_BASE + SPIRIT_PER_CHA * dv.ability_mod(ch, "cha"))
    rows = [rule_row("spirit_base", base, "resources.md")]
    rows += [_row("bonus:%d" % i, name, STORED, v) for i, (name, v) in enumerate(ch.spirit_bonuses)]
    rows += _target_rows(ch, "spirit_max", "spirit_max")
    total = dv.spirit_max(ch)
    return total, _floor(rows, total)


def _mana(ch):
    rows = [stored_row("mana_base", ch.mana.max)] + _target_rows(ch, "mana_max", "mana_max")
    total = dv.mana_pool(ch).max
    return total, _floor(rows, total)


def _pool(ch, pid):
    from wp.model import formulas as fx
    from wp.model import pool_view as pv
    p = next(x for x in ch.pools if x.pid == pid)
    kind = RULE if isinstance(p.max, str) else STORED
    rows = [_row("pool_base", "source.pool_base", kind, fx.safe_value(p.max, ch), derived=kind == RULE,
                 rule=str(p.max) if kind == RULE else "")]
    rows += _target_rows(ch, sr.POOL + pid, sr.POOL_TARGET + pid)
    total = pv.max_of(ch, p)
    return total, _floor(rows, total)


def _temp(ch):
    rows = [stored_row("temp_button", ch.temp_hp)]
    rows += [_row(s.sid, s.name, EFFECT, s.temp_hp_left) for s in ch.statuses if s.active and s.temp_hp_left]
    return dv.temp_hp_total(ch), rows


def _lines(ch, number, lines, bonuses, rule="combat.md"):
    """A breakdown (label, value) with its "bonuses" line opened up into effect rows."""
    rows = []
    for label, value in lines:
        if label == "bonuses":
            rows += effect_rows(ch, bonuses) + off_rows(ch, number)
        else:
            rows.append(rule_row(label.replace(":", "_"), int(value), rule))
    return rows


def _attack(ch, kind):
    from wp.model import screen_view as scr
    a = scr.attack_number(ch, kind)
    number = "attack_" + kind
    return a["total"], _lines(ch, number, a["lines"], target_bonuses(ch, number))


def _stat(ch, number):
    from wp.model import stats_view as stv
    if number in SAVES:
        s, bs = stv.save(ch, number), typed_bonuses(ch, bo.SAVE, bo.SAVE_PREFIX + number)
    else:
        s = {"initiative": stv.initiative, "cmb": stv.cmb, "cmd": stv.cmd}[number](ch)
        bs = typed_bonuses(ch, {"initiative": bo.INITIATIVE, "cmb": bo.CMB, "cmd": bo.CMD}[number])
    return s.total, _lines(ch, number, s.lines, bs, "progression.md" if number in SAVES else "combat.md")


def _speed(ch):
    from wp.model import body_view as bv
    rows = [stored_row("base_speed", ch.base_speed)] + effect_rows(ch, typed_bonuses(ch, bo.SPEED)) + \
        off_rows(ch, "speed")
    rows.append(rule_row("armor_slowdown", -bv.armor_slowdown(ch), "gear.md"))
    total = bv.speed(ch)
    over = total - sum(r["value"] for r in rows if r["counted"])
    if over:                           # overload -10 ft and the speed multiplier (gear.md, rule switch)
        rows.append(rule_row("speed_other", over, "gear.md"))
    return total, rows


def _load(ch):
    rows = [rule_row("stat_str", dv.ability_mod(ch, "str"), "gear.md")] + _target_rows(ch, "load", "load_mod")
    return sum(r["value"] for r in rows if r["counted"]), rows


def _attention(ch):
    from wp.model.derived_view import ATTENTION_DRIVE_LEVEL, ATTENTION_LEVEL_STEP
    rows = [rule_row("attention_base", 1, "narrative.md"),
            rule_row("attention_level", ch.level // ATTENTION_LEVEL_STEP, "narrative.md"),
            rule_row("attention_drives", sum(1 for d in ch.drives if d.level >= ATTENTION_DRIVE_LEVEL),
                     "narrative.md")]
    rows += _target_rows(ch, "attention", "attention_per_cycle")
    return dv.attention_per_cycle(ch), rows


def _ac(ch, cell):
    from wp.model import ac_zones_view as zv
    from wp.model import screen_view as scr
    total = zv.cells(ch)[cell]["full"]
    parts = scr.cell_lines(ch)[cell]
    manual = [r for r in ch.source_rows if r.number == sr.AC + cell]
    on_sum = sum(int(r.value) for r in manual if r.on)
    rows = []
    for layer, value in parts:         # the manual rows are inside the flat layer: shown apart
        v = int(value) - (on_sum if layer == bo.FLAT else 0)
        if v or layer != bo.FLAT:
            rows.append(_row("layer_" + layer, "layer." + layer, RULE, v, derived=True, rule="defense_layers.md"))
    rows += [_row(r.sid, r.name, MANUAL, r.value, on=r.on, manual=True) for r in manual]
    rows = [rule_row("ac_base", rd.const("ac.base"), "defense.md")] + rows
    diff = total - sum(r["value"] for r in rows if r["counted"])
    if diff:                           # a rule the layers do not name (shown, so the rows add up)
        rows.append(rule_row("ac_other", diff, "defense_layers.md"))
    return total, rows


def _floor(rows, total):
    """A floor of the rules (max(0, ...)) shown as its own row so the rows still add up."""
    diff = total - sum(r["value"] for r in rows if r["counted"])
    return rows + ([rule_row("floor", diff, "resources.md")] if diff else [])


_BUILD = {"hp_max": _hp, "balance_max": _balance, "spirit_max": _spirit, "mana_max": _mana, "temp_hp": _temp,
          "attack_melee": lambda ch: _attack(ch, "melee"), "attack_ranged": lambda ch: _attack(ch, "ranged"),
          "speed": _speed, "load": _load, "attention": _attention}


def _status(ch, sid):
    """The effects of a status: one row per effect (target, value; a formula / "all" shown as its text)."""
    st = next(s for s in ch.statuses if s.sid == sid)
    ctx = dv.context(ch)
    rows = []
    for i, e in enumerate(st.effects):
        try:
            v = int(e.resolve(ctx))
        except Exception:              # noqa: BLE001 - a broken formula counts as 0 in a view (GOTCHAS)
            v = 0
        rule = "" if isinstance(e.value, int) else str(e.value)
        rows.append(_row("effect:%d" % i, e.target, EFFECT, v, on=st.active, rule=rule))
    return 0, rows


def view(ch, number):
    if number.startswith(STATUS):
        total, rows = _status(ch, number[len(STATUS):])
        return {"number": number, "total": 0, "rows": tuple(rows), "target": "", "editable_target": False,
                "effects_only": True}
    if number.startswith(sr.POOL):
        total, rows = _pool(ch, number[len(sr.POOL):])
    elif number.startswith(sr.AC):
        total, rows = _ac(ch, number[len(sr.AC):])
    elif number in ("initiative", "cmb", "cmd") + SAVES:
        total, rows = _stat(ch, number)
    else:
        total, rows = _BUILD[number](ch)
    target, _ = sr.target_of(number)
    return {"number": number, "total": int(total), "rows": tuple(rows), "target": target or "",
            "editable_target": bool(target), "effects_only": False}
