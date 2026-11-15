# pdf_export.py — экспорт в PDF (v7)
# v7: Нагрузка, Деньги, Снаряжение (надето), База, Сумка, Разгрузка;
#     атаки с бонусами от предметов (attack_crit, attack_damage_bonus)

import os
from fpdf.enums import XPos, YPos
from fpdf import FPDF

from character import (BASE_DIR, EXPORTS_DIR, WEAPON_LEVELS,
                       SOURCE_NAMES, SKILL_TIER_NAMES,
                       ARMOR_DISPLAY, SHIELD_DISPLAY, PAIN_MAX,
                       EQUIP_SLOTS, SLOT_NAMES, LOCATION_NAMES)


# T-P2: единый словарь — из gui_alphabet.
from gui_alphabet import CATEGORY_NAMES


# ============ Цвета ============
C_DARK = (60, 20, 20)
C_HEADER_BG = (180, 30, 30)
C_LIGHT_BG = (245, 235, 230)
C_BORDER = (140, 100, 100)
C_TEXT = (30, 30, 30)
C_MUTED = (110, 110, 110)
C_GREEN = (20, 120, 40)
C_RED = (170, 30, 30)


def _find_font(names):
    """Ищет файл шрифта в нескольких местах."""
    candidates = []
    for n in names:
        candidates.extend([
            os.path.join(BASE_DIR, "assets", "fonts", n),
            os.path.join(r"C:\Windows\Fonts", n),
            os.path.join(r"C:\WINNT\Fonts", n),
            os.path.join("/usr/share/fonts/truetype/dejavu", n),
            os.path.join("/usr/share/fonts/truetype/liberation", n),
            os.path.join("/usr/share/fonts/truetype/msttcorefonts", n),
            os.path.join("/Library/Fonts", n),
            os.path.join("/System/Library/Fonts", n),
        ])
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


REGULAR = _find_font([
    "DejaVuSans.ttf", "arial.ttf", "Arial.ttf",
    "LiberationSans-Regular.ttf", "times.ttf", "Times.ttf",
    "calibri.ttf", "tahoma.ttf",
])
BOLD = _find_font([
    "DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf",
    "arialbd.ttf", "LiberationSans-Bold.ttf",
    "timesbd.ttf", "calibrib.ttf", "tahomabd.ttf",
])


