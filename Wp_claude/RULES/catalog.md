# Catalog [OWNER]

- The catalog is a DATABASE of everything: items, weapons, weapon groups, feats, class/race abilities, spells, injuries, recipes...
  Loaded from files dropped into a folder on the PC (and later maybe from a shared link, e.g. cloud drive: give a link, others get the data).
- Any character can buy or copy (get) anything from it: feat, class ability, race ability, etc.
- Filters COMBINE: category + sub-filter + source/country.
  Examples: Items = all items; Items + Weapons = weapons only; Items + country X = items of X; Weapons + country X;
  Weapon groups + country X = all groups of X (add at level 0, then train); filter by class name "wizard" = all its class abilities
  (take those needed for the level).
- Sort/filter axes: weapons, armor and shields, source (tag = player name or module), magic items, spells, feats, "other".
- Users create their own catalogs and entries; players share files. Anything a player creates can be put into a catalog.
- Enabled catalogs: one list for the user (global), not per character.
- Weight in catalog rows [OWNER]: "L" = 1 L; a plain number N = N * 10 L (1 = 10 L = 1 B). The unit "B" is not
  written in the rows.
- Skills: the default skill catalog ships with the app as data (skills_list.md, 45 templates); see skills.md "Skill catalog".
- Armor and shields [OWNER, package 9]: two example data sets ship as data (since package 18 both live in the
  catalog file armor_shields.json, field "set": set_1 "Country 1", 8 rows; set_2 "Country 2", 15 rows). They are tables from a game, rules may differ per game: plain
  selectable data sets, not hard rules; another value of "set" is one more set. Row fields: id, name, kind
  (armor / shield), category (armor light / medium / heavy; shield light / heavy / tower), weight, price (text as
  written), access_class (set 1 only), ac_bonus, touch_bonus, max_dex, skill_penalty (positive = penalty),
  speed_penalty_ft, spell_penalty_mana, spell_failure_pct, special ("+" column of set 2), hardness, hp, durable.
  English names for now; the owner adds Russian names later. [OWNER, package 10, closes Q53] Set 1 "magic" numbers
  are a positive extra mana cost (source -1 -> 1); weight "(1)" = 1 = 10 L as usual; access class and set 2 "+" are
  data; rules per game may change.
- Shop is just a layer on the catalog [OWNER]: taking an item from the catalog can buy it at once (gold deducted automatically);
  taking a feat can buy it for training (only if the checkbox "pay with training" is on). Items only for gold.
  [OWNER, package 17] Money is NARRATIVE: the app keeps no money and deducts nothing (Q122 closed); the shop layer
  only copies an item from the catalog.
  Old characters are not migrated (D1).

## Two names [OWNER]
- Everything can store two names: the list name and a short name (used on chips and buttons).
- Plan (not rule): button label may be replaced by an image.

## Catalog files [OWNER, package 18, D21]
- Every catalog is ONE self-contained JSON file that the program (and later the UI) loads, lists, edits, adds to,
  deletes from and creates from scratch with no code change. One shipped file per kind in wp/catalog/data/:
  weapons, armor_shields, items, spells, statuses, skills, weapon_groups, feats, damage_types, doll_slots. A user can
  create more catalog files of a kind.
- Format: {"kind", "format": 1, "title", "counter", "retired", "meta", "entries": [...]}. Every entry: a stable id (made
  by the program from the name: transliteration, a number from the file's counter on a collision; a deleted id goes
  to "retired" and is never given again), name (free text), sample (bool), the fields of its kind. Unknown entry
  fields are KEPT on edit and save and never interpreted; unknown top-level fields are dropped on load (no
  migrations). The fields of each kind (name, type, required, allowed values) are DATA: catalog_schemas.json.
- Two layers: shipped catalogs (read-only, the install folder) and user catalogs (a folder next to the characters,
  catalogs/<kind>.json; more user files of the same kind are named <kind>__<name>.json, package 22 B9, Q152).
  A user entry with the same id wins ("override"); removing a shipped entry writes a
  tombstone into the user file; reset drops the override or the tombstone. The program never writes into the
  shipped folder. The program's own loaders (weapons, groups, armor, feats, skills, damage types, doll slots) read
  through this layer.
- Catalog commands are the ONLY way to change a catalog (like character commands, D5): catalog_add_entry,
  catalog_edit_entry, catalog_rename_entry (id stays), catalog_remove_entry, catalog_duplicate_entry,
  catalog_reset_entry, catalog_import_entry, catalog_create. Refusals carry a reason id + params. Saving is atomic
  (temp file + replace; a failed save keeps the old file). The UI later reads catalogs through the catalog view (list
  with a filter text and a sort; get, with the layer shipped / user / override) and writes them only through these
  commands.
- Sharing: one entry -> a text code (export) and back (import as a new entry, gear.md "Item codes"); a whole
  catalog file can be exported / imported as it is.
- The rows shipped in package 18 for weapons, armor / shields, items, spells and statuses are TEST SAMPLES
  (sample = true) [OWNER]: the owner replaces them through the future UI.
