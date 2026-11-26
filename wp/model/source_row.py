"""A manual source row of a sheet number (package 34, owner: every derived number has sources, the editor mode shows
and changes them). Stored on the character (Character.source_rows); an ON row acts as a flat effect on the number's
effect target (derived_view.other_sources), so every formula that reads effects counts it. The derived total is never
stored. `number` = the id of the number (wp/model/sources.py NUMBERS, e.g. "hp_max", "pool:ki", "ac:1")."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceRow:
    sid: str
    number: str
    name: str = ""
    value: int = 0
    on: bool = True


# number id -> the effect target an ON manual row feeds (a flat bonus); None = no effect target (read-only sources)
TARGETS = {"hp_max": "hp_max", "balance_max": "balance_max", "spirit_max": "spirit_max", "mana_max": "mana_max",
           "attack_melee": "attack_melee", "attack_ranged": "attack_ranged", "initiative": "initiative",
           "cmb": "cmb", "cmd": "cmd", "fort": "save:fort", "ref": "save:ref", "will": "save:will",
           "speed": "speed", "load": "load_mod", "attention": "attention_per_cycle",
           "temp_hp": "temp_hp"}
POOL = "pool:"
AC = "ac:"
POOL_TARGET = "pool_max:"
AC_TARGET = "ac"


def target_of(number):
    """(effect target, cells) of a number id; (None, ()) when it has none (or the id is unknown)."""
    if number.startswith(POOL):
        return POOL_TARGET + number[len(POOL):], ()
    if number.startswith(AC):
        return AC_TARGET, (number[len(AC):],)
    return TARGETS.get(number), ()


def effects(rows):
    """(source id, Effect) of the ON rows with an effect target."""
    from wp.core.effects import Effect
    out = []
    for r in rows:
        target, cells = target_of(r.number)
        if r.on and target:
            out.append(("source:" + r.sid, (Effect(target, int(r.value), cells=cells),)))
    return out
