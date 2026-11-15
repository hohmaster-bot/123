# gui_chips.py — чипы + панель ресурсов + отдых (T-SPLIT-3.2, v18.6).
# Пассивный модуль: только функции, принимают app первым аргументом.
# НЕ импортирует gui.py. Зависимости — ленивые (внутри функций) или из соседних модулей.

import tkinter as tk
from tkinter import messagebox

from gui_shared import ToolTip
import purchases as P
import chips


# ===== Отдых =====

# (удалено: T-CHIPS — отдых теперь в chips._rest)


def do_short_rest(app):
    if not app.c: return
    app.c.short_rest()
    app._refresh()


def do_long_rest(app):
    if not app.c: return
    if not messagebox.askyesno(
            "Длинный отдых",
            "Восстановить всё до максимума?\n(Комфорт, внимание, неснимаемая боль, травмы, бафы не тронуты.)",
            parent=app.get_dialog_parent()):
        return
    app.c.long_rest()
    app._refresh()
    messagebox.showinfo("Длинный отдых", "Всё восстановлено.",
                        parent=app.get_dialog_parent())
    app._refresh()


# ===== Удаление бафа =====

def maybe_remove_buff(app, idx, act=False, bid=None):
    if not app.c: return
    if not (0 <= idx < len(app.c.situational_bonuses)): return
    b = app.c.situational_bonuses[idx]
    if app.c.settings.get("confirm_chip_delete", False):
        name = b.get("name", "?")
        if not messagebox.askyesno("Удалить баф", f"Удалить «{name}»?",
                                    parent=app.get_dialog_parent()):
            return
    if act and bid:
        app.c.deactivate_item(bid)
    else:
        app.c.situational_bonuses.pop(idx)
    app._refresh()


# ===== Flow-контейнер чипов =====

def init_flow_container(app):
    flow_frame = tk.Frame(app.resources_frame, bg="#2a2a2a")
    flow_frame.pack(side="left", fill="x", expand=True)
    app._flow_frame = flow_frame
    app._flow_items = []
    app._flow_lines = []
    app._flow_chip_ids = {}
    flow_frame.bind("<Configure>", lambda e: app._reflow_chips())


def add_chip(app, widget, chip_id=None):
    if not hasattr(app, "_flow_items"): return
    app._flow_items.append(widget)
    if chip_id:
        if not hasattr(app, "_flow_chip_ids"):
            app._flow_chip_ids = {}
        app._flow_chip_ids[widget] = chip_id
    app._reflow_chips()


def reflow_chips(app, event=None):
    if not getattr(app, "_flow_frame", None): return
    if not app._flow_frame.winfo_exists(): return
    width = app._flow_frame.winfo_width()
    if width < 50: width = app.root.winfo_width() - 120
    if width < 50: return
    pad = 6
    rows, cur, used = [], [], 0
    for w in app._flow_items:
        try:
            if not w.winfo_exists(): continue
            req = w.winfo_reqwidth() + pad
        except Exception:
            continue
        if cur and used + req > width:
            rows.append(cur); cur = []; used = 0
        cur.append(w); used += req
    if cur: rows.append(cur)
    for w in app._flow_items:
        try: w.pack_forget()
        except Exception: pass
    for line in app._flow_lines:
        try: line.destroy()
        except Exception: pass
    app._flow_lines = []
    dragging_src = getattr(app, "_drag_src", None) if getattr(app, "_drag_started", False) else None
    for widgets in rows:
        line = tk.Frame(app._flow_frame, bg="#2a2a2a")
        line.pack(fill="x", pady=1)
        app._flow_lines.append(line)
        for w in widgets:
            if w is dragging_src: continue  # скрыт во время drag
            try: w.pack(in_=line, side="left", padx=3)
            except Exception: pass


# ===== Модульные хелперы =====

