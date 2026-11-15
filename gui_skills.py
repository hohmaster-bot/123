# gui_skills.py — редактор навыков (v4)
# v4: статы в 2 строки (STR/DEX/CON | INT/WIS/CHA)
import tkinter as tk
from tkinter import messagebox

from character import SKILL_TIER_NAMES
from gui_shared import make_scrollable
from gui_windows import open_window
import purchases as P

def _gi_int_val(m, key="value", default=0):
    """Безопасно достаёт int из dict-модификатора."""
    try:
        return int(m.get(key, default))
    except (TypeError, ValueError):
        return default


STATS_ROW1 = [("str", "Сила"), ("dex", "Ловкость"),
              ("con", "Телосложение")]
STATS_ROW2 = [("int", "Интеллект"), ("wis", "Мудрость"),
              ("cha", "Харизма")]

TIERS_LIST = [("normal", "Обычный"),
              ("advanced", "Продвинутый"),
              ("specialized", "Спец")]


def _render_stat_radios(parent, stat_var):
    """Рендерит 2 ряда радиокнопок для выбора стата."""
    fr1 = tk.Frame(parent)
    fr1.pack(fill="x", padx=5)
    for ab, label in STATS_ROW1:
        tk.Radiobutton(fr1, text=label, value=ab,
                       variable=stat_var).pack(side="left", padx=3)
    fr2 = tk.Frame(parent)
    fr2.pack(fill="x", padx=5)
    for ab, label in STATS_ROW2:
        tk.Radiobutton(fr2, text=label, value=ab,
                       variable=stat_var).pack(side="left", padx=3)


def edit_skills(app):
    if not app.c:
        return

    def build(parent):
        c = app.c
        top = tk.Frame(parent, bg="#f4f4f4")
        top.pack(fill="x", pady=4)
        tk.Button(top, text="＋ Добавить навык",
                  command=lambda: _add_skill_dialog(app, rebuild)
                  ).pack(side="left", padx=5)
        tk.Button(top, text="📚 Из каталога",
                  command=lambda: _skill_from_catalog(app, rebuild),
                  bg="#446", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="left", padx=5)
        lbl_pts = tk.Label(top, text="", bg="#f4f4f4",
                           fg="#c06000",
                           font=("Segoe UI", 10, "bold"))
        lbl_pts.pack(side="right", padx=10)
        outer, canvas, body = make_scrollable(parent)
        outer.pack(fill="both", expand=True)

        def rebuild():
            lbl_pts.config(text=f"Тренировок: "
                                f"{app.c.training['available']}")
            for w in body.winfo_children():
                w.destroy()
            if not c.skills:
                tk.Label(body, text="(навыков нет)",
                         bg="#f4f4f4", fg="#888",
                         font=("Segoe UI", 10, "italic")
                         ).pack(pady=20)
                return
            for s in c.skills:
                row = tk.Frame(body, bg="#f4f4f4")
                row.pack(fill="x", pady=2, padx=5)
                tier_ru = SKILL_TIER_NAMES.get(
                    s.get("tier", "normal"), "?")
                bonus = c.skill_bonus(s)
                txt = (f"{s['name']}, {bonus:+d}  "
                       f"({s.get('rank', 0)} рангов, {tier_ru})")
                nl = tk.Label(row, text=txt, bg="#f4f4f4",
                              font=("Segoe UI", 10, "bold"),
                              anchor="w")
                nl.pack(side="left", padx=4)
                tk.Button(row, text="✖", width=3,
                          command=lambda s=s: _skill_delete(
                              app, s["name"], rebuild)
                          ).pack(side="right", padx=2)
                tk.Button(row, text="✎", width=3,
                          command=lambda s=s: _skill_edit_dialog(
                              app, s["name"], rebuild)
                          ).pack(side="right", padx=2)

        rebuild()

    app._show_editor("Навыки", build)

