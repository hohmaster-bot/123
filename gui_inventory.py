# gui_inventory.py — инвентарь (v1)
# 5 вкладок: Разгрузка / Кукла / Сумка / База / Даунтайм
# Единый редактор предмета, перенос, стрелки, активация

import base64
import io
import json
import zlib
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

from character import (
    CATEGORY_TO_SLOTS, EQUIP_SLOTS, SLOT_NAMES, LOCATIONS,
    LOCATION_NAMES, ITEM_CATEGORIES, VALID_SIT_TARGETS,
    _make_item,
)
from tkinter import ttk
from gui_shared import ToolTip, make_scrollable
from gui_windows import open_window
from gui_alphabet import TARGET_NAMES
import purchases as P

# T-P2: единый словарь — из gui_alphabet.
from gui_alphabet import CATEGORY_NAMES

def _clean_bonus(b):
    """Формирует чистый dict бонуса для save().
    skill_name пишем только если target=='skill'."""
    out = {"target": b.get("target", "attack"),
           "value": b.get("value", 0)}
    if out["target"] == "skill":
        out["skill_name"] = (b.get("skill_name") or "").strip()
    return out

# ============ ТОСТЫ ============

def show_toast(app, text, color="#333", duration=1500):
    """Неблокирующее всплывающее уведомление."""
    try:
        x = app.root.winfo_rootx() + app.root.winfo_width() - 350
        y = app.root.winfo_rooty() + 60
        t = tk.Toplevel(app.top)
        t.wm_overrideredirect(True)
        t.wm_geometry(f"+{x}+{y}")
        t.configure(bg=color)
        lbl = tk.Label(t, text=text, bg=color, fg="white",
                       font=("Segoe UI", 10, "bold"),
                       padx=12, pady=8, wraplength=320,
                       justify="left")
        lbl.pack()
        t.after(duration, t.destroy)
    except Exception as e:
        print(f"[toast] {e}")


# ============ ГЛАВНОЕ ОКНО ============

def open_inventory(app):
    if not app.c:
        return
    c = app.c

    def build(parent):
        # Верхняя панель
        top = tk.Frame(parent, bg="#2b2b2b", pady=6, padx=10)
        top.pack(fill="x")
        tk.Label(top, text="Инвентарь",
                 font=("Segoe UI", 12, "bold"),
                 fg="white", bg="#2b2b2b").pack(side="left")

        # Статус веса
        weight_lbl = tk.Label(top, text="", fg="#f0c040",
                                bg="#2b2b2b",
                                font=("Segoe UI", 10, "bold"))
        weight_lbl.pack(side="left", padx=20)

        def upd_weight():
            w = c.total_weight_L()
            s = c.weight_status()
            color = {"light": "#339933",
                     "loaded": "#cc8800",
                     "over": "#cc3333"}[s]
            status_txt = {"light": "легко",
                          "loaded": "нагружен",
                          "over": "ПЕРЕГРУЗ"}[s]
            weight_lbl.config(
                text=f"Вес: {c.total_weight_display()}  "
                     f"(light ≤{c.max_weight_light()}L / "
                     f"loaded ≤{c.max_weight_loaded()}L)  "
                     f"[{status_txt}]",
                fg=color)

        # Кнопки верхней панели
        # Вместо d (Toplevel) передаём parent
        tk.Button(top, text="📥 Ввести код предмета",
                  command=lambda: _import_code(app, parent, rebuild_all),
                  bg="#446", fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="right", padx=2)
        tk.Button(top, text="🎁 Поделиться",
                  command=lambda: _share_info(app),
                  bg="#446", fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="right", padx=2)

        # Notebook
        nb = tk.Frame(parent)
        nb.pack(fill="both", expand=True, padx=4, pady=4)
        tabs_frame = tk.Frame(nb, bg="#2b2b2b")
        tabs_frame.pack(fill="x")
        content_frame = tk.Frame(nb, bg="#f4f4f4")
        content_frame.pack(fill="both", expand=True)

        tab_buttons = {}
        tab_frames = {}

        def select_tab(name):
            for n, btn in tab_buttons.items():
                if n == name:
                    btn.config(bg="#f4f4f4", fg="black",
                                relief="flat")
                else:
                    btn.config(bg="#3a3a3a", fg="white",
                                relief="flat")
            for n, fr in tab_frames.items():
                if n == name:
                    fr.pack(fill="both", expand=True)
                else:
                    fr.pack_forget()

        tabs = [
            ("unload", "🛡 Разгрузка"),
            ("equipped", "👤 Кукла"),
            ("bag", "🎒 Сумка"),
            ("base", "🏠 База"),
            ("downtime", "⏳ Даунтайм"),
        ]
        for key, label in tabs:
            btn = tk.Button(tabs_frame, text=label,
                             font=("Segoe UI", 10, "bold"),
                             bg="#3a3a3a", fg="white",
                             relief="flat", padx=12, pady=6,
                             command=lambda k=key: select_tab(k))
            btn.pack(side="left", padx=1)
            tab_buttons[key] = btn
            fr = tk.Frame(content_frame, bg="#f4f4f4")
            tab_frames[key] = fr

        def rebuild_all():
            upd_weight()
            for key in ("unload", "equipped", "bag", "base"):
                for w in tab_frames[key].winfo_children():
                    w.destroy()
                _build_items_tab(app, tab_frames[key], key,
                                  parent, rebuild_all, upd_weight)
            for w in tab_frames["downtime"].winfo_children():
                w.destroy()
            _build_downtime_tab(app, tab_frames["downtime"], parent,
                                 rebuild_all)

        rebuild_all()
        select_tab("unload")

        # Кнопка закрытия (в сплите она вернёт в main, в классике закроет)
        bf = tk.Frame(parent, bg="#2b2b2b", pady=6, padx=10)
        bf.pack(fill="x")
        tk.Button(bf, text="Закрыть",
                  command=app._show_main,
                  bg="#4a7", fg="white",
                  font=("Segoe UI", 10, "bold"),
                  padx=20).pack(side="right")

    app._show_editor("Инвентарь", build)


# ============ ВКЛАДКИ ПРЕДМЕТОВ ============

def _build_items_tab(app, parent, location, dialog, rebuild,
                      upd_weight):
    c = app.c

    # Верхняя строка с действиями
    top = tk.Frame(parent, bg="#f4f4f4", pady=4, padx=6)
    top.pack(fill="x")
    tk.Button(top, text="＋ Создать предмет",
              command=lambda: _item_dialog(
                  app, None, rebuild, default_location=location),
              bg="#4a7", fg="white",
              font=("Segoe UI", 9, "bold")
              ).pack(side="left", padx=2)

    tk.Button(top, text="📚 Из каталога",
              command=lambda: _item_from_catalog(
                  app, location, rebuild, upd_weight),
              bg="#446", fg="white",
              font=("Segoe UI", 9, "bold")
              ).pack(side="left", padx=2)

    if location == "bag":
        drop_text = ("↩ Вернуть сумку"
                     if c.bag_dropped
                     else "🗑 Выбросить сумку")
        tk.Button(top, text=drop_text,
                  command=lambda: _toggle_drop_bag(
                      app, rebuild, upd_weight),
                  bg="#855", fg="white",
                  font=("Segoe UI", 9, "bold")
                  ).pack(side="left", padx=2)
        if c.bag_dropped:
            tk.Label(top, text="  [сумка выброшена — вес не учитывается]",
                     fg="#cc3333", bg="#f4f4f4",
                     font=("Segoe UI", 9, "italic")
                     ).pack(side="left", padx=4)

    if location == "base":
        used = sum((it.get("base_slots", 1) or 1)
                    for it in c.items_by_location("base"))
        max_slots = c.base.get("slots_max", 5)
        tk.Label(top,
                 text=f"  Слотов: {used}/{max_slots}",
                 fg="#333", bg="#f4f4f4",
                 font=("Segoe UI", 10, "bold")
                 ).pack(side="left", padx=10)

    if location == "unload":
        rate = (c.level + 1) * 5
        tk.Label(top,
                 text=f"  (Разгрузка: до 10L, "
                      f"редактируется в настройках)",
                 fg="#666", bg="#f4f4f4",
                 font=("Segoe UI", 9, "italic")
                 ).pack(side="left", padx=6)

    # Скроллируемый список
    outer, canvas, body = make_scrollable(parent)
    outer.pack(fill="both", expand=True, padx=4, pady=4)

    items = c.items_by_location(location)
    if not items:
        tk.Label(body, text="(пусто)",
                 bg="#f4f4f4", fg="#888",
                 font=("Segoe UI", 10, "italic")
                 ).pack(pady=20)
        return

    for i, item in enumerate(items):
        _item_row(app, body, item, i, len(items),
                   location, dialog, rebuild, upd_weight)

