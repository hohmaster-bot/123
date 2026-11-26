"""Package 35 P2: the sources of the bottom strip numbers (OT, pain, morale) and the journal note command. Numbers by
hand from RULES (resources.md "OT", "Pain"; defense.md morale scale). Run: python Wp_claude/tests/model/test_pkg35b.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.model import sources as src  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.model.source_row import SourceRow  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_pkg35b")


def sv(ch, number):
    with rd.using(ch):
        return src.view(ch, number)


def counted(v):
    return sum(r["value"] for r in v["rows"] if r["counted"])


def ref(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


HERO = Character(trauma=3, hp_current=-7, pain=(PainEntry(2, "wound"), PainEntry(1, "", True)), morale_scale=2,
                 statuses=(Status("Banner", sid="banner", active=True, effects=(Effect("morale_scale", 1),)),),
                 source_rows=(SourceRow("drum", "morale", "Drum", 2),))

# OT 3 stored; pain 2 + 1 + floor(7 / 3) = 2 from HP -7 -> 5; morale 2 + banner 1 + drum 2 = 5
S.case("n-totals", "resources.md / defense.md: OT 3; pain 2 + 1 + 2 (HP -7: floor(7 / 3)) = 5; morale scale "
       "2 + 1 + 2 = 5; the counted rows add up", ((3, 3), (5, 5), (5, 5)))(
    lambda: tuple((sv(HERO, n)["total"], counted(sv(HERO, n))) for n in ("ot", "pain", "morale")))
S.case("n-rows", "pkg 35: pain rows = each entry (its source or 'pain entry') and the HP pain; morale rows = stored "
       "scale, the buff, the manual row",
       (["wound", "source.pain_entry", "source.pain_hp"], ["morale_scale", "Banner", "drum"]))(
    lambda: ([r["name"] for r in sv(HERO, "pain")["rows"]], [r["id"] for r in sv(HERO, "morale")["rows"]]))
S.case("n-editable", "pkg 35: OT and pain have no effect target (read-only); morale rows use the target morale_scale",
       (False, False, True, "sources_read_only", "allowed"))(
    lambda: (sv(HERO, "ot")["editable_target"], sv(HERO, "pain")["editable_target"],
             sv(HERO, "morale")["editable_target"],
             ref(lambda: dispatch(HERO, "source_add", number="ot", name="x", value=1)),
             ref(lambda: dispatch(HERO, "source_add", number="morale", name="x", value=1))))


def _note():
    r = dispatch(Character(), "journal_note", text="Met the Duke")
    e = r.state.log[-1]
    return e.command, e.kind, e.params.get("text"), r.state.journal_notes, \
        ref(lambda: dispatch(Character(), "journal_note", text="  "))


S.case("j-note", "pkg 35: journal_note writes a journal line (kind note) with the player's text; an empty note refused",
       ("journal_note", "note", "Met the Duke", 1, "note_needs_text"))(_note)

if __name__ == "__main__":
    sys.exit(S.run())
