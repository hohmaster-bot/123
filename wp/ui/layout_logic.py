"""The Classic layout editor without Qt (package 35 P5, ROADMAP step 8; UI_WISHES "Classic screen v2" point 13).
Pure functions over the layout profile items (the classic profile "panels"), tested without PySide6.

snap(value, step) -> the value rounded to the grid step (half up; the step from data/screen_blocks.json
    "layout_grid"); a step of 0 or less leaves the value.
column_items(panels, dock) -> the visible-or-hidden items of one column (dock) ordered by position y, then x.
move_fields(panels, item_id, direction) -> {item id: {"position": [x, y]}} that swap the item with its neighbour in
    its column (direction -1 = up, +1 = down); {} at the edge.
to_column(panels, item_id, dock, step) -> the fields that put the item at the end of another column (left / center /
    right): dock and the position below the last item there (snapped).
resize_fields(size, dw, dh, step) -> {"size": [w, h]} snapped (never below one step; a size under the block minimum
    is allowed: the warnings say so, they never forbid).
"""
COLUMNS = ("left", "center", "right")
ROUND_HALF = 0.5


def snap(value, step):
    step = int(step)
    if step <= 0:
        return int(value)
    return int((float(value) / step) + ROUND_HALF) * step


def _key(item):
    pos = tuple(item.get("position") or (0, 0)) + (0, 0)
    return int(pos[1]), int(pos[0])


def column_items(panels, dock):
    return sorted((i for i in panels if i.get("dock") == dock), key=_key)


def move_fields(panels, item_id, direction):
    item = next(i for i in panels if i["id"] == item_id)
    col = column_items(panels, item.get("dock"))
    k = [i["id"] for i in col].index(item_id)
    j = k + int(direction)
    if not 0 <= j < len(col):
        return {}
    other = col[j]
    a, b = list(item.get("position") or (0, 0)), list(other.get("position") or (0, 0))
    if a == b:                         # same place: push the lower one one unit down
        b = [b[0], b[1] + 1]
    return {item_id: {"position": b}, other["id"]: {"position": a}}


def to_column(panels, item_id, dock, step):
    col = [i for i in column_items(panels, dock) if i["id"] != item_id]
    if col:
        last = col[-1]
        y = _key(last)[0] + int((last.get("size") or (0, 0))[1]) + int(step)
    else:
        y = 0
    return {"dock": dock, "position": [0, snap(y, step)]}


def resize_fields(size, dw, dh, step):
    w, h = int(size[0]) + int(dw), int(size[1]) + int(dh)
    return {"size": [max(int(step), snap(w, step)), max(int(step), snap(h, step))]}