def _item_from_catalog(app, location, rebuild, upd_weight):
    """K2e: взять предмет из WEAPON_ITEM_CATALOG / MISC_CATALOG / CUSTOM_CATALOG."""
    from character import (WEAPON_ITEM_CATALOG,
                           CUSTOM_CATALOG, _make_item)
    all_items = (list(WEAPON_ITEM_CATALOG)
                 + list(CUSTOM_CATALOG))
    if not all_items:
        messagebox.showinfo("Каталог предметов пуст",
                             "Создай файл в catalogs/weapon_items/, "
                             "misc/ или custom/.",
                             parent=app.get_dialog_parent())
        return
    d = open_window(app, "Из каталога: предметы", 700, 600)
    tk.Label(d, text="Выбери предмет:",
             font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=6)
    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=4)

    for it in all_items:
        row = tk.Frame(body, bg="#f4f4f4", relief="solid", borderwidth=1)
        row.pack(fill="x", padx=2, pady=1)
        info = tk.Frame(row, bg="#f4f4f4")
        info.pack(side="left", fill="x", expand=True, padx=4, pady=2)
        cat = it.get("category", "misc")
        tk.Label(info, text=f"[{cat}] {it.get('name', '?')}",
                 bg="#f4f4f4", font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(anchor="w")
        if it.get("desc"):
            tk.Label(info, text=it["desc"][:100],
                     bg="#f4f4f4", fg="#666",
                     font=("Segoe UI", 8), anchor="w").pack(anchor="w")

        def _take(it=it):
            kwargs = dict(it)
            kwargs.pop("pack", None)
            kwargs["location"] = location
            item = _make_item(**{k: v for k, v in kwargs.items()
                                  if k in _make_item.__code__.co_varnames
                                  or k == "name"})
            # Проще: скопировать поля
            new_item = _make_item()
            for k, v in it.items():
                if k in new_item and k != "id":
                    new_item[k] = v
            new_item["location"] = location
            app.c.items[new_item["id"]] = new_item
            app.c._sync_item_bonuses()
            app._refresh()
            upd_weight()
            rebuild()
            d.destroy()
        tk.Button(row, text="＋ Взять",
                  command=_take,
                  bg="#4a7", fg="white",
                  font=("Segoe UI", 8, "bold")
                  ).pack(side="right", padx=4)

    tk.Button(d, text="Закрыть",
              command=d.destroy).pack(pady=6)


def _item_row(app, parent, item, idx, total, location,
                dialog, rebuild, upd_weight):
    c = app.c
    row = tk.Frame(parent, bg="#f8f8f8", relief="solid",
                    borderwidth=1)
    row.pack(fill="x", padx=2, pady=1)

    # Иконка
    icon_frame = tk.Frame(row, bg="#e8e8e8", width=40, height=40)
    icon_frame.pack(side="left", padx=2, pady=2)
    icon_frame.pack_propagate(False)
    if item.get("icon_b64"):
        try:
            from gui_shared import _load_image_from_data
            photo = _load_image_from_data(
                item["icon_b64"], 36, 36, mode="fit")
            if photo:
                lbl = tk.Label(icon_frame, image=photo,
                                bg="#e8e8e8")
                lbl.image = photo
                lbl.pack()
            else:
                tk.Label(icon_frame, text="?",
                          bg="#e8e8e8").pack(expand=True)
        except Exception:
            tk.Label(icon_frame, text="?",
                      bg="#e8e8e8").pack(expand=True)
    else:
        tk.Label(icon_frame, text="·",
                  bg="#e8e8e8", fg="#aaa",
                  font=("Segoe UI", 14)).pack(expand=True)

    # Основная информация
    info = tk.Frame(row, bg="#f8f8f8")
    info.pack(side="left", fill="both", expand=True,
               padx=4, pady=2)

    # Название (с иконкой-индикатором если активирован)
    title_text = item.get("name", "Без названия")
    if item.get("activated"):
        title_text = "✨ " + title_text
    name_lbl = tk.Label(info, text=title_text,
                         bg="#f8f8f8",
                         font=("Segoe UI", 10, "bold"),
                         anchor="w", cursor="hand2")
    name_lbl.pack(anchor="w")

    # Описание — в тултип
    # Tooltip: описание + реальные HP/прочность с бонусами владения
    desc = item.get("desc", "")
    tip_parts = []
    if desc:
        tip_parts.append(desc)

    _hp_cur = c.item_hp_actual(item)
    _hp_max = c.item_max_hp_actual(item)
    _hrd = c.item_hardness_actual(item)
    _hp_base = int(item.get("hp", 0) or 0)
    _hpmax_base = int(item.get("max_hp", 0) or 0)
    _hrd_base = int(item.get("hardness", 0) or 0)

    if _hp_max > 0 or _hpmax_base > 0:
        hp_line = f"HP: {_hp_cur}/{_hp_max}"
        if _hp_max != _hpmax_base:
            hp_line += f" (база {_hp_base}/{_hpmax_base})"
        tip_parts.append(hp_line)
    if _hrd > 0 or _hrd_base > 0:
        hrd_line = f"Прочность: {_hrd}"
        if _hrd != _hrd_base:
            hrd_line += f" (база {_hrd_base})"
        tip_parts.append(hrd_line)

    if tip_parts:
        ToolTip(name_lbl, "\n".join(tip_parts))

    # Вторая строка: категория, вес, кол-во, HP, заряды
    line2 = tk.Frame(info, bg="#f8f8f8")
    line2.pack(anchor="w")
    cat = CATEGORY_NAMES.get(item.get("category", "misc"), "?")
    parts = [cat]
    if item.get("armor_type"):
        parts.append(f"тип {item['armor_type']}")
    if item.get("ac_bonus", 0) > 0:
        from character import AC_TYPE_NAMES as _ACN
        _ac_t = item.get("ac_type", "armor")
        _ac_short = {"armor": "досп.", "shield": "щит",
                      "natural": "натур.", "deflection": "отраж.",
                      "dodge": "уклон.", "insight": "предв.",
                      "morale": "мор.", "competence": "комп.",
                      "luck": "удача", "circumstance": "обст."}
        parts.append(f"AC +{item['ac_bonus']} "
                     f"({_ac_short.get(_ac_t, _ac_t)})")
    if item.get("speed_penalty", 0) > 0:
        parts.append(f"скорость −{item['speed_penalty']}")
    qty = item.get("qty", 1)
    if qty > 1:
        parts.append(f"×{qty}")
    w = c._item_weight_L(item)
    if w > 0:
        parts.append(f"{round(w, 1)}L")
    elif item.get("weight_type") == "-":
        parts.append("—")
    _hp_cur_r = c.item_hp_actual(item)
    _hp_max_r = c.item_max_hp_actual(item)
    if _hp_max_r > 0:
        parts.append(f"HP {_hp_cur_r}/{_hp_max_r}")
    _hrd_r = c.item_hardness_actual(item)
    if _hrd_r > 0:
        parts.append(f"HRD {_hrd_r}")
    if item.get("uses") and item.get("uses_max", 0) > 0:
        parts.append(f"заряды {item.get('uses_current', 0)}/"
                     f"{item['uses_max']}")
    if location == "base" and item.get("gray"):
        parts.append("серая")
    if location == "base":
        parts.append(f"слотов: {item.get('base_slots', 1)}")

    # Проверка невладения
    if item["location"] == "equipped" and c._is_unproficient(item):
        parts.append("⚠ не владеет")

    tk.Label(line2, text=" | ".join(parts),
              bg="#f8f8f8", fg="#666",
              font=("Segoe UI", 8)).pack(anchor="w")

    # Строка атаки, если из предмета уже создана атака (from_item)
    _atk_for_item = None
    for _a in c.attacks:
        if _a.get("from_item") == item["id"]:
            _atk_for_item = _a
            break
    if _atk_for_item:
        _ab = c.attack_bonus(_atk_for_item)
        _db = c.attack_damage_bonus(_atk_for_item)
        _ct, _cm = c.attack_crit(_atk_for_item)
        _lk, _ = c.attack_lucky(_atk_for_item)
        _dice = _atk_for_item.get("damage_dice", "") or "—"
        _dmg_txt = _dice + (f"{_db:+d}" if _db else "")
        line3 = (f"⚔ {_ab:+d} / {_dmg_txt} / "
                 f"крит {_ct}+ ×{_cm} / лаки {_lk}+")
        tk.Label(info, text=line3, bg="#f8f8f8", fg="#4a7",
                 font=("Segoe UI", 8, "italic")
                 ).pack(anchor="w")

    # Кнопки справа
    btns = tk.Frame(row, bg="#f8f8f8")
    btns.pack(side="right", padx=4, pady=2)

    # Стрелки вверх/вниз
    if idx > 0:
        tk.Button(btns, text="↑", width=2,
                  command=lambda: _move_order(
                      app, item["id"], -1, rebuild)
                  ).pack(side="left", padx=1)
    if idx < total - 1:
        tk.Button(btns, text="↓", width=2,
                  command=lambda: _move_order(
                      app, item["id"], 1, rebuild)
                  ).pack(side="left", padx=1)

    # Создать атаку из надетого оружия
    if (item["location"] == "equipped"
            and item.get("category") == "weapon"):
        has_attack = any(
            a.get("from_item") == item["id"]
            for a in c.attacks)
        if not has_attack:
            tk.Button(btns, text="⚔ атака",
                      command=lambda: _create_attack_from_item(
                          app, item["id"], dialog, rebuild),
                      bg="#4a7", fg="white",
                      font=("Segoe UI", 8, "bold")
                      ).pack(side="left", padx=1)
        else:
            tk.Label(btns, text="⚔",
                      bg="#f8f8f8", fg="#4a7",
                      font=("Segoe UI", 11, "bold")
                      ).pack(side="left", padx=2)


    # Активация / Использование
    if item.get("activatable"):
        if item.get("activated"):
            tk.Button(btns, text="⏹ деакт.", width=7,
                      command=lambda: _deactivate(
                          app, item["id"], dialog, rebuild,
                          upd_weight),
                      bg="#888", fg="white",
                      font=("Segoe UI", 8)
                      ).pack(side="left", padx=1)
        else:
            cost = item.get("activation_cost_spirit", 0)
            label = "✨ акт." if cost == 0 else f"✨ −{cost} духа"
            tk.Button(btns, text=label, width=10,
                      command=lambda: _activate(
                          app, item["id"], dialog, rebuild,
                          upd_weight),
                      bg="#6a4a9a", fg="white",
                      font=("Segoe UI", 8, "bold")
                      ).pack(side="left", padx=1)

    # Перенос
    tk.Button(btns, text="↔", width=2,
              command=lambda: _move_dialog(
                  app, item["id"], dialog, rebuild, upd_weight)
              ).pack(side="left", padx=1)

    # Поделиться
    tk.Button(btns, text="📤", width=2,
              command=lambda: _share_item(app, item["id"])
              ).pack(side="left", padx=1)

    # Редактировать
    tk.Button(btns, text="✎", width=2,
              command=lambda: _item_dialog(
                  app, item["id"], rebuild)
              ).pack(side="left", padx=1)

    # Удалить
    tk.Button(btns, text="✖", width=2,
              command=lambda: _delete_item(
                  app, item["id"], rebuild, upd_weight)
              ).pack(side="left", padx=1)


def _toggle_drop_bag(app, rebuild, upd_weight):
    c = app.c
    c.bag_dropped = not c.bag_dropped
    upd_weight()
    rebuild()


def _move_order(app, item_id, delta, rebuild):
    item = app.c.get_item(item_id)
    if not item:
        return
    same_loc = app.c.items_by_location(item["location"])
    idx = next((i for i, it in enumerate(same_loc)
                if it["id"] == item_id), -1)
    if idx < 0:
        return
    new_idx = idx + delta
    if new_idx < 0 or new_idx >= len(same_loc):
        return
    # Меняем order местами
    other = same_loc[new_idx]
    item["order"], other["order"] = (
        other.get("order", 0), item.get("order", 0))
    if item["order"] == other["order"]:
        # Если одинаковые — пересчитываем всё
        for j, it in enumerate(same_loc):
            it["order"] = j
        item["order"], other["order"] = (
            other["order"], item["order"])
    rebuild()


def _move_dialog(app, item_id, dialog, rebuild, upd_weight):
    c = app.c
    item = c.get_item(item_id)
    if not item:
        return
    d = open_window(app, f"Перенести: {item.get('name', '?')}", 400, 420)

    tk.Label(d, text=f"«{item.get('name', '?')}»",
             font=("Segoe UI", 12, "bold")).pack(pady=8)
    tk.Label(d, text=f"Сейчас: {LOCATION_NAMES.get(item['location'], '?')}",
             fg="#666").pack()

    result = {"loc": None, "slot": None}

    if item["location"] == "equipped":
        tk.Button(d, text="🎒 Снять в сумку",
                  command=lambda: (
                      result.update({"loc": "bag"}),
                      d.destroy()),
                  bg="#855", fg="white", width=30, pady=4
                  ).pack(pady=4)

    # Кнопки локаций
    for loc in LOCATIONS:
        if loc == item["location"]:
            continue
        if loc == "equipped":
            continue  # обрабатываем отдельно через слоты
        tk.Button(d, text=f"→ {LOCATION_NAMES[loc]}",
                  command=lambda l=loc: (
                      result.update({"loc": l}),
                      d.destroy()),
                  bg="#4a7", fg="white", width=30, pady=4
                  ).pack(pady=2)

    # Слоты (если можно надеть)
    cat = item.get("category", "misc")
    equip_slots = CATEGORY_TO_SLOTS.get(cat, [])
    if equip_slots:
        tk.Label(d, text="Надеть в слот:",
                 font=("Segoe UI", 10, "bold")
                 ).pack(pady=(10, 2))
        for slot in equip_slots:
            occupied = c.equipped_in_slot(slot)
            occ_text = ""
            if occupied and occupied["id"] != item_id:
                occ_text = f" (заменит: {occupied.get('name','?')[:15]})"
            tk.Button(d,
                      text=f"👤 {SLOT_NAMES.get(slot, slot)}{occ_text}",
                      command=lambda s=slot: (
                          result.update({"loc": "equipped",
                                          "slot": s}),
                          d.destroy()),
                      bg="#446", fg="white", width=30, pady=3
                      ).pack(pady=1)

    tk.Button(d, text="Отмена",
              command=d.destroy).pack(pady=10)

    d.wait_window()

    if not result["loc"]:
        return

    # Проверка веса при добавлении в разгрузку/сумку/куклу
    if result["loc"] != "base":
        old_loc = item["location"]
        old_slot = item.get("slot")
        # Временно перемещаем для проверки
        try:
            c.move_item(item_id, result["loc"], result["slot"])
            if c.weight_status() == "over":
                show_toast(app,
                            "⚠ ПЕРЕГРУЗ — вы не сможете уйти, "
                            "пока не выбросите что-то",
                            color="#aa3333", duration=2500)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e),
                                  parent=app.get_dialog_parent())
    else:
        try:
            c.move_item(item_id, result["loc"], result["slot"])
        except Exception as e:
            messagebox.showerror("Ошибка", str(e),
                                  parent=app.get_dialog_parent())

    upd_weight()
    rebuild()
    app._refresh()


