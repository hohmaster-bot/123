"""States at HP below 0 (RULES/resources.md "Pain", statuses at hp < 0).

The player sets the state by hand (no auto-switch):
  DYING       base acting state: -2 HP per tick (hits balance like normal damage);
              3 action slots: 1 clean, 2nd and 3rd cost 1 pain each.
  RESTING     resting in negatives: unconscious, -1 HP per tick (d100 90+ stabilizes, rolled outside).
  STABILIZED  unconscious, no HP loss; replaces the two others.
Diehard: 2 clean actions, 3rd still painful, HP loss per tick 0 (custom amount possible).
Auto-stabilize: the player may always choose STABILIZED.
Concentration DC 20 (rolled outside): each success clears one more action slot.
"""
from dataclasses import dataclass

DYING = "dying"
RESTING = "resting"
STABILIZED = "stabilized"

ACTION_SLOTS = 3
CONCENTRATION_DC = 20
PAIN_PER_PAINFUL_ACTION = 1

HP_LOSS = {DYING: 2, RESTING: 1, STABILIZED: 0}


@dataclass(frozen=True)
class NegativeTraits:
    diehard: bool = False
    diehard_hp_loss: int = 0       # custom HP loss per tick with Diehard
    auto_stabilize: bool = False


def in_negatives(hp):
    return int(hp) < 0


def choose_state(hp, state, traits=NegativeTraits(), stabilize_roll_ok=False):
    """Player picks the state while HP < 0. None when HP >= 0.
    STABILIZED needs auto-stabilize or a successful d100 90+ roll (outside the app)."""
    if not in_negatives(hp):
        return None
    if state not in HP_LOSS:
        raise ValueError("unknown state: %r" % (state,))
    if state == STABILIZED and not (traits.auto_stabilize or stabilize_roll_ok):
        raise ValueError("stabilizing needs auto-stabilize or a d100 90+ roll")
    return state


def can_act(state):
    """Resting and stabilized are unconscious."""
    return state in (None, DYING)


def hp_loss_per_tick(state, traits=NegativeTraits()):
    if state is None:
        return 0
    if state == DYING and traits.diehard:
        return int(traits.diehard_hp_loss)
    return HP_LOSS[state]


def clean_actions(state, traits=NegativeTraits(), concentration_successes=0):
    """Clean action slots this turn. Dying: 1 (Diehard 2) + concentration successes, max 3."""
    if state is None:
        return ACTION_SLOTS
    if state != DYING:
        return 0
    base = 2 if traits.diehard else 1
    return min(ACTION_SLOTS, base + max(0, int(concentration_successes)))


def painful_slots(state, traits=NegativeTraits(), concentration_successes=0):
    """Slot numbers (1-based) that cost pain: shown red in the UI."""
    clean = clean_actions(state, traits, concentration_successes)
    if state != DYING:
        return ()
    return tuple(range(clean + 1, ACTION_SLOTS + 1))


def action_pain(actions_used, state, traits=NegativeTraits(), concentration_successes=0):
    """Pain for the actions spent this turn: 1 per used slot beyond the clean ones."""
    used = int(actions_used)
    if used > ACTION_SLOTS:
        raise ValueError("only %d action slots" % ACTION_SLOTS)
    if state != DYING:
        if used and not can_act(state):
            raise ValueError("unconscious: cannot act")
        return 0
    clean = clean_actions(state, traits, concentration_successes)
    return PAIN_PER_PAINFUL_ACTION * max(0, used - clean)