def _skill_from_catalog(app, rebuild):
    """K2e: взять навык из SKILLS_CATALOG."""
    from character import SKILLS_CATALOG
    if not SKILLS_CATALOG:
        messagebox.showinfo("Каталог навыков пуст",
                             "Создай файл в catalogs/skills/ через "
                             "«📚 Каталоги» в инвентаре.",
                             parent=app.get_dialog_parent())
        return
    d = open_window(app, "Из каталога: навыки", 600, 500)
    tk.Label(d, text="Выбери навык:",
             font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=6)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=4)

    for it in SKILLS_CATALOG:
        row = tk.Frame(body, bg="#f4f4f4", relief="solid", borderwidth=1)
        row.pack(fill="x", padx=2, pady=1)
        info = tk.Frame(row, bg="#f4f4f4")
        info.pack(side="left", fill="x", expand=True, padx=4, pady=2)
        stat = (it.get("stat") or "int").upper()
        tier = it.get("tier", "normal")
        tk.Label(info, text=f"[{stat}/{tier}] {it.get('name', '?')}",
                 bg="#f4f4f4", font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(anchor="w")
        if it.get("desc"):
            tk.Label(info, text=it["desc"][:100],
                     bg="#f4f4f4", fg="#666",
                     font=("Segoe UI", 8), anchor="w").pack(anchor="w")

        def _take(it=it):
            name = it.get("name", "?")
            if P.find_skill(app.c, name):
                messagebox.showwarning("Уже есть",
                                        f"Навык '{name}' уже есть",
                                        parent=d)
                return
            app.c.skills.append({
                "name": name,
                "stat": it.get("stat", "int"),
                "tier": it.get("tier", "normal"),
                "rank": int(it.get("rank", 0) or 0),
                "source": "loot",
                "invested": 0,
                "mods": [],
            })
            app._refresh()
            rebuild()
            d.destroy()
        tk.Button(row, text="＋ Взять",
                  command=_take,
                  bg="#4a7", fg="white",
                  font=("Segoe UI", 8, "bold")
                  ).pack(side="right", padx=4)

    tk.Button(d, text="Закрыть",
              command=d.destroy).pack(pady=6)



def _add_skill_dialog(app, refresh):
    d = open_window(app, "Новый навык", 460, 380, mode="center")
    body = tk.Frame(d)
    body.pack(fill="both", expand=True)
    tk.Label(body, text="Название:").pack(anchor="w", padx=5,
                                            pady=(8, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    e_name.pack(fill="x", padx=5)
    tk.Label(body, text="Стат:").pack(anchor="w", padx=5,
                                       pady=(8, 0))
    stat_var = tk.StringVar(value="int")
    _render_stat_radios(body, stat_var)
    tk.Label(body, text="Создаётся пустым (0 рангов, обычный).",
             fg="#666", font=("Segoe UI", 9)
             ).pack(anchor="w", padx=5, pady=8)

    def save():
        name = e_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        try:
            if getattr(app, "force_free", False):
                if P.find_skill(app.c, name):
                    messagebox.showwarning("Уже есть",
                                            f"Навык '{name}' уже есть",
                                            parent=d)
                    return
                app.c.skills.append({
                    "name": name, "stat": stat_var.get(),
                    "tier": "normal", "rank": 0,
                    "source": "loot", "invested": 0, "mods": [],
                })
            else:
                P.add_skill(app.c, name, stat_var.get(), "training")
            try:
                d.grab_release()
            except Exception:
                pass
            refresh()
            d.destroy()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e), parent=d)

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Добавить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")


def _skill_edit_dialog(app, skill_name, refresh):
    skill = P.find_skill(app.c, skill_name)
    if not skill:
        return
    d = open_window(app, f"Навык: {skill['name']}", 620, 850)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True)

    tk.Label(body, text="Название:").pack(anchor="w", padx=5,
                                            pady=(8, 0))
    e_name = tk.Entry(body, font=("Segoe UI", 11))
    e_name.insert(0, skill["name"])
    e_name.pack(fill="x", padx=5)
    tk.Label(body, text="Стат:").pack(anchor="w", padx=5,
                                       pady=(6, 0))
    stat_var = tk.StringVar(value=skill.get("stat", "int"))
    _render_stat_radios(body, stat_var)

    tk.Label(body, text="Качество:",
             font=("Segoe UI", 11, "bold")
             ).pack(anchor="w", padx=5, pady=(10, 2))
    tier_var = tk.StringVar(value=skill.get("tier", "normal"))
    fr_tier = tk.Frame(body)
    fr_tier.pack(fill="x", padx=5)
    for val, label in TIERS_LIST:
        tk.Radiobutton(fr_tier, text=label, value=val,
                       variable=tier_var).pack(side="left", padx=4)

    tk.Label(body, text="Ранг:",
             font=("Segoe UI", 11, "bold")
             ).pack(anchor="w", padx=5, pady=(10, 2))
    fr_rank = tk.Frame(body)
    fr_rank.pack(fill="x", padx=5)
    tk.Label(fr_rank, text="Текущий:").pack(side="left")
    tk.Label(fr_rank, text=str(skill.get("rank", 0)),
             font=("Segoe UI", 11, "bold")
             ).pack(side="left", padx=4)
    tk.Label(fr_rank, text="→ новый:").pack(side="left",
                                              padx=(10, 2))
    rank_var = tk.IntVar(value=skill.get("rank", 0))
    tk.Spinbox(fr_rank, from_=0, to=30,
                textvariable=rank_var, width=5
                ).pack(side="left")

    # Модификаторы
    tk.Label(body, text="Модификаторы (вещи, раса, ситуация и т.п.):",
             font=("Segoe UI", 11, "bold")
             ).pack(anchor="w", padx=5, pady=(10, 2))
    mods_data = list(skill.get("mods", []))
    while len(mods_data) < 5:
        mods_data.append({"source": "", "value": 0})
    mods_frame = tk.Frame(body, bg="#f4f4f4")
    mods_frame.pack(fill="x", padx=5)

    def render_mods():
        for w in mods_frame.winfo_children():
            w.destroy()
        for i, row in enumerate(mods_data):
            fr = tk.Frame(mods_frame, bg="#f4f4f4")
            fr.pack(fill="x", pady=1)
            tk.Label(fr, text=f"  {i+1}.", width=4,
                     bg="#f4f4f4").pack(side="left")
            e_src = tk.Entry(fr)
            e_src.insert(0, row.get("source", ""))
            e_src.pack(side="left", fill="x", expand=True)

            def on_src(event=None, idx=i, entry=e_src):
                mods_data[idx]["source"] = entry.get()
            e_src.bind("<KeyRelease>", on_src)
            e_src.bind("<FocusOut>", on_src)

            tk.Label(fr, text="бонус:", bg="#f4f4f4"
                     ).pack(side="left", padx=(6, 2))
            v_val = tk.IntVar(value=row.get("value", 0))
            tk.Spinbox(fr, from_=-20, to=20,
                        textvariable=v_val, width=5
                        ).pack(side="left", padx=2)

            def on_val(idx=i, var=v_val):
                try:
                    mods_data[idx]["value"] = int(var.get())
                except (tk.TclError, ValueError):
                    mods_data[idx]["value"] = 0
            v_val.trace_add("write", lambda *a, f=on_val: f())

            def del_row(idx=i):
                mods_data.pop(idx)
                if not mods_data:
                    mods_data.append({"source": "", "value": 0})
                render_mods()
            tk.Button(fr, text="✖", width=3,
                      command=del_row).pack(side="right", padx=2)

    render_mods()

    def add_mod_row():
        mods_data.append({"source": "", "value": 0})
        render_mods()
    tk.Button(body, text="＋ Строка модификатора",
              command=add_mod_row).pack(anchor="w", padx=10,
                                         pady=4)

    info = tk.Frame(body, bg="#e8e8e8", pady=6, padx=6)
    info.pack(fill="x", padx=5, pady=8)
    lbl_tier = tk.Label(info, text="", bg="#e8e8e8",
                         font=("Segoe UI", 10), anchor="w",
                         justify="left")
    lbl_tier.pack(fill="x")
    lbl_rank = tk.Label(info, text="", bg="#e8e8e8",
                         font=("Segoe UI", 10), anchor="w",
                         justify="left")
    lbl_rank.pack(fill="x")
    lbl_total = tk.Label(info, text="", bg="#e8e8e8",
                          font=("Segoe UI", 11, "bold"),
                          fg="#c06000", anchor="w")
    lbl_total.pack(fill="x", pady=(4, 0))

    free_var = tk.BooleanVar(value=False)
    tk.Checkbutton(body,
                    text="Всё бесплатно (за класс/расу/лут/квирк)",
                    variable=free_var
                    ).pack(anchor="w", padx=5, pady=4)

    def upd(*args):
        try:
            new_tier = tier_var.get()
            new_rank = rank_var.get()
            tc, td = P.skill_tier_transition_cost(
                app.c, skill["name"], new_tier)
            rc, rd = P.skill_rank_cost_to(
                app.c, skill["name"], new_rank,
                target_tier=new_tier)
            if tc > 0:
                lbl_tier.config(
                    text=f"Качество: потратишь {tc}"
                         + (f" ({', '.join(td)})" if td else ""))
            elif tc < 0:
                lbl_tier.config(
                    text=f"Качество: вернёшь {-tc}"
                         + (f" ({', '.join(td)})" if td else ""))
            else:
                lbl_tier.config(text="Качество: без изменений")
            if rc > 0:
                lbl_rank.config(
                    text=f"Ранг: потратишь {rc}"
                         + (f" ({', '.join(rd)})" if rd else ""))
            elif rc < 0:
                lbl_rank.config(
                    text=f"Ранг: вернёшь {-rc}"
                         + (f" ({', '.join(rd)})" if rd else ""))
            else:
                lbl_rank.config(text="Ранг: без изменений")
            if free_var.get():
                lbl_total.config(text="Итого: бесплатно", fg="#339933")
            else:
                total = tc + rc
                if total > 0:
                    lbl_total.config(
                        text=f"Итого: потратишь {total}",
                        fg="#cc3333")
                elif total < 0:
                    lbl_total.config(
                        text=f"Итого: вернёшь {-total}",
                        fg="#339933")
                else:
                    lbl_total.config(text="Итого: без изменений",
                                      fg="#333")
        except Exception as e:
            lbl_total.config(text=f"Ошибка: {e}", fg="#cc3333")

    tier_var.trace_add("write", upd)
    rank_var.trace_add("write", upd)
    free_var.trace_add("write", upd)
    upd()

    def _gi_int(var, default=0):
        """Безопасно читает IntVar; пусто/мусор -> default."""
        try:
            return int(var.get())
        except (tk.TclError, ValueError):
            return default

    def save():
        new_name = e_name.get().strip()
        if not new_name:
            messagebox.showwarning("Внимание", "Введите название",
                                    parent=d)
            return
        if (new_name != skill["name"]
                and P.find_skill(app.c, new_name)):
            messagebox.showwarning(
                "Внимание", "Навык с таким именем уже есть",
                parent=d)
            return
        try:
            skill["name"] = new_name
            P.set_skill_stat(app.c, new_name, stat_var.get())
            force_free = getattr(app, "force_free", False)
            P.apply_skill_changes(
                app.c, new_name, tier_var.get(),
                _gi_int(rank_var, skill.get("rank", 0)),
                free=(free_var.get() or force_free))
            skill["mods"] = [
                {"source": m["source"].strip(),
                 "value": _gi_int_val(m)}
                for m in mods_data
                if m["source"].strip()
            ]
            try:
                d.grab_release()
            except Exception:
                pass
            refresh()
            d.destroy()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e), parent=d)

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=8, padx=5)
    tk.Button(bf, text="Применить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Удалить навык",
              command=lambda: _skill_delete(
                  app, skill["name"],
                  lambda: (refresh(), d.destroy()))
              ).pack(side="left", padx=8)
    tk.Button(bf, text="Отмена",
              command=lambda: (d.grab_release(), d.destroy())
              ).pack(side="right")


def _skill_delete(app, skill_name, refresh):
    skill = P.find_skill(app.c, skill_name)
    if not skill:
        return
    inv = skill.get("invested", 0)
    if inv > 0:
        ans = messagebox.askyesnocancel(
            "Удаление навыка",
            f"Удалить '{skill_name}'?\n\n"
            f"Вложено: {inv}\n\n"
            f"Да — вернуть {inv}\nНет — без возврата")
        if ans is None:
            return
        try:
            P.remove_skill(app.c, skill_name, return_points=ans)
            refresh()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e))
    else:
        if not messagebox.askyesno(
                "Удаление навыка",
                f"Удалить '{skill_name}'?"):
            return
        try:
            P.remove_skill(app.c, skill_name, return_points=False)
            refresh()
        except P.PurchaseError as e:
            messagebox.showerror("Ошибка", str(e))