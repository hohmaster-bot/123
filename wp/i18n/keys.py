"""Every text key the program needs (package 21): collected from the code and the data, never typed twice.

required() -> {key: group} for: refusal reasons (reason.<id>, found in the code: CommandError(..., "<id>") and the
schema checks), warnings (warning.<id>), settings labels and descriptions (settings schema, incl. the rule constants:
rules.<id>), catalog kinds and fields (catalog.kind.<kind>, catalog.field.<name>), skills (skill.<id>), stats, tiers,
damage types, doll slots, resources, statuses and stance feats of the samples, panels, themes, UI buttons.
"""
import ast
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCES = ("hp", "temp_hp", "balance", "bp", "mana", "spirit", "comfort", "pain", "ot", "overload", "morale",
             "attention", "ov", "training")
UI_BUTTONS = ("short_rest", "long_rest", "damage", "heal", "temp_hp", "lose_balance", "new_turn", "injury", "pain",
              "morale", "restore_balance", "stance", "end_of_cycle", "start_combat", "end_combat")
SCHEMA_FILES = ("settings/schema.py", "catalog/schema.py")


def _module_strings(tree):
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) \
                and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
            out[n.targets[0].id] = n.value.value
    return out


def reason_ids():
    """Reason ids written in the code (literal or a module-level string constant), plus the schema checks."""
    out = set()
    for path in glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True):
        tree = ast.parse(open(path, encoding="ascii").read())
        names = _module_strings(tree)
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "CommandError":
                arg = node.args[1] if len(node.args) > 1 else next((k.value for k in node.keywords if k.arg == "reason"), None)
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    out.add(arg.value)
                elif isinstance(arg, ast.Name) and arg.id in names:
                    out.add(names[arg.id])
            if rel in SCHEMA_FILES and isinstance(node, ast.Return) and isinstance(node.value, ast.Tuple) \
                    and node.value.elts and isinstance(node.value.elts[0], ast.Constant) \
                    and isinstance(node.value.elts[0].value, str):
                out.add(node.value.elts[0].value)
    from wp.commands import base
    from wp.commands import params
    out |= {base.INVALID, base.NOT_FOUND, base.UNKNOWN_COMMAND} | set(params.REASONS)
    return out


def warning_ids():
    from wp.commands import progression_cmds
    from wp.settings import images, layout
    return {progression_cmds.HIT_DIE_DEFAULT_USED, images.MISSING_FILE, images.NO_IMAGE, layout.UNKNOWN_SOURCE}


def required():
    from wp.catalog import schema as cat
    from wp.catalog import store as cs
    from wp.core import skills as sk
    from wp.model.character import ABILITIES
    from wp.settings import schema as sch
    keys = {}

    def add(group, *ks):
        for k in ks:
            keys.setdefault(k, group)
    add("reason", *("reason." + r for r in reason_ids()))
    add("warning", *("warning." + w for w in warning_ids()))
    for s in sch.KEYS.values():
        add("rules" if s.get("constant") else "settings", s["label"], s["description"])
    for g in {s["group"] for s in sch.KEYS.values()}:
        add("settings", "settings.group." + g)
    add("catalog", *("catalog.kind." + k for k in cat.KINDS))
    add("catalog", *sorted({"catalog.field." + f["name"] for fs in cat.SCHEMAS.values() for f in fs}))
    add("skill", *("skill." + e["id"] for e in cs.load_shipped("skills").entries))
    add("stat", *("stat." + a for a in ABILITIES))
    add("tier", *("tier." + t for t in sk.TIERS), "tier.specialized.full")   # full name for tooltips (package 22 C)
    add("damage", *("damage." + e["id"] for e in cs.load_shipped("damage_types").entries))
    add("slot", *("slot." + e["id"] for e in cs.load_shipped("doll_slots").entries))
    add("resource", *("resource." + r for r in RESOURCES))
    add("status", *("status." + e["id"] for e in cs.load_shipped("statuses").entries))
    add("feat", *("feat." + e["id"] for e in cs.load_shipped("feats").entries if e.get("is_stance")))
    add("ui", *("ui." + b for b in UI_BUTTONS))
    add("mode", "mode.classic", "mode.lite")
    try:
        from wp.panels import registry
        for p in registry.PANELS.values():
            add("panel", p["title"], p["description"])
    except ImportError:
        pass
    try:
        from wp.theme import themes
        for tid in themes.shipped_ids():
            add("theme", "theme." + tid)
    except ImportError:
        pass
    return keys