class CharPDF(FPDF):
    def __init__(self, char):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.char = char
        self.set_auto_page_break(auto=True, margin=12)
        self.set_margins(left=10, top=10, right=10)

        if not REGULAR:
            raise RuntimeError(
                "Не найден шрифт для PDF.\n"
                "Положите DejaVuSans.ttf или arial.ttf в "
                f"{os.path.join(BASE_DIR, 'assets', 'fonts')}\n"
                "Или установите один из:\n"
                "- DejaVu Sans (обычно есть на Linux)\n"
                "- Arial (есть на Windows)\n"
                "- Liberation Sans\n\n"
                f"BASE_DIR = {BASE_DIR}\n"
                f"C:\\Windows\\Fonts существует: "
                f"{os.path.isdir(r'C:\Windows\Fonts')}")

        self.add_font("Main", "", REGULAR)
        if BOLD:
            self.add_font("Main", "B", BOLD)
        else:
            self.add_font("Main", "B", REGULAR)

        self.set_font("Main", "", 9)

    def _safe(self, text):
        if text is None:
            return ""
        s = str(text)
        replacements = {
            "⏱": "T:", "⚡": "Z:", "⭐": "*",
            "★": "*", "☆": "-", "•": "-",
            "🩹": "", "🛡": "", "✨": "", "📖": "",
            "😌": "", "🎲": "", "💀": "(X)",
            "→": "->", "←": "<-", "×": "x",
            "✓": "+", "✗": "-",
            "🛌": "", "🛏": "", "💤": "",
            "⚔": "*", "🎒": "", "🏠": "", "⏳": "",
        }
        for k, v in replacements.items():
            s = s.replace(k, v)
        return s

    def section(self, title):
        self.ln(3)
        self.set_fill_color(*C_HEADER_BG)
        self.set_text_color(255, 255, 255)
        self.set_font("Main", "B", 10)
        self.cell(0, 6, "  " + self._safe(title),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.set_text_color(*C_TEXT)
        self.ln(1)

    def subhead(self, title):
        self.set_font("Main", "B", 9)
        self.set_text_color(*C_DARK)
        self.cell(0, 5, self._safe(title),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*C_TEXT)

    def body_line(self, text, indent=3):
        self.set_font("Main", "", 9)
        self.set_x(10 + indent)
        self.multi_cell(self.w - 20 - indent, 4.5,
                        self._safe(text))
        self.set_x(10)

    def kv(self, label, value, label_w=42, bold_val=False):
        self.set_font("Main", "B", 9)
        self.set_text_color(*C_MUTED)
        self.set_x(10)
        self.cell(label_w, 4.8, self._safe(label))
        self.set_text_color(*C_TEXT)
        if bold_val:
            self.set_font("Main", "B", 9)
        else:
            self.set_font("Main", "", 9)
        self.multi_cell(self.w - 10 - label_w, 4.8,
                        self._safe(value))
        self.set_x(10)

    def two_col(self, pairs, label_w=25):
        col_w = (self.w - 20) / 2
        self.set_font("Main", "", 9)
        self.set_x(10)
        for i, (k, v) in enumerate(pairs):
            self.set_font("Main", "B", 9)
            self.set_text_color(*C_MUTED)
            self.cell(label_w, 4.8, self._safe(k))
            self.set_font("Main", "", 9)
            self.set_text_color(*C_TEXT)
            self.cell(col_w - label_w, 4.8, self._safe(v))
            if i % 2 == 1:
                self.ln()
        if len(pairs) % 2 == 1:
            self.ln()

    def bullet(self, text, indent=3):
        self.set_font("Main", "", 9)
        self.set_x(10 + indent)
        self.cell(4, 4.5, "-")
        self.multi_cell(self.w - 20 - indent - 4, 4.5,
                        self._safe(text))
        self.set_x(10)

    def hint(self, text, indent=3):
        self.set_font("Main", "", 8)
        self.set_text_color(*C_MUTED)
        self.set_x(10 + indent)
        self.multi_cell(self.w - 20 - indent, 4,
                        self._safe(text))
        self.set_text_color(*C_TEXT)
        self.set_x(10)


def export_pdf(char, path=None):
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    if path is None:
        safe = "".join(c for c in char.name
                        if c.isalnum() or c in " _-").strip() \
               or "character"
        path = os.path.join(EXPORTS_DIR, f"{safe}.pdf")

    pdf = CharPDF(char)
    pdf.add_page()
    pdf.set_font("Main", "", 9)

    # ============ ШАПКА ============
    has_portrait = False
    portrait_data = char.portrait_b64 or char.portrait
    if portrait_data:
        img_path = None
        try:
            import base64 as _b64
            import tempfile as _tmp
            if os.path.exists(str(portrait_data)):
                img_path = portrait_data
            else:
                data = str(portrait_data)
                if "," in data:
                    data = data.split(",", 1)[1]
                raw = _b64.b64decode(data)
                suffix = ".png"
                if raw[:2] == b"\xff\xd8":
                    suffix = ".jpg"
                f = _tmp.NamedTemporaryFile(
                    suffix=suffix, delete=False)
                f.write(raw)
                f.close()
                img_path = f.name
            pdf.image(img_path, x=10, y=10, w=35)
            has_portrait = True
            text_x = 50
        except Exception as e:
            print(f"[pdf portrait] {e}")
            text_x = 10
    else:
        text_x = 10

    pdf.set_xy(text_x, 12)
    pdf.set_font("Main", "B", 20)
    pdf.set_text_color(*C_DARK)
    pdf.cell(0, 8, pdf._safe(char.name),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*C_TEXT)

    cls_line = f"{char.char_class.get('name','')} {char.level}".strip()
    if char.race.get("name"):
        cls_line += f" — {char.race['name']}"
        if char.race.get("type"):
            cls_line += f" ({char.race['type']})"
    pdf.set_x(text_x)
    pdf.set_font("Main", "", 11)
    pdf.cell(0, 6, pdf._safe(cls_line),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(text_x)
    pdf.set_font("Main", "", 9)
    pdf.set_text_color(*C_MUTED)
    pdf.cell(0, 5,
             f"XP: {char.xp} / {char.xp_threshold}   |   "
             f"Тренировки: {char.training['available']}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*C_TEXT)

    if has_portrait:
        pdf.set_y(max(pdf.get_y(), 48))

    # ============ БОЕВЫЕ ============
    pdf.section("Боевые параметры")

    hp_line = f"{char.combat['hp_current']}/{char.hp_max_actual()}"
    temp = char.combat.get("hp_temp", 0)
    if temp > 0:
        hp_line += f"  (+{temp} temp)"

    ac_full = char.ac_full()
    ac_touch = char.ac_touch()
    ac_flat = char.ac_flat()
    ac_parry = char.ac_parry()
    pain = char.pain_level()
    pain_max = getattr(char, "pain_max", PAIN_MAX)
    mb = char.morale_bonus()
    sit_d20 = char.situational_bonus("attack")
    pen_total = char.pain_penalty() + mb + sit_d20
    dmg_mod = char.damage_modifier()

    pdf.two_col([
        ("HP", hp_line),
        ("AC", f"{ac_full}  (touch {ac_touch}, flat {ac_flat})"),
        ("Парирование", f"{char.total_parrying()}  "
                         f"(AC parry {ac_parry})"),
        ("ББА", f"{char.bab_base():+d}"),
        ("CMB", f"{char.cmb_total():+d}"),
        ("CMD", f"{char.cmd_total()}"),
        ("БП", f"{char.pain_threshold['current']}/"
                f"{char.pain_threshold['max']}"),
        ("Баланс", f"{char.balance['current']}/"
                    f"{char.balance['max']}"),
        ("Дух", f"{char.spirit['current']}/"
                 f"{char.spirit['max']}"),
        ("Реакции", char.reactions),
        ("Размер", char.combat.get("size", "Medium")),
        ("Скорость", f"{char.speed_total()} фт"),
    ])

    pdf.kv("Штраф d20",
            f"{pen_total:+d}  (боль {char.pain_penalty():+d}, "
            f"мораль {mb:+d}"
            + (f", сит {sit_d20:+d}" if sit_d20 else "") + ")")
    pdf.kv("Мод. урона", f"{dmg_mod:+d}")

    pain_breakdown = []
    if char.pain_from_hp():
        pain_breakdown.append(f"HP {char.pain_from_hp()}")
    if char.pain_extra:
        pain_breakdown.append(f"доп {char.pain_extra}")
    if char.pain_extra_temp:
        pain_breakdown.append(f"врем {char.pain_extra_temp}")
    pain_txt = f"{pain}/{pain_max}"
    if pain_breakdown:
        pain_txt += f"  ({', '.join(pain_breakdown)})"
    if char.ignore_pain:
        pain_txt += "  [игнор]"
    if pain >= pain_max:
        pain_txt += "  СМЕРТЬ"
    pdf.kv("Боль", pain_txt)

    morale_note = ""
    if char.ignore_negative_morale and char.morale < 0:
        morale_note = "  [игнор]"
    pdf.kv("Мораль", f"{char.morale}{morale_note}")

    if char.injury_points > 0:
        pdf.kv("ОТ", char.injury_points)

    if char.mana.get("enabled") and char.mana["max"] > 0:
        parts = []
        for nm, val in char.mana_detail():
            parts.append(f"{nm} {val}")
        detail = f"  ({', '.join(parts)})" if parts else ""
        pdf.kv("Мана",
                f"{char.mana['current']}/{char.mana['max']}{detail}")

    # ============ НАГРУЗКА ============
    total_L = char.total_weight_L()
    light_max = char.max_weight_light()
    loaded_max = char.max_weight_loaded()
    ws = char.weight_status()
    status_ru = {"light": "легко",
                 "loaded": "нагружен",
                 "over": "ПЕРЕГРУЗ"}[ws]
    pdf.kv("Вес",
            f"{char.total_weight_display()}  "
            f"(light <={light_max}L / loaded <={loaded_max}L)  "
            f"— {status_ru}")
    unload_cap = char.unload_capacity_L()
    unload_used = sum(char._item_weight_L(it)
                       for it in char.items_by_location("unload"))
    pdf.kv("Разгрузка",
            f"{round(unload_used, 1)}/{unload_cap}L")

    # ============ ДЕНЬГИ ============
    dt = char.downtime
    g_name = dt["gold"].get("name", "Золото")
    g_val = dt["gold"].get("amount", 0)
    s_name = dt["silver"].get("name", "Серебро")
    s_val = dt["silver"].get("amount", 0)
    c_name = dt["copper"].get("name", "Медь")
    c_val = dt["copper"].get("amount", 0)
    r1 = dt["rates"].get("gold_to_silver", 100)
    r2 = dt["rates"].get("silver_to_copper", 100)
    total_gold = (g_val * r1 * r2 + s_val * r2 + c_val) / (r1 * r2)
    pdf.kv("Деньги",
            f"{g_val} {g_name}, {s_val} {s_name}, "
            f"{c_val} {c_name}  (≈ {total_gold:.2f} зол.)")

    # ============ ХАРАКТЕРИСТИКИ ============
    pdf.section("Характеристики")
    pairs = []
    for ab, full in [("str", "СИЛ"), ("dex", "ЛОВ"),
                      ("con", "ТЕЛ"), ("int", "ИНТ"),
                      ("wis", "МДР"), ("cha", "ХАР")]:
        base = char.abilities[ab]
        dmg = char.ability_damage.get(ab, 0)
        eff = char.effective_ability(ab)
        sit = char.situational_bonus(ab)
        mod = char.ability_modifier(ab)
        txt = f"{eff}"
        if dmg > 0:
            txt += f"/{base} (урон {dmg})"
        if sit:
            txt += f" баф {sit:+d}"
        txt += f" ({mod:+d})"
        pairs.append((full, txt))
    pdf.two_col(pairs, label_w=18)

    # ============ СПАСБРОСКИ ============
    pdf.section("Спасброски")
    for key, name in [("fort", "Fort (ТЕЛ)"),
                       ("ref", "Ref (ЛОВ)"),
                       ("will", "Will (МДР)")]:
        b = char.save_breakdown(key)
        good = "хор." if key in char.char_class.get("good_saves", []) \
               else "плох."
        parts = [f"класс {b['auto']:+d}",
                 f"{b['ability_stat']} {b['ability']:+d}"]
        for m in b["mods"]:
            parts.append(f"{m.get('source','?')} {m['value']:+d}")
        if b.get("penalty"):
            parts.append(f"боль/мор {b['penalty']:+d}")
        pdf.kv(name, f"{b['total']:+d}  [{good}; {', '.join(parts)}]",
               label_w=30, bold_val=True)

    # ============ БАФЫ ============
    if char.situational_bonuses:
        pdf.section("Активные бафы")
        for b in char.situational_bonuses:
            eff_parts = []
            for e in b.get("effects", []):
                t = e.get("target", "all")
                v = e.get("value", 0)
                if t == "speed_mult":
                    eff_parts.append(f"x{v/100:.2f}")
                elif t == "speed":
                    eff_parts.append(f"{v:+d} фт")
                else:
                    eff_parts.append(f"{v:+d} {t.upper()}")
            eff_txt = ", ".join(eff_parts)
            tags = []
            if b.get("duration_rounds", 0) > 0:
                tags.append(f"T:{b.get('duration_current', 0)}/"
                            f"{b['duration_rounds']}р")
            if b.get("charges_max", 0) > 0:
                tags.append(f"Z:{b.get('charges_current', 0)}/"
                            f"{b['charges_max']}")
            tag_str = f"  [{' '.join(tags)}]" if tags else ""
            pdf.bullet(f"{b.get('name','?')}: {eff_txt}{tag_str}")
            if b.get("desc"):
                pdf.hint(b["desc"], indent=7)

    # ============ ТРАВМЫ ============
    if char.injuries:
        pdf.section(f"Травмы (ОТ: {char.injury_points})")
        sev_ru = {"light": "лёгкая", "medium": "средняя",
                  "heavy": "тяжёлая", "custom": "своя"}
        for inj in char.injuries:
            sev = sev_ru.get(inj.get("severity", "custom"), "?")
            rl = inj.get("heal_rating", 1)
            uses = ""
            if inj.get("uses") and inj.get("uses_max", 0) > 0:
                uses = (f"  [{inj.get('uses_current', 0)}/"
                        f"{inj['uses_max']}]")
            pdf.subhead(f"- {inj.get('name', 'Травма')} "
                        f"({sev}, РЛ {rl}){uses}")
            if inj.get("desc"):
                pdf.hint(inj["desc"], indent=5)

    # ============ РАСА ============
    if char.race.get("name"):
        pdf.section(f"Раса: {char.race['name']}")
        if char.race.get("speed"):
            pdf.kv("Скорость", f"{char.race['speed']} фт")
        for a in char.race.get("abilities", []):
            name = a.get("name", "?")
            desc = a.get("desc", "")
            if desc:
                pdf.subhead(f"- {name}")
                pdf.hint(desc, indent=5)
            else:
                pdf.bullet(name)

    # ============ КЛАСС ============
    if char.char_class.get("name"):
        pdf.section(f"Класс: {char.char_class['name']}")
        if char.char_class.get("has_spellbook"):
            pdf.bullet("Книга заклинаний (скидка x2)")
        for a in char.char_class.get("abilities", []):
            name = a.get("name", "?")
            desc = a.get("desc", "")
            uses = ""
            if a.get("uses"):
                uses = (f" [{a.get('uses_current', 0)}/"
                        f"{a.get('uses_max', 0)}]")
            if desc:
                pdf.subhead(f"- {name}{uses}")
                pdf.hint(desc, indent=5)
            else:
                pdf.bullet(f"{name}{uses}")

    # ============ ЧЕРТЫ ============
    if char.feats:
        pdf.section("Черты")
        for f in char.feats:
            src = SOURCE_NAMES.get(f.get("source", ""), "?")
            pdf.subhead(f"- {f['name']}  [{src}]")
            if f.get("desc"):
                pdf.hint(f["desc"], indent=5)

    # ============ КВИРКИ ============
    if char.quirks:
        pdf.section("Квирки")
        for q in char.quirks:
            parts = [q.get("seed",""), q.get("court",""),
                     q.get("focus","")]
            parts = [p for p in parts if p]
            prefix = f"[{'/'.join(parts)}] " if parts else ""
            pdf.subhead(f"- {prefix}{q.get('name','?')}")
            if q.get("desc"):
                pdf.hint(q["desc"], indent=5)

    # ============ ШАБЛОНЫ ============
    if char.templates:
        pdf.section("Шаблоны")
        for t in char.templates:
            type_tag = (f"[{t.get('type', '')}] "
                        if t.get("type") else "")
            pdf.subhead(f"- {type_tag}{t.get('name', '?')}")
            if t.get("desc"):
                pdf.hint(t["desc"], indent=5)

    # ============ АТАКИ ============
    if char.attacks:
        pdf.section("Атаки")
        for a in char.attacks:
            bonus = char.attack_bonus(a)
            ct, cm = char.attack_crit(a)
            crit = f"{ct}+ x{cm}"
            dmg = a.get("damage_dice", "") or "-"
            dmg_b = char.attack_damage_bonus(a)
            if dmg_b:
                dmg_disp = f"{dmg} ({dmg_b:+d})"
            else:
                dmg_disp = dmg
            maneuver = " [прием]" if a.get("is_maneuver") else ""
            item_tag = ""
            iid = a.get("from_item")
            if iid:
                it = char.items.get(iid)
                if it:
                    item_tag = f" [* {it.get('name','?')[:20]}]"
            pdf.subhead(f"- {a['name']}{maneuver}{item_tag}")
            pdf.kv("Атака", f"{bonus:+d}", label_w=20)
            pdf.kv("Урон", dmg_disp, label_w=20)
            pdf.kv("Крит", crit, label_w=20)
            if a.get("desc"):
                pdf.hint(a["desc"], indent=5)

    # ============ СНАРЯЖЕНИЕ (КУКЛА) ============
    equipped = char.items_by_location("equipped")
    if equipped:
        pdf.section("Снаряжение (надето)")
        by_slot = {}
        for it in equipped:
            slot = it.get("slot") or "?"
            by_slot.setdefault(slot, []).append(it)
        for slot in EQUIP_SLOTS:
            if slot not in by_slot:
                continue
            slot_name = SLOT_NAMES.get(slot, slot)
            for it in by_slot[slot]:
                parts = [it.get("name", "?")]
                cat = CATEGORY_NAMES.get(it.get("category"),
                                          it.get("category", "?"))
                parts.append(f"[{cat}]")
                if it.get("armor_type"):
                    parts.append(it["armor_type"])
                if it.get("ac_bonus"):
                    parts.append(f"AC +{it['ac_bonus']}")
                if it.get("damage"):
                    parts.append(f"урон {it['damage']}")
                if it.get("hp", 0) > 0 or it.get("max_hp", 0) > 0:
                    parts.append(f"HP {it.get('hp', 0)}/"
                                  f"{it.get('max_hp', 0)}")
                if it.get("hardness", 0) > 0:
                    parts.append(f"HRD {it['hardness']}")
                if it.get("uses") and it.get("uses_max", 0) > 0:
                    parts.append(f"заряды "
                                  f"{it.get('uses_current', 0)}/"
                                  f"{it['uses_max']}")
                if it.get("activated"):
                    parts.append("акт.")
                pdf.subhead(f"- {slot_name}")
                pdf.hint("  " + " * ".join(parts), indent=5)
                if it.get("passive_bonuses") or \
                        it.get("activation_effects"):
                    bon_parts = []
                    for b in it.get("passive_bonuses", []):
                        bon_parts.append(
                            f"{b.get('target')} "
                            f"{b.get('value'):+d}")
                    for b in it.get("activation_effects", []):
                        bon_parts.append(
                            f"акт. {b.get('target')} "
                            f"{b.get('value'):+d}")
                    if bon_parts:
                        pdf.hint("  Бонусы: "
                                  + ", ".join(bon_parts),
                                  indent=5)
                if it.get("desc"):
                    pdf.hint(it["desc"], indent=5)

    # ============ НАВЫКИ ============
    if char.skills:
        pdf.section("Навыки")
        pairs = []
        for s in char.skills:
            tier = {"normal": "об.", "advanced": "прод.",
                    "specialized": "спец."}.get(
                        s.get("tier", "normal"), "")
            bonus = char.skill_bonus(s)
            stat = s.get("stat", "int").upper()
            pairs.append((s["name"],
                          f"{bonus:+d}  [{stat} {tier}, "
                          f"р{s.get('rank', 0)}]"))
        pdf.two_col(pairs, label_w=55)

    # ============ ОРУЖИЕ (ВЛАДЕНИЕ) ============
    if char.proficiencies.get("weapons"):
        pdf.section("Оружие (владение)")
        for w in char.proficiencies["weapons"]:
            lvl = WEAPON_LEVELS[w["level"]]
            basics = " [основы]" if w.get("basics") else ""
            line = f"{w['name']}: {lvl}{basics} " \
                   f"(сложн. {w['difficulty']}, " \
                   f"масштаб {w['scale']})"
            if w.get("desc"):
                line += f" - {w['desc']}"
            pdf.bullet(line)

    # ============ ВЛАДЕНИЯ ============
    pdf.section("Владения (броня/щит)")
    pdf.two_col([
        ("Броня", ARMOR_DISPLAY.get(
            char.proficiencies.get("armor"), "?")),
        ("Щит", SHIELD_DISPLAY.get(
            char.proficiencies.get("shields"), "?")),
    ], label_w=20)

    # ============ СЛОТЫ ============
    if char.spell_slots_enabled and char.spell_slots:
        pdf.section("Слоты заклинаний")
        pairs = []
        for lvl in sorted(char.spell_slots.keys(),
                           key=lambda x: int(x)):
            s = char.spell_slots[lvl]
            pairs.append((f"Круг {lvl}",
                          f"{s['current']}/{s['max']}"))
        pdf.two_col(pairs, label_w=25)

    # ============ ЗАКЛИНАНИЯ ============
    if char.spells:
        pdf.section("Заклинания")
        by_circle = {}
        for s in char.spells:
            by_circle.setdefault(s["circle"], []).append(s)
        for circle in sorted(by_circle.keys()):
            pdf.subhead(f"Круг {circle}")
            for s in by_circle[circle]:
                mast = ""
                masteries = s.get("masteries", [])
                if masteries:
                    stars = sum(m.get("stars", 1)
                                for m in masteries)
                    mast = f"  [маст. {stars}/3]"
                pdf.bullet(f"{s['name']}{mast}")
                for m in masteries:
                    stars_str = "*" * m.get("stars", 1)
                    extra = ""
                    if m.get("desc"):
                        extra = f" - {m['desc']}"
                    pdf.hint(f"{stars_str} {m.get('name','?')}{extra}",
                             indent=8)

    # ============ ЯЗЫКИ ============
    if char.languages:
        pdf.section("Языки")
        langs = [l['name'] + (" (родной)" if l.get("native") else "")
                 for l in char.languages]
        pdf.body_line(", ".join(langs))

    # ============ БАЗА ============
    base_items = char.items_by_location("base")
    if base_items:
        used = sum((it.get("base_slots", 1) or 1)
                    for it in base_items)
        max_slots = char.base.get("slots_max", 5)
        pdf.section(f"База ({used}/{max_slots} слотов)")
        for it in base_items:
            cat = CATEGORY_NAMES.get(it.get("category"),
                                      it.get("category", "?"))
            tags = [cat]
            if it.get("gray"):
                tags.append("серая")
            tags.append(f"слотов: {it.get('base_slots', 1)}")
            pdf.bullet(f"{it.get('name','?')}  "
                       f"[{' * '.join(tags)}]")
            if it.get("desc"):
                pdf.hint(it["desc"], indent=7)

    # ============ СУМКА ============
    bag_items = char.items_by_location("bag")
    if bag_items:
        bag_tag = " (выброшена)" if char.bag_dropped else ""
        pdf.section(f"Сумка{bag_tag}")
        for it in bag_items:
            cat = CATEGORY_NAMES.get(it.get("category"),
                                      it.get("category", "?"))
            qty = it.get("qty", 1)
            qty_tag = f" x{qty}" if qty > 1 else ""
            w = char._item_weight_L(it)
            w_tag = f" — {round(w, 1)}L" if w > 0 else ""
            pdf.bullet(f"{it.get('name','?')}{qty_tag} "
                       f"[{cat}]{w_tag}")

    # ============ РАЗГРУЗКА ============
    unload_items = char.items_by_location("unload")
    if unload_items:
        cap = char.unload_capacity_L()
        pdf.section(f"Разгрузка (<={cap}L)")
        for it in unload_items:
            cat = CATEGORY_NAMES.get(it.get("category"),
                                      it.get("category", "?"))
            qty = it.get("qty", 1)
            qty_tag = f" x{qty}" if qty > 1 else ""
            w = char._item_weight_L(it)
            w_tag = f" — {round(w, 1)}L" if w > 0 else ""
            pdf.bullet(f"{it.get('name','?')}{qty_tag} "
                       f"[{cat}]{w_tag}")

    # ============ ЗАМЕТКИ ============
    if char.notes:
        pdf.section("Заметки")
        pdf.body_line(char.notes)

    # ============ ПОДВАЛ ============
    pdf.ln(4)
    pdf.set_font("Main", "", 7)
    pdf.set_text_color(*C_MUTED)
    pdf.set_x(10)
    pdf.cell(pdf.w - 20, 4,
             "WiPeFinder - сгенерировано автоматически",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output(path)
    return path


if __name__ == "__main__":
    print(f"REGULAR: {REGULAR}")
    print(f"BOLD: {BOLD}")
    from character import Character, ensure_dirs
    ensure_dirs()
    c = Character("Тест Pathfinder")
    c.char_class = {"name": "Воин", "level": 5, "hp_die": 10,
                    "hp_rolls": [10, 7, 8, 6, 9], "abilities": [],
                    "has_spellbook": False, "spell_discount_extra": 0,
                    "bab_type": "good", "good_saves": ["fort"]}
    c.race = {"name": "Человек", "type": "гуманоид", "speed": 30,
              "abilities": [{"name": "Универсальность",
                              "desc": "+2 к одной характеристике"}]}
    c.abilities = {"str": 16, "dex": 14, "con": 12,
                   "int": 10, "wis": 12, "cha": 10}
    c.proficiencies["armor"] = "Medium"
    c.proficiencies["shields"] = "Tower"
    c.natural_armor = 1
    c.ac_bonus = 1
    c.pain_max = 10
    c.injury_points = 4
    c.injuries = [
        {"name": "Лёгкая травма", "severity": "light",
         "heal_rating": 3, "desc": "Ушиб плеча, -1 к атакам",
         "uses": False, "uses_max": 0, "uses_current": 0,
         "tick_on_initiative": False},
    ]
    c.init_defaults()
    c.downtime["gold"]["amount"] = 150
    c.downtime["silver"]["amount"] = 30
    c.downtime["copper"]["amount"] = 5

    # Броня
    armor = c.add_item(name="Кольчуга", category="armor",
                        location="equipped", slot="armor",
                        armor_type="Medium", ac_bonus=6,
                        ac_max_dex=2, weight=2.5, weight_type="mass",
                        desc="Средняя броня")
    # Оружие
    sword = c.add_item(name="Длинный меч", category="weapon",
                        location="equipped", slot="weapon_main",
                        damage="1d8", crit_threshold=19, crit_mult=2,
                        attack_bonus=2, damage_bonus=3,
                        weight=1.5, weight_type="mass",
                        weapon_group="Длинные клинки")
    # Атака из оружия
    try:
        c.attack_from_item(sword["id"], name="Длинный меч")
    except Exception:
        pass

    # Сумка
    c.add_item(name="Зелье лечения", category="consumable",
                location="bag", qty=3, weight=0.1,
                weight_type="mass")
    # База
    c.add_item(name="Сундук", category="misc",
                location="base", base_slots=2,
                weight=5, weight_type="mass")

    c.situational_bonuses = [{
        "name": "Ярость", "desc": "+4 STR, +2 урон",
        "duration_rounds": 5, "duration_current": 3,
        "charges_max": 0, "charges_current": 0,
        "tick_on_initiative": True,
        "effects": [{"target": "str", "value": 4},
                    {"target": "damage", "value": 2}],
    }]
    c.start_session()
    path = export_pdf(c, os.path.join(EXPORTS_DIR, "test.pdf"))
    print(f"PDF создан: {path}")