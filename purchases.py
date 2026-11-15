# purchases.py — движок покупок v5.3
# v5.3: set_weapon_bonuses с правилом «1 раз за ступень»,
#       add_weapon использует поле bonuses (а не устаревшие
#       specialist_bonuses/expert_bonuses/master_bonuses)

from character import (Character, WEAPON_LEVELS, ARMOR_LEVELS,
                       SHIELD_LEVELS, SOURCE_ICONS, SOURCE_NAMES,
                       SKILL_TIERS, SKILL_TIER_NAMES,
                       INJURY_SEVERITIES,
                       WEAPON_BONUS_CATALOG, WEAPON_BONUS_SLOTS,
                       allowed_bonus_types_for_slot)


class PurchaseError(Exception):
    pass


def _pay(c, cost, desc, kind, source="training"):
    actual = 0
    if cost > 0:
        if cost > c.training["available"]:
            raise PurchaseError(
                f"Не хватает: нужно {cost}, есть "
                f"{c.training['available']}")
        c.training["available"] -= cost
        c.training["spent"] += cost
        actual = cost
    c.training["purchases"].append({
        "type": kind, "desc": desc, "cost": actual, "source": source})
    return actual


def _refund(c, amount):
    c.training["available"] += amount
    c.training["spent"] = max(0, c.training["spent"] - amount)


def add_training_points(c, n):
    c.training["available"] += n
    if c.training["available"] < 0:
        c.training["available"] = 0


def set_comfort(c, new_value):
    c.comfort["current"] = max(0, int(new_value))
    return c.comfort["current"]


# ============ Черты / Характеристики ============

def buy_feat(c, name, desc="", cost=200, source="training", link=""):
    if source == "training" and cost < 200:
        raise PurchaseError("Черта не может стоить меньше 200")
    invested = _pay(c, cost, f"Черта: {name}", "feat", source)
    if invested == 0 and cost > 0:
        invested = cost
    c.feats.append({"name": name, "desc": desc, "link": link,
                    "source": source, "invested": invested})


def remove_feat(c, index, return_points=False):
    f = c.feats.pop(index)
    if return_points and f.get("invested", 0) > 0:
        _refund(c, f["invested"])
        return f["invested"]
    return 0


def ability_up_cost(c, ab):
    new_mod = (c.abilities[ab] + 1 - 10) // 2
    return 150 * max(1, new_mod)


def ability_up_cost_total(c, ab, target):
    if target <= c.abilities[ab]:
        return 0
    total = 0
    cur = c.abilities[ab]
    for _ in range(target - cur):
        cur += 1
        new_mod = (cur - 10) // 2
        total += 150 * max(1, new_mod)
    return total


def buy_ability_up(c, ab, source="training"):
    cost = ability_up_cost(c, ab)
    _pay(c, cost, f"{ab.upper()} → {c.abilities[ab] + 1}",
         "ability", source)
    c.abilities[ab] += 1
    c.recompute_derived()
    return cost


def buy_ability_up_to(c, ab, target, source="training"):
    if target <= c.abilities[ab]:
        return 0
    cost = ability_up_cost_total(c, ab, target)
    _pay(c, cost, f"{ab.upper()} → {target}", "ability", source)
    c.abilities[ab] = target
    c.recompute_derived()
    return cost