def _activate(app, item_id, dialog, rebuild, upd_weight):
    c = app.c
    item = c.get_item(item_id)
    if not item:
        return
    try:
        cost = c.activate_item(item_id)
        if cost > 0:
            show_toast(app,
                        f"✨ −{cost} духа",
                        color="#6a4a9a", duration=1500)
        else:
            show_toast(app,
                        f"✨ {item.get('name','?')} активирован",
                        color="#4a7", duration=1500)
        app._refresh()
        rebuild()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e),
                              parent=app.get_dialog_parent())


def _deactivate(app, item_id, dialog, rebuild, upd_weight):
    c = app.c
    c.deactivate_item(item_id)
    app._refresh()
    rebuild()


def _create_attack_from_item(app, item_id, dialog, rebuild):
    c = app.c
    item = c.get_item(item_id)
    if not item:
        return
    d = open_window(app, f"Создать атаку: {item.get('name', '?')}", 520, 480)

    tk.Label(d,
             text=f"⚔ Создать атаку из «{item.get('name', '?')}»",
             font=("Segoe UI", 11, "bold")
             ).pack(pady=10)

    fr_name = tk.Frame(d)
    fr_name.pack(fill="x", padx=10, pady=4)
    tk.Label(fr_name, text="Название:",
             width=14, anchor="w").pack(side="left")
    name_var = tk.StringVar(value=item.get("name", "Оружие"))
    tk.Entry(fr_name, textvariable=name_var,
             font=("Segoe UI", 10)).pack(side="left",
                                          fill="x", expand=True)

    fr_stat = tk.Frame(d)
    fr_stat.pack(fill="x", padx=10, pady=4)
    tk.Label(fr_stat, text="Стат:",
             width=14, anchor="w").pack(side="left")
    stat_var = tk.StringVar(value="str")
    for ab in ("str", "dex", "con", "int", "wis", "cha"):
        tk.Radiobutton(fr_stat, text=ab.upper(), value=ab,
                        variable=stat_var).pack(side="left",
                                                 padx=2)

    use_bab_var = tk.BooleanVar(value=True)
    tk.Checkbutton(d,
                    text="Считать бонус автоматически (ББА + стат)",
                    variable=use_bab_var
                    ).pack(anchor="w", padx=10, pady=4)

    info = tk.Frame(d, bg="#e8e8e8", pady=6, padx=8)
    info.pack(fill="x", padx=10, pady=6)
    info_text = (
        f"Урон: {item.get('damage', '—')}\n"
        f"Крит: {item.get('crit_threshold', 20)}+ "
        f"x{item.get('crit_mult', 2)}\n"
        f"Бонус атаки: {item.get('attack_bonus', 0):+d}\n"
        f"Бонус урона: {item.get('damage_bonus', 0):+d}\n"
        f"Зачарований: {len(item.get('enchants', []))}"
    )
    tk.Label(info, text=info_text, bg="#e8e8e8",
             justify="left",
             font=("Segoe UI", 9)).pack(anchor="w")

    def do_create():
        try:
            c.attack_from_item(
                item_id,
                name=name_var.get().strip(),
                stat=stat_var.get(),
                use_bab=use_bab_var.get())
            show_toast(app, "✓ Атака создана",
                        color="#4a7")
            app._refresh()
            rebuild()
            try:
                d.grab_release()
            except Exception:
                pass
            d.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=d)

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=8, padx=10)
    tk.Button(bf, text="Создать атаку", command=do_create,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=d.destroy).pack(side="right")


def _delete_item(app, item_id, rebuild, upd_weight):
    item = app.c.get_item(item_id)
    if not item:
        return
    if not messagebox.askyesno(
            "Удалить",
            f"Удалить «{item.get('name', '?')}»?",
            parent=app.get_dialog_parent()):
        return
    app.c.remove_item(item_id)
    upd_weight()
    rebuild()
    app._refresh()


# ============ РЕДАКТОР ПРЕДМЕТА ============

