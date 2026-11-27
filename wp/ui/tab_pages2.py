"""The heavy content tabs (package 35 P4): Inventory, Training, Skills, Feats, Catalogs (wp/ui/tab_pages.py has the
common Page and the module rules). Inventory: items, weight, worn / in hands, the load; Equip / Take off
(equip_item / unequip_item). Training: training points, level, base slots, reactions, comfort, attention and the item
qualifications (buy_item_qualification). Skills: name, tier, ranks, bonus; +1 rank (buy_skill_rank). Feats: the
character's feats with charges and cooldown; a star makes one a favourite (set_favorite). Catalogs: a read-only browser
of every catalog kind (shipped, override and own entries; game-module data, nothing hard-coded).
"""
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout

from wp.app import ui_data
from wp.ui import params_logic as pl
from wp.ui import tab_logic as tl
from wp.ui.tab_pages import Page, yes


class InventoryPage(Page):
    TAB = "inventory"
    COLS = ("name", "weight", "quantity", "worn", "in_hands", "state")
    ACTIONS = ("equip", "unequip", "effects")

    def show_data(self, tr, s):
        v = s.view("items")
        rows = tl.item_rows(s.character.items, v["items"])
        ld = v["load"]
        cat = pl.load_category(ld["carried_l"], ld["light_max_l"], ld["heavy_max_l"])
        self.summary.setText(tr("tabs_page.inventory.summary", load=tr("load.of", values=(ld["carried_l"],
                                                                                       ld["heavy_max_l"])),
                                cat=tr("load." + cat)))
        self.fill(rows, [(name, weight, qty, yes(tr, worn), yes(tr, hands), state)
                         for _iid, name, weight, qty, worn, hands, state in rows])
        links = s.view("links")                  # package 37: what the item holds (hover)
        danger = s.theme(self.block.win.system_dark() if self.block.win is not None else None)["colors"]["danger"]
        for r, row in enumerate(rows):
            self.table.item(r, 0).setToolTip(tl.link_tooltip(links, "item:" + row[0], tr, danger))

    def act(self, key):
        row = self.selected()
        if row is None:
            return None
        if key == "effects":
            return self.open_effects("items", row[0])
        return self.run("equip_item" if key == "equip" else "unequip_item", iid=row[0])


class SkillsPage(Page):
    TAB = "skills"
    COLS = ("name", "tier", "ranks", "bonus")
    ACTIONS = ("rank_up",)

    def show_data(self, tr, s):
        rows = tl.skill_rows(s.view("skills"))
        self.summary.setText(tr("tabs_page.skills.summary", tp=s.view("training")["training"], n=len(rows)))
        self.fill(rows, [(name, tier, ranks, pl.signed(bonus)) for name, tier, ranks, bonus in rows])

    def act(self, key):
        row = self.selected()
        return None if row is None else self.run("buy_skill_rank", name=row[0])


class FeatsPage(Page):
    TAB = "feats"
    COLS = ("name", "charges", "cooldown")
    ACTIONS = ("favorite", "fire", "link", "effects")
    INDENT = "    "                    # a dependent ability under its holder (package 37)

    def __init__(self, block):
        super().__init__(block)
        self.condition_boxes = {}
        self.holder = QComboBox()          # package 37 (decision 5): the "held by" chooser of the selected feat
        self.links_box = QHBoxLayout()
        self.links_box.addWidget(self.holder, 1)
        self.layout().addLayout(self.links_box)

    def show_data(self, tr, s):
        links = s.view("links")
        flat = tl.feat_rows(s.view("sheet"))
        rows_depth = tl.nested(flat, links, lambda r: "feat:" + r[0])
        rows = [r for r, _d in rows_depth]
        n = len(ui_data.catalog_rows(s, "feats"))
        self.summary.setText(tr("tabs_page.feats.summary", n=len(rows), catalog=n))
        self.fill(rows, [(self.INDENT * d + (title or fid), "" if charges is None else charges,
                          "" if cooldown is None else cooldown) for (fid, title, charges, cooldown), d in rows_depth])
        texts = {f.fid: f.text for f in s.character.feats}
        danger = s.theme(self.block.win.system_dark() if self.block.win is not None else None)["colors"]["danger"]
        for r, (fid, _t, _c, _cd) in enumerate(rows):
            self.table.item(r, 0).setToolTip(tl.link_tooltip(links, "feat:" + fid, tr, danger, texts.get(fid, "")))
        self.holder.clear()
        self.holder.addItem(tr("links.none"), "")
        for ref, v in sorted(links.items()):
            self.holder.addItem("%s (%s)" % (v["name"], tr("links.kind." + v["collection"])), ref)
        self._conditions(tr, s)

    def _conditions(self, tr, s):
        """Package 36 (decision 7): the manual conditions of the feats as checkboxes."""
        while self.extra.count():
            w = self.extra.takeAt(0).widget()
            if w is not None:
                w.hide()
                w.setParent(None)
                w.deleteLater()
        self.condition_boxes = {}
        for text in tl.manual_conditions(s.character.feats):
            box = QCheckBox(tr("tabs_page.condition", text=text))
            box.setChecked(text in s.character.manual_conditions)
            box.toggled.connect(lambda on, t=text: self.run("set_manual_condition", text=t, on=bool(on)))
            self.extra.addWidget(box)
            self.condition_boxes[text] = box

    def act(self, key):
        row = self.selected()
        if row is None:
            return None
        if key == "effects":               # package 38 P5: the effect editor of the ability
            return self.open_effects("feats", row[0])
        if key == "link":                  # package 37: link the selected ability to the chosen holder ("" = none)
            return self.run("set_held_by", collection="feats", oid=row[0], holder=self.holder.currentData() or "")
        if key == "fire":                  # package 36: the manual triggers of the ability (a button on its card)
            ts = tl.manual_triggers(self.session.character.feats, row[0])
            r = None
            for tid in ts:
                r = self.run("fire_trigger", source="feat:" + row[0], tid=tid)
            return r
        return self.run("set_favorite", kind="feat", oid=row[0], on=True)


class CatalogsPage(Page):
    TAB = "catalogs"
    COLS = ("id", "name", "layer")
    ACTIONS = ("effects",)

    def __init__(self, block):
        super().__init__(block)
        self.kind = QComboBox()
        for k in ui_data.catalog_kinds():
            self.kind.addItem(k, k)
        self.kind.currentIndexChanged.connect(lambda _=0: self._show())
        self.extra.addWidget(self.kind)
        self.extra.addStretch(1)

    def show_data(self, tr, s):
        kinds = ui_data.catalog_kinds()
        for i, k in enumerate(kinds):
            self.kind.setItemText(i, tr("tabs_page.catalog_kind." + k))
        rows = ui_data.catalog_rows(s, self.kind.currentData() or kinds[0])
        self.summary.setText(tr("tabs_page.catalogs.summary", n=len(rows)))
        self.fill(rows, [(eid, name, tr("tabs_page.layer." + layer)) for eid, name, layer in rows])

    def act(self, key):
        row = self.selected()
        kind = self.kind.currentData()
        if row is None or kind not in ui_data.effect_catalog_kinds():
            return None
        return self.open_effects(catalog=(kind, row[0]))