def _lens_step(app, idx, delta):
    if not app.c or not (0 <= idx < len(app.c.lenses)): return
    ln = app.c.lenses[idx]
    cur, mx = int(ln.get("current", 0) or 0), int(ln.get("max", 0) or 0)
    new = max(0, cur + delta)
    if mx > 0 and new > mx: new = mx
    ln["current"] = new
    app._refresh()


# ===== Drag & drop чипов =====

def _drag_bind(app, widget):
    """Привязать drag к лейблу чипа (widget — Label)."""
    widget.bind("<ButtonPress-1>", lambda e: _drag_start(app, e), add="+")
    widget.bind("<B1-Motion>", lambda e: _drag_move(app, e), add="+")
    widget.bind("<ButtonRelease-1>", lambda e: _drag_end(app, e), add="+")


def _find_src(app, widget):
    """Найти Frame чипа, поднимаясь от widget вверх по master."""
    items = getattr(app, "_flow_items", [])
    while widget is not None:
        if widget in items:
            return widget
        widget = getattr(widget, "master", None)
    return None


def _drag_start(app, event):
    src = _find_src(app, event.widget)
    if src is None: return
    app._drag_src = src
    app._drag_started = False
    app._drag_ghost = None
    app._drag_ghost_offset = (0, 0)
    app._drag_indicator = None
    app._drag_want = None
    try:
        app._drag_orig_bg = src.cget("bg")
    except Exception:
        app._drag_orig_bg = "#3a3a3a"

def _drag_move(app, event):
    src = getattr(app, "_drag_src", None)
    if src is None: return
    if not getattr(app, "_drag_started", False):
        app._drag_started = True
        _make_ghost(app, src, event.x_root, event.y_root)
        try:
            src.config(highlightthickness=2, highlightbackground="#000",
                       bg="#222")
        except Exception:
            pass
    _move_ghost(app, event.x_root, event.y_root)
    _preview_insert(app, event.x_root, event.y_root)


def _drag_end(app, event):
    started = getattr(app, "_drag_started", False)
    src = getattr(app, "_drag_src", None)
    orig_bg = getattr(app, "_drag_orig_bg", "#3a3a3a")
    _destroy_ghost(app)
    _hide_indicator(app)
    want = getattr(app, "_drag_want", None)
    app._drag_src = None
    app._drag_started = False
    app._drag_want = None
    if src is not None:
        try:
            src.config(highlightthickness=0, bg=orig_bg)
        except Exception:
            pass
    if not started or src is None or want is None: return
    target, before = want
    _reorder(app, src, target, before)


def _make_ghost(app, src, x_root, y_root):
    """Создать полупрозрачный Toplevel-призрак с текстом чипа."""
    try:
        text = ""
        for ch in src.winfo_children():
            if ch.winfo_class() == "Label":
                text = ch.cget("text")
                break
        g = tk.Toplevel(app.root)
        g.overrideredirect(True)
        g.attributes("-topmost", True)
        try:
            g.attributes("-alpha", 0.75)
        except Exception:
            pass
        g.configure(bg="#3a3a3a")
        tk.Label(g, text=text or "?", bg="#3a3a3a", fg="white",
                 font=("Segoe UI", 9, "bold"), padx=8, pady=4).pack()
        app._drag_ghost = g
        app._drag_ghost_offset = (10, 10)
    except Exception:
        app._drag_ghost = None


def _move_ghost(app, x_root, y_root):
    g = getattr(app, "_drag_ghost", None)
    if g is None: return
    ox, oy = getattr(app, "_drag_ghost_offset", (10, 10))
    try:
        g.geometry(f"+{x_root + ox}+{y_root + oy}")
    except Exception:
        pass


def _destroy_ghost(app):
    g = getattr(app, "_drag_ghost", None)
    if g is not None:
        try: g.destroy()
        except Exception: pass
    app._drag_ghost = None


def _hide_indicator(app):
    line = getattr(app, "_drag_indicator", None)
    if line is not None:
        try: line.destroy()
        except Exception: pass
    app._drag_indicator = None