def edit_item(app, item, mode="inventory", on_save=None,
               on_cancel=None):
    """Единый редактор предмета."""
    c = app.c
    is_new = not item.get("name")
    title = ("Новый предмет" if mode == "inventory"
             else "Новый предмет каталога") if is_new else \
            f"Редактор: {item.get('name', '?')}"

    d = open_window(app, title, 680, 820)

    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True)

    # ===== Цена (только shop) =====
    price_var = tk.StringVar(value=str(item.get("price", 0)))
    if mode == "shop":
        _section(body, "Цена")
        fr_price = tk.Frame(body, bg="#f4f4f4")
        fr_price.pack(fill="x", padx=5, pady=2)
        tk.Label(fr_price, text="Цена (золото):",
                 bg="#f4f4f4", width=18, anchor="w"
                 ).pack(side="left")
        tk.Entry(fr_price, textvariable=price_var,
                 width=10).pack(side="left")

    # ===== Основное =====
    _section(body, "Основное")
    e_name = _row_entry(body, "Название:",
                        item.get("name", ""))
    cat_var = tk.StringVar(value=item.get("category", "misc"))
    _row_option(body, "Категория:", cat_var,
                 ITEM_CATEGORIES, CATEGORY_NAMES)
    e_desc = _row_text(body, "Описание:",
                        item.get("desc", ""), height=3)

    # ===== Вес и количество =====
    _section(body, "Вес и количество")
    fr_w = tk.Frame(body, bg="#f4f4f4")
    fr_w.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_w, text="Вес:",
             bg="#f4f4f4", width=14, anchor="w").pack(side="left")
    w_var = tk.StringVar(value=str(item.get("weight", 0)))
    tk.Entry(fr_w, textvariable=w_var, width=8).pack(side="left")
    wt_var = tk.StringVar(value=item.get("weight_type", "mass"))
    tk.OptionMenu(fr_w, wt_var, "mass", "L", "-",
                   ).pack(side="left", padx=4)
    from gui_shared import hint as _hint
    if not c.settings.get("hide_hints", False):
        tk.Label(fr_w, text="(масса ×10L / L / — без веса)",
                 bg="#f4f4f4", fg="#666",
                 font=("Segoe UI", 8)).pack(side="left")

    fr_q = tk.Frame(body, bg="#f4f4f4")
    fr_q.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_q, text="Количество:",
             bg="#f4f4f4", width=14, anchor="w").pack(side="left")
    qty_var = tk.IntVar(value=item.get("qty", 1))
    tk.Spinbox(fr_q, from_=1, to=999,
                textvariable=qty_var, width=6).pack(side="left")

    # ===== HP =====
    _section(body, "HP и прочность (0 = не учитывать)")
    fr_hp = tk.Frame(body, bg="#f4f4f4")
    fr_hp.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_hp, text="HP:",
             bg="#f4f4f4", width=14, anchor="w").pack(side="left")
    hp_var = tk.IntVar(value=item.get("hp", 0))
    tk.Spinbox(fr_hp, from_=0, to=9999,
                textvariable=hp_var, width=6).pack(side="left")
    tk.Label(fr_hp, text="/ Макс:",
             bg="#f4f4f4", padx=6).pack(side="left")
    max_hp_var = tk.IntVar(value=item.get("max_hp", 0))
    tk.Spinbox(fr_hp, from_=0, to=9999,
                textvariable=max_hp_var, width=6).pack(side="left")
    tk.Label(fr_hp, text="Hardness:",
             bg="#f4f4f4", padx=6).pack(side="left")
    hardness_var = tk.IntVar(value=item.get("hardness", 0))
    tk.Spinbox(fr_hp, from_=0, to=9999,
                textvariable=hardness_var, width=6).pack(side="left")

    # Подпись: реальные значения с бонусами владения (только справка)
    lbl_real = tk.Label(body, text="", bg="#f4f4f4",
                         fg="#0066cc",
                         font=("Segoe UI", 9, "italic"),
                         anchor="w", justify="left",
                         wraplength=620)
    lbl_real.pack(fill="x", padx=5, pady=(0, 4))

    def _upd_real_hint(*args):
        """Пересчитывает реальные HP/прочность с бонусами владения.
        Показывает подпись только если бонусы есть."""
        try:
            # Ищем владение по weapon_group или name (как в character.py)
            w_name = ((item.get("weapon_group") or "").strip()
                      or item.get("name", ""))
            w = c.weapon_by_name(w_name) if w_name else None
            if not w:
                lbl_real.config(text="")
                return

            # Берём ТЕКУЩИЕ значения из Spinbox (что ввёл игрок),
            # а не item["hp"] (там может быть старое).
            base_hp = max(0, hp_var.get())
            base_max = max(0, max_hp_var.get())
            base_hrd = max(0, hardness_var.get())

            hp_bonus = c.weapon_hp_bonus(w)
            real_hp = base_hp + hp_bonus if base_hp > 0 else 0
            real_max = base_max + hp_bonus if base_max > 0 else 0

            mult = c.weapon_hardness_multiplier(w)
            real_hrd = int(base_hrd * mult) if base_hrd > 0 else 0

            parts = []
            if hp_bonus and (base_hp > 0 or base_max > 0):
                parts.append(f"HP {real_hp}/{real_max} "
                             f"(+{hp_bonus} от владения)")
            if (mult != 1.0) and base_hrd > 0:
                parts.append(f"прочность {real_hrd} "
                             f"(×{mult:.2f} от владения)")

            if parts:
                lbl_real.config(
                    text="С бонусами владения: " + "; ".join(parts))
            else:
                lbl_real.config(text="")
        except Exception:
            lbl_real.config(text="")

    def _gi_int(var, default=0):
        try:
            return int(var.get())
        except (tk.TclError, ValueError):
            return default

    hp_var.trace_add("write", _upd_real_hint)
    max_hp_var.trace_add("write", _upd_real_hint)
    hardness_var.trace_add("write", _upd_real_hint)
    _upd_real_hint()

    # ===== Заряды =====
    _section(body, "Заряды")
    uses_var = tk.BooleanVar(value=item.get("uses", False))
    fr_u = tk.Frame(body, bg="#f4f4f4")
    fr_u.pack(fill="x", padx=5, pady=2)
    tk.Checkbutton(fr_u, text="Есть заряды",
                    variable=uses_var, bg="#f4f4f4",
                    font=("Segoe UI", 10)).pack(side="left")
    tk.Label(fr_u, text="Макс:",
             bg="#f4f4f4", padx=6).pack(side="left")
    umax_var = tk.IntVar(value=item.get("uses_max", 0))
    tk.Spinbox(fr_u, from_=0, to=999,
                textvariable=umax_var, width=5).pack(side="left")
    tk.Label(fr_u, text="Текущее:",
             bg="#f4f4f4", padx=6).pack(side="left")
    ucur_var = tk.IntVar(value=item.get("uses_current", 0))
    tk.Spinbox(fr_u, from_=0, to=999,
                textvariable=ucur_var, width=5).pack(side="left")
    panel_var = tk.BooleanVar(
        value=item.get("show_on_panel", False))
    tk.Checkbutton(body, text="Показывать заряды на панели",
                    variable=panel_var, bg="#f4f4f4"
                    ).pack(anchor="w", padx=5, pady=2)

    # ===== Броня / Щит =====
    _section(body, "Броня / Щит / AC")
    at_var = tk.StringVar(value=item.get("armor_type") or "None")
    at_fr = tk.Frame(body, bg="#f4f4f4")
    at_fr.pack(fill="x", padx=5, pady=2)
    tk.Label(at_fr, text="Тип брони:",
             bg="#f4f4f4", width=18, anchor="w"
             ).pack(side="left")
    at_om = tk.OptionMenu(at_fr, at_var, "None")
    at_om.config(width=15)
    at_om.pack(side="left")

    AT_NAMES = {"None": "—", "Light": "Лёгкая",
                "Medium": "Средняя", "Heavy": "Тяжёлая",
                "Tower": "Ростовая"}

    def _upd_at_options(*args):
        cat = cat_var.get()
        if cat == "shield":
            options = ["None", "Light", "Heavy", "Tower"]
        elif cat == "armor":
            options = ["None", "Light", "Medium", "Heavy"]
        else:
            options = ["None", "Light", "Medium", "Heavy",
                       "Tower"]
        menu = at_om["menu"]
        menu.delete(0, "end")
        for o in options:
            menu.add_command(
                label=AT_NAMES.get(o, o),
                command=lambda v=o: at_var.set(v))
        if at_var.get() not in options:
            at_var.set("None")

    cat_var.trace_add("write", _upd_at_options)
    _upd_at_options()

    fr_ac = tk.Frame(body, bg="#f4f4f4")
    fr_ac.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_ac, text="AC бонус:",
             bg="#f4f4f4", width=14, anchor="w").pack(side="left")
    acb_var = tk.IntVar(value=item.get("ac_bonus", 0))
    tk.Spinbox(fr_ac, from_=0, to=30,
                textvariable=acb_var, width=5).pack(side="left")
    tk.Label(fr_ac, text="  Макс DEX (пусто=нет):",
             bg="#f4f4f4").pack(side="left")

    tk.Label(body, text="Тип AC-бонуса:",
             bg="#f4f4f4",
             font=("Segoe UI", 9, "bold")
             ).pack(anchor="w", padx=5, pady=(4, 0))
    ac_type_var = tk.StringVar(value=item.get("ac_type", "armor"))
    from character import AC_TYPE_NAMES as _ACN
    fr_actype1 = tk.Frame(body, bg="#f4f4f4")
    fr_actype1.pack(fill="x", padx=5, pady=1)
    for _val in ("armor", "shield", "natural", "deflection",
                  "dodge"):
        tk.Radiobutton(fr_actype1, text=_ACN.get(_val, _val),
                        value=_val, variable=ac_type_var,
                        font=("Segoe UI", 9)
                        ).pack(side="left", padx=2)
    fr_actype2 = tk.Frame(body, bg="#f4f4f4")
    fr_actype2.pack(fill="x", padx=5, pady=1)
    for _val in ("insight", "morale", "competence", "luck",
                  "circumstance"):
        tk.Radiobutton(fr_actype2, text=_ACN.get(_val, _val),
                        value=_val, variable=ac_type_var,
                        font=("Segoe UI", 9)
                        ).pack(side="left", padx=2)

    maxdex_var = tk.StringVar(
        value="" if item.get("ac_max_dex") is None
        else str(item.get("ac_max_dex")))
    tk.Entry(fr_ac, textvariable=maxdex_var,
              width=5).pack(side="left", padx=4)

    fr_pen = tk.Frame(body, bg="#f4f4f4")
    fr_pen.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_pen, text="Штраф к навыкам (СИЛ/ЛОВ):",
             bg="#f4f4f4").pack(side="left")
    sk_pen_var = tk.IntVar(
        value=abs(item.get("skill_penalty", 0) or 0))
    tk.Spinbox(fr_pen, from_=0, to=20,
                textvariable=sk_pen_var, width=4).pack(side="left",
                                                       padx=4)
    if not c.settings.get("hide_hints", False):
        tk.Label(fr_pen,
                 text="(введи 4 — применится как −4; знак не важен)",
                 bg="#f4f4f4", fg="#666",
                 font=("Segoe UI", 8)).pack(side="left", padx=4)

    tk.Label(fr_pen, text="Скорость −:",
             bg="#f4f4f4").pack(side="left")
    spd_var = tk.IntVar(value=item.get("speed_penalty", 0))
    tk.Spinbox(fr_pen, from_=0, to=30,
                textvariable=spd_var, width=4).pack(side="left",
                                                      padx=4)

    # ===== Разгрузка =====
    _section(body, "Разгрузка (если категория = Разгрузка)")
    fr_ub = tk.Frame(body, bg="#f4f4f4")
    fr_ub.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_ub, text="+L к лимиту разгрузки:",
             bg="#f4f4f4", width=24, anchor="w"
             ).pack(side="left")
    ub_var = tk.IntVar(value=item.get("unload_bonus", 0))
    tk.Spinbox(fr_ub, from_=0, to=200,
                textvariable=ub_var, width=5).pack(side="left")

    # ===== Оружие =====
    _section(body, "Оружие")
    e_dmg = _row_entry(body, "Урон (1d8):",
                        item.get("damage", ""))

    fr_ft = tk.Frame(body, bg="#f4f4f4")
    fr_ft.pack(fill="x", padx=5, pady=2)
    finesse_var = tk.BooleanVar(value=item.get("finesse", False))
    tk.Checkbutton(fr_ft,
                   text="Фехтовальное (попадание от ЛОВ, "
                        "урон от СИЛ)",
                   variable=finesse_var, bg="#f4f4f4",
                   font=("Segoe UI", 9)
                   ).pack(side="left", padx=2)
    twohand_var = tk.BooleanVar(value=item.get("two_handed", False))
    tk.Checkbutton(fr_ft,
                   text="Двуручное (×1.5 СИЛ к урону)",
                   variable=twohand_var, bg="#f4f4f4",
                   font=("Segoe UI", 9)
                   ).pack(side="left", padx=10)

    fr_c = tk.Frame(body, bg="#f4f4f4")
    fr_c.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_c, text="Крит порог:",
             bg="#f4f4f4").pack(side="left")
    ct_var = tk.IntVar(value=item.get("crit_threshold", 20))
    tk.Spinbox(fr_c, from_=2, to=20,
                textvariable=ct_var, width=4).pack(side="left",
                                                    padx=4)
    tk.Label(fr_c, text="Множитель:",
             bg="#f4f4f4").pack(side="left")
    cm_var = tk.IntVar(value=item.get("crit_mult", 2))
    tk.Spinbox(fr_c, from_=2, to=10,
                textvariable=cm_var, width=3).pack(side="left")

    # Группа оружия — Combobox с существующими владениями
    fr_wg = tk.Frame(body, bg="#f4f4f4")
    fr_wg.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_wg, text="Группа оружия:",
             bg="#f4f4f4", width=18, anchor="w"
             ).pack(side="left")
    _prof_names = [w["name"] for w in
                   c.proficiencies.get("weapons", [])]
    _cur_wg = item.get("weapon_group", "") or ""
    wgroup_var = tk.StringVar(value=_cur_wg)
    wgroup_combo = ttk.Combobox(
        fr_wg, values=_prof_names, textvariable=wgroup_var,
        width=28, font=("Segoe UI", 10))
    wgroup_combo.pack(side="left", fill="x", expand=True,
                       padx=4)
    from gui_shared import hint as _hint
    _hint(body,
          "Выбери из списка групп владения "
          "или впиши вручную (например, для оружия, "
          "которым ещё не владеешь).",
          character=c,
          fg="#666", font=("Segoe UI", 8, "italic"),
          wraplength=620, justify="left")
    e_wgroup = wgroup_var
    # ===== Дальнее / Метательное =====
    _section(body, "Дальнее / Метательное оружие")
    fr_ranged = tk.Frame(body, bg="#f4f4f4")
    fr_ranged.pack(fill="x", padx=5, pady=2)
    
    ranged_var = tk.BooleanVar(value=item.get("ranged", False))
    tk.Checkbutton(fr_ranged, text="Стрелковое (лук, арбалет)",
                   variable=ranged_var, bg="#f4f4f4",
                   font=("Segoe UI", 9)).pack(side="left", padx=2)
    
    thrown_var = tk.BooleanVar(value=item.get("thrown", False))
    tk.Checkbutton(fr_ranged, text="Метательное (дротик, топор)",
                   variable=thrown_var, bg="#f4f4f4",
                   font=("Segoe UI", 9)).pack(side="left", padx=10)
    
    fr_rng2 = tk.Frame(body, bg="#f4f4f4")
    fr_rng2.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_rng2, text="Диапазон (фт):",
             bg="#f4f4f4", width=18, anchor="w").pack(side="left")
    range_ft_var = tk.IntVar(value=item.get("range_ft", 0))
    tk.Spinbox(fr_rng2, from_=0, to=1000,
                textvariable=range_ft_var, width=6).pack(side="left")
    
    tk.Label(fr_rng2, text="Требуемый уровень владения:",
             bg="#f4f4f4", padx=10).pack(side="left")
    req_lvl_var = tk.IntVar(value=item.get("required_level", 0))
    tk.Spinbox(fr_rng2, from_=0, to=10,
                textvariable=req_lvl_var, width=4).pack(side="left")
    # ===== База (только inventory) =====
    gray_var = tk.BooleanVar(value=item.get("gray", False))
    bs_var = tk.IntVar(value=item.get("base_slots", 1))
    if mode == "inventory":
        _section(body, "База")
        fr_b = tk.Frame(body, bg="#f4f4f4")
        fr_b.pack(fill="x", padx=5, pady=2)
        tk.Label(fr_b, text="Занимает слотов:",
                 bg="#f4f4f4", width=20, anchor="w"
                 ).pack(side="left")
        tk.Spinbox(fr_b, from_=1, to=20,
                    textvariable=bs_var, width=4
                    ).pack(side="left")
        tk.Checkbutton(body, text="Серая (в базе)",
                        variable=gray_var, bg="#f4f4f4"
                        ).pack(anchor="w", padx=5)

    # ===== Пассивные бонусы =====
    _section(body, "Пассивные бонусы (работают пока надет)")
    passive_data = list(item.get("passive_bonuses", []))
    passive_frame = tk.Frame(body, bg="#f4f4f4")
    passive_frame.pack(fill="x", padx=5)
    _render_bonuses(passive_frame, passive_data, c)

    def add_passive():
        passive_data.append({"target": "ac", "value": 0})
        _render_bonuses(passive_frame, passive_data, c)
    tk.Button(body, text="＋ Пассивный бонус",
              command=add_passive
              ).pack(anchor="w", padx=10, pady=2)

    # ===== Активация =====
    _section(body, "Активация")
    act_var = tk.BooleanVar(value=item.get("activatable", False))
    tk.Checkbutton(body, text="Активируется",
                    variable=act_var, bg="#f4f4f4",
                    font=("Segoe UI", 10)
                    ).pack(anchor="w", padx=5, pady=2)
    fr_ac2 = tk.Frame(body, bg="#f4f4f4")
    fr_ac2.pack(fill="x", padx=5, pady=2)
    tk.Label(fr_ac2, text="Цена в духе:",
             bg="#f4f4f4").pack(side="left")
    acost_var = tk.IntVar(
        value=item.get("activation_cost_spirit", 0))
    tk.Spinbox(fr_ac2, from_=0, to=99,
                textvariable=acost_var, width=4
                ).pack(side="left", padx=4)
    tk.Label(fr_ac2, text="Длит. (раундов, 0=до отдыха):",
             bg="#f4f4f4").pack(side="left")
    adur_var = tk.IntVar(
        value=item.get("activation_duration", 0))
    tk.Spinbox(fr_ac2, from_=0, to=99,
                textvariable=adur_var, width=4
                ).pack(side="left", padx=4)

    tk.Label(body, text="Эффекты активации:",
             bg="#f4f4f4", font=("Segoe UI", 9, "bold")
             ).pack(anchor="w", padx=5, pady=(4, 2))
    act_data = list(item.get("activation_effects", []))
    act_frame = tk.Frame(body, bg="#f4f4f4")
    act_frame.pack(fill="x", padx=5)
    _render_bonuses(act_frame, act_data, c)

    def add_act():
        act_data.append({"target": "ac", "value": 0})
        _render_bonuses(act_frame, act_data, c)
    tk.Button(body, text="＋ Эффект активации",
              command=add_act
              ).pack(anchor="w", padx=10, pady=2)

    # ===== Иконка =====
    _section(body, "Иконка (32×32)")
    fr_icon = tk.Frame(body, bg="#f4f4f4")
    fr_icon.pack(fill="x", padx=5, pady=2)
    icon_status = tk.Label(
        fr_icon,
        text=("загружена" if item.get("icon_b64")
              else "не задана"),
        bg="#f4f4f4", fg="#666",
        font=("Segoe UI", 9, "italic"))
    icon_status.pack(side="left", padx=4)
    icon_data = {"b64": item.get("icon_b64", "")}

    def load_icon():
        path = filedialog.askopenfilename(
            parent=d,
            filetypes=[("Картинки",
                        "*.png *.jpg *.jpeg *.gif *.bmp"),
                        ("Все", "*.*")])
        if not path:
            return
        try:
            from PIL import Image
            img = Image.open(path)
            img.thumbnail((32, 32), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            icon_data["b64"] = base64.b64encode(
                buf.getvalue()).decode("ascii")
            icon_status.config(text="загружена")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=d)

    def clear_icon():
        icon_data["b64"] = ""
        icon_status.config(text="не задана")

    tk.Button(fr_icon, text="📷 Загрузить",
              command=load_icon).pack(side="left", padx=2)
    tk.Button(fr_icon, text="✖ Убрать",
              command=clear_icon).pack(side="left", padx=2)

    # ===== Сохранить =====
    def save():
        def _safe(val, default=0):
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return default

        def _gi(var, default=0):
            """Безопасно читает IntVar; пусто/мусор -> default."""
            try:
                return int(var.get())
            except (tk.TclError, ValueError):
                return default

        try:
            if mode == "shop":
                try:
                    item["price"] = float(
                        price_var.get() or 0)
                except Exception:
                    item["price"] = 0
            item["name"] = (e_name.get().strip()
                             or "Без названия")
            item["category"] = cat_var.get()
            item["desc"] = (e_desc.get("1.0", "end").strip())
            item["weight"] = _safe(w_var.get(), 0)
            item["weight_type"] = wt_var.get()
            item["qty"] = max(1, _gi(qty_var, 1))
            item["hp"] = max(0, _gi(hp_var, 0))
            item["max_hp"] = max(0, _gi(max_hp_var, 0))
            item["hardness"] = max(0, _gi(hardness_var, 0))
            item["uses"] = uses_var.get()
            if item["uses"]:
                _umax = max(0, _gi(umax_var, 0))
                _ucur = max(0, min(_gi(ucur_var, 0), _umax))
                item["uses_max"] = _umax
                item["uses_current"] = _ucur
            else:
                item["uses_max"] = 0
                item["uses_current"] = 0
            item["show_on_panel"] = panel_var.get()
            at = at_var.get()
            item["armor_type"] = at if at != "None" else None
            item["ac_bonus"] = max(0, _gi(acb_var, 0))
            item["ac_type"] = ac_type_var.get()
            md = maxdex_var.get().strip()
            item["ac_max_dex"] = (int(md) if md.isdigit() else None)
            item["skill_penalty"] = abs(_gi(sk_pen_var, 0))
            item["speed_penalty"] = max(0, _gi(spd_var, 0))
            item["unload_bonus"] = max(0, _gi(ub_var, 0))
            item["damage"] = e_dmg.get().strip()
            item["crit_threshold"] = max(2, min(20, _gi(ct_var, 20)))
            item["crit_mult"] = max(2, _gi(cm_var, 2))
            item["weapon_group"] = wgroup_var.get().strip()
            item["finesse"] = finesse_var.get()
            item["two_handed"] = twohand_var.get()
            item["ranged"] = ranged_var.get()
            item["thrown"] = thrown_var.get()
            item["range_ft"] = max(0, _gi(range_ft_var, 0))
            item["required_level"] = max(0, _gi(req_lvl_var, 0))
            item["base_slots"] = max(1, _gi(bs_var, 1))
            item["gray"] = gray_var.get()
            item["passive_bonuses"] = [
                _clean_bonus(b)
                for b in passive_data if b.get("value", 0) != 0
            ]
            item["activatable"] = act_var.get()
            item["activation_cost_spirit"] = max(0, _gi(acost_var, 0))
            item["activation_duration"] = max(0, _gi(adur_var, 0))
            item["activation_effects"] = [
                _clean_bonus(b)
                for b in act_data if b.get("value", 0) != 0
            ]
            item["icon_b64"] = icon_data["b64"]

            if mode == "inventory":
                c._sync_item_bonuses()
                app._refresh()
            if on_save:
                on_save()
            try:
                d.grab_release()
            except Exception:
                pass
            d.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка формата", 
                                 f"Введено некорректное число. "
                                 f"Проверьте поля (вес, HP, крит и т.д.).\n"
                                 f"Детали: {e}", parent=d)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=d)

    def cancel():
        try:
            d.grab_release()
        except Exception:
            pass
        if on_cancel:
            try:
                on_cancel()
            except Exception as e:
                print(f"[on_cancel] {e}")
        d.destroy()

    bf = tk.Frame(body)
    bf.pack(fill="x", pady=10, padx=5)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Отмена", command=cancel
              ).pack(side="right")
