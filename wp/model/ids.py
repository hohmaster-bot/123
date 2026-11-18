"""Stable ids (D7) made by the program: the player never types an id.

make_id(title, taken): lower-case ASCII from the title (Cyrillic transliterated), other
characters -> "_"; when the id is taken, "_2", "_3", ... is added.
"""
# Cyrillic a..ya (U+0430..U+044F) in order, then yo (U+0451).
_RU = ("a", "b", "v", "g", "d", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p",
       "r", "s", "t", "u", "f", "kh", "ts", "ch", "sh", "shch", "", "y", "", "e", "yu", "ya")
_TRANSLIT = {chr(0x430 + i): t for i, t in enumerate(_RU)}
_TRANSLIT[chr(0x451)] = "e"
FALLBACK = "id"


def slug(title):
    out = []
    for c in str(title).lower():
        if c in _TRANSLIT:
            out.append(_TRANSLIT[c])
        elif c.isascii() and c.isalnum():
            out.append(c)
        else:
            out.append("_")
    s = "_".join(p for p in "".join(out).split("_") if p)
    return s or FALLBACK


def make_id(title, taken=()):
    """New id from a title; a number is added when it collides with an existing id."""
    return unique(slug(title), taken)


def unique(base, taken=()):
    """base, or base_2, base_3, ... (the first one not taken)."""
    taken = set(taken)
    if base not in taken:
        return base
    n = 2
    while "%s_%d" % (base, n) in taken:
        n += 1
    return "%s_%d" % (base, n)