def _preview_insert(app, x_root, y_root):
    """Показать линию-индикатор (без reflow — чтобы не мигало)."""
    src = getattr(app, "_drag_src", None)
    if src is None: return
    target, before = _find_target(app, x_root, y_root, src)
    _hide_indicator(app)
    if target is None: return
    frame = getattr(app, "_flow_frame", None)
    if frame is None or not frame.winfo_exists(): return
    try:
        tx = target.winfo_rootx() - frame.winfo_rootx()
        ty = target.winfo_rooty() - frame.winfo_rooty()
        th = target.winfo_height()
        tw = target.winfo_width()
    except Exception:
        return
    lx = tx if before else tx + tw
    line = tk.Frame(frame, bg="#4af", width=2, height=th)
    line.place(x=lx, y=ty, width=2, height=th)
    app._drag_indicator = line
    app._drag_want = (target, before)


def _find_target(app, x_root, y_root, src):
    """Найти чип под курсором или ближайший. Возвращает (widget, before) или (None, None).
    before=True → вставить ПЕРЕД target, False → ПОСЛЕ."""
    items = [w for w in getattr(app, "_flow_items", []) if w is not src]
    if not items: return None, None
    # 1) Точное попадание
    for w in items:
        try:
            x, y = w.winfo_rootx(), w.winfo_rooty()
            ww, hh = w.winfo_width(), w.winfo_height()
        except Exception:
            continue
        if x <= x_root <= x + ww and y <= y_root <= y + hh:
            cx = x + ww / 2
            return w, (x_root < cx)
    # 2) Ближайший по расстоянию до центра
    best, best_d = None, 10**9
    for w in items:
        try:
            x, y = w.winfo_rootx(), w.winfo_rooty()
            ww, hh = w.winfo_width(), w.winfo_height()
        except Exception:
            continue
        cx, cy = x + ww / 2, y + hh / 2
        d = (cx - x_root) ** 2 + (cy - y_root) ** 2
        if d < best_d:
            best_d, best = d, w
    if best is None: return None, None
    try:
        x = best.winfo_rootx()
        ww = best.winfo_width()
    except Exception:
        return best, True
    return best, (x_root < x + ww / 2)


def _reorder(app, src, target, before=True):
    """Вставить src перед target (before=True) или после (before=False)."""
    items = app._flow_items
    if src not in items or target not in items: return
    i = items.index(src)
    items.pop(i)
    j = items.index(target)  # после pop
    if not before:
        j += 1
    items.insert(j, src)
    ids = []
    for w in items:
        cid = getattr(app, "_flow_chip_ids", {}).get(w)
        if cid: ids.append(cid)
    if app.c:
        app.c.settings["chips_order"] = ids
    app._refresh()


def bind_edit_number(app, widget, get_value, set_value, title, minv=0):
    """Правый клик по виджету → диалог ввода числа (gui_dialogs.ask_int)."""
    def _on_right(event):
        from gui_dialogs import ask_int
        current = get_value()
        new_val = ask_int(app, title,
                          f"Текущее: {current}\nВведите новое:",
                          default=current, minvalue=minv)
        if new_val is not None:
            set_value(new_val)
            app._refresh()
    widget.bind("<Button-3>", _on_right)


# ===== Реестр рендереров чипов =====

CHIP_REGISTRY = {}

def register(kind):
    def deco(fn):
        CHIP_REGISTRY[kind] = fn
        return fn
    return deco


def render_chip(app, spec):
    """Нарисовать один чип по ChipSpec. Возвращает Frame.
    Вызывает _render_* (создаёт Frame), затем add_chip(app, fr, spec["id"])."""
    fn = CHIP_REGISTRY.get(spec["kind"])
    if fn is None:
        return None
    fr = fn(app, spec)
    if fr is not None:
        add_chip(app, fr, spec["id"])
    return fr


