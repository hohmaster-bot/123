"""The statuses block and the combat tab without Qt (package 34 part 2): pure functions, tested without PySide6.

filter_entries(entries, mode) -> the container entries shown by the filter All / Active / Favorites (statuses and
    injuries of the statuses view; hidden entries only under All).
entry_text(entry) -> (duration key, values) for the i18n call: rounds left (ticks), until the end of combat, no end;
    "off" for an inactive entry.
next_square(squares) -> the number the next spend takes: the SMALLEST free one (the core spends smallest first);
    None when every square is spent.
grid_shape(cells, columns, lo, hi) -> (cells, columns, rows): the quick grid size clamped to lo..hi (UI_WISHES 9:
    default 8, 4-16); columns at least 1 and at most cells.
tab_list(item, default) -> the tab ids of the tab bar (the layout item's own "tabs" or the default data).
"""
ALL, ACTIVE, FAVORITES = "all", "active", "favorites"
MODES = (ALL, ACTIVE, FAVORITES)
TICKS = "ticks"                        # Status.duration kinds (core effects.TICKS / END_OF_COMBAT)
END_OF_COMBAT = "end_of_combat"


def filter_entries(entries, mode):
    if mode == ACTIVE:
        return tuple(e for e in entries if e.active and not e.hidden)
    if mode == FAVORITES:
        return tuple(e for e in entries if e.favorite and not e.hidden)
    return tuple(entries)


def entry_text(entry):
    rem = getattr(entry, "remaining", None)
    if not entry.active:
        return "statuses.off", ()
    kind = getattr(entry, "duration", None)
    if kind == TICKS and isinstance(rem, int):
        return "statuses.rounds", (rem,)
    if kind == END_OF_COMBAT:
        return "statuses.end_of_combat", ()
    return "statuses.infinite", ()


def next_square(squares):
    free = [n for n, spent in squares if not spent]
    return min(free) if free else None


def grid_shape(cells, columns, lo, hi):
    n = max(lo, min(hi, int(cells or lo)))
    cols = max(1, min(n, int(columns or 1)))
    rows = (n + cols - 1) // cols
    return n, cols, rows


def tab_list(item, default):
    return list((item or {}).get("tabs") or default)
