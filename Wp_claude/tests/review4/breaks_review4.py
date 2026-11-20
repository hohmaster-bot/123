"""Review 4: my own deliberate breaks (not part of the package registry). Same format as tests/breaks/*.py.
Each entry breaks ONE rule; run_breaks.py runs the WHOLE test set (run_all.py) on a temp copy for every entry and
reports the ones no test catches. Areas: training and prices, rests, spells and mana, maneuvers and tags,
charges and cooldown, pools, stances, AC layers, item HP, misc commands.
"""
TR, RS, MG, SV = "wp/core/training.py", "wp/core/rest.py", "wp/core/magic.py", "wp/model/spell_view.py"
RC, GC, CC, IT = "wp/commands/resource_cmds.py", "wp/commands/gear_cmds.py", "wp/commands/combat_cmds.py", "wp/model/items.py"
MV, US, UC, PC = "wp/model/maneuver_view.py", "wp/model/usage.py", "wp/commands/usage_cmds.py", "wp/commands/pool_cmds.py"
PV, SC, AC, DV = "wp/model/pool_view.py", "wp/commands/sheet_cmds.py", "wp/core/ac.py", "wp/model/derived_view.py"
PG, SP, IC, SK = "wp/commands/progression_cmds.py", "wp/commands/spell_cmds.py", "wp/commands/item_cmds.py", "wp/core/skills.py"


def e(id, file, old, new, rule):
    return dict(id=id, file=file, old=old, new=new, rule=rule)


