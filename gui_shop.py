# gui_shop.py — каталог/магазин (v1)
# JSON-каталог shop.json, покупка, импорт CSV, экспорт JSON

import csv
import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

from character import (CATALOGS_DIR, CATALOG_SUBDIRS, load_catalogs,
                       BASE_DIR, ITEM_CATEGORIES, _make_item,
                       ARMOR_CATALOG, SHIELD_CATALOG, WEAPON_ITEM_CATALOG,
                       FEATS_CATALOG, TEMPLATES_CATALOG, SKILLS_CATALOG,
                       RACE_ABILITIES_CATALOG, CLASS_ABILITIES_CATALOG,
                       SPELLS_CATALOG, BUFFS_CATALOG, CUSTOM_CATALOG)
from gui_shared import (ToolTip, make_scrollable)
from gui_windows import open_window
from gui_alphabet import CATEGORY_NAMES
from gui_inventory import (
    show_toast,
    _section, _row_entry, _row_text, _row_option,
)

SHOP_FILE = os.path.join(BASE_DIR, "shop.json")

ARMOR_TYPE_RU = {
    "лёгкая": "Light", "легкая": "Light",
    "средняя": "Medium",
    "тяжёлая": "Heavy", "тяжелая": "Heavy",
    "ростовая": "Tower",
}


