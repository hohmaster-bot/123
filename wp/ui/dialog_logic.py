"""Qt-free logic of the dialogs and the tab bar (package 35 P1), tested without PySide6.

visible_rows(rows, show_all) -> the source rows the Sources dialog shows: by default the rows whose value is 0 are
    hidden (owner review 3); show_all shows every row.
show_all_start(saved, editor) -> the first state of the "show all" toggle: ON in the editor mode, else the saved one.
fit_size(content, saved, screen) -> (w, h) of a dialog: the size the owner dragged it to (saved) or the size of its
    content, never larger than the screen (owner review 4).
flow_rows(widths, avail, gap) -> rows of item indexes: the items flow onto further rows when the width is short.
pinned_rows(count, rows) -> rows of item indexes for a pinned tab bar: exactly `rows` rows (0 = automatic).
"""
import math


def visible_rows(rows, show_all):
    return [r for r in rows if show_all or int(r.get("value", 0)) != 0]


def show_all_start(saved, editor):
    return True if editor else bool(saved)


def fit_size(content, saved, screen):
    w, h = (int(v) for v in (saved or content))
    sw, sh = (int(v) for v in screen)
    return max(1, min(w, sw)), max(1, min(h, sh))


def flow_rows(widths, avail, gap):
    rows, row, used = [], [], 0
    for i, w in enumerate(widths):
        need = w if not row else used + gap + w
        if row and need > avail:
            rows.append(row)
            row, need = [], w
        row.append(i)
        used = need
    if row:
        rows.append(row)
    return rows


def pinned_rows(count, rows):
    if rows <= 0 or count <= 0:
        return []
    per = int(math.ceil(count / float(min(rows, count))))
    return [list(range(i, min(count, i + per))) for i in range(0, count, per)]