def _item_dialog(app, item_id, rebuild, default_location=None):
    """Обёртка: открыть редактор для предмета из инвентаря."""
    c = app.c
    is_new = item_id is None
    if is_new:
        item = _make_item(location=default_location or "bag")
        # Автослот при создании на кукле
        if item["location"] == "equipped":
            try:
                slot = c._default_slot(item)
                if slot:
                    item["slot"] = slot
            except Exception:
                pass
        c.items[item["id"]] = item
        need_cleanup = True
    else:
        item = c.get_item(item_id)
        if not item:
            return
        need_cleanup = False

    def on_save():
        rebuild()

    def on_cancel():
        if need_cleanup:
            c.items.pop(item["id"], None)

    edit_item(app, item, mode="inventory",
                on_save=on_save, on_cancel=on_cancel)




# ============ ВСПОМОГАТЕЛЬНЫЕ ДЛЯ РЕДАКТОРА ============

def _section(parent, title):
    f = tk.Frame(parent, bg="#c8c8c8")
    f.pack(fill="x", pady=(10, 2))
    tk.Label(f, text=title, font=("Segoe UI", 10, "bold"),
             bg="#c8c8c8", anchor="w", padx=8).pack(fill="x")


def _row_entry(parent, label, value):
    fr = tk.Frame(parent, bg="#f4f4f4")
    fr.pack(fill="x", padx=5, pady=2)
    tk.Label(fr, text=label, bg="#f4f4f4",
             width=18, anchor="w").pack(side="left")
    e = tk.Entry(fr, font=("Segoe UI", 10))
    e.insert(0, value or "")
    e.pack(side="left", fill="x", expand=True)
    return e


