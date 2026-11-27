"""Panel views (package 23 A2): one function per panel of the registry (wp/panels/data/panels.json). Each returns the
derived data the panel shows (dataclasses, tuples, dicts of plain values). Read only; the Session calls them inside
rules.using(character), so the UI never has to.

A view: fn(ch, session, **params). Params are listed in PARAMS (the view contract, ARCH/view_contract.md).
"""
import json
from wp.catalog import schema as cat
from wp.commands.base import CommandError
from wp.commands import action_cmds, edit_cmds, notebook_cmds, reaction_cmds
from wp.core import rest as rs
from wp.model import active_list as al
from wp.model import attack_view as av
from wp.model import bridge
from wp.model import classes as klass
from wp.model import container_view as cv
from wp.model import defense_view as dfv
from wp.model import derived_view as dv
from wp.model import doll
from wp.model import experience
from wp.model import flask
from wp.model import iterative as itv
from wp.model import load_view as lv
from wp.model import maneuver_view as mv
from wp.model import pick_flags
from wp.model import pool_view as pv
from wp.model import spell_view as sv
from wp.model import stance_view as stv
from wp.model import stats_view as stats
from wp.settings import settings_view
from wp.settings import store as st

DEFENSE_SETTINGS = "rules.ac_zones"     # the rule constants listed by the defense panel (package 24 B3)
LOG_TAIL = 50                          # not a rule: how many journal lines the log view returns by default


def _pool(p):
    return {"current": p.current, "max": p.max, "over_max": p.over_max}


def _pool_row(ch, p):
    """A class pool: current, max and over_max (owner, package 27 F28: a pool above its max is not clamped, it is
    flagged like HP and balance)."""
    cur, mx = pv.current(ch, p), pv.max_of(ch, p)
    return {"current": cur, "max": mx, "over_max": cur > mx}


def resources(ch, session=None):
    return {"hp": _pool(dv.hp_pool(ch)), "temp_hp": dv.temp_hp_total(ch), "balance": _pool(dv.balance_pool(ch)),
            "bp": _pool(dv.bp_pool(ch)), "spirit": _pool(dv.spirit_pool(ch)), "mana": _pool(dv.mana_pool(ch)),
            "comfort": _pool(dv.comfort_pool(ch)), "pain": dv.pain_total(ch), "ot": ch.trauma,
            "overload": ch.overload, "reactions": _pool(reaction_cmds.reactions_pool(ch)),
            "pools": tuple((p.pid, p.name, _pool_row(ch, p)) for p in ch.pools),
            "actions": action_cmds.actions_view(ch),
            "flasks": flask.view(ch, session.app if session is not None else None),
            "damage_types": tuple(dfv.TYPES), "buttons": _resource_buttons(session)}


def sources_view(ch, session=None, number="hp_max"):
    """The sources of one sheet number (package 34, model/sources.py) + editable = the Session editor mode."""
    from wp.model import sources as src
    if not src.known(ch, number):
        raise CommandError("no sheet number %r" % (number,), "unknown_number", values=(number,))
    out = dict(src.view(ch, number))
    out["editable"] = bool(getattr(session, "editor_mode", False)) and out["editable_target"]
    return out


RESOURCE_GROUP = "resource:"           # a quick button with group "resource:<id>" shows under that resource (pkg 33)


def _resource_buttons(session):
    """{resource id: ((button id, label), ...)} from the app quick buttons (Session.run_quick runs them)."""
    out = {}
    for b in (session.app.quick_buttons if session is not None else ()):
        g = str(b.get("group") or "")
        if g.startswith(RESOURCE_GROUP):
            out.setdefault(g[len(RESOURCE_GROUP):], []).append((b["id"], b.get("label") or b["id"]))
    return {k: tuple(v) for k, v in out.items()}


