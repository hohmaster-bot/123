"""The heavy content tabs (package 35 P4): Inventory, Training, Skills, Feats, Catalogs (wp/ui/tab_pages.py has the
common Page and the module rules). Inventory: items, weight, worn / in hands, the load; Equip / Take off
(equip_item / unequip_item). Training: training points, level, base slots, reactions, comfort, attention and the item
qualifications (buy_item_qualification). Skills: name, tier, ranks, bonus; +1 rank (buy_skill_rank). Feats: the
character's feats with charges and cooldown; a star makes one a favourite (set_favorite). Catalogs: a read-only browser
of every catalog kind (shipped, override and own entries; game-module data, nothing hard-coded).
"""
from PySide6.QtWidgets import QComboBox

from wp.app import ui_data
from wp.ui import params_logic as pl
from wp.ui import tab_logic as tl
from wp.ui.tab_pages import Page, yes


class InventoryPage(Page):
    TAB = "inventory"
    COLS = ("name", "weight", "quantity", "worn", "in_hands", "state")
    ACTIONS = ("equip", "unequip")

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

    def act(self, key):
        row = self.selected()
        if row is None:
            return None
        return self.run("equip_item" if key == "equip" else "unequip_item", iid=row[0])


class TrainingPage(Page):
    TAB = "training"
    COLS = ("name", "qualification", "bought")
    ACTIONS = ("qualify",)

    def show_data(self, tr, s):
        v = s.view("training")
        tp, level, slots, reactions, comfort, attention = tl.training_summary(v)
        self.summary.setText(tr("tabs_page.training.summary", tp=tp, level=level, slots=slots, reactions=reactions,
                                comfort=comfort, attention=attention))
        rows = tl.qualification_rows(s.character.items)
        self.fill(rows, [(name, n, yes(tr, bought)) for _iid, name, n, bought in rows])

    def act(self, key):
        row = self.selected()
        return None if row is None else self.run("buy_item_qualification", iid=row[0])


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
    ACTIONS = ("favorite",)

    def show_data(self, tr, s):
        rows = tl.feat_rows(s.view("sheet"))
        n = len(ui_data.catalog_rows(s, "feats"))
        self.summary.setText(tr("tabs_page.feats.summary", n=len(rows), catalog=n))
        self.fill(rows, [(title or fid, "" if charges is None else charges, "" if cooldown is None else cooldown)
                         for fid, title, charges, cooldown in rows])

    def act(self, key):
        row = self.selected()
        return None if row is None else self.run("set_favorite", kind="feat", oid=row[0], on=True)


class CatalogsPage(Page):
    TAB = "catalogs"
    COLS = ("id", "name", "layer")
    ACTIONS = ()

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
        return None
