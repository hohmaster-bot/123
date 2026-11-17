"""Iterative attack penalties (RULES/combat.md "Attack tag and iteration").

Options spent in the own turn may carry the "attack" tag. The 2nd tagged option
gets -5, the 3rd -10. A paired (two-weapon) option is one option: the penalty
applies to both attacks. Options without the tag take no penalty. An effect flag
"ignores iterative" makes a tagged option count as untagged (e.g. master bonus).
"""
from dataclasses import dataclass

ITERATIVE_STEP = -5


@dataclass(frozen=True)
class TurnOption:
    name: str
    attack_tag: bool = False
    paired: bool = False             # two-weapon pair: one option, two attacks
    ignores_iterative: bool = False  # effect flag


def counts_as_attack(opt):
    return opt.attack_tag and not opt.ignores_iterative


def iterative_penalties(options):
    """Penalty per option, in turn order. A paired option's penalty applies to both attacks."""
    out = []
    k = 0
    for opt in options:
        if counts_as_attack(opt):
            out.append(ITERATIVE_STEP * k)
            k += 1
        else:
            out.append(0)
    return tuple(out)


def attack_penalties(options):
    """Penalty per single attack (a paired option gives two equal entries)."""
    out = []
    for opt, pen in zip(options, iterative_penalties(options)):
        if not opt.attack_tag:
            continue
        out.extend([pen, pen] if opt.paired else [pen])
    return tuple(out)
