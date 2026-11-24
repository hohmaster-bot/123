# Class system v0, undo, drives (D27, package 25)

- Catalog kind `classes` (`wp/catalog/data/classes.json`, three SAMPLE entries; schema in catalog_schemas.json).
- `set_class(class_id, catalog)` copies the entry into `Character.class_info` (ClassInfo, `wp/model/class_types.py`);
  `class_id` "" = no class. `wp/model/classes.py` is the only reader: `bab`, `save_base`, `hit_die`, `divine`,
  `spellbook`, `own_professionalism`, `class_skills`. Precedence: no class -> the typed values (Character.bab,
  save_base); class -> `bab_override` / `save_override` when set, else the class formulas (constants `class.*`,
  ASSUMPTION Q167).
- Undo / redo: `Session.undo()` / `redo()`; the stack holds (Character before, command), bounded by the app setting
  `undo_depth`; commands in `wp/app/data/undo.json` are skipped; open / new clear both stacks; a new command clears
  redo; the journal gets "undo" / "redo" lines; the result has the command's topics. States are frozen and share
  their unchanged parts (no copies; `tools/bench.py` prints dispatch + undo + redo).
- Drives: `Drive.level_notes` ({"0".."5": text}) and `Drive.principle`; `notebook_cmds.drive_view` adds `note`
  (of the current level) and `principle_missing` (level >= `narrative.principle_min_level`, empty principle).
- Hidden item properties: `Item.hidden_properties` (HiddenProperty), unlocked by `items.qualification_level`.
- Pick flags: `wp/model/pick_flags.py`; spell damage: `Spell.damage` (SpellDamage), `wp/model/spell_damage.py`.