def combat(ch, session=None):
    return {"in_combat": ch.in_combat, "round": ch.combat_round, "iterative_count": ch.iterative_count,
            "next_iterative": itv.penalty(ch), "morale_scale": ch.morale_scale, "morale_bonus": dv.morale_bonus(ch),
            "negative_state": ch.negative_state, "dead": dv.is_dead(ch), "reactions": _pool(reaction_cmds.reactions_pool(ch)),
            "stance": stv.stance_view(ch), "defense": dfv.defense_view(ch), "actions": action_cmds.actions_view(ch),
            "morale_active": ch.in_combat, "action_squares": _squares(action_cmds.actions_pool(ch)),
            "reaction_squares": _squares(reaction_cmds.reactions_pool(ch))}


def _squares(pool):
    """Numbered squares ((n, spent), ...): spending takes the smallest numbers first (owner, package 30)."""
    from wp.model import screen_view as scr
    return scr.squares(pool.current, pool.max)


def defense(ch, session=None):
    from wp.model import ac_zones_view
    app = session.app if session is not None else st.AppSettings()
    from wp.model import screen_view as scr
    the_cells = ac_zones_view.cells(ch)
    return {"modes": ac_zones_view.modes(ch, the_cells), "cells": the_cells, "shield_side": scr.shield_side(ch),
            "cell_lines": scr.cell_lines(ch), "cell_labels": {c: "ac_cell." + c for c in the_cells},
            "display": ac_zones_view.display(app), "defense": dfv.defense_view(ch),
            "abilities": pick_flags.abilities(ch),
            "settings": settings_view.list_settings(app, ch, group=DEFENSE_SETTINGS)}


def attacks(ch, session=None):
    return tuple(av.attack(ch, r) for r in ch.attacks)


def maneuvers(ch, session=None):
    return mv.maneuver_view(ch)


def items(ch, session=None, doll_view="body"):
    from wp.model import doll_layout as dl
    from wp.model import hands as hd
    background = None
    profile = None
    if session is not None:
        from wp.settings import images
        profile = session.profile("classic")
        background = images.resolve(session.app, dl.layout_of(profile).get("background", ""), session.user_dir)
    return {"doll": doll.doll_view(ch), "hands": hd.view(ch), "layout": dl.view(ch, profile, doll_view, background),
            "items": tuple(dv.item_view(ch, it.iid) for it in ch.items),
            "weight": lv.weight_view(ch), "load": _load(ch), "base": dv.base_view(ch)}


def _load(ch):
    from wp.model import screen_view as scr
    return scr.load(ch)


def statuses(ch, session=None):
    from wp.model import screen_view as scr
    from wp.model import links
    from wp.model import trigger_view as tv
    return {"container": cv.container_view(ch), "active": al.active_list(ch), "favorites": scr.favorites(ch),
            "reminders": scr.reminders(ch), "triggers": tv.notes_view(ch), "manual_conditions": ch.manual_conditions,
            "not_backed": links.not_backed(ch)}


def skills(ch, session=None):
    return tuple((s.name, s.tier, s.ranks, dv.skill_bonus(ch, s.name)) for s in ch.skills)


def rest(ch, session=None):
    session_state = rs.start_short_rest(bridge.to_rest(ch))
    return {"free_heal": session_state.free_heal, "options": rs.options(session_state)}


def log(ch, session=None, tail=LOG_TAIL):
    return tuple(ch.log[-int(tail):]) if tail else tuple(ch.log)


def notebook(ch, session=None):
    return notebook_cmds.notebook_view(ch)


def training(ch, session=None):
    return {"training": ch.training, "level": ch.level, "base_slots": dv.base_slots(ch), "reactions": dv.reactions(ch),
            "comfort": _pool(dv.comfort_pool(ch)), "attention": ch.attention, "experience": experience.view(ch),
            "weapons": _weapon_rows(ch), "languages": ch.languages}


def _weapon_rows(ch):
    """Per weapon node (review 5 F16): (id, title, level, grades bought, combat basics bought)."""
    from wp.core import weapons as wpn
    catalog = ch.weapon_catalog()
    return tuple((e.weapon.name, e.title, wpn.level(catalog, e.weapon.name), e.weapon.grades, e.weapon.basics)
                 for e in ch.weapons)