def _row_text(parent, label, value, height=4):
    tk.Label(parent, text=label, bg="#f4f4f4",
             anchor="w").pack(anchor="w", padx=5, pady=(4, 0))
    t = tk.Text(parent, font=("Segoe UI", 10), height=height,
                 wrap="word")
    t.pack(fill="x", padx=5, pady=(0, 2))
    t.insert("1.0", value or "")
    return t


def _row_option(parent, label, var, options, names):
    fr = tk.Frame(parent, bg="#f4f4f4")
    fr.pack(fill="x", padx=5, pady=2)
    tk.Label(fr, text=label, bg="#f4f4f4",
             width=18, anchor="w").pack(side="left")
    om = tk.OptionMenu(fr, var, *options)
    om.config(width=20)
    om.pack(side="left")

    def _upd(*args):
        try:
            text = names.get(var.get(), var.get())
            om.config(text=text)
        except Exception:
            pass
    var.trace_add("write", _upd)
    _upd()
    return om


def _render_bonuses(frame, data, character=None):
    for w in frame.winfo_children():
        w.destroy()
    for i, bon in enumerate(data):
        fr = tk.Frame(frame, bg="#f4f4f4")
        fr.pack(fill="x", pady=1)
        tk.Label(fr, text=f"  {i+1}.", width=4,
                 bg="#f4f4f4").pack(side="left")

        tgt_var = tk.StringVar(value=bon.get("target", "attack"))
        options = list(TARGET_NAMES.keys())

        def _on_target(v, idx=i):
            data[idx]["target"] = v
            # Перерисовать, чтобы показать/скрыть выбор навыка
            _render_bonuses(frame, data, character)

        om = tk.OptionMenu(fr, tgt_var, *options, command=_on_target)
        om.config(width=22)
        om.pack(side="left", padx=2)

        # Дополнительный выбор навыка, если target == "skill"
        if tgt_var.get() == "skill":
            skill_names = []
            if character is not None:
                skill_names = [s.get("name", "")
                               for s in getattr(character, "skills", [])
                               if s.get("name")]
            cur_skill = bon.get("skill_name", "")
            sk_var = tk.StringVar(value=cur_skill)
            if skill_names:
                sk_om = tk.OptionMenu(
                    fr, sk_var, *skill_names,
                    command=lambda v, idx=i:
                        data[idx].__setitem__("skill_name", v))
                sk_om.config(width=18)
                sk_om.pack(side="left", padx=2)
                tk.Label(fr, text="к",
                         bg="#f4f4f4").pack(side="left")
            else:
                tk.Label(fr, text="(нет навыков — добавь в Навыки)",
                         bg="#f4f4f4", fg="#cc3333",
                         font=("Segoe UI", 8)
                         ).pack(side="left", padx=2)

        tk.Label(fr, text=":", bg="#f4f4f4").pack(side="left")
        v_var = tk.IntVar(value=bon.get("value", 0))
        tk.Spinbox(fr, from_=-50, to=50,
                    textvariable=v_var, width=5
                    ).pack(side="left", padx=2)

        def on_val(idx=i, var=v_var):
            try:
                data[idx]["value"] = int(var.get())
            except (tk.TclError, ValueError):
                data[idx]["value"] = 0
        v_var.trace_add("write", lambda *a, f=on_val: f())

        def del_b(idx=i):
            data.pop(idx)
            _render_bonuses(frame, data, character)
        tk.Button(fr, text="✖", width=2,
                  command=del_b).pack(side="right", padx=2)


