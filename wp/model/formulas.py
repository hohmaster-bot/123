"""Formula values on the sheet (package 14 C): the variables of wp.core.formula read from the character.
A bad formula never crashes a derived view: safe_value gives 0 (validation happens when it is added or
edited, see validate)."""
from wp.core import formula as cf
from wp.model import classes as klass
from wp.model.character import ABILITIES

STATS = ABILITIES


def variables(ch):
    from wp.model import derived_view as dv
    out = {"level": ch.level, "bab": klass.bab(ch)}
    for a in STATS:
        out["%s_mod" % a] = dv.ability_mod(ch, a)
    return out


def safe_value(value, ch):
    """A number as is; a formula string evaluated on the current sheet; a broken formula -> 0."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    try:
        return cf.evaluate(value, variables(ch))
    except (cf.FormulaError, TypeError, ValueError):
        return 0


def validate(value):
    """None when fine; raises FormulaError with the reason otherwise (numbers are always fine)."""
    if isinstance(value, str):
        cf.validate(value)


def validate_effects(effects):
    """Raise FormulaError for the first effect whose value is a broken formula ("all" is not a formula)."""
    from wp.core.effects import ALL
    for e in effects:
        if isinstance(e.value, str) and e.value != ALL:
            cf.validate(e.value)
