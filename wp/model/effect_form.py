"""The effect editor form, Qt-free (package 38 P5, owner decision 9; ARCH decision D37; closes Q276).

targets() -> every effect target an editor offers: the roll and defence targets of the core, the sheet targets
    (wp/catalog/data/sheet_targets.json; a prefix target ends with ':' and takes an id) and const:<id> of every
    numeric rule constant (the view effect_targets).
search(text) -> the targets containing the text (case-insensitive).
build(form) -> Effect from a form {target, value, mode, condition, scope, situational, btype}, or EffectFormError
    (reason, values): a target outside the list, an empty value, a broken formula (the formula checker), "replace" on
    a target that is not a rule constant, an unknown condition kind, a scope where the target has none, an unknown
    bonus type. Invalid input never becomes an effect.
form_of(effect) -> the form of an existing effect (the editor fills its fields); to_data(effect) -> the catalog form
    of an effect (only the fields that differ from the defaults).
"""
from wp.core import bonuses as bo
from wp.core import formula as fm
from wp.core.effects import Effect

CONST = "const:"
REPLACE = "replace"
MODES = ("add", REPLACE)
SCOPES = ("", "melee", "ranged")
SCOPED_TARGETS = ("damage_per_pain",)          # Effect.scope exists only there (package 37, Q279)
CORE_TARGETS = (bo.AC, bo.ATTACK, bo.DAMAGE, bo.SAVE, bo.SAVE_PREFIX + "fort", bo.SAVE_PREFIX + "ref",
                bo.SAVE_PREFIX + "will", bo.SKILL, bo.SKILL_PREFIX, bo.INITIATIVE, bo.CMB, bo.MANEUVER, bo.CMD,
                bo.ROLLS, bo.SPEED, bo.CRIT_RANGE)
PLAIN_CONDITIONS = ("hp_full", "bp_full", "in_combat")
NUMBER_CONDITIONS = ("pressure_eq:", "pressure_ge:", "pressure_le:", "pain_ge:")
ID_CONDITIONS = ("charges_left:", "status_tag:", "manual:")
FIELDS = ("target", "value", "mode", "condition", "scope", "situational", "btype")


class EffectFormError(ValueError):
    def __init__(self, reason, values=()):
        super().__init__(reason)
        self.reason, self.values = reason, tuple(values)


def targets():
    from wp.model import sheet_targets as stg
    from wp.rules_data import rules as rd
    sheet = tuple(t for t in stg.TARGETS if t != CONST)
    consts = tuple(CONST + cid for cid in sorted(rd.numeric_ids()))
    return tuple(sorted(set(CORE_TARGETS + sheet))) + consts


def search(text):
    t = str(text or "").strip().lower()
    return tuple(x for x in targets() if t in x.lower())


def target_ok(target, offered=None):
    offered = targets() if offered is None else offered
    if target in offered and not target.endswith(":"):
        return True
    if target.startswith(CONST):
        return False                               # a rule constant must be one of the listed ids
    return any(p.endswith(":") and target.startswith(p) and len(target) > len(p) for p in offered)


def condition_ok(cid):
    if not cid:
        return True
    for part in cid.split("&"):
        if part in PLAIN_CONDITIONS:
            continue
        num = next((p for p in NUMBER_CONDITIONS if part.startswith(p)), None)
        if num is not None:
            rest = part[len(num):]
            if rest.lstrip("-").isdigit():
                continue
            return False
        idp = next((p for p in ID_CONDITIONS if part.startswith(p)), None)
        if idp is None or not part[len(idp):].strip():
            return False
    return True


def _value(text):
    v = str(text if text is not None else "").strip()
    if not v:
        raise EffectFormError("effect_value_needed")
    if v.lstrip("-").isdigit():
        return int(v)
    try:
        fm.validate(v)
    except fm.FormulaError as e:
        raise EffectFormError("bad_effect_formula", (v, str(e)))
    return v


def build(form):
    f = dict(form or {})
    target = str(f.get("target", "")).strip()
    if not target_ok(target):
        raise EffectFormError("unknown_effect_target", (target,))
    value = _value(f.get("value"))
    mode = f.get("mode") or "add"
    if mode not in MODES:
        raise EffectFormError("unknown_effect_mode", (mode,))
    if mode == REPLACE and not target.startswith(CONST):
        raise EffectFormError("replace_const_only", (target,))
    cond = str(f.get("condition", "") or "").strip()
    if not condition_ok(cond):
        raise EffectFormError("unknown_condition", (cond,))
    scope = f.get("scope", "") or ""
    if scope not in SCOPES or (scope and target not in SCOPED_TARGETS):
        raise EffectFormError("scope_not_allowed", (scope, target))
    btype = f.get("btype", "") or bo.FLAT
    if btype not in bo.TYPES:
        raise EffectFormError("unknown_bonus_type", (btype,))
    return Effect(target, value, btype, note=REPLACE if mode == REPLACE else "", condition=cond,
                  situational=str(f.get("situational", "") or "").strip(), scope=scope)


def form_of(e):
    return {"target": e.target, "value": str(e.value), "mode": REPLACE if e.note == REPLACE else "add",
            "condition": e.condition, "scope": e.scope, "situational": e.situational, "btype": e.btype}


def to_data(e):
    """The catalog form of an effect: the fields that differ from the defaults."""
    import dataclasses
    base = Effect(e.target)
    out = {"target": e.target}
    for fld in dataclasses.fields(e):
        v = getattr(e, fld.name)
        if fld.name != "target" and v != getattr(base, fld.name):
            out[fld.name] = list(v) if isinstance(v, tuple) else v
    return out