# ============ SHARE / IMPORT ============

def _share_info(app):
    messagebox.showinfo(
        "Поделиться",
        "Кнопка 📤 на каждом предмете — копирует код "
        "в буфер обмена.\n"
        "Друг вставляет этот код в «📥 Ввести код "
        "предмета».\n\n"
        "Размер ~200-800 символов, влезает в Discord/"
        "Telegram.",
        parent=app.get_dialog_parent())


def _share_item(app, item_id):
    c = app.c
    item = c.get_item(item_id)
    if not item:
        return
    try:
        # Сериализация
        payload = {k: v for k, v in item.items()}
        payload.pop("id", None)  # ID не переносим
        data = json.dumps(payload, ensure_ascii=False)
        compressed = zlib.compress(data.encode("utf-8"))
        encoded = base64.b64encode(compressed).decode("ascii")
        code = "WPITEM:" + encoded

        # Показать в окне
        d = open_window(app, f"Код: {item.get('name', '?')}", 700, 300)
        tk.Label(d, text="Скопируйте этот код и отправьте другу:",
                 font=("Segoe UI", 10)).pack(pady=6)
        t = tk.Text(d, font=("Consolas", 9), height=8,
                     wrap="char")
        t.pack(fill="both", expand=True, padx=8, pady=4)
        t.insert("1.0", code)
        t.tag_add("sel", "1.0", "end")
        try:
            d.clipboard_clear()
            d.clipboard_append(code)
            tk.Label(d, text="✓ Скопировано в буфер",
                     fg="#339933",
                     font=("Segoe UI", 10, "bold")
                     ).pack()
        except Exception:
            pass
        tk.Button(d, text="Закрыть",
                  command=d.destroy).pack(pady=6)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e), parent=app.get_dialog_parent())


def _import_code(app, dialog, rebuild):
    d = open_window(app, "Импорт предмета", 600, 350)
    tk.Label(d, text="Вставьте код (WPITEM:...)",
             font=("Segoe UI", 10)).pack(pady=6)
    t = tk.Text(d, font=("Consolas", 9), height=10,
                 wrap="char")
    t.pack(fill="both", expand=True, padx=8, pady=4)

    def do_import():
        code = t.get("1.0", "end").strip()
        if not code.startswith("WPITEM:"):
            messagebox.showerror("Ошибка",
                                  "Код должен начинаться с WPITEM:",
                                  parent=d)
            return
        try:
            encoded = code[len("WPITEM:"):]
            compressed = base64.b64decode(encoded)
            data = zlib.decompress(compressed).decode("utf-8")
            payload = json.loads(data)
            item = app.c.add_item(**payload)
            app.c._sync_item_bonuses()
            app._refresh()
            show_toast(app,
                        f"✓ Импортирован: {item.get('name','?')}",
                        color="#339933")
            d.destroy()
            rebuild()
        except Exception as e:
            messagebox.showerror("Ошибка импорта", str(e),
                                  parent=d)

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=6, padx=8)
    tk.Button(bf, text="Импортировать", command=do_import,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")
              ).pack(side="left")
    tk.Button(bf, text="Отмена",
              command=d.destroy).pack(side="right")


# ============ ВКЛАДКА ДАУНТАЙМ ============

