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
- Armor and shields [OWNER, package 9]: two example data sets ship as data (wp/catalog/data/armor_set_1.json "Country
  1", 8 rows; armor_set_2.json "Country 2", 15 rows). They are tables from a game, rules may differ per game: plain
  selectable data sets, not hard rules; any file armor_set_*.json is one more set. Row fields: id, name, kind
  (armor / shield), category (armor light / medium / heavy; shield light / heavy / tower), weight, price (text as
  written), access_class (set 1 only), ac_bonus, touch_bonus, max_dex, skill_penalty (positive = penalty),
  speed_penalty_ft, spell_penalty_mana, spell_failure_pct, special ("+" column of set 2), hardness, hp, durable.
  English names for now; the owner adds Russian names later.
- Shop is just a layer on the catalog [OWNER]: taking an item from the catalog can buy it at once (gold deducted automatically);
  taking a feat can buy it for training (only if the checkbox "pay with training" is on). Items only for gold.
  Old characters are not migrated (D1).

## Two names [OWNER]
- Everything can store two names: the list name and a short name (used on chips and buttons).
- Plan (not rule): button label may be replaced by an image.
