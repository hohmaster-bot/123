"""Languages of a race (package 36, owner decision 16; RULES/training.md "Languages"): a race gives "known languages";
the first is the native one (free), the others are known, not native. Ids are made by the program."""
from wp.model import ids
from wp.model.character import Language


def languages(names, taken=()):
    """Language records for the names (the first native); names already known (by name) are skipped."""
    out, have = [], [lg.lid for lg in taken]
    known = {lg.name for lg in taken}
    first = True
    for name in names:
        if name in known:
            first = False
            continue
        lid = ids.make_id(name, have + [x.lid for x in out])
        out.append(Language(lid, name, native=first and not any(lg.native for lg in taken)))
        first = False
    return tuple(out)
