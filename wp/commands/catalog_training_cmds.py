"""Buying a catalog training (package 37, owner decision 2): buy_training(training, units). The entry comes from the
catalog (the Session / UI gives it); refused while locked (the unlock is missing), above the limit, or without enough
training points; the price per unit times units is paid; the units are counted on the character (TrainingTaken, a
snapshot of the unit effects). Journal, undo; no refund.
"""
from dataclasses import replace

from wp.catalog import convert
from wp.commands.base import CommandError, command, commit
from wp.core import training as tr
from wp.model import trainings as trn
from wp.model.training_taken import TrainingTaken


@command
def buy_training(ch, training=None, units=1):
    e = training
    if not e or not isinstance(e, dict) or not e.get("id"):
        raise CommandError("no training entry given", "no_training_given")
    units = int(units)
    if units < 1:
        raise CommandError("buy at least one unit", "out_of_range", values=(units, 1, None), min=1)
    ok, why = trn.unlocked(ch, e)
    if not ok:
        raise CommandError("the training %s is locked" % e["id"], "training_locked", values=(e["id"],) + tuple(why[1]))
    have, cap = trn.units(ch, e["id"]), trn.limit(ch, e)
    if cap is not None and have + units > cap:
        raise CommandError("the limit of %s is %d units" % (e["id"], cap), "training_limit", values=(e["id"], cap, have))
    cost = trn.price(ch, e) * units
    try:
        left = tr.pay(ch.training, cost, tr.TRAINING)
    except ValueError as err:
        raise CommandError(str(err), "rule_refused")
    old = trn.taken(ch, e["id"])
    rec = TrainingTaken(e["id"], e.get("name", e["id"]), have + units,
                        tuple(convert.effect(x) for x in e.get("effects", ())), e.get("module", ""))
    if old is not None:
        rec = replace(old, units=have + units)
        rows = tuple(rec if t.tid == e["id"] else t for t in ch.trainings)
    else:
        rows = ch.trainings + (rec,)
    return commit(replace(ch, trainings=rows, training=left), "buy_training", "%s +%d for %d" % (e["id"], units, cost),
                  {"cost": cost, "units": have + units})