@register("button")
def _render_button(app, spec):
    """Кнопка-чип (gui_combat). command — строка (ленивый вызов)."""
    d = spec["data"]
    import gui_combat
    import gui_rest
    cmd_name = d.get("command")
    cmd = None
    if cmd_name:
        if hasattr(gui_combat, cmd_name):
            cmd = getattr(gui_combat, cmd_name)
        elif hasattr(gui_rest, cmd_name):
            cmd = getattr(gui_rest, cmd_name)
        elif hasattr(app, cmd_name):
            cmd = getattr(app, cmd_name)

    label_fn = d.get("label_fn")
    label = label_fn() if label_fn else spec["label"]

    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=4, pady=2)
    btn = tk.Button(fr, text=label, command=(lambda: cmd(app)) if cmd else None,
                    bg=spec["color"], fg="white", relief="flat",
                    font=("Segoe UI", 9), activebackground="#666",
                    activeforeground="white")
    btn.pack()
    _drag_bind(app, btn)
    if spec.get("tip"):
        ToolTip(btn, spec["tip"])
    return fr


@register("button")
def _render_button(app, spec):
    """Кнопка-чип. Drag — за чёрную точку внизу справа. Клик — command."""
    d = spec["data"]
    import gui_combat
    import gui_rest
    cmd_name = d.get("command")
    cmd = None
    if cmd_name:
        if hasattr(gui_combat, cmd_name):
            cmd = getattr(gui_combat, cmd_name)
        elif hasattr(gui_rest, cmd_name):
            cmd = getattr(gui_rest, cmd_name)
        elif hasattr(app, cmd_name):
            cmd = getattr(app, cmd_name)

    label_fn = d.get("label_fn")
    label = label_fn() if label_fn else spec["label"]
    color_fn = d.get("color_fn")
    color = color_fn() if color_fn else spec["color"]

    fr = tk.Frame(app.resources_frame, bg=color)
    btn = tk.Button(fr, text=label, command=(lambda: cmd(app)) if cmd else None,
                    bg=color, fg="white", relief="flat",
                    font=("Segoe UI", 9), activebackground="#666",
                    activeforeground="white")
    btn.pack(padx=4, pady=2)
    if spec.get("tip"):
        ToolTip(btn, spec["tip"])

    # Чёрная квадратная точка drag — в самом правом нижнем углу fr (без отступа)
    dot = tk.Frame(fr, bg="#000", width=6, height=6, cursor="fleur")
    dot.place(relx=1.0, rely=1.0, anchor="se", width=6, height=6)
    _drag_bind(app, dot)

    return fr


@register("resource")
def _render_resource(app, spec):
    """Стандартный чип ресурса: ИМЯ cur/max."""
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)

    lbl = tk.Label(fr, text=f"{spec['icon']} {spec['label']}".strip(),
                   bg=spec["color"], fg="white", font=("Segoe UI", 9))
    lbl.pack(side="left")
    _drag_bind(app, lbl)
    if spec.get("edit"):
        bind_edit_number(app, lbl, spec["edit"]["get"],
                         spec["edit"]["set"], spec["edit"]["title"])

    if spec["max"] > 0:
        val = f"{spec['cur']}/{spec['max']}"
    else:
        val = str(spec["cur"])
    lbl_val = tk.Label(fr, text=val, bg=spec["color"], fg="white",
                       font=("Segoe UI", 9, "bold"))
    lbl_val.pack(side="left", padx=4)

    if spec.get("tip"):
        ToolTip(lbl, spec["tip"])
        ToolTip(lbl_val, spec["tip"])
    return fr


