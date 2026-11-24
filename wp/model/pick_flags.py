"""Stored-only weapon picks shown as "available abilities" (package 25 E, RULES/weapons.md): one attack per turn
without the [attack] tag, ignore the first vulnerability in a fight, ignore 20% cover. No numbers change.
"Ignore the first vulnerability in a fight" is once per fight: a usage charge (max 1, recharge at the end of combat,
the COUNTER_PICKS mechanism of package 17; spend_charge owner kind "pick"). The other two only show.
"""
from wp.core import weapons as wpn
from wp.model import usage as us

FLAG_PICKS = ("no_attack_tag", "ignore_vulnerability", "ignore_cover_20")
TEXT = "pick."                         # i18n key prefix of the ability text


def _flag(entry, pick):
    counter = pick.bonus in wpn.COUNTER_PICKS
    return {"pick": us.pick_id(entry, pick), "bonus": pick.bonus, "text": TEXT + pick.bonus, "weapon": entry.weapon.name,
            "charges": us.charges(us.PICK, pick) if counter else None}


def abilities(ch, group=None):
    """Flags of the character (group None) or of one weapon node (an attack record's group)."""
    return tuple(_flag(e, p) for e in ch.weapons if group is None or e.weapon.name == group
                 for p in e.picks if p.bonus in FLAG_PICKS)