ENTRIES = [
    # ---------------------------------------------------------------- training and prices
    e("tr-ability-old-mod", TR, "return ABILITY_STEP * max(1, ability_mod(price_score(base, race_bonus) + 1))",
      "return ABILITY_STEP * max(1, ability_mod(price_score(base, race_bonus)))", "training.md:26 price uses the NEW modifier"),
    e("tr-native-cheap-le", TR, "return LANG_NATIVE_CHEAP if natives < int(int_mod) else LANG_NATIVE_EXPENSIVE",
      "return LANG_NATIVE_CHEAP if natives <= int(int_mod) else LANG_NATIVE_EXPENSIVE", "training.md:65 cheap only while natives < Int mod"),
    e("tr-base-max-plus5", TR, "    return 10 * int(level)", "    return 10 * int(level) + 5", "training.md:97 base max 10 * level"),
    e("tr-base-slot-at-max", TR, "    if slots >= base_max(level):", "    if slots > base_max(level):", "training.md:97 no slot above max"),
    e("tr-reaction-current", TR, "    return REACTION_STEP * (int(current) + 1)", "    return REACTION_STEP * int(current)",
      "training.md:87 200 * NEW number"),
    e("tr-qualification-flat", TR, "    return QUALIFICATION_STEP * int(n)", "    return QUALIFICATION_STEP", "training.md:85 50 * N"),
    e("tr-spell-no-discount", TR, "    return cost // SPELL_DISCOUNT_DIVISOR if discount else cost", "    return cost",
      "training.md:92 half price with a book"),
    e("tr-comfort-rate-level", TR, '    """1 comfort = 5 + 5 * level training (training.md); item/class bonuses change it."""\n    return 5 + 5 * int(level) + int(bonus)',
      '    """1 comfort = 5 + 5 * level training (training.md); item/class bonuses change it."""\n    return 5 * int(level) + int(bonus)',
      "training.md:31 10/15/20 at levels 1/2/3"),
    e("tr-prof-points-gt", TR, "        if int(class_skill_points) >= need:", "        if int(class_skill_points) > need:",
      "training.md:150 2+ / 4+ points"),
    e("tr-promote-other-adv", SK, "    return 40 + 20 * _count(skills, (ADVANCED, SPECIALIZED), name)",
      "    return 40 + 20 * _count(skills, (ADVANCED,), name)", "skills.md:59 specialized count as advanced"),
    e("tr-levelup-roll-above-die", PG, "    if not 1 <= roll <= ch.hit_die:", "    if not 1 <= roll:", "training.md:137 roll 1..die"),
    e("tr-exchange-comfort-short", PG, '    if ch.comfort_current < n:\n        raise CommandError("not enough comfort: have %d, exchange',
      '    if False:\n        raise CommandError("not enough comfort: have %d, exchange', "training.md:140 refused above the comfort"),
    # ---------------------------------------------------------------- rests
    e("rs-free-heal-sum", RS, "    return max(2 + int(level), int(other_heal))", "    return 2 + int(level) + int(other_heal)",
      "rest.md:39 the larger value is used"),
    e("rs-no-free-bp", RS, "    bp = replace(state.bp, current=state.bp.current + 1 + int(extra_bp))",
      "    bp = replace(state.bp, current=state.bp.current + int(extra_bp))", "rest.md:38 free +1 BP"),
    e("rs-mana-never-free", RS, "    if option == OPT_MANA and not rest.mana_free_used:\n        return 0",
      "    if option == OPT_MANA and not rest.mana_free_used:\n        return 1", "rest.md:48 mana free once"),
    e("rs-spirit-cost-1", RS, "COST = {OPT_HEAL: 1, OPT_CHARGES: 2, OPT_SPIRIT: 2, OPT_STAT: 1,",
      "COST = {OPT_HEAL: 1, OPT_CHARGES: 2, OPT_SPIRIT: 1, OPT_STAT: 1,", "rest.md:45 spirit 2 BP"),
    e("rs-pain-permanent-removable", RS, "        OPT_PAIN: any(e.amount > 0 and not e.permanent for e in s.pain),",
      "        OPT_PAIN: any(e.amount > 0 for e in s.pain),", "rest.md:50 hidden when only permanent pain"),
    e("rs-long-clears-permanent", RS, "        pain=pn.clear_temporary(state.pain),", "        pain=(),",
      "rest.md:27 permanent pain stays"),
    e("rs-long-no-stats", RS, "        stats={n: restore_stat(p, p.max) for n, p in state.stats.items()},",
      "        stats=state.stats,", "rest.md:29 stat damage healed"),
    e("rs-long-keeps-overload", RC, "    new = replace(new, overload=0)", "    new = replace(new, overload=new.overload)",
      "rest.md:31 overload 0"),
    e("rs-short-keeps-temp-hp", RC, "    new = replace(new, temp_hp=0, statuses=tuple(replace(s, temp_hp_left=0) for s in new.statuses))",
      "    new = new", "rest.md:54 ALL temp HP cleared"),
    e("rs-long-no-balance-max", RC, "    new = replace(new, balance_current=max(new.balance_current, dv.balance_max(new)))",
      "    new = new", "rest.md:31 balance to max"),
    e("rs-short-day-items-stay", GC, "if it.activated and (rest_kind == LONG or it.active_until == SHORT) else it",
      "if it.activated and rest_kind == LONG else it", "gear.md:176 short rest switches day items off"),
    # ---------------------------------------------------------------- spells and mana
    e("mg-no-base-balance", MG, "        return CastCost(mana=m + max(0, int(extra_mana)), balance=m + max(0, int(extra_balance)),",
      "        return CastCost(mana=m + max(0, int(extra_mana)), balance=max(0, int(extra_balance)),",
      "classes_magic.md:128 balance = mana cost"),
    e("mg-cantrip-no-slot", MG, "        slot = 0 if circle0_slots > 0 else None", "        slot = None",
      "classes_magic.md:132 cantrip spends a circle-0 slot"),
    e("mg-short-balance-no-pain", MG, "    pain = 1 if missing > 0 else 0", "    pain = 0", "classes_magic.md:136 +1 pain"),
    e("mg-limit-penalty-ignored", SV, "    if mana_cost + extra > lvl:", "    if False:", "gear.md:65 cost + penalty <= level"),
    e("mg-divine-default-cancel", SV, "    return ZERO_BALANCE if ch.divine_slots else CANCEL", "    return CANCEL",
      "gear.md:72 divine default zero_balance"),
    e("mg-upgrade-repeat-1-slot", SP, "    return 1 + sum(1 for u in spell.upgrades if u.name == name and u.metamagic == 0)",
      "    return 1", "progression.md:26 second identical upgrade 2 slots"),
    e("mg-four-mastery-slots", TR, "MASTERY_SLOTS = 3", "MASTERY_SLOTS = 4", "progression.md:21 three slots"),
    # ---------------------------------------------------------------- maneuvers and tags
    e("mv-all-as-any", MV, '    return req <= tags if m.tag_mode == "all" else bool(req & tags)', "    return bool(req & tags)",
      "combat.md:73 tag_mode all"),
    e("mv-no-kind-tag", MV, "    return set(rec.attack_groups(item)) | ({item.wkind} if item.wkind else set())",
      "    return set(rec.attack_groups(item))", "combat.md:80 weapon kind id is a tag"),
    e("mv-feat-ignored", MV, "    if m.required_feat and not any(f.fid == m.required_feat for f in ch.feats):", "    if False:",
      "combat.md:76 required_feat"),
    e("mv-unarmed-always", MV, "    return not any(it.groups for it in ch.items if it.in_hands)", "    return True",
      "combat.md:83 unarmed only without a weapon"),
    e("mv-to-hit-ignored", MV, "    out = [bo.Bonus(m.to_hit, bo.FLAT, bo.ATTACK, source=m.name),",
      "    out = [bo.Bonus(0, bo.FLAT, bo.ATTACK, source=m.name),", "combat.md:82 + the maneuver's modifiers"),
    e("mv-no-tags-fit-nothing", MV, "    if not req:\n        return True", "    if not req:\n        return False",
      "combat.md:88 no tags fits any weapon (Q79)"),
    # ---------------------------------------------------------------- charges and cooldown
    e("us-cooldown-ignored", UC, "    if cool > 0:\n        raise CommandError", "    if False:\n        raise CommandError",
      "gear.md:201 refused while cooldown > 0"),
    e("us-cooldown-not-started", UC, "current=cur - n, cool=rounds if rounds > 0 else None)", "current=cur - n, cool=None)",
      "gear.md:202 spending starts the cooldown"),
    e("us-never-recharge", US, '        if kind == "status" or x.usage is None or x.usage.recharge not in rules:',
      '        if kind == "status" or x.usage is None or x.usage.recharge not in rules or True:', "gear.md:203 rests recharge"),
    e("us-long-not-short", RC, "    new = us.recharge(new, us.LONG_REST, us.SHORT_REST)", "    new = us.recharge(new, us.LONG_REST)",
      "gear.md:204 long rest also restores short_rest charges (Q96)"),
    e("us-set-above-max", UC, "    if value < 0 or value > mx:", "    if value < 0:", "gear.md:202 set_charges bounds"),
    e("us-cooldown-not-ticking", US, "            ch = put(ch, kind, with_values(kind, x, cool=cur - 1))",
      "            ch = put(ch, kind, with_values(kind, x, cool=cur))", "gear.md:203 tick lowers cooldown"),
    # ---------------------------------------------------------------- pools
    e("pl-spend-below-zero", PC, "    if have - n < 0:\n        raise CommandError", "    if False:\n        raise CommandError",
      "resources.md:155 refused below 0"),
    e("pl-current-not-clamped", PV, "    return max(0, min(pool.current, max_of(ch, pool)))", "    return max(0, pool.current)",
      "buffs.md:152 current read clamped to max"),
    e("pl-long-not-short", RC, "    new = pools.restore_by(pools.restore_by(new, pools.LONG_REST), pools.SHORT_REST)",
      "    new = pools.restore_by(new, pools.LONG_REST)", "resources.md:157 long rest restores short_rest pools"),
    e("pl-combat-start-none", GC, "    ch = rst.guard(ch, pool_cmds.restore_by(ch, pool_cmds.COMBAT_START))", "    ch = ch",
      "resources.md:157 start_combat restores combat_start pools"),
    # ---------------------------------------------------------------- stances
    e("st-stance-always", "wp/model/stance_view.py", "    return not feat.is_stance or ch.active_stance == feat.fid",
      "    return True", "combat.md:159 stance effects only while active"),
    e("st-remove-keeps-active", SC, "    stance = None if ch.active_stance == fid else ch.active_stance",
      "    stance = ch.active_stance", "combat.md:161 removing the stance feat clears it"),
    e("st-not-stance-allowed", SC, "    if not feat.is_stance:", "    if False:", "combat.md:158 refused for a non-stance"),
    # ---------------------------------------------------------------- AC layers / defense
    e("ac-odd-level-1", AC, "    return max(0, (int(level) - 1) // 2)", "    return max(0, int(level) // 2)",
      "training.md:43 level 1 gives no parry"),
    e("ac-overload-cap-3", AC, "OVERLOAD_DODGE_CAP = 2", "OVERLOAD_DODGE_CAP = 3", "gear.md:32 dodge capped at +2"),
    e("ac-shield-balance-no-grade", DV, "if it.shield_type in BALANCE_SHIELDS and shield_proficient(ch, it)] or [0])",
      "if it.shield_type in BALANCE_SHIELDS] or [0])", "training.md:54 below the rank no balance bonus"),
    # ---------------------------------------------------------------- item HP
    e("it-broken-strict", IT, "    if 2 * cur <= mx:", "    if 2 * cur < mx:", "gear.md:127 broken at exactly 50%"),
    e("it-off-to-zero", IT, "    v = (2 * cur * new_max + old_max) // (2 * old_max)\n    return max(1, v)",
      "    v = (2 * cur * new_max + old_max) // (2 * old_max)\n    return v", "gear.md:125 never rounded to 0"),
    e("it-zero-works", IT, "    if cur <= 0:\n        return NOT_WORKING", "    if cur < 0:\n        return NOT_WORKING",
      "gear.md:130 HP 0 does not work"),
    e("it-enchant-no-hp", IT, "return wpn.final_hp(it.hp, picks) + (it.enchant if on else 0)", "return wpn.final_hp(it.hp, picks)",
      "gear.md:100 item HP +N"),
    # ---------------------------------------------------------------- misc commands
    e("cm-dtb-no-cap", CC, "    if ch.in_combat and rep.balance_loss > 0:", "    if False:", "combat.md:114 damage to balance lowers cap"),
    e("cm-end-keeps-morale", GC, "new = replace(ch, in_combat=False, combat_round=0, overload=0, morale_scale=0,",
      "new = replace(ch, in_combat=False, combat_round=0, overload=0, morale_scale=ch.morale_scale,", "defense.md:51 morale reset"),
    e("cm-consumable-below-0", IC, "    if it.quantity - n < 0:", "    if False:", "gear.md:186 refused below 0"),
    e("cm-ot-comfort-x2", PG, "    trauma = max(0, ch.trauma - n * inj.COMFORT_OT)", "    trauma = max(0, ch.trauma - n * 2)",
      "injuries.md:61 1 comfort removes 3 OT"),
]