def load_shop():
    if not os.path.exists(SHOP_FILE):
        default = {"version": 1, "items": []}
        try:
            with open(SHOP_FILE, "w", encoding="utf-8") as f:
                json.dump(default, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        return default
    try:
        with open(SHOP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {"version": 1, "items": []}
        data.setdefault("version", 1)
        data.setdefault("items", [])
        if not isinstance(data["items"], list):
            data["items"] = []
        return data
    except Exception as e:
        messagebox.showerror(
            "Ошибка", f"Не удалось прочитать shop.json:\n{e}")
        return {"version": 1, "items": []}


def save_shop(data):
    try:
        with open(SHOP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror(
            "Ошибка", f"Не удалось сохранить shop.json:\n{e}")
        return False


def _money_snapshot(c):
    """Возвращает (total_copper, rates) — для точных расчётов."""
    g = c.downtime["gold"]["amount"]
    s = c.downtime["silver"]["amount"]
    co = c.downtime["copper"]["amount"]
    r1 = c.downtime["rates"]["gold_to_silver"]
    r2 = c.downtime["rates"]["silver_to_copper"]
    total = int(round(g * r1 * r2 + s * r2 + co))
    return total, r1, r2


def _apply_money(c, total_copper, r1, r2):
    if total_copper < 0:
        total_copper = 0
    co_new = total_copper % r2
    tmp = total_copper // r2
    s_new = tmp % r1
    g_new = tmp // r1
    c.downtime["gold"]["amount"] = int(g_new)
    c.downtime["silver"]["amount"] = int(s_new)
    c.downtime["copper"]["amount"] = int(co_new)


def _format_money(c):
    total, r1, r2 = _money_snapshot(c)
    gold = total / (r1 * r2)
    return f"≈ {gold:.2f} зол."


def _catalog_packs():
    """Уникальные источники (pack) из всех загруженных каталогов."""
    packs = set()
    for lst in (ARMOR_CATALOG, SHIELD_CATALOG, WEAPON_ITEM_CATALOG,
                FEATS_CATALOG, TEMPLATES_CATALOG, SKILLS_CATALOG,
                RACE_ABILITIES_CATALOG, CLASS_ABILITIES_CATALOG,
                SPELLS_CATALOG, BUFFS_CATALOG, CUSTOM_CATALOG):
        for it in lst:
            p = (it.get("pack") or "").strip()
            if p:
                packs.add(p)
    return sorted(packs)


def _catalog_categories():
    """Категории, где есть хотя бы один включённый элемент."""
    cats = set()
    for lst in (ARMOR_CATALOG, SHIELD_CATALOG, WEAPON_ITEM_CATALOG,
                FEATS_CATALOG, TEMPLATES_CATALOG, SKILLS_CATALOG,
                RACE_ABILITIES_CATALOG, CLASS_ABILITIES_CATALOG,
                SPELLS_CATALOG, BUFFS_CATALOG, CUSTOM_CATALOG):
        for it in lst:
            c = (it.get("category") or "").strip()
            if c:
                cats.add(c)
    return sorted(cats)


def _catalog_items_for_shop():
    """Все элементы включённых каталогов (без фильтра)."""
    out = []
    for lst in (ARMOR_CATALOG, SHIELD_CATALOG, WEAPON_ITEM_CATALOG,
                FEATS_CATALOG, TEMPLATES_CATALOG, SKILLS_CATALOG,
                RACE_ABILITIES_CATALOG, CLASS_ABILITIES_CATALOG,
                SPELLS_CATALOG, BUFFS_CATALOG, CUSTOM_CATALOG):
        out.extend(lst)
    return out


def open_shop(app):
    if not app.c:
        return
    # Перезагружаем каталоги, чтобы учесть catalogs_enabled.
    try:
        load_catalogs(app.c.settings)
    except Exception as e:
        print(f"[open_shop load_catalogs] {e}")
    shop = load_shop()

    d = open_window(app, "Каталог предметов", 980, 760)

    top_bar = tk.Frame(d, bg="#2b2b2b", pady=4, padx=8)
    top_bar.pack(fill="x")
    tk.Button(top_bar, text="⚙ Управление каталогами",
              command=lambda: _open_catalogs_manager(app),
              bg="#446", fg="white", relief="flat",
              font=("Segoe UI", 9, "bold")
              ).pack(side="right", padx=2)

    top = tk.Frame(d, bg="#2b2b2b", pady=6, padx=10)
    top.pack(fill="x")
    tk.Label(top, text="📦 Каталог",
             font=("Segoe UI", 12, "bold"),
             fg="white", bg="#2b2b2b").pack(side="left")
    money_lbl = tk.Label(top, text="", fg="#f0c040",
                          bg="#2b2b2b",
                          font=("Segoe UI", 10, "bold"))
    money_lbl.pack(side="left", padx=20)

    def upd_money():
        money_lbl.config(text=f"Деньги: {_format_money(app.c)}")

    # ===== Фильтры =====
    filter_frame = tk.Frame(d, bg="#3a3a3a", pady=4)
    filter_frame.pack(fill="x")

    all_cats = ["Все"] + _catalog_categories()
    cat_var = tk.StringVar(value="Все")
    tk.Label(filter_frame, text="Категория:",
             bg="#3a3a3a", fg="white",
             font=("Segoe UI", 9, "bold")
             ).pack(side="left", padx=(6, 2))
    cat_om = tk.OptionMenu(filter_frame, cat_var, *all_cats)
    cat_om.config(width=16)
    cat_om.pack(side="left", padx=2)

    all_packs = ["все"] + _catalog_packs()
    src1_var = tk.StringVar(value="все")
    tk.Label(filter_frame, text="Источник 1:",
             bg="#3a3a3a", fg="white",
             font=("Segoe UI", 9, "bold")
             ).pack(side="left", padx=(12, 2))
    src1_om = tk.OptionMenu(filter_frame, src1_var, *all_packs)
    src1_om.config(width=14)
    src1_om.pack(side="left", padx=2)

    src2_var = tk.StringVar(value="— нет —")
    tk.Label(filter_frame, text="Источник 2:",
             bg="#3a3a3a", fg="white",
             font=("Segoe UI", 9, "bold")
             ).pack(side="left", padx=(12, 2))
    src2_om = tk.OptionMenu(filter_frame, src2_var,
                             *(["— нет —"] + all_packs))
    src2_om.config(width=14)
    src2_om.pack(side="left", padx=2)

    tk.Label(filter_frame, text="  Поиск:",
             bg="#3a3a3a", fg="white",
             font=("Segoe UI", 9, "bold")
             ).pack(side="left", padx=(12, 2))
    search_var = tk.StringVar()
    tk.Entry(filter_frame, textvariable=search_var, width=20
             ).pack(side="left", padx=2)

    # ===== Панель кнопок каталога (старая, для shop.json) =====
    bf = tk.Frame(d, bg="#2a2a2a", pady=4, padx=6)
    bf.pack(fill="x")
    tk.Button(bf, text="＋ Добавить",
              command=lambda: _shop_item_dialog(
                  app, shop, None, rebuild),
              bg="#4a7", fg="white",
              font=("Segoe UI", 9, "bold"),
              padx=8).pack(side="left", padx=2)
    tk.Button(bf, text="📥 Импорт CSV",
              command=lambda: _import_csv(app, shop, rebuild),
              bg="#446", fg="white",
              font=("Segoe UI", 9, "bold"),
              padx=8).pack(side="left", padx=2)
    tk.Button(bf, text="📤 Экспорт JSON",
              command=lambda: _export_json(shop),
              bg="#446", fg="white",
              font=("Segoe UI", 9, "bold"),
              padx=8).pack(side="left", padx=2)
    tk.Button(bf, text="🔄 Перезагрузить",
              command=lambda: _reload_catalog(app, shop, rebuild),
              bg="#666", fg="white",
              font=("Segoe UI", 9),
              padx=8).pack(side="left", padx=2)

    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=4, pady=4)

    def _matches_filters(it):
        cat = cat_var.get()
        s1 = src1_var.get()
        s2 = src2_var.get()
        q = search_var.get().strip().lower()
        if cat != "Все" and (it.get("category") or "") != cat:
            return False
        p = (it.get("pack") or "").strip()
        ok_src = True
        if s1 != "все" or (s2 != "— нет —" and s2 != "все"):
            ok_src = False
            if s1 != "все" and p == s1:
                ok_src = True
            if s2 not in ("— нет —", "все") and p == s2:
                ok_src = True
        if not ok_src:
            return False
        if q:
            nm = (it.get("name") or "").lower()
            ds = (it.get("desc") or "").lower()
            if q not in nm and q not in ds:
                return False
        return True

    def rebuild():
        upd_money()
        for w in body.winfo_children():
            w.destroy()
        cat = cat_var.get()
        s1 = src1_var.get()
        s2 = src2_var.get()
        q = search_var.get().strip().lower()
        show_shop_json = (cat == "Все" and s1 == "все"
                          and s2 in ("— нет —", "все")
                          and not q)
        items = [it for it in _catalog_items_for_shop()
                 if _matches_filters(it)]
        shop_items = []
        if show_shop_json:
            shop_items = list(shop.get("items", []))
            if not shop_items and not items:
                tk.Label(body, text="(каталог пуст)",
                         fg="#888", bg="#f4f4f4",
                         font=("Segoe UI", 10, "italic")
                         ).pack(pady=20)
                return
        if items:
            _section(body, "📚 Из каталогов")
            items_sorted = sorted(
                items, key=lambda x: (x.get("category", ""),
                                      x.get("pack", ""),
                                      x.get("name", "")))
            for item in items_sorted:
                _shop_catalog_row(app, body, item, rebuild)
        if shop_items:
            _section(body, "🛒 Мой магазин (shop.json)")
            shop_sorted = sorted(
                shop_items, key=lambda x: (x.get("category", ""),
                                           x.get("name", "")))
            for item in shop_sorted:
                _shop_item_row(app, body, shop, item, rebuild)
        if not items and not shop_items:
            tk.Label(body, text="(ничего не найдено)",
                     fg="#888", bg="#f4f4f4",
                     font=("Segoe UI", 10, "italic")
                     ).pack(pady=20)

    cat_var.trace_add("write", lambda *a: rebuild())
    src1_var.trace_add("write", lambda *a: rebuild())
    src2_var.trace_add("write", lambda *a: rebuild())
    search_var.trace_add("write", lambda *a: rebuild())

    def _reload_catalog(app2, shop2, rb):
        try:
            load_catalogs(app2.c.settings)
        except Exception as e:
            print(f"[reload] {e}")
        for om, var, base in ((cat_om, cat_var,
                               ["Все"] + _catalog_categories()),
                              (src1_om, src1_var,
                               ["все"] + _catalog_packs()),
                              (src2_om, src2_var,
                               ["— нет —"] + ["все"] + _catalog_packs())):
            menu = om["menu"]
            menu.delete(0, "end")
            for v in base:
                menu.add_command(
                    label=v,
                    command=lambda vv=v, vvar=var: vvar.set(vv))
            if var.get() not in base:
                var.set(base[0])
        rb()

    rebuild()
    app._refresh()

def _shop_catalog_row(app, parent, item, rebuild):
    """Строка элемента каталога (не shop.json)."""
    row = tk.Frame(parent, bg="#f8f8f8",
                   relief="solid", borderwidth=1)
    row.pack(fill="x", padx=2, pady=1)

    info = tk.Frame(row, bg="#f8f8f8")
    info.pack(side="left", fill="both", expand=True,
               padx=4, pady=2)

    name = item.get("name", "?")
    pack = item.get("pack", "")
    cat = item.get("category", "")
    price = item.get("price", 0)

    title = f"• {name}"
    if pack:
        title += f"  [{pack}]"
    tk.Label(info, text=title, bg="#f8f8f8",
             font=("Segoe UI", 10, "bold"),
             anchor="w").pack(anchor="w")
    if item.get("desc"):
        tk.Label(info, text=item["desc"][:100],
                 bg="#f8f8f8", fg="#666",
                 font=("Segoe UI", 8),
                 anchor="w").pack(anchor="w")

    parts = []
    if cat:
        parts.append(CATEGORY_NAMES.get(cat, cat))
    if price:
        parts.append(f"{price} зол.")
    if item.get("damage"):
        parts.append(f"урон {item['damage']}")
    if item.get("ac_bonus"):
        parts.append(f"AC +{item['ac_bonus']}")
    if parts:
        tk.Label(info, text=" | ".join(parts),
                 bg="#f8f8f8", fg="#666",
                 font=("Segoe UI", 8)).pack(anchor="w")

    btns = tk.Frame(row, bg="#f8f8f8")
    btns.pack(side="right", padx=4, pady=2)
    tk.Button(btns, text="💰 Купить",
              command=lambda: _buy_from_catalog(app, item),
              bg="#4a7", fg="white",
              font=("Segoe UI", 8, "bold"),
              padx=6).pack(side="left", padx=2)


def _buy_from_catalog(app, item):
    """Купить элемент из каталога (копия в инвентарь, если предмет)."""
    c = app.c
    cat = item.get("category", "")
    price = float(item.get("price", 0) or 0)
    total, r1, r2 = _money_snapshot(c)
    price_cp = int(round(price * r1 * r2))
    if total < price_cp:
        messagebox.showerror(
            "Не хватает денег",
            f"Нужно {price} зол.\n"
            f"У тебя: {_format_money(c)}",
            parent=app.get_dialog_parent())
        return
    if not messagebox.askyesno(
            "Купить",
            f"Купить «{item.get('name','?')}» за {price} зол.?",
            parent=app.get_dialog_parent()):
        return
    _apply_money(c, total - price_cp, r1, r2)
    payload = {k: v for k, v in item.items()
               if k not in ("price", "id", "pack")}
    payload["location"] = "bag"
    if not payload.get("category"):
        payload["category"] = "misc"
    c.add_item(**payload)
    c._sync_item_bonuses()
    show_toast(app,
               f"✓ Куплено: {item.get('name','?')}",
               color="#4a7", duration=2000)
    app._refresh()


def _open_catalogs_manager(app):
    """⚙ Управление каталогами (модуль gui_catalogs)."""
    import gui_catalogs
    gui_catalogs.open_catalogs_manager(app)

def _shop_item_row(app, parent, shop, item, rebuild):
    row = tk.Frame(parent, bg="#f8f8f8",
                   relief="solid", borderwidth=1)
    row.pack(fill="x", padx=2, pady=1)

    info = tk.Frame(row, bg="#f8f8f8")
    info.pack(side="left", fill="both", expand=True,
               padx=4, pady=2)

    cat = CATEGORY_NAMES.get(item.get("category", "misc"), "?")
    price = item.get("price", 0)

    name_lbl = tk.Label(info,
                        text=f"• {item.get('name','?')}",
                        bg="#f8f8f8",
                        font=("Segoe UI", 10, "bold"),
                        anchor="w")
    name_lbl.pack(anchor="w")
    if item.get("desc"):
        ToolTip(name_lbl, item["desc"])

    parts = [cat, f"{price} зол."]
    w = item.get("weight", 0)
    qty = item.get("qty", 1)
    if item.get("weight_type") == "-":
        parts.append("—")
    elif item.get("weight_type") == "L":
        parts.append(f"{w*qty}L")
    else:
        parts.append(f"{w*qty} балк")
    if item.get("ac_bonus"):
        parts.append(f"AC +{item['ac_bonus']}")
    if item.get("armor_type"):
        parts.append(item["armor_type"])
    if item.get("damage"):
        parts.append(f"урон {item['damage']}")

    tk.Label(info, text=" | ".join(parts),
             bg="#f8f8f8", fg="#666",
             font=("Segoe UI", 8)).pack(anchor="w")

    btns = tk.Frame(row, bg="#f8f8f8")
    btns.pack(side="right", padx=4, pady=2)

    tk.Button(btns, text="💰 Купить",
              command=lambda: _buy(app, shop, item, rebuild),
              bg="#4a7", fg="white",
              font=("Segoe UI", 8, "bold"),
              padx=6).pack(side="left", padx=2)
    tk.Button(btns, text="✎", width=2,
              command=lambda: _shop_item_dialog(
                  app, shop, item, rebuild)
              ).pack(side="left", padx=1)
    tk.Button(btns, text="✖", width=2,
              command=lambda: _delete_shop_item(
                  shop, item, rebuild)
              ).pack(side="left", padx=1)


def _buy(app, shop, item, rebuild):
    c = app.c
    price = float(item.get("price", 0) or 0)
    total, r1, r2 = _money_snapshot(c)
    price_cp = int(round(price * r1 * r2))
    if total < price_cp:
        messagebox.showerror(
            "Не хватает денег",
            f"Нужно {price} зол.\n"
            f"У тебя: {_format_money(c)}",
            parent=app.get_dialog_parent())
        return
    if not messagebox.askyesno(
            "Купить",
            f"Купить «{item.get('name','?')}» за {price} зол.?",
            parent=app.get_dialog_parent()):
        return

    _apply_money(c, total - price_cp, r1, r2)
    payload = {k: v for k, v in item.items()
               if k not in ("price", "id")}
    payload["location"] = "bag"
    new_item = c.add_item(**payload)
    c._sync_item_bonuses()
    show_toast(app,
               f"✓ Куплено: {item.get('name','?')}",
               color="#4a7", duration=2000)
    app._refresh()
    rebuild()


def _delete_shop_item(shop, item, rebuild):
    if not messagebox.askyesno(
            "Удалить",
            f"Удалить «{item.get('name','?')}» из каталога?"):
        return
    shop["items"] = [it for it in shop["items"]
                     if it is not item]
    save_shop(shop)
    rebuild()

def _shop_item_dialog(app, shop, item, rebuild):
    from gui_inventory import edit_item, _make_item as _mk
    is_new = item is None
    if is_new:
        item = _mk(name="", location="bag")
        item["price"] = 0
        shop["items"].append(item)

    def on_save():
        item.pop("id", None)
        save_shop(shop)
        rebuild()

    def on_cancel():
        if is_new and item in shop["items"]:
            shop["items"].remove(item)
        rebuild()

    edit_item(app, item, mode="shop",
                on_save=on_save, on_cancel=on_cancel)

def _import_csv(app, shop, rebuild):
    path = filedialog.askopenfilename(
        parent=app.get_dialog_parent(),
        title="Импорт CSV",
        filetypes=[("CSV", "*.csv"), ("Все", "*.*")])
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        messagebox.showerror(
            "Ошибка", f"Не удалось прочитать CSV:\n{e}")
        return

    if not rows:
        messagebox.showwarning("CSV", "Файл пуст")
        return

    headers = list(rows[0].keys())
    msg = (f"Колонки:\n{', '.join(headers)}\n\n"
           f"Импортировать {len(rows)} предметов?")
    if not messagebox.askyesno("Импорт CSV", msg):
        return

    imported = 0
    skipped = 0
    for row in rows:
        try:
            item = _make_item(location="bag")
            item.pop("id", None)
            item["price"] = 0
            for key, val in row.items():
                if not val or not str(val).strip():
                    continue
                key_l = str(key).strip().lower()
                val = str(val).strip()
                if key_l in ("name", "название"):
                    item["name"] = val
                elif key_l in ("category", "категория"):
                    found = False
                    for k, v in CATEGORY_NAMES.items():
                        if v.lower() == val.lower():
                            item["category"] = k
                            found = True
                            break
                    if not found:
                        item["category"] = val
                elif key_l in ("price", "цена"):
                    item["price"] = float(
                        val.replace(",", "."))
                elif key_l in ("weight", "вес"):
                    try:
                        item["weight"] = float(
                            val.replace(",", "."))
                    except Exception:
                        if val in ("L", "l", "л"):
                            item["weight_type"] = "L"
                            item["weight"] = 0
                        elif val == "-":
                            item["weight_type"] = "-"
                            item["weight"] = 0
                elif key_l in ("weight_type", "тип веса"):
                    if val in ("L", "l", "л"):
                        item["weight_type"] = "L"
                    elif val == "-":
                        item["weight_type"] = "-"
                    else:
                        item["weight_type"] = "mass"
                elif key_l in ("damage", "урон"):
                    item["damage"] = val
                elif key_l in ("ac_bonus", "ac", "бонус ac",
                                "бонус ац"):
                    try:
                        item["ac_bonus"] = int(float(val))
                    except Exception:
                        pass
                elif key_l in ("armor_type", "тип брони"):
                    if val in ARMOR_TYPE_RU:
                        item["armor_type"] = ARMOR_TYPE_RU[val]
                    elif val in ("Light", "Medium", "Heavy",
                                  "Tower"):
                        item["armor_type"] = val
                    elif val == "-":
                        item["armor_type"] = None
                elif key_l in ("desc", "описание"):
                    item["desc"] = val
                elif key_l in ("qty", "количество"):
                    try:
                        item["qty"] = int(float(val))
                    except Exception:
                        pass

            if not item.get("name"):
                skipped += 1
                continue
            shop["items"].append(item)
            imported += 1
        except Exception as e:
            print(f"[csv row] {e}")
            skipped += 1
            continue

    save_shop(shop)
    msg = f"✓ Импортировано: {imported}"
    if skipped:
        msg += f" (пропущено: {skipped})"
    show_toast(app, msg, color="#4a7", duration=2500)
    rebuild()


def _export_json(shop):
    path = filedialog.asksaveasfilename(
        title="Экспорт JSON",
        defaultextension=".json",
        initialfile="shop_export.json",
        filetypes=[("JSON", "*.json")])
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(shop, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Экспорт",
                             f"Сохранено:\n{path}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def _reload(app, shop, rebuild):
    new_data = load_shop()
    shop.clear()
    shop.update(new_data)
    rebuild()

# ============ K2b: редактор каталогов ============

def open_catalogs(app):
    """Окно «Каталоги»: список всех папок + файлы + создание/редактирование."""
    if not app.c:
        return
    d = open_window(app, "Каталоги", 760, 700)

    tk.Label(d, text="📚 Каталоги",
             font=("Segoe UI", 13, "bold"),
             bg="#2b2b2b", fg="white", pady=8
             ).pack(fill="x")

    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=6)

    def rebuild():
        for w in body.winfo_children():
            w.destroy()
        q = search_var.get().strip().lower()
        kf = kind_var.get()
        for sub in CATALOG_SUBDIRS:
            if kf != "все" and sub != kf:
                continue
            folder = os.path.join(CATALOGS_DIR, sub)
            os.makedirs(folder, exist_ok=True)
            sec = tk.Frame(body, bg="#c8c8c8")
            sec.pack(fill="x", pady=(8, 2))
            tk.Label(sec, text=f"📁 {sub}",
                     font=("Segoe UI", 11, "bold"),
                     bg="#c8c8c8", anchor="w", padx=8
                     ).pack(side="left", fill="x", expand=True)
            tk.Button(sec, text="＋ Новый каталог",
                      command=lambda s=sub: _new_catalog(app, s, rebuild),
                      bg="#4a7", fg="white",
                      font=("Segoe UI", 9, "bold")
                      ).pack(side="right", padx=4)
            files = sorted([f for f in os.listdir(folder)
                            if f.endswith(".json")
                            and (not q or q in f.lower())])
            if not files:
                tk.Label(body, text="  (нет файлов)",
                         bg="#f4f4f4", fg="#888",
                         font=("Segoe UI", 10, "italic")
                         ).pack(anchor="w", padx=10, pady=2)
                continue
            for fn in files:
                row = tk.Frame(body, bg="#f8f8f8",
                                relief="solid", borderwidth=1)
                row.pack(fill="x", padx=4, pady=1)
                tk.Label(row, text=f"  📄 {fn}",
                         bg="#f8f8f8",
                         font=("Segoe UI", 10),
                         anchor="w").pack(side="left", fill="x",
                                           expand=True, padx=4, pady=2)
                tk.Button(row, text="✎",
                          command=lambda s=sub, f=fn:
                          _edit_catalog_file(app, s, f, rebuild),
                          width=2).pack(side="right", padx=1)
                tk.Button(row, text="✖",
                          command=lambda s=sub, f=fn:
                          _delete_catalog_file(app, s, f, rebuild),
                          width=2).pack(side="right", padx=1)
                # T35b: показать элементы внутри JSON
                try:
                    with open(os.path.join(folder, fn),
                              "r", encoding="utf-8") as _f:
                        _data = json.load(_f)
                except Exception:
                    continue
                _items = (_data.get("items")
                          or _data.get("groups") or [])
                for _it in _items:
                    if not isinstance(_it, dict):
                        continue
                    _nm = (_it.get("name") or "").strip()
                    if q and q not in _nm.lower():
                        continue
                    _r = tk.Frame(body, bg="#fcfcfc",
                                   relief="flat", borderwidth=1)
                    _r.pack(fill="x", padx=20, pady=0)
                    tk.Label(_r, text=f"    • {_nm or '?'}",
                             bg="#fcfcfc",
                             font=("Segoe UI", 9),
                             anchor="w").pack(side="left",
                                               padx=4, pady=1)
                    tk.Button(
                        _r, text="＋ Взять",
                        command=lambda s=sub, i=_it:
                        _take_from_catalog(app, s, i, rebuild),
                        bg="#4a7", fg="white",
                        font=("Segoe UI", 8, "bold"),
                        padx=4
                        ).pack(side="right", padx=2, pady=1)

    # T35: поиск + фильтр
    top_filter = tk.Frame(d, bg="#e8e8e8", pady=4, padx=6)
    top_filter.pack(fill="x", padx=6, pady=(0, 4), before=outer)
    tk.Label(top_filter, text="🔎 Поиск:",
             bg="#e8e8e8").pack(side="left")
    search_var = tk.StringVar()
    tk.Entry(top_filter, textvariable=search_var, width=24
             ).pack(side="left", padx=4)
    tk.Label(top_filter, text="  Тип:",
             bg="#e8e8e8").pack(side="left")
    kind_var = tk.StringVar(value="все")
    kinds = ["все"] + list(CATALOG_SUBDIRS)
    kind_om = tk.OptionMenu(top_filter, kind_var, *kinds)
    kind_om.config(width=18)
    kind_om.pack(side="left", padx=4)

    def _on_filter(*args):
        rebuild()
    search_var.trace_add("write", _on_filter)
    kind_var.trace_add("write", _on_filter)

    rebuild()

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=6, padx=6)
    tk.Button(bf, text="📥 Импорт по URL",
              command=lambda: _import_catalog_url(app, rebuild),
              bg="#446", fg="white",
              font=("Segoe UI", 9, "bold"),
              padx=12).pack(side="left")
    tk.Button(bf, text="Закрыть",
              command=d.destroy,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold"),
              padx=20).pack(side="right")

def _take_from_catalog(app, sub, item, rebuild):
    """T35c: взять элемент из каталога в персонажа (по типу папки)."""
    if not app.c:
        return
    c = app.c
    nm = item.get("name", "?")
    try:
        if sub == "weapon_items":
            c.add_item(**{k: v for k, v in item.items()
                           if k != "id" and k != "pack"})
        elif sub == "armor":
            c.add_item(**{k: v for k, v in item.items()
                           if k != "id" and k != "pack"},
                        category="armor")
        elif sub == "shields":
            c.add_item(**{k: v for k, v in item.items()
                           if k != "id" and k != "pack"},
                        category="shield")
        elif sub == "feats":
            c.feats.append({"name": nm,
                             "desc": item.get("desc", ""),
                             "link": item.get("link", ""),
                             "source": "loot", "invested": 0})
        elif sub == "templates":
            c.templates.append({"name": nm,
                                 "type": item.get("type", ""),
                                 "desc": item.get("desc", "")})
        elif sub == "skills":
            from purchases import find_skill
            if find_skill(c, nm):
                messagebox.showwarning("Уже есть",
                                        f"Навык '{nm}' уже есть",
                                        parent=app.get_dialog_parent())
                return
            c.skills.append({"name": nm,
                              "stat": item.get("stat", "int"),
                              "tier": item.get("tier", "normal"),
                              "rank": int(item.get("rank", 0) or 0),
                              "source": "loot", "invested": 0,
                              "mods": []})
        elif sub == "race_abilities":
            a = dict(item)
            a.pop("pack", None)
            c.race.setdefault("abilities", []).append(a)
        elif sub == "class_abilities":
            a = dict(item)
            a.pop("pack", None)
            c.char_class.setdefault("abilities", []).append(a)
        elif sub == "spells":
            sp = dict(item)
            sp.pop("pack", None)
            sp.setdefault("source", "loot")
            sp.setdefault("invested", 0)
            sp.setdefault("masteries", [])
            sp.setdefault("mastery", False)
            c.spells.append(sp)
        elif sub == "buffs":
            inj = dict(item)
            inj.pop("pack", None)
            inj.setdefault("name", "Травма")
            inj.setdefault("severity", "custom")
            inj.setdefault("heal_rating", 1)
            inj.setdefault("desc", "")
            inj.setdefault("uses", False)
            inj.setdefault("uses_max", 0)
            inj.setdefault("uses_current", 0)
            inj.setdefault("tick_on_initiative", False)
            inj.setdefault("active", True)
            inj.setdefault("effects", [])
            c.injuries.append(inj)
        elif sub == "custom":
            kind = item.get("kind", "")
            if kind == "lens" or "current" in item:
                ln = dict(item)
                ln.pop("pack", None)
                ln.pop("kind", None)
                ln.setdefault("name", "Линза")
                ln.setdefault("desc", "")
                ln.setdefault("current", 0)
                ln.setdefault("max", 12)
                ln.setdefault("show_on_panel", False)
                c.lenses.append(ln)
            else:
                messagebox.showinfo("Custom",
                                     "Тип элемента не определён. "
                                     "Добавь \"kind\": \"lens\" или "
                                     "используй другую папку.",
                                     parent=app.get_dialog_parent())
                return
        else:
            messagebox.showinfo("Пока",
                                 f"Папка '{sub}' пока не "
                                 f"поддерживает «Взять».",
                                 parent=app.get_dialog_parent())
            return
        app._refresh()
        rebuild()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e), parent=app.get_dialog_parent())

