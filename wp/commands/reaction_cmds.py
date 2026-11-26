"""Reactions as a resource and the manual mana restore (package 22 A1, A2; RULES/combat.md, classes_magic.md).

Reactions: a resource with the fixed id "reactions": max = the bought reactions (+ effects "reactions"),
current = Character.reactions_current (None = full). spend_reaction(n) (free attacks of opportunity, readied
attacks: the player presses), restore_reactions (manual, edit level). The zero-initiative tick (a new round) and
the end of combat bring them back to max. An attack record with cost_reactions spends them in use_attack.
restore_mana(amount): a manual mana restore (a GM narrative effect or an ability): up to the max (an over-max value
is kept, never raised further), refused while a block_restore covers mana. The rest regeneration of mana is separate.
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import damage as dm
from wp.model import blocks as blk
from wp.model import derived_view as dv

RESOURCE = "reactions"
NOT_ENOUGH = "not_enough_reactions"


def reactions_max(ch):
    return dv.reactions(ch)


def reactions_current(ch):
    mx = reactions_max(ch)
    return mx if ch.reactions_current is None else max(0, ch.reactions_current)


def reactions_pool(ch):
    return dm.Pool(reactions_current(ch), reactions_max(ch))


def spend(ch, n):
    """The character with n reactions spent, or CommandError not_enough_reactions."""
    n = int(n)
    have = reactions_current(ch)
    if n < 0:
        raise CommandError("cannot spend a negative number of reactions", "cannot_spend_negative_amount")
    if have < n:
        raise CommandError("not enough reactions: need %d, have %d" % (n, have), NOT_ENOUGH, values=(n, have))
    return replace(ch, reactions_current=have - n)


def refill(ch):
    return replace(ch, reactions_current=None)


@command
def spend_reaction(ch, n=1):
    new = spend(ch, n)
    return commit(new, "spend_reaction", "reactions -%d" % int(n), {"left": reactions_current(new)})


@command
def restore_reactions(ch):
    return commit(refill(ch), "restore_reactions", "reactions to max")


@command
def return_reaction(ch, n=1):
    """Give back n spent reactions (owner, package 35: a click on a spent square returns that one)."""
    n = int(n)
    have, mx = reactions_current(ch), reactions_max(ch)
    if have + n > mx:
        raise CommandError("only %d reactions are spent" % (mx - have), "nothing_spent", values=(n, mx - have))
    new = replace(ch, reactions_current=None if have + n == mx else have + n)
    return commit(new, "return_reaction", "reactions +%d" % n, {"left": have + n})


@command
def restore_mana(ch, amount=0):
    amount = int(amount)
    if amount < 0:
        raise CommandError("amount must be >= 0", "amount_must_0")
    if blk.restore_blocked(ch, "mana"):
        raise CommandError("restoring mana is blocked by %s" % ", ".join(blk.restore_block_reasons(ch, "mana")),
                           "restoring_blocked", values=("mana", ", ".join(blk.restore_block_reasons(ch, "mana"))))
    before = dv.mana_pool(ch)
    after = dm.restore(before, amount)
    return commit(replace(ch, mana=replace(ch.mana, current=after.current)), "restore_mana",
                  "mana %d -> %d" % (before.current, after.current), {"gained": after.current - before.current})