def settings(ch, session=None):
    return settings_view.list_settings(session.app if session is not None else st.AppSettings(), ch)


def catalogs(ch, session=None):
    return {"kinds": cat.KINDS}


def sheet(ch, session=None):
    return {"abilities": {a: (dv.ability_current(ch, a), dv.ability_mod(ch, a)) for a in ch.abilities},
            "stats": stats.view(ch), "level": ch.level, "bab": klass.bab(ch), "class_id": ch.class_id, "speed": dv.speed(ch),
            "bab_override": ch.bab_override, "save_override": dict(ch.save_override),
            "feats": _feat_rows(ch), "attack_melee": _attack(ch, "melee"), "attack_ranged": _attack(ch, "ranged"),
            "class": ch.class_info, "name": session.name if session is not None else "", "moves": _moves(ch),
            "switches": _switches(ch)}


def trainings(ch, session=None):
    """The catalog trainings (package 37): rows (id, name, module, price, units, limit, unlocked, reason)."""
    from wp.catalog import store as cs
    from wp.model import trainings as trn
    if session is None:
        return ()
    return trn.rows(ch, [json.loads(json.dumps(e)) for e, _layer in cs.merged(session.catalog("trainings"))])


def links(ch, session=None):
    """The held-by links both ways (package 37, decision 5): {carrier ref: name, held_by, backed, holds}."""
    from wp.model import links as lk
    return lk.view(ch)


def effect_targets(ch, session=None):
    """Every effect target an editor may offer (package 37): the sheet targets (prefix targets end with ':') and
    const:<id> for every numeric rule constant (generated from the rule data, no hand-kept list)."""
    from wp.model import sheet_targets as stg
    from wp.rules_data import rules as rd
    return tuple(sorted(t for t in stg.TARGETS if t != "const:")) + tuple("const:" + cid for cid in sorted(rd.numeric_ids()))


def race(ch, session=None):
    """The race of the character (package 36 P3, model/races.py view)."""
    from wp.model import races
    return races.view(ch)


def situational(ch, session=None):
    """{sheet number: ((value, text, source), ...)} of the situational bonuses (package 36, decision 8)."""
    from wp.model import situational as sit
    return sit.by_number(ch)


def _moves(ch):
    from wp.model import moves as mv
    return mv.moves(ch)


def _switches(ch):
    from wp.model import switches as sw
    return sw.view(ch)


def _attack(ch, kind):
    from wp.model import screen_view as scr
    return scr.attack_number(ch, kind)



def _feat_rows(ch):
    """Feats with their charges and cooldown (package 28: spend_charge on a feat must be visible)."""
    from wp.model import usage as us
    return tuple((f.fid, f.title, us.charges("feat", f), us.cooldown("feat", f)) for f in ch.feats)


def spells(ch, session=None):
    from wp.model import spell_damage as sd
    return {"view": sv.view(ch), "spells": ch.spells, "damage": sd.view(ch), "mana": _pool(dv.mana_pool(ch)),
            "slots": {c: _pool(p) for c, p in dv.slot_pools(ch).items()}}


def injuries(ch, session=None):
    return {"injuries": ch.injuries, "trauma": ch.trauma}


def editor(ch, session=None):
    return {"collections": edit_cmds.COLLECTIONS}


VIEWS = {"resources": resources, "combat": combat, "defense": defense, "attacks": attacks, "maneuvers": maneuvers,
         "items": items, "statuses": statuses, "skills": skills, "rest": rest, "log": log, "notebook": notebook,
         "training": training, "settings": settings, "catalogs": catalogs, "sheet": sheet, "spells": spells,
         "injuries": injuries, "editor": editor, "sources": sources_view,
         "situational": situational, "race": race, "effect_targets": effect_targets,
         "trainings": trainings, "links": links}
PARAMS = {"log": ("tail",), "items": ("doll_view",), "sources": ("number",)}