def _import_catalog_url(app, rebuild):
    """T57: импорт каталога по URL → в выбранную папку."""
    import urllib.request
    from tkinter import simpledialog as _sd

    url = _sd.askstring(
        "Импорт каталога по URL",
        "URL к JSON-файлу каталога:",
        parent=app.get_dialog_parent())
    if not url:
        return
    url = url.strip()
    if not (url.startswith("http://")
            or url.startswith("https://")):
        messagebox.showerror("Ошибка",
                              "URL должен начинаться с http:// "
                              "или https://",
                              parent=app.get_dialog_parent())
        return
    sub = _sd.askstring(
        "Куда сохранить?",
        f"Папка (одна из: {', '.join(CATALOG_SUBDIRS)}):",
        initialvalue="custom",
        parent=app.get_dialog_parent())
    if not sub:
        return
    sub = sub.strip()
    if sub not in CATALOG_SUBDIRS:
        messagebox.showerror("Ошибка",
                              f"Папка '{sub}' не существует. "
                              f"Допустимые: {', '.join(CATALOG_SUBDIRS)}",
                              parent=app.get_dialog_parent())
        return
    name = _sd.askstring(
        "Имя файла",
        "Имя файла (без .json):",
        initialvalue="imported_catalog",
        parent=app.get_dialog_parent())
    if not name:
        return
    name = name.strip().replace(".json", "")
    if not name:
        return
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "WiPeFinder/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8")
        parsed = json.loads(data)
        if not isinstance(parsed, dict):
            messagebox.showerror("Ошибка",
                                  "JSON не является объектом",
                                  parent=app.get_dialog_parent())
            return
        folder = os.path.join(CATALOGS_DIR, sub)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{name}.json")
        if os.path.exists(path):
            if not messagebox.askyesno("Файл есть",
                                         f"{name}.json уже есть. "
                                         f"Заменить?",
                                         parent=app.get_dialog_parent()):
                return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        load_catalogs()
        rebuild()
        messagebox.showinfo("Импорт",
                             f"Сохранено: {sub}/{name}.json",
                             parent=app.get_dialog_parent())
    except urllib.error.URLError as e:
        messagebox.showerror("Ошибка сети", str(e),
                              parent=app.get_dialog_parent())
    except json.JSONDecodeError as e:
        messagebox.showerror("Ошибка JSON", str(e),
                              parent=app.get_dialog_parent())
    except Exception as e:
        messagebox.showerror("Ошибка", str(e),
                              parent=app.get_dialog_parent())