def _build_downtime_tab(app, parent, dialog, rebuild):
    c = app.c

    outer, canvas, body = make_scrollable(parent)
    outer.pack(fill="both", expand=True)

    # --- Деньги ---
    _section(body, "Деньги")
    money_frame = tk.Frame(body, bg="#f4f4f4")
    money_frame.pack(fill="x", padx=5, pady=4)

    def make_money_row(key, default_name):
        dt = c.downtime[key]
        fr = tk.Frame(money_frame, bg="#f4f4f4")
        fr.pack(fill="x", pady=2)
        name_var = tk.StringVar(value=dt.get("name", default_name))
        e_name = tk.Entry(fr, textvariable=name_var, width=12)
        e_name.pack(side="left")
        amt_var = tk.IntVar(value=dt.get("amount", 0))
        tk.Spinbox(fr, from_=0, to=9999999,
                    textvariable=amt_var, width=10
                    ).pack(side="left", padx=4)

        def on_change(*args, k=key, nv=name_var, av=amt_var):
            c.downtime[k]["name"] = nv.get()
            c.downtime[k]["amount"] = av.get()
            _update_money_total()
        name_var.trace_add("write", on_change)
        amt_var.trace_add("write", on_change)
        return fr

    make_money_row("gold", "Золото")
    make_money_row("silver", "Серебро")
    make_money_row("copper", "Медь")

    # Курс
    fr_rate = tk.Frame(body, bg="#f4f4f4")
    fr_rate.pack(fill="x", padx=5, pady=4)
    tk.Label(fr_rate, text="Курс: 1 зол. =",
             bg="#f4f4f4").pack(side="left")
    g2s_var = tk.IntVar(
        value=c.downtime["rates"].get("gold_to_silver", 100))
    tk.Spinbox(fr_rate, from_=1, to=1000,
                textvariable=g2s_var, width=5
                ).pack(side="left", padx=2)
    tk.Label(fr_rate, text="сер. =",
             bg="#f4f4f4").pack(side="left")
    s2c_var = tk.IntVar(
        value=c.downtime["rates"].get("silver_to_copper", 100))
    tk.Spinbox(fr_rate, from_=1, to=1000,
                textvariable=s2c_var, width=5
                ).pack(side="left", padx=2)
    tk.Label(fr_rate, text="меди",
             bg="#f4f4f4").pack(side="left")

    def save_rates(*args):
        c.downtime["rates"]["gold_to_silver"] = g2s_var.get()
        c.downtime["rates"]["silver_to_copper"] = s2c_var.get()
        _update_money_total()
    g2s_var.trace_add("write", save_rates)
    s2c_var.trace_add("write", save_rates)

    total_lbl = tk.Label(body, text="", bg="#f4f4f4",
                          fg="#c06000",
                          font=("Segoe UI", 11, "bold"))
    total_lbl.pack(anchor="w", padx=10, pady=6)

    def _update_money_total():
        g = c.downtime["gold"]["amount"]
        s = c.downtime["silver"]["amount"]
        co = c.downtime["copper"]["amount"]
        r1 = c.downtime["rates"]["gold_to_silver"]
        r2 = c.downtime["rates"]["silver_to_copper"]
        total_silver = g * r1 + s + co / r2
        total_gold = total_silver / r1
        total_lbl.config(
            text=f"Итого: ≈ {total_gold:.2f} золотых")
    _update_money_total()

    # --- Внимание ---
    _section(body, "Внимание")
    fr_att = tk.Frame(body, bg="#f4f4f4")
    fr_att.pack(fill="x", padx=5, pady=4)
    att_var = tk.IntVar(value=c.attention.get("current", 0))
    tk.Label(fr_att, text="Текущее:",
             bg="#f4f4f4", width=12, anchor="w").pack(side="left")
    tk.Spinbox(fr_att, from_=0, to=999,
                textvariable=att_var, width=6).pack(side="left")
    show_att_var = tk.BooleanVar(
        value=c.settings.get("show_attention_chip", False))
    tk.Checkbutton(fr_att, text="На панели",
                    variable=show_att_var, bg="#f4f4f4"
                    ).pack(side="left", padx=10)

    def on_att_change(*args):
        c.attention["current"] = att_var.get()
        c.settings["show_attention_chip"] = show_att_var.get()
        app._refresh()
    att_var.trace_add("write", on_att_change)
    show_att_var.trace_add("write", on_att_change)

    # Справка внимания
    hint_frame = tk.Frame(body, bg="#e8e8e8", pady=6, padx=8)
    hint_frame.pack(fill="x", padx=5, pady=4)
    drives_bonus = sum(
        1 for v in c.drives.values() if v >= 4) \
        if isinstance(c.drives, dict) else 0
    cycle = c.attention_per_cycle()
    base = 1 + c.level // 3
    hint_text = (
        f"За цикл: {cycle} внимания = "
        f"1 + {c.level}//3 (={base}) "
        f"+ драйвы 4+ (={drives_bonus}).\n\n"
        "Можно потратить внимание на:"
    )

    tk.Label(hint_frame, text=hint_text, bg="#e8e8e8",
             justify="left", wraplength=800,
             font=("Segoe UI", 9)).pack(anchor="w")

    # Кнопки внимания
    btns_frame = tk.Frame(body, bg="#f4f4f4")
    btns_frame.pack(fill="x", padx=5, pady=4)

    def spend_attention(action_name, apply_fn):
        if c.attention["current"] < 1:
            messagebox.showerror(
                "Ошибка", "Нет внимания", parent=app.get_dialog_parent())
            return
        try:
            result = apply_fn()
            c.attention["current"] -= 1
            show_toast(app,
                        f"✓ {action_name}: {result}",
                        color="#4a7", duration=2000)
            app._refresh()
            rebuild()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e),
                                  parent=app.get_dialog_parent())

    # РЛ травмы
    def rl_action():
        d = open_window(app, "Повысить РЛ травмы", 500, 400)
        tk.Label(d, text="Кому повысить рейтинг лечения?",
                 font=("Segoe UI", 10)).pack(pady=6)
        bonus = max(2, c.ability_modifier("str"))
        tk.Label(d, text=f"Бонус: +{bonus} навсегда",
                 fg="#c06000",
                 font=("Segoe UI", 10, "bold")).pack()
        if not c.injuries:
            tk.Label(d, text="(нет травм)",
                     fg="#888").pack(pady=20)
            return
        for i, inj in enumerate(c.injuries):
            fr = tk.Frame(d)
            fr.pack(fill="x", padx=10, pady=2)
            tk.Label(fr,
                     text=f"{inj.get('name','?')} (РЛ {inj.get('heal_rating',1)})",
                     font=("Segoe UI", 9), anchor="w"
                     ).pack(side="left", fill="x", expand=True)

            def pick(idx=i):
                try:
                    P.upgrade_heal_rating(c, idx)
                    c.attention["current"] -= 1
                    show_toast(app, f"✓ РЛ повышен", "#4a7")
                    app._refresh()
                    rebuild()
                    d.destroy()
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e),
                                          parent=d)
            tk.Button(fr, text=f"+{bonus} РЛ",
                      command=pick).pack(side="right")

    tk.Button(btns_frame,
              text="Повысить РЛ травмы (+СИЛ, мин 2)",
              command=rl_action, bg="#6a4a9a", fg="white",
              font=("Segoe UI", 9, "bold"),
              width=40, pady=3
              ).pack(anchor="w", pady=1)

    # Тренировки
    def train_action():
        dex_mod = c.ability_modifier("dex")
        comfort_eq = max(1.0, dex_mod / 2)
        rate = (5 + c.level * 5)
        trainings = int((comfort_eq * rate) // 2)
        if not messagebox.askyesno(
                "Тренировки",
                f"Получить {trainings} тренировок за 1 внимание?\n"
                f"(DEX_mod = {dex_mod}, comfort = {comfort_eq}, "
                f"rate = {rate})",
                parent=app.get_dialog_parent()):
            return
        spend_attention("Тренировки",
                        lambda: _grant_training(
                            c, trainings))

    def _grant_training(ch, n):
        ch.training["available"] += n
        return f"+{n} тренировок"

    tk.Button(btns_frame,
              text="Получить тренировок (ЛОВ/2 комфорта)",
              command=train_action, bg="#6a4a9a", fg="white",
              font=("Segoe UI", 9, "bold"),
              width=40, pady=3
              ).pack(anchor="w", pady=1)

    # ОВ (ВЫН времени)
    def time_action():
        con_mod = c.ability_modifier("con")
        n = max(2, con_mod)
        if messagebox.askyesno(
                "Очки Времени (ОВ)",
                f"Получить {n} ОВ?\n"
                f"(ВЫН мод = {con_mod})",
                parent=app.get_dialog_parent()):
            c.downtime["time_points"]["current"] += n
            c.attention["current"] -= 1
            show_toast(app, f"✓ +{n} ОВ", color="#4a7")
            app._refresh()
            rebuild()

    tk.Button(btns_frame,
              text="Получить ОВ (ВЫН, мин 2)",
              command=time_action, bg="#6a4a9a", fg="white",
              font=("Segoe UI", 9, "bold"),
              width=40, pady=3
              ).pack(anchor="w", pady=1)

    # Очки базы
    def base_action():
        int_mod = c.ability_modifier("int")
        n = max(0.4, 0.2 * int_mod)
        if messagebox.askyesno(
                "Очки базы",
                f"Получить {n} слотов базы?\n"
                f"(ИНТ мод = {int_mod})",
                parent=app.get_dialog_parent()):
            c.base["slots_max"] = int(
                c.base.get("slots_max", 5) + round(n))
            c.attention["current"] -= 1
            show_toast(app, f"✓ +{round(n)} слотов базы",
                        color="#4a7")
            app._refresh()
            rebuild()

    tk.Button(btns_frame,
              text="Получить слотов базы (0.2×ИНТ)",
              command=base_action, bg="#6a4a9a", fg="white",
              font=("Segoe UI", 9, "bold"),
              width=40, pady=3
              ).pack(anchor="w", pady=1)

    # Квесты / Мощь историй (заглушки)
    tk.Label(btns_frame, text="",
              bg="#f4f4f4").pack()
    tk.Button(btns_frame,
              text="Квесты от дворов (МДР, мин 1) [заглушка]",
              command=lambda: show_toast(
                  app, "Квесты — в разработке", color="#666"),
              bg="#999", fg="white", state="disabled",
              font=("Segoe UI", 9),
              width=40, pady=3
              ).pack(anchor="w", pady=1)
    tk.Button(btns_frame,
              text="Мощь историй (ХАР, мин 2) [заглушка]",
              command=lambda: show_toast(
                  app, "Мощь историй — в разработке", color="#666"),
              bg="#999", fg="white", state="disabled",
              font=("Segoe UI", 9),
              width=40, pady=3
              ).pack(anchor="w", pady=1)

    # --- Комфорт ---
    _section(body, "Комфорт")
    fr_cf = tk.Frame(body, bg="#f4f4f4")
    fr_cf.pack(fill="x", padx=5, pady=4)
    cf_var = tk.IntVar(value=c.comfort.get("current", 0))
    cf_max_var = tk.IntVar(value=c.comfort.get("max", 10))
    tk.Label(fr_cf, text="Текущий:",
             bg="#f4f4f4", width=12, anchor="w").pack(side="left")
    tk.Spinbox(fr_cf, from_=0, to=999,
                textvariable=cf_var, width=6).pack(side="left")
    tk.Label(fr_cf, text="Макс:",
             bg="#f4f4f4", padx=6).pack(side="left")
    tk.Spinbox(fr_cf, from_=0, to=999,
                textvariable=cf_max_var, width=6).pack(side="left")
    show_cf_var = tk.BooleanVar(
        value=c.settings.get("show_comfort_chip", True))
    tk.Checkbutton(fr_cf, text="На панели",
                    variable=show_cf_var, bg="#f4f4f4"
                    ).pack(side="left", padx=10)

    def on_cf_change(*args):
        c.comfort["current"] = cf_var.get()
        c.comfort["max"] = cf_max_var.get()
        c.settings["show_comfort_chip"] = show_cf_var.get()
        app._refresh()
    cf_var.trace_add("write", on_cf_change)
    cf_max_var.trace_add("write", on_cf_change)
    show_cf_var.trace_add("write", on_cf_change)

    # Формула тренировок
    rate = (5 + c.level * 5)
    formula_frame = tk.Frame(body, bg="#e8e8e8", pady=6, padx=8)
    formula_frame.pack(fill="x", padx=5, pady=4)
    tk.Label(formula_frame,
             text=f"Формула: 1 комфорт = ({5} + 5×{c.level}) "
                  f"= {rate} тренировок",
             bg="#e8e8e8", font=("Segoe UI", 9)
             ).pack(anchor="w")

    # Кнопка тренировки через комфорт
    def train_comfort():
        if c.comfort["current"] < 1:
            messagebox.showerror("Ошибка",
                                  "Нет комфорта", parent=app.get_dialog_parent())
            return
        n = messagebox.askinteger(
            "Тренироваться",
            f"Потратить сколько комфорта? "
            f"(1 = {rate} тренировок)",
            initialvalue=1, minvalue=1,
            maxvalue=c.comfort["current"],
            parent=app.get_dialog_parent())
        if not n:
            return
        try:
            got = P.spend_comfort(c, n)
            show_toast(app, f"✓ +{got} тренировок",
                        color="#4a7")
            app._refresh()
            rebuild()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e),
                                  parent=app.get_dialog_parent())

    tk.Button(body,
              text=f"🛌 Тренироваться (1 комфорт = {rate})",
              command=train_comfort, bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold"),
              pady=4
              ).pack(anchor="w", padx=5, pady=4)

    # --- ОВ ---
    _section(body, "Очки Времени (ОВ)")
    fr_tp = tk.Frame(body, bg="#f4f4f4")
    fr_tp.pack(fill="x", padx=5, pady=4)
    tp_var = tk.IntVar(
        value=c.downtime["time_points"].get("current", 0))
    tk.Label(fr_tp, text="Текущие:",
             bg="#f4f4f4", width=12, anchor="w").pack(side="left")
    tk.Spinbox(fr_tp, from_=0, to=999,
                textvariable=tp_var, width=6).pack(side="left")

    def on_tp(*args):
        c.downtime["time_points"]["current"] = tp_var.get()
    tp_var.trace_add("write", on_tp)

    show_tp_var = tk.BooleanVar(
        value=c.settings.get("show_time_chip", False))
    tk.Checkbutton(fr_tp, text="На панели",
                    variable=show_tp_var, bg="#f4f4f4"
                    ).pack(side="left", padx=10)

    def on_show_tp(*args):
        c.settings["show_time_chip"] = show_tp_var.get()
        app._refresh()
    show_tp_var.trace_add("write", on_show_tp)

    # --- База справка ---
    _section(body, "Справка: База")
    hint_base = tk.Frame(body, bg="#e8e8e8", pady=6, padx=8)
    hint_base.pack(fill="x", padx=5, pady=4)
    tk.Label(hint_base,
             text="База — «склад» персонажа. "
                  "У нового персонажа 5 слотов; "
                  "увеличивается за внимание. "
                  "Обычные предметы (илвл 0) хранятся "
                  "в любом количестве в 1 слоте. "
                  "Каждый необычный предмет занимает "
                  "1+ слотов. Идентичные ресурсы — 1 слот.",
             bg="#e8e8e8", justify="left",
             wraplength=800,
             font=("Segoe UI", 9)).pack(anchor="w")