@register("ability")
def _render_ability(app, spec):
    """Абилка с uses: [−] ИМЯ cur/max [+]"""
    c = app.c
    d = spec["data"]
    i, src = d["idx"], d["source"]
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)

    lbl = tk.Label(fr, text=spec["label"], bg=spec["color"], fg="white",
                   font=("Segoe UI", 9, "bold"))
    lbl.pack(side="left")
    _drag_bind(app, lbl)
    if spec.get("tip"):
        ToolTip(lbl, spec["tip"])

    def _minus():
        if src == "class": c.use_ability(i)
        else: c.use_race_ability(i)
        app._refresh()
    def _plus():
        if src == "class": c.restore_ability(i)
        else: c.restore_race_ability(i)
        app._refresh()

    tk.Button(fr, text="−", width=2, command=_minus,
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    tk.Label(fr, text=f"{spec['cur']}/{spec['max']}", bg=spec["color"],
             fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=4)
    tk.Button(fr, text="+", width=2, command=_plus,
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    return fr


@register("item")
def _render_item(app, spec):
    """Предмет с uses: [−] 📦 ИМЯ cur/max [+]"""
    c = app.c
    iid = spec["data"]["iid"]
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)

    lbl = tk.Label(fr, text=f"📦 {spec['label']}", bg=spec["color"],
                   fg="white", font=("Segoe UI", 9, "bold"))
    lbl.pack(side="left")
    _drag_bind(app, lbl)
    if spec.get("tip"): ToolTip(lbl, spec["tip"])

    def _minus():
        it = c.items.get(iid)
        if it: it["uses_current"] = max(0, it.get("uses_current", 0) - 1); app._refresh()
    def _plus():
        it = c.items.get(iid)
        if it: it["uses_current"] = min(it.get("uses_max", 0), it.get("uses_current", 0) + 1); app._refresh()

    tk.Button(fr, text="−", width=2, command=_minus,
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    tk.Label(fr, text=f"{spec['cur']}/{spec['max']}", bg=spec["color"],
             fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=4)
    tk.Button(fr, text="+", width=2, command=_plus,
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    return fr


@register("attack")
def _render_attack(app, spec):
    """Атака: [−] ⚔ ИМЯ cur/max [+] или просто ⚔ ИМЯ"""
    c = app.c
    d = spec["data"]
    i, has_uses = d["idx"], d["has_uses"]
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)

    if not has_uses:
        lbl = tk.Label(fr, text=f"⚔ {spec['label']}", bg=spec["color"],
                       fg="white", font=("Segoe UI", 9, "bold"))
        lbl.pack()
        _drag_bind(app, lbl)
        if spec.get("tip"): ToolTip(lbl, spec["tip"])
        return fr

    def _minus():
        if i < len(c.attacks): c.attacks[i]["uses_current"] = max(0, c.attacks[i].get("uses_current", 0) - 1); app._refresh()
    def _plus():
        if i < len(c.attacks): c.attacks[i]["uses_current"] = min(c.attacks[i].get("uses_max", 0), c.attacks[i].get("uses_current", 0) + 1); app._refresh()

    lbl = tk.Label(fr, text=f"⚔ {spec['label']}", bg=spec["color"],
                   fg="white", font=("Segoe UI", 9, "bold"))
    lbl.pack(side="left")
    _drag_bind(app, lbl)
    if spec.get("tip"): ToolTip(lbl, spec["tip"])
    tk.Button(fr, text="−", width=2, command=_minus,
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    tk.Label(fr, text=f"{spec['cur']}/{spec['max']}", bg=spec["color"],
             fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=4)
    tk.Button(fr, text="+", width=2, command=_plus,
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    return fr


@register("buff")
def _render_buff(app, spec):
    """Баф: [−] icon ИМЯ cur [⟳] ⚡N/M [−][+] [+] [×]"""
    c = app.c
    d = spec["data"]
    idx = d["idx"]
    is_perm = d["is_permanent"]
    b_max = spec["max"]
    b_cur = spec["cur"]
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)

    if not is_perm:
        def _dur_minus():
            if not (0 <= idx < len(c.situational_bonuses)): return
            bb = c.situational_bonuses[idx]
            cur = int(bb.get("duration_current", 0) or 0)
            if cur <= 0:
                app._maybe_remove_buff(idx); return
            bb["duration_current"] = cur - 1; app._refresh()
        tk.Button(fr, text="−", width=2, command=_dur_minus,
                  font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
                  activebackground="#777").pack(side="left", padx=(0, 2))

    lbl = tk.Label(fr, text=f"{spec['icon']} {spec['label']}", bg=spec["color"],
                   fg="white", font=("Segoe UI", 9, "bold"))
    lbl.pack(side="left")
    _drag_bind(app, lbl)
    if spec.get("tip"): ToolTip(lbl, spec["tip"])
    lbl_val = tk.Label(fr, text=" ∞" if is_perm else f" {b_cur}",
                       bg=spec["color"], fg="white",
                       font=("Segoe UI", 9, "bold"))
    lbl_val.pack(side="left", padx=(2, 2))
    if spec.get("tip"): ToolTip(lbl_val, spec["tip"])

    charges_max = d["charges_max"]
    has_on_act = d["has_on_act"]
    if charges_max > 0 or has_on_act:
        charges_cur = d["charges_cur"]
        def _buff_activate():
            if not (0 <= idx < len(c.situational_bonuses)): return
            if c.trigger_buff(idx): app._refresh()
        act_state = "normal" if (charges_max == 0 or charges_cur > 0) else "disabled"
        tk.Button(fr, text="⟳", width=2, command=_buff_activate, state=act_state,
                  font=("Segoe UI", 9), relief="flat", bg="#665", fg="white",
                  activebackground="#887").pack(side="left", padx=(2, 1))
        def _charges_minus():
            if not (0 <= idx < len(c.situational_bonuses)): return
            bb = c.situational_bonuses[idx]
            if bb.get("charges_current", 0) > 0:
                bb["charges_current"] -= 1; app._refresh()
        def _charges_plus():
            if not (0 <= idx < len(c.situational_bonuses)): return
            bb = c.situational_bonuses[idx]
            if bb.get("charges_max", 0) > 0 and bb.get("charges_current", 0) < bb.get("charges_max", 0):
                bb["charges_current"] += 1; app._refresh()
        tk.Label(fr, text=f"⚡{charges_cur}/{charges_max}", bg=spec["color"],
                 fg="white", font=("Segoe UI", 9)).pack(side="left", padx=(1, 1))
        tk.Button(fr, text="−", width=1, command=_charges_minus,
                  font=("Segoe UI", 8), relief="flat", bg="#444", fg="white",
                  activebackground="#777").pack(side="left")
        tk.Button(fr, text="+", width=1, command=_charges_plus,
                  font=("Segoe UI", 8), relief="flat", bg="#444", fg="white",
                  activebackground="#777").pack(side="left")

    if not is_perm:
        def _dur_plus():
            if not (0 <= idx < len(c.situational_bonuses)): return
            bb = c.situational_bonuses[idx]
            cur = int(bb.get("duration_current", 0) or 0)
            mx = int(bb.get("duration_rounds", 0) or 0)
            if mx > 0 and cur >= mx: return
            bb["duration_current"] = cur + 1; app._refresh()
        plus_state = "normal" if (b_max == 0 or b_cur < b_max) else "disabled"
        tk.Button(fr, text="+", width=2, command=_dur_plus, state=plus_state,
                  font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
                  activebackground="#777").pack(side="left", padx=(0, 2))

    def _remove():
        app._maybe_remove_buff(idx, act=d["is_activation"], bid=d["bid"])
    tk.Button(fr, text="×", width=2, command=_remove,
              font=("Segoe UI", 9), relief="flat", bg="#444", fg="white",
              activebackground="#777").pack(side="left", padx=(4, 0))
    return fr


@register("feat")
def _render_feat(app, spec):
    """Активная черта (не стойка): ⭐ ИМЯ."""
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)
    lbl = tk.Label(fr, text=f"⭐ {spec['label']}", bg=spec["color"],
                   fg="white", font=("Segoe UI", 9, "bold"))
    lbl.pack()
    _drag_bind(app, lbl)
    if spec.get("tip"): ToolTip(lbl, spec["tip"])
    return fr


@register("lens")
def _render_lens(app, spec):
    """Линза: [−] 🔍 ИМЯ cur/max [+]"""
    i = spec["data"]["idx"]
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)

    lbl = tk.Label(fr, text=f"🔍 {spec['label']}", bg=spec["color"],
                   fg="white", font=("Segoe UI", 9, "bold"))
    lbl.pack(side="left")
    _drag_bind(app, lbl)
    if spec.get("tip"): ToolTip(lbl, spec["tip"])
    tk.Button(fr, text="−", width=2, command=lambda: _lens_step(app, i, -1),
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    tk.Label(fr, text=f"{spec['cur']}/{spec['max']}", bg=spec["color"],
             fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=2)
    tk.Button(fr, text="+", width=2, command=lambda: _lens_step(app, i, 1),
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    return fr


@register("spell")
def _render_spell(app, spec):
    """Заклинание: 📖 ИМЯ [✨ cast]"""
    c = app.c
    d = spec["data"]
    idx, can = d["idx"], d["can_cast"]
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)

    lbl = tk.Label(fr, text=f"📖 {spec['label']}", bg=spec["color"],
                   fg="white" if can else "#888",
                   font=("Segoe UI", 9, "bold"))
    lbl.pack(side="left")
    _drag_bind(app, lbl)
    if spec.get("tip"): ToolTip(lbl, spec["tip"])

    if can:
        def _cast():
            r = c.cast_spell(idx)
            if not r.get("ok"):
                messagebox.showinfo("Заклинание", r.get("msg", "?"),
                                    parent=app.get_dialog_parent()); return
            ks = int(r.get("concentration_ks", 0) or 0)
            if ks > 0:
                messagebox.showinfo("Концентрация",
                    f"Баланса не хватило: получено {r.get('injury', 0)} ОТ.\n\n"
                    f"Проверка концентрации: КС {ks}\n(10 + 2×ОТ).\n\n"
                    f"Бросьте кубик в реальности:\n  прошли — заклинание сработало;\n"
                    f"  провалили — заклинание не сработало.\n\n"
                    f"Ресурсы, баланс и перегрузка уже списаны.",
                    parent=app.get_dialog_parent())
            app._refresh()
        tk.Button(fr, text="✨", width=2, command=_cast,
                  font=("Segoe UI", 9), relief="flat", bg="#665", fg="white",
                  activebackground="#887").pack(side="left", padx=(2, 0))
    return fr


@register("quest")
def _render_quest(app, spec):
    """Квест: 📜 ИМЯ."""
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)
    lbl = tk.Label(fr, text=f"📜 {spec['label']}", bg=spec["color"],
                   fg="white", font=("Segoe UI", 9, "bold"))
    lbl.pack(side="left")
    _drag_bind(app, lbl)
    if spec.get("tip"): ToolTip(lbl, spec["tip"])
    return fr


@register("overload")
def _render_overload(app, spec):
    """Перегрузка: ⛓ Перегрузка: N [−] [+] [0]"""
    c = app.c
    val = spec["data"]["val"]
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)

    txt = f"⛓ Перегрузка: {val}"
    if val > 0: txt += " ⚠"
    lbl = tk.Label(fr, text=txt, bg=spec["color"], fg="white",
                   font=("Segoe UI", 9, "bold"))
    lbl.pack(side="left")
    _drag_bind(app, lbl)
    if spec.get("tip"): ToolTip(lbl, spec["tip"])

    def _minus(): setattr(c, "overload", max(0, val - 1)); app._refresh()
    def _plus():  setattr(c, "overload", val + 1); app._refresh()
    def _zero():  setattr(c, "overload", 0); app._refresh()

    tk.Button(fr, text="−", width=2, command=_minus,
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    tk.Button(fr, text="+", width=2, command=_plus,
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    if val > 0:
        tk.Button(fr, text="0", width=2, command=_zero,
                  font=("Segoe UI", 9, "bold"), relief="flat", bg="#777",
                  fg="white", activebackground="#999").pack(side="left", padx=2)
    return fr


@register("comfort")
def _render_comfort(app, spec):
    """Комфорт: [−] 😌 Комфорт cur/max [+]"""
    c = app.c
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)

    lbl = tk.Label(fr, text="😌 Комфорт", bg=spec["color"], fg="white",
                   font=("Segoe UI", 9))
    lbl.pack(side="left")
    _drag_bind(app, lbl)
    if spec.get("tip"): ToolTip(lbl, spec["tip"])

    def _minus():
        try: P.spend_comfort(c, 1)
        except P.PurchaseError: pass
        app._refresh()
    def _plus():
        c.comfort["current"] += 1; app._refresh()

    tk.Button(fr, text="−", width=2, command=_minus,
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    lbl_val = tk.Label(fr, text=f"{spec['cur']}/{spec['max']}", bg=spec["color"],
                       fg="white", font=("Segoe UI", 9, "bold"))
    lbl_val.pack(side="left", padx=4)
    if spec.get("tip"): ToolTip(lbl_val, spec["tip"])
    tk.Button(fr, text="+", width=2, command=_plus,
              font=("Segoe UI", 9), relief="flat", bg="#555", fg="white",
              activebackground="#777").pack(side="left", padx=2)
    return fr


@register("stance")
def _render_stance(app, spec):
    c = app.c
    fr = tk.Frame(app.resources_frame, bg=spec["color"], padx=6, pady=2)
    d = spec["data"]
    names, cur = d["names"], d["current"]

    var = tk.StringVar(value=cur)
    def _pick(val):
        if c.active_stance is not None:
            d["on_pick"](val)
        app._refresh()

    opt = tk.OptionMenu(fr, var, *names, command=_pick)
    opt.config(width=14, font=("Segoe UI", 9), bg="#3a3a3a",
               fg="white", activebackground="#555",
               activeforeground="white", relief="flat", highlightthickness=0)
    opt["menu"].config(bg="#2a2a2a", fg="white", activebackground="#555")
    opt.pack(side="left", padx=(0, 4))

    btn = tk.Button(fr, text="", width=4, relief="flat",
                    font=("Segoe UI", 9, "bold"),
                    command=lambda: (d["on_toggle"](), app._refresh()))
    if c.active_stance is not None:
        btn.config(text="ON", bg="#6fbf3f", fg="#111", activebackground="#8fdf5f")
    else:
        btn.config(text="Off", bg="#555", fg="#aaa", activebackground="#777")
    btn.pack(side="left")

    if c.active_stance:
        for s in c.stances():
            if s.get("name") == c.active_stance:
                if s.get("desc"):
                    ToolTip(btn, s["desc"]); ToolTip(opt, s["desc"])
                break
    return fr


# ===== Панель ресурсов =====

def rebuild_resources_panel(app):
    if not app.c: return
    if not (getattr(app, "resources_frame", None)
            and app.resources_frame.winfo_exists()):
        return
    c = app.c
    for w in app.resources_frame.winfo_children(): w.destroy()
    tk.Label(app.resources_frame, text="Ресурсы:", bg="#2a2a2a", fg="#aaa",
             font=("Segoe UI", 9, "bold")).pack(side="left", padx=(4, 8))
    init_flow_container(app)

    all_specs = chips.collect_all(c)
    if c.settings.get("chips_visible_enabled", False):
        visible = set(c.settings.get("chips_visible", []) or [])
        all_specs = [s for s in all_specs if s["id"] in visible]
    order = c.settings.get("chips_order", []) or []
    order_map = {sid: i for i, sid in enumerate(order)}
    all_specs.sort(key=lambda s: order_map.get(s["id"], 10**9))
    for spec in all_specs:
        render_chip(app, spec)