def remove_ability_up(c, ab, return_points=False):
    if c.abilities[ab] <= 1:
        raise PurchaseError(f"{ab.upper()} уже на минимуме")
    old_mod = max(1, (c.abilities[ab] - 10) // 2)
    refund = 150 * old_mod if return_points else 0
    c.abilities[ab] -= 1
    if refund > 0:
        _refund(c, refund)
    c.recompute_derived()
    return refund


# ============ Реакции / HP / Броня ============

def reaction_up_cost(c):
    return 200 * (c.reactions + 1)


def buy_reaction_up(c, source="training"):
    cost = reaction_up_cost(c)
    actual = _pay(c, cost, f"Реакция → {c.reactions + 1}",
                  "reaction", source)
    c.reactions += 1
    c.reactions_invested += actual
    return actual


def remove_reaction(c, return_points=False):
    if c.reactions <= 1:
        raise PurchaseError("Нельзя удалить базовую реакцию")
    refund = c.reactions_invested if return_points else 0
    if refund:
        _refund(c, refund)
    c.reactions -= 1
    c.reactions_invested = 0
    return refund


def hp_up_cost(c, n=1):
    return 50 * n


def hp_up_available(c):
    return max(0, c.hp_max_cap() - c.hp_max_actual())


def buy_hp_up(c, n=1, source="training"):
    cap = c.hp_max_cap()
    if c.hp_max_actual() + n > cap:
        raise PurchaseError(
            f"HP не больше капа ({cap}). "
            f"Можно ещё {cap - c.hp_max_actual()}")
    cost = 50 * n
    _pay(c, cost, f"HP +{n}", "hp", source)
    c.combat["hp_bought"] += n
    c.combat["hp_current"] += n
    c.recompute_derived()
    return cost


def remove_hp(c, n=1, return_points=False):
    if c.combat["hp_bought"] < n:
        raise PurchaseError(
            f"Докуплено только {c.combat['hp_bought']} HP")
    refund = 50 * n if return_points else 0
    if refund:
        _refund(c, refund)
    c.combat["hp_bought"] -= n
    c.combat["hp_current"] = max(0, c.combat["hp_current"] - n)
    c.recompute_derived()
    return refund


def armor_next_grade(c):
    idx = ARMOR_LEVELS.index(c.proficiencies["armor"])
    return None if idx >= len(ARMOR_LEVELS) - 1 else ARMOR_LEVELS[idx + 1]


def buy_armor_grade(c, source="training"):
    nxt = armor_next_grade(c)
    if not nxt:
        raise PurchaseError("Уже максимум")
    actual = _pay(c, 250, f"Броня → {nxt}", "armor", source)
    c.proficiencies["armor"] = nxt
    c.armor_invested += actual
    c.recompute_derived()
    return actual


def remove_armor(c, return_points=False):
    idx = ARMOR_LEVELS.index(c.proficiencies["armor"])
    if idx <= 0:
        raise PurchaseError("Уже нет владения")
    refund = 0
    if return_points and c.armor_invested > 0:
        refund = min(250, c.armor_invested)
        _refund(c, refund)
        c.armor_invested -= refund
    c.proficiencies["armor"] = ARMOR_LEVELS[idx - 1]
    c.recompute_derived()
    return refund


def shield_next_grade(c):
    idx = SHIELD_LEVELS.index(c.proficiencies["shields"])
    return (None if idx >= len(SHIELD_LEVELS) - 1
            else SHIELD_LEVELS[idx + 1])


def buy_shield_grade(c, source="training"):
    nxt = shield_next_grade(c)
    if not nxt:
        raise PurchaseError("Уже максимум")
    actual = _pay(c, 100, f"Щит → {nxt}", "shield", source)
    c.proficiencies["shields"] = nxt
    c.shield_invested += actual
    c.recompute_derived()
    return actual


def remove_shield(c, return_points=False):
    idx = SHIELD_LEVELS.index(c.proficiencies["shields"])
    if idx <= 0:
        raise PurchaseError("Уже нет владения")
    refund = 0
    if return_points and c.shield_invested > 0:
        refund = min(100, c.shield_invested)
        _refund(c, refund)
        c.shield_invested -= refund
    c.proficiencies["shields"] = SHIELD_LEVELS[idx - 1]
    c.recompute_derived()
    return refund


# ============ НАВЫКИ ============

TIERS_ORDER = {"normal": 0, "advanced": 1, "specialized": 2}


def find_skill(c, name):
    for s in c.skills:
        if s["name"] == name:
            return s
    return None


def skill_promote_cost(c, name):
    other = sum(1 for s in c.skills
                if s.get("tier") in ("advanced", "specialized")
                and s["name"] != name)
    return 40 + 20 * other


def skill_spec_cost(c, name):
    other = sum(1 for s in c.skills
                if s.get("tier") == "specialized"
                and s["name"] != name)
    return 200 + 50 * other


def skill_tier_transition_cost(c, name, to_tier):
    skill = find_skill(c, name)
    if not skill:
        raise PurchaseError(f"Навык {name} не найден")
    from_tier = skill.get("tier", "normal")
    if from_tier == to_tier:
        return 0, []
    total = 0
    details = []
    if TIERS_ORDER[to_tier] > TIERS_ORDER[from_tier]:
        cur = from_tier
        while cur != to_tier:
            if cur == "normal":
                st = skill_promote_cost(c, name)
                details.append(f"→прод: {st}")
                total += st
                cur = "advanced"
            elif cur == "advanced":
                st = skill_spec_cost(c, name)
                details.append(f"→спец: {st}")
                total += st
                cur = "specialized"
    else:
        cur = from_tier
        while cur != to_tier:
            if cur == "specialized":
                st = skill_spec_cost(c, name)
                details.append(f"спец→: -{st}")
                total -= st
                cur = "advanced"
            elif cur == "advanced":
                st = skill_promote_cost(c, name)
                details.append(f"прод→: -{st}")
                total -= st
                cur = "normal"
    return total, details


def skill_rank_step_cost(tier, new_rank, level):
    if tier == "normal":
        return 20 * new_rank
    if tier == "advanced":
        return 15 * new_rank
    if new_rank <= level:
        return 0
    return 10 * new_rank


def skill_rank_cost_to(c, name, new_rank, target_tier=None):
    skill = find_skill(c, name)
    if not skill:
        raise PurchaseError(f"Навык {name} не найден")
    old_rank = skill.get("rank", 0)
    if new_rank == old_rank:
        return 0, []
    old_tier = skill.get("tier", "normal")
    level = c.level
    total = 0
    details = []
    if new_rank > old_rank:
        tier = target_tier if target_tier else old_tier
        for r in range(old_rank + 1, new_rank + 1):
            st = skill_rank_step_cost(tier, r, level)
            total += st
            if st:
                details.append(f"р{r}: {st}")
    else:
        tier = old_tier
        for r in range(old_rank, new_rank, -1):
            st = skill_rank_step_cost(tier, r, level)
            total -= st
            if st:
                details.append(f"р{r}: -{st}")
    return total, details


def add_skill(c, name, stat="int", source="training"):
    if find_skill(c, name):
        raise PurchaseError(f"Навык {name} уже есть")
    if stat not in c.abilities:
        raise PurchaseError(f"Неизвестный стат: {stat}")
    c.skills.append({
        "name": name, "stat": stat, "tier": "normal",
        "rank": 0, "source": source, "invested": 0, "mods": [],
    })


def set_skill_stat(c, name, stat):
    skill = find_skill(c, name)
    if not skill:
        raise PurchaseError(f"Навык {name} не найден")
    if stat not in c.abilities:
        raise PurchaseError(f"Неизвестный стат: {stat}")
    skill["stat"] = stat


def apply_skill_changes(c, name, new_tier, new_rank, free=False,
                        source="training"):
    skill = find_skill(c, name)
    if not skill:
        raise PurchaseError(f"Навык {name} не найден")
    if new_tier not in SKILL_TIERS:
        raise PurchaseError(f"Неизвестный tier: {new_tier}")
    if new_rank < 0:
        raise PurchaseError("Ранг не может быть < 0")
    if new_tier in ("normal", "advanced") and new_rank > c.level:
        raise PurchaseError(
            f"Ранг {new_rank} выше уровня {c.level} "
            f"(разрешено только для спец)")

    tc, _ = skill_tier_transition_cost(c, name, new_tier)
    rc, _ = skill_rank_cost_to(c, name, new_rank,
                                target_tier=new_tier)
    total = tc + rc

    if not free:
        if total > 0:
            if total > c.training["available"]:
                raise PurchaseError(
                    f"Не хватает: нужно {total}, "
                    f"есть {c.training['available']}")
            c.training["available"] -= total
            c.training["spent"] += total
            skill["invested"] = skill.get("invested", 0) + total
        elif total < 0:
            refund = -total
            if refund > c.training["spent"]:
                refund = c.training["spent"]
            if refund > 0:
                c.training["available"] += refund
                c.training["spent"] -= refund
                skill["invested"] = max(
                    0, skill.get("invested", 0) - refund)

    skill["tier"] = new_tier
    skill["rank"] = new_rank
    if new_tier == "specialized":
        skill.setdefault("used_this_session", False)
    else:
        skill.pop("used_this_session", None)
    return total


def remove_skill(c, name, return_points=False):
    skill = find_skill(c, name)
    if not skill:
        raise PurchaseError(f"Навык {name} не найден")
    refund = 0
    if return_points and skill.get("invested", 0) > 0:
        refund = skill["invested"]
        _refund(c, refund)
    c.skills.remove(skill)
    return refund


# ============ Оружие / Атаки / База ============

def weapon_x(c, exclude_name=None):
    return sum(1 for w in c.proficiencies["weapons"]
               if w["name"] != exclude_name and w["level"] >= 8)


def weapon_x_groups(c, exclude_name=None):
    return [w["name"] for w in c.proficiencies["weapons"]
            if w["name"] != exclude_name and w["level"] >= 8]


def weapon_grade_up_cost(c, weapon_name):
    w = next((w for w in c.proficiencies["weapons"]
              if w["name"] == weapon_name), None)
    if not w:
        raise PurchaseError(f"Оружие {weapon_name} не найдено")
    x = weapon_x(c, exclude_name=weapon_name)
    return (30 + 5 * x) * w["difficulty"] * w["scale"]


def weapon_grade_up_cost_total(c, weapon_name, target):
    w = next((w for w in c.proficiencies["weapons"]
              if w["name"] == weapon_name), None)
    if not w:
        raise PurchaseError(f"Оружие {weapon_name} не найдено")
    if target <= w["level"]:
        return 0
    if target > 12:
        target = 12
    total = 0
    old_lvl = w["level"]
    for new_lvl in range(old_lvl + 1, target + 1):
        w["level"] = new_lvl - 1
        total += weapon_grade_up_cost(c, weapon_name)
    w["level"] = old_lvl
    return total


def add_weapon(c, name, difficulty=1, scale=1, level=0,
               source="training", desc=""):
    if any(w["name"] == name for w in c.proficiencies["weapons"]):
        raise PurchaseError(f"Оружие {name} уже есть")
    c.proficiencies["weapons"].append({
        "name": name, "level": level, "difficulty": difficulty,
        "scale": scale, "desc": desc,
        "bonuses": [],
        "source": source, "invested": 0})


def buy_weapon_grade_up(c, weapon_name, source="training"):
    w = next((w for w in c.proficiencies["weapons"]
              if w["name"] == weapon_name), None)
    if not w:
        raise PurchaseError(f"Оружие {weapon_name} не найдено")
    if w["level"] >= 12:
        raise PurchaseError("Уже Мастер (12)")
    cost = weapon_grade_up_cost(c, weapon_name)
    x = weapon_x(c, exclude_name=weapon_name)
    desc = (f"Оружие {weapon_name} → "
            f"{WEAPON_LEVELS[w['level']+1]} (X={x})")
    actual = _pay(c, cost, desc, "weapon", source)
    w["level"] += 1
    w["invested"] = w.get("invested", 0) + actual
    return actual


def remove_weapon_grade_up(c, weapon_name, return_points=False):
    w = next((w for w in c.proficiencies["weapons"]
              if w["name"] == weapon_name), None)
    if not w:
        raise PurchaseError(f"Оружие {weapon_name} не найдено")
    if w["level"] <= 0:
        raise PurchaseError(f"'{weapon_name}' уже на 0 уровне")
    refund = 0
    if return_points:
        x = weapon_x(c, exclude_name=weapon_name)
        cost = (30 + 5 * x) * w["difficulty"] * w["scale"]
        refund = min(cost, w.get("invested", 0))
        if refund > 0:
            _refund(c, refund)
            w["invested"] = w.get("invested", 0) - refund
    w["level"] -= 1
    return refund


def buy_weapon_grade_up_to(c, weapon_name, target, source="training"):
    w = next((w for w in c.proficiencies["weapons"]
              if w["name"] == weapon_name), None)
    if not w:
        raise PurchaseError(f"Оружие {weapon_name} не найдено")
    if target > 12:
        target = 12
    if target <= w["level"]:
        return 0
    cost = weapon_grade_up_cost_total(c, weapon_name, target)
    desc = (f"Оружие {weapon_name} → {WEAPON_LEVELS[target]}")
    actual = _pay(c, cost, desc, "weapon", source)
    w["level"] = target
    w["invested"] = w.get("invested", 0) + actual
    return actual


def remove_weapon(c, weapon_name, return_points=False):
    w = next((w for w in c.proficiencies["weapons"]
              if w["name"] == weapon_name), None)
    if not w:
        raise PurchaseError(f"Оружие {weapon_name} не найдено")
    refund = 0
    if return_points and w.get("invested", 0) > 0:
        refund = w["invested"]
        _refund(c, refund)
    c.proficiencies["weapons"].remove(w)
    return refund


def weapon_basics_cost(scale):
    return {1: 50, 2: 100, 3: 150}[scale]


def buy_weapon_basics(c, name, difficulty=1, scale=1,
                      source="training", desc=""):
    if any(f["name"] == f"Основы: {name}" for f in c.feats):
        raise PurchaseError(f"Основы для {name} уже куплены")
    cost = weapon_basics_cost(scale)
    actual = _pay(c, cost, f"Основы: {name} (масштаб {scale})",
                  "weapon_basics", source)
    bump = max(0, 5 - difficulty)
    existing = next((w for w in c.proficiencies["weapons"]
                     if w["name"] == name), None)
    if existing:
        old_level = existing["level"]
        new_level = min(12, old_level + bump)
        actual_bump = new_level - old_level
        existing["level"] = new_level
        existing["invested"] = existing.get("invested", 0) + actual
        existing["bump_applied"] = actual_bump
        existing["basics_invested"] = actual
        existing["basics"] = True
        if desc:
            existing["desc"] = desc
    else:
        start_level = min(12, bump)
        add_weapon(c, name, difficulty=difficulty, scale=scale,
                   level=start_level, source=source, desc=desc)
        w = c.proficiencies["weapons"][-1]
        w["invested"] = actual
        w["bump_applied"] = start_level
        w["basics_invested"] = actual
        w["basics"] = True
    c.feats.append({"name": f"Основы: {name}",
                    "desc": f"масштаб {scale}, +{bump} грейдов",
                    "link": "", "source": source,
                    "invested": actual})
    return actual


def remove_weapon_basics(c, weapon_name, return_points=False):
    w = next((w for w in c.proficiencies["weapons"]
              if w["name"] == weapon_name), None)
    if not w:
        raise PurchaseError(f"Оружие {weapon_name} не найдено")
    if not w.get("basics", False):
        raise PurchaseError(f"Основы для '{weapon_name}' не куплены")
    refund = 0
    if return_points:
        refund = w.get("basics_invested", 0)
        if refund > 0:
            _refund(c, refund)
            w["invested"] = max(0, w.get("invested", 0) - refund)
    bump = w.get("bump_applied", 0)
    w["level"] = max(0, w["level"] - bump)
    w["bump_applied"] = 0
    w["basics_invested"] = 0
    w["basics"] = False
    c.feats = [f for f in c.feats
               if f["name"] != f"Основы: {weapon_name}"]
    return refund


def add_attack(c, name, use_bab=True, stat="str", extra_bonus=0,
               manual_bonus=0, damage_dice="", crit_threshold=20,
               crit_mult=2, desc="", source="training",
               is_maneuver=False):
    c.attacks.append({
        "name": name, "use_bab": use_bab, "stat": stat,
        "extra_bonus": extra_bonus, "manual_bonus": manual_bonus,
        "damage_dice": damage_dice,
        "crit_threshold": crit_threshold,
        "crit_mult": crit_mult,
        "desc": desc, "source": source,
        "is_maneuver": is_maneuver})


def remove_attack(c, index):
    if 0 <= index < len(c.attacks):
        c.attacks.pop(index)


def buy_base_slot(c, source="training"):
    cap = 10 * c.level
    if c.base["slots_max"] >= cap:
        raise PurchaseError(f"База на максимуме ({cap})")
    actual = _pay(c, 100, f"Очко базы → {c.base['slots_max'] + 1}",
                  "base", source)
    c.base["slots_max"] += 1
    c.base_invested += actual
    return actual


def remove_base_slot(c, return_points=False):
    if c.base["slots_max"] <= 5:
        raise PurchaseError("Нельзя убрать базовые 5 слотов")
    refund = 0
    if return_points and c.base_invested > 0:
        refund = min(100, c.base_invested)
        _refund(c, refund)
        c.base_invested -= refund
    c.base["slots_max"] -= 1
    return refund


def buy_qualification(c, name, n, source="training"):
    cost = 50 * n
    label = f"Квалификация: {name} {n}"
    actual = _pay(c, cost, label, "qualification", source)
    c.feats.append({"name": label, "desc": "", "link": "",
                    "source": source, "invested": actual})
    return actual


# ============ Заклинания ============

def spell_cost(c, circle):
    cost = 20 + 10 * (circle ** 2)
    if c.char_class.get("has_spellbook"):
        cost //= 2
    cost -= c.char_class.get("spell_discount_extra", 0)
    return max(1, cost)


def buy_spell(c, name, circle, source="training", desc="", link=""):
    cost = spell_cost(c, circle)
    actual = _pay(c, cost, f"Заклинание: {name} (круг {circle})",
                  "spell", source)
    c.spells.append({"name": name, "circle": circle, "desc": desc,
                     "link": link, "mastery_level": 0,
                     "masteries": [], "mastery": False,
                     "source": source, "invested": actual})
    return actual


def remove_spell(c, spell_name, return_points=False):
    s = next((s for s in c.spells if s["name"] == spell_name), None)
    if not s:
        raise PurchaseError(f"Заклинание {spell_name} не найдено")
    refund = 0
    if return_points:
        total = s.get("invested", 0) + sum(
            m.get("invested", 0) for m in s.get("masteries", []))
        if total > 0:
            _refund(c, total)
            refund = total
    c.spells.remove(s)
    return refund


def spell_mastery_cost(circle):
    return 25 * (1 + circle ** 2)


def buy_spell_mastery(c, spell_name, mname="", mdesc="", stars=1,
                      free=False, source="training"):
    s = next((s for s in c.spells if s["name"] == spell_name), None)
    if not s:
        raise PurchaseError(f"Заклинание {spell_name} не найдено")
    if stars < 1 or stars > 3:
        raise PurchaseError("Стоимость в звёздах: 1-3")
    current = sum(m.get("stars", 1) for m in s.get("masteries", []))
    if current + stars > 3:
        raise PurchaseError(
            f"Не хватает слотов (занято {current}/3, "
            f"нужно {stars})")
    cost = spell_mastery_cost(s["circle"])
    src = source
    if free:
        src = source if source != "training" else "class"
    actual = _pay(c, cost,
                  f"Мастерство: {spell_name} → "
                  f"{mname or '(без названия)'}",
                  "spell_mastery", src)
    s.setdefault("masteries", []).append({
        "name": mname or "(без названия)", "desc": mdesc,
        "stars": stars, "invested": actual, "source": src})
    s["mastery_level"] = sum(
        m.get("stars", 1) for m in s["masteries"])
    s["mastery"] = True
    return actual


def remove_spell_mastery(c, spell_name, return_points=False):
    s = next((s for s in c.spells if s["name"] == spell_name), None)
    if not s:
        raise PurchaseError(f"Заклинание {spell_name} не найдено")
    masteries = s.get("masteries", [])
    if not masteries:
        raise PurchaseError(f"У '{spell_name}' нет мастерства")
    m = masteries.pop()
    refund = 0
    if return_points and m.get("invested", 0) > 0:
        refund = m["invested"]
        _refund(c, refund)
    s["mastery_level"] = sum(
        x.get("stars", 1) for x in masteries)
    s["mastery"] = s["mastery_level"] > 0
    return refund


# ============ Разное / Языки ============

def buy_professionalism(c, source="training"):
    return _pay(c, 300, "Профессионализм",
                "professionalism", source)


def buy_seed(c, source="training"):
    return _pay(c, 200, "Зерно", "seed", source)


def buy_sprout_seed(c, source="training"):
    return _pay(c, 200, "Прорастить зерно", "sprout", source)


def buy_attention_course(c, source="training"):
    return _pay(c, 200, "Курс трансформации внимания",
                "attention_course", source)


def language_cost(c, native=False):
    if not native:
        return 30
    native_count = sum(1 for l in c.languages if l["native"])
    return 50 if native_count < c.abilities["int"] else 100


def buy_language(c, name, native=False, source="training"):
    if any(l["name"] == name for l in c.languages):
        raise PurchaseError(f"Язык {name} уже есть")
    cost = language_cost(c, native=native)
    label = f"Язык: {name}{' (р)' if native else ''}"
    actual = _pay(c, cost, label, "language", source)
    c.languages.append({"name": name, "native": native,
                        "source": source, "invested": actual})
    return actual


def remove_language(c, name, return_points=False):
    l = next((l for l in c.languages if l["name"] == name), None)
    if not l:
        raise PurchaseError(f"Язык {name} не найден")
    refund = 0
    if return_points and l.get("invested", 0) > 0:
        refund = l["invested"]
        _refund(c, refund)
    c.languages.remove(l)
    return refund


def language_native_extra_cost(c):
    return max(0, language_cost(c, native=True)
               - language_cost(c, native=False))


def set_language_native(c, name, native, free=False):
    l = next((l for l in c.languages if l["name"] == name), None)
    if not l:
        raise PurchaseError(f"Язык {name} не найден")
    if l["native"] == native:
        raise PurchaseError("Уже так")
    if not free:
        diff = language_native_extra_cost(c)
        if native:
            if diff > c.training["available"]:
                raise PurchaseError(f"Не хватает: нужно {diff}")
            c.training["available"] -= diff
            c.training["spent"] += diff
        else:
            c.training["available"] += diff
            c.training["spent"] = max(0, c.training["spent"] - diff)
    l["native"] = native


def comfort_to_training_rate(c):
    return (c.level + 1) * 5


def spend_comfort(c, points=1):
    points = min(points, c.comfort["current"])
    if points <= 0:
        raise PurchaseError("Нет комфорта")
    gained = comfort_to_training_rate(c) * points
    c.comfort["current"] -= points
    c.training["available"] += gained
    return gained


def lose_comfort(c, points=1):
    points = min(points, c.comfort["current"])
    if points <= 0:
        raise PurchaseError("Нет комфорта")
    c.comfort["current"] -= points
    return points


# ============ Урон по статам ============

def damage_stat(c, ab, n):
    if ab not in c.abilities:
        raise PurchaseError(f"Неизвестный стат: {ab}")
    if n <= 0:
        return 0
    base = c.abilities[ab]
    cur = c.ability_damage.get(ab, 0)
    new = min(base, cur + n)
    actual = new - cur
    c.ability_damage[ab] = new
    return actual


def restore_stat_damage(c, ab, n):
    if ab not in c.abilities:
        raise PurchaseError(f"Неизвестный стат: {ab}")
    if n <= 0:
        return 0
    cur = c.ability_damage.get(ab, 0)
    new = max(0, cur - n)
    actual = cur - new
    c.ability_damage[ab] = new
    return actual


def restore_stat_full(c, ab):
    cur = c.ability_damage.get(ab, 0)
    c.ability_damage[ab] = 0
    return cur


def any_stat_damaged(c):
    return any(v > 0 for v in c.ability_damage.values())


def first_damaged_stat(c, exclude=None):
    for ab in ("str", "dex", "con", "int", "wis", "cha"):
        if exclude and ab in exclude:
            continue
        if c.ability_damage.get(ab, 0) > 0:
            return ab
    return None


# ============ Травмы ============

def add_injury(c, severity, name=None, heal_rating=None, desc="",
               consume_ot=True):
    """Добавить травму.
    severity='light'/'medium'/'heavy'/'custom'.
    consume_ot=True — списывает ОТ (2/5/12)."""
    if severity in INJURY_SEVERITIES:
        info = INJURY_SEVERITIES[severity]
        cost = info["cost"] if consume_ot else 0
        default_heal = info["heal_rating"]
        default_name = info["name"]
    else:
        cost = 0
        default_heal = 1
        default_name = "Травма"
    if consume_ot and cost > 0:
        if c.injury_points < cost:
            raise PurchaseError(
                f"Не хватает ОТ: нужно {cost}, есть {c.injury_points}")
        c.injury_points -= cost
    injury = {
        "name": name or default_name,
        "severity": severity if severity in INJURY_SEVERITIES
                    else "custom",
        "heal_rating": (heal_rating if heal_rating is not None
                        else default_heal),
        "desc": desc,
        "uses": False,
        "uses_max": 0,
        "uses_current": 0,
        "tick_on_initiative": False,
    }
    c.injuries.append(injury)
    return injury


def add_injury_manual(c):
    """Добавить пустую травму без списания ОТ (для ручного заполнения)."""
    return add_injury(c, "custom", consume_ot=False)


def remove_injury(c, idx, refund_ot=False):
    """Удалить травму. refund_ot=True — вернуть ОТ за неё по severity."""
    if idx < 0 or idx >= len(c.injuries):
        raise PurchaseError("Травма не найдена")
    inj = c.injuries.pop(idx)
    if refund_ot:
        sev = inj.get("severity", "custom")
        if sev in INJURY_SEVERITIES:
            c.injury_points += INJURY_SEVERITIES[sev]["cost"]
    return inj


def upgrade_heal_rating(c, idx):
    """Потратить 1 внимание → heal_rating += max(2, STR_mod).
    Без потолка."""
    if idx < 0 or idx >= len(c.injuries):
        raise PurchaseError("Травма не найдена")
    if c.attention.get("current", 0) <= 0:
        raise PurchaseError("Нет внимания")
    bonus = max(2, c.ability_modifier("str"))
    c.attention["current"] -= 1
    c.injuries[idx]["heal_rating"] = (
        c.injuries[idx].get("heal_rating", 0) + bonus)
    return bonus


def spend_comfort_for_ot(c):
    """1 комфорт → −3 ОТ (уменьшает ОТ, без травмы)."""
    if c.comfort.get("current", 0) <= 0:
        raise PurchaseError("Нет комфорта")
    if c.injury_points <= 0:
        raise PurchaseError("Нет ОТ для снятия")
    gain = min(3, c.injury_points)
    c.comfort["current"] -= 1
    c.injury_points -= gain
    return gain


def spend_attention_for_ot(c):
    """1 внимание → −max(2, STR_mod) ОТ (без травмы)."""
    if c.attention.get("current", 0) <= 0:
        raise PurchaseError("Нет внимания")
    if c.injury_points <= 0:
        raise PurchaseError("Нет ОТ для снятия")
    gain = min(max(2, c.ability_modifier("str")), c.injury_points)
    c.attention["current"] -= 1
    c.injury_points -= gain
    return gain


def heal_stat_for_bp(c, ab, cost_bp=1):
    """Потратить 1 БП → снять 1 урон с ability_damage[ab]."""
    if ab not in c.ability_damage:
        raise PurchaseError(f"Неизвестный стат: {ab}")
    dmg = c.ability_damage.get(ab, 0)
    if dmg <= 0:
        raise PurchaseError(f"{ab.upper()} не повреждён")
    if c.pain_threshold["current"] < cost_bp:
        raise PurchaseError(
            f"Не хватает БП: нужно {cost_bp}, "
            f"есть {c.pain_threshold['current']}")
    c.pain_threshold["current"] -= cost_bp
    healed = min(1, dmg)
    c.ability_damage[ab] = dmg - healed
    c.recompute_derived()
    return healed


# ============ Бонусы владения оружием ============

def set_weapon_bonuses(c, weapon_name, bonuses):
    """Сохраняет бонусы оружия с валидацией.
    bonuses — список [{"slot": 5, "id": "spec_attack_1"}, ...].

    Правила:
      • на каждом слоте — только один бонус;
      • в рамках одной ступени (spec 5-7, expert 8-11,
        master 12) конкретный бонус можно взять не более
        одного раза;
      • глобальный max_stacks из каталога — верхний предел
        для всего оружия."""
    w = c.weapon_by_name(weapon_name)
    if not w:
        raise PurchaseError(f"Оружие {weapon_name} не найдено")
    level = w.get("level", 0)
    available_slots = {lvl for lvl, _ in WEAPON_BONUS_SLOTS
                       if lvl <= level}

    def _slot_tier(slot):
        if slot <= 7:
            return "spec"
        if slot <= 11:
            return "expert"
        return "master"

    TIER_NAMES = {"spec": "Специалист",
                  "expert": "Эксперт",
                  "master": "Мастер"}

    counts = {}
    tier_counts = {}
    used_slots = set()
    validated = []

    for entry in bonuses:
        slot = entry.get("slot")
        bid = entry.get("id")
        if not slot or not bid:
            continue
        if slot not in available_slots:
            raise PurchaseError(
                f"Слот уровня {slot} недоступен "
                f"(уровень оружия {level})")
        if slot in used_slots:
            raise PurchaseError(
                f"Слот уровня {slot} уже занят")
        bdef = WEAPON_BONUS_CATALOG.get(bid)
        if not bdef:
            raise PurchaseError(f"Неизвестный бонус: {bid}")
        if bdef["type"] not in allowed_bonus_types_for_slot(slot):
            raise PurchaseError(
                f"Бонус «{bdef['name']}» нельзя брать "
                f"на слоте {slot}")

        tier = _slot_tier(slot)
        key = (bid, tier)
        tier_counts[key] = tier_counts.get(key, 0) + 1
        if tier_counts[key] > 1:
            raise PurchaseError(
                f"Бонус «{bdef['name']}» можно взять "
                f"только один раз за ступень "
                f"«{TIER_NAMES[tier]}». "
                f"Возьми его на следующей ступени "
                f"(или сними дубль).")

        counts[bid] = counts.get(bid, 0) + 1
        if counts[bid] > bdef["max_stacks"]:
            raise PurchaseError(
                f"Бонус «{bdef['name']}» можно брать "
                f"не больше {bdef['max_stacks']} раз "
                f"за всё оружие")
        used_slots.add(slot)
        validated.append({"slot": slot, "id": bid})

    w["bonuses"] = validated
    c.recompute_derived()


if __name__ == "__main__":
    from character import ensure_dirs
    ensure_dirs()
    g = Character("Тест")
    g.char_class = {"name": "Воин", "level": 5, "hp_die": 10,
                    "hp_rolls": [10, 7, 8, 6, 9], "abilities": [],
                    "has_spellbook": False, "spell_discount_extra": 0,
                    "bab_type": "good", "good_saves": ["fort"]}
    g.abilities = {"str": 16, "dex": 14, "con": 12,
                   "int": 10, "wis": 12, "cha": 10}
    g.training["available"] = 5000
    g.attention["current"] = 5
    g.comfort["current"] = 3
    g.injury_points = 10

    print("=== Тест v5.3 ===")
    print(f"ОТ: {g.injury_points}, комфорт: {g.comfort['current']}, "
          f"внимание: {g.attention['current']}")

    add_injury(g, "light")
    print(f"После light: ОТ={g.injury_points}, "
          f"травм={len(g.injuries)}, "
          f"heal_rating={g.injuries[-1]['heal_rating']}")

    add_injury(g, "medium")
    print(f"После medium: ОТ={g.injury_points}, "
          f"травм={len(g.injuries)}")

    gain = spend_comfort_for_ot(g)
    print(f"1 комфорт → −{gain} ОТ, теперь ОТ={g.injury_points}, "
          f"комфорт={g.comfort['current']}")

    gain = spend_attention_for_ot(g)
    print(f"1 внимание → −{gain} ОТ, теперь ОТ={g.injury_points}, "
          f"внимание={g.attention['current']}")

    bonus = upgrade_heal_rating(g, 0)
    print(f"Внимание → РЛ +{bonus}, РЛ={g.injuries[0]['heal_rating']}, "
          f"внимание={g.attention['current']}")

    print(f"\nТравмы: {[i['name'] for i in g.injuries]}")
    print("\n=== OK ===")