"""The Race tab (package 36 P3; owner decision 15; RULES/races.md). Replaces the placeholder (the Class tab stays one).

The race view (name, module, type tags, speed, languages, the race effects) and the race abilities (name, price in
training, the ability it needs, taken; the text on hover). Take race / Change race choose a race of the catalog
(game-module data: nothing hard-coded); Change race first shows the list of everything the old race gave and asks
to confirm (change_race confirm=True: one command, one undo step, no refund). A priced ability has "Take" (the normal
purchase: buy_race_ability). Empty state when the character has no race.
"""
from PySide6.QtWidgets import QComboBox

from wp.app import ui_data
from wp.ui.tab_pages import Page, yes

NEWLINE = "\n"


class RacePage(Page):
    TAB = "race"
    COLS = ("name", "price", "needs", "taken")
    ACTIONS = ("take", "change", "buy")
    NEEDS_ROW = False

    def __init__(self, block):
        super().__init__(block)
        self.choice = QComboBox()
        self.extra.addWidget(self.choice, 1)
        self.view = None

    def show_data(self, tr, s):
        v = self.view = s.view("race")
        races = ui_data.catalog_rows(s, "races")
        keep = self.choice.currentData()
        self.choice.clear()
        for rid, name, _layer in races:
            self.choice.addItem(name or rid, rid)
        if keep is not None and self.choice.findData(keep) >= 0:
            self.choice.setCurrentIndex(self.choice.findData(keep))
        rows = list(v["abilities"])
        if v["race_id"]:
            self.summary.setText(tr("tabs_page.race.summary", name=v["name"], module=v["module"],
                                    tags=", ".join(v["type_tags"]), speed=v["speed"],
                                    langs=", ".join(n + (" *" if native else "") for n, native in v["languages"])))
        else:
            self.summary.setText(tr("tabs_page.race.none"))
        self.fill(rows, [(name, price or "", needs, yes(tr, taken)) for _aid, name, _text, price, needs, taken in rows])
        for r, (_aid, _name, text, _price, _needs, _taken) in enumerate(rows):
            for c in range(self.table.columnCount()):
                self.table.item(r, c).setToolTip(text)
        self.buttons["take"].setEnabled(not v["race_id"] and bool(races))
        self.buttons["change"].setEnabled(bool(v["race_id"]) and bool(races))
        self.buttons["buy"].setEnabled(bool(rows))

    def entry(self):
        rid = self.choice.currentData()
        return ui_data.catalog_entry(self.session, "races", rid) if rid else None

    def change_list(self):
        """The names of everything the current race gave (the confirmation list)."""
        r = self.session.dispatch("change_race", race=self.entry(), confirm=False)
        return list(r.params.get("values", ("",)))[0].split(", ") if not r.ok else []

    def act(self, key):
        if key == "take":
            return self.run("take_race", race=self.entry())
        if key == "change":
            gone = self.change_list()
            text = self._tr("tabs_page.race.confirm", items=NEWLINE.join(gone))
            if not self.block.win.ask(text):
                return None
            return self.run("change_race", race=self.entry(), confirm=True)
        row = self.selected()
        return None if row is None else self.run("buy_race_ability", aid=row[0])
