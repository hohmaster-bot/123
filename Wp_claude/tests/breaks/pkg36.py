"""Break registry: package 36 (P1 owner fixes; later parts add their entries below)."""
M = ("model/test_pkg36a.py",)
UI = ("ui/test_p36a.py",)
REP = ("storage/test_reports.py",)

ENTRIES = [
    dict(id="p36-report-sections", file="Wp_claude/tests/storage/test_reports.py",
         old="    if missing:\n        bad.append((os.path.basename(path), \"missing\", missing))", new="    pass",
         suites=REP, rule="owner P1.1: a report missing a fixed section fails"),
    dict(id="p36-report-short", file="Wp_claude/tests/storage/test_reports.py",
         old="    if len(lines) < MIN_LINES:", new="    if False:", suites=REP,
         rule="owner P1.1: a truncated report fails"),
    dict(id="p36-untyped", file="wp/core/bonuses.py", old='            object.__setattr__(self, "btype", UNTYPED)',
         new='            raise ValueError("unknown bonus type: %r" % (self.btype,))', suites=M + ("core/test_bonuses.py",),
         rule="decision 17: an unknown bonus type is untyped and never raises"),
    dict(id="p36-top-menus", file="wp/ui/menus.py", old="        bar.addAction(a)", new="        pass", suites=UI,
         rule="owner P1.3: Settings and Catalog are top menus"),
    dict(id="p36-court-giver", file="wp/ui/tab_logic.py",
         old='        return [(q.qid, q.name + ((" (" + courts.get(q.giver, q.giver) + ")") if q.giver else ""),',
         new="        return [(q.qid, q.name,", suites=UI, rule="owner P1.4: a court quest names its court"),
    dict(id="p36-quest-close", file="wp/ui/tab_narrative.py",
         old='            return self.run("edit_entry", collection="quests", oid=oid, done=state != "done")',
         new="            return None", suites=UI, rule="owner P1.4: a quest is closed from the Narrative tab"),
    dict(id="p36-drive-quest", file="wp/ui/tab_pages.py",
         old='            text = self.quests.get(row[0]) or tr("tabs_page.drives.no_quest")', new='            text = ""',
         suites=UI, rule="owner P1.4: the Drives tab shows the drive quest text"),
    dict(id="p36-fit-content", file="wp/ui/blocks.py",
         old="            self.setFixedSize(max(base.width(), need.width()), max(base.height(), need.height()))",
         new="            self.setFixedSize(base)", suites=UI,
         rule="owner P1.5: after a font change a block fits its content"),
    dict(id="p36-refit", file="wp/ui/window.py",
         old="        QTimer.singleShot(0, self.refit)       # the new style sheet is polished on the next event: measure again",
         new="        pass", suites=UI, rule="owner P1.5: the sizes are measured again after the new style is applied"),
]
