# Panel registry (D24, package 21)

- Data: `wp/panels/data/panels.json`. A panel: id, title / description (i18n keys `panel.<id>`, `panel.<id>.desc`),
  modes (classic / lite), defaults per mode (dock, position, size), min_size, resizable, cell_capable, requires,
  icon id, source (the model view it shows), described (False = the docs only name it). Missing fields come from the
  file's "defaults" block.
- 18 panels: resources, combat, defense, attacks, maneuvers, items, statuses, skills, rest, log, notebook, training,
  settings, catalogs (described) and sheet, spells, injuries, editor (id + title only; the owner describes them later).
  Lite panels: resources, combat, attacks, statuses, log, notebook, settings.
- Layout profiles (ARCH/settings.md) name registry panels: a classic panel item has the field `panel`; cells and lite
  elements may name one. layout_add / layout_edit refuse unknown_panel, panel_not_in_mode, panel_needed; a stored
  profile with a problem loads with a warning (`registry.warnings(app)`). The shipped default profiles reference
  registry ids only.
- Views: `list_panels(mode)`, `get(id)`, `check_profile(profile, mode)`.

## Classic v2 blocks (package 29, UI_WISHES.md "Classic screen v2")
The screen is built of blocks; a block reads one or more registry views (the registry stays the list of VIEWS; the
block ids below are layout blocks, added to the registry in the UI phase, ARCH/ui_gaps.md):
- experience_strip (training.experience), identity (avatar: image target character; sheet), resources (resources,
  flasks), ac_block (defense.cells, display), parameters (sheet.stats, attacks, items.weight; a cell block),
  statuses (statuses), favorites (statuses favourites + abilities), reminders (notebook.drive_summary.reminders and
  other sources), combat (combat, attacks, maneuvers, spells, quick buttons), tabs (the other panels as tabs:
  log, skills, sheet, injuries, notebook, items, training, rest, catalogs, settings), bottom_strip (resources, combat,
  sheet, items.weight; a cell block).