def _new_catalog(app, sub, rebuild):
    name = simpledialog.askstring(
        "Новый каталог",
        f"Имя файла для {sub}/ (без .json):",
        parent=app.get_dialog_parent())
    if not name:
        return
    name = name.strip()
    if not name:
        return
    folder = os.path.join(CATALOGS_DIR, sub)
    path = os.path.join(folder, f"{name}.json")
    if os.path.exists(path):
        messagebox.showwarning("Файл есть",
                                f"{name}.json уже существует",
                                parent=app.get_dialog_parent())
        return
    # Шаблон по типу папки
    if sub == "weapons":
        data = {"groups": []}
    else:
        data = {"items": []}
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        load_catalogs()
        rebuild()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e), parent=app.get_dialog_parent())


def _edit_catalog_file(app, sub, fname, rebuild):
    folder = os.path.join(CATALOGS_DIR, sub)
    path = os.path.join(folder, fname)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e), parent=app.get_dialog_parent())
        return
    d = open_window(app, f"Редактор: {sub}/{fname}", 800, 700, mode="center")
    tk.Label(d, text=f"JSON: {sub}/{fname}",
             font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=6, pady=4)
    txt = tk.Text(d, font=("Consolas", 9), wrap="none")
    txt.pack(fill="both", expand=True, padx=6, pady=4)
    txt.insert("1.0", content)

    def save():
        try:
            data = json.loads(txt.get("1.0", "end"))
        except Exception as e:
            messagebox.showerror("JSON", f"Ошибка: {e}", parent=d)
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            load_catalogs()
            rebuild()
            d.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=d)

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=6, padx=6)
    tk.Button(bf, text="Сохранить", command=save,
              bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(bf, text="Отмена", command=d.destroy
              ).pack(side="right")


def _delete_catalog_file(app, sub, fname, rebuild):
    if not messagebox.askyesno("Удалить",
                                 f"Удалить {sub}/{fname}?",
                                 parent=app.get_dialog_parent()):
        return
    folder = os.path.join(CATALOGS_DIR, sub)
    path = os.path.join(folder, fname)
    try:
        os.remove(path)
        load_catalogs()
        rebuild()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e), parent=app.get_dialog_parent())