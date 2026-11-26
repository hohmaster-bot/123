"""Command plumbing (D5): validate -> new state -> action log -> 'changed' event.

A command is a plain function `cmd(ch, **params) -> Result`. It never mutates
the character: it returns a new one. `dispatch` looks a command up by name,
runs it and calls listeners (the future UI) with the result.
"""
from dataclasses import dataclass, field, replace
from typing import Any, Dict, Tuple

from wp.model.character import LogEntry

CHANGED = "changed"
INVALID = "invalid_value"          # reason of a plain ValueError from the core
NOT_FOUND = "not_found"            # reason of a KeyError (unknown id)
UNKNOWN_COMMAND = "unknown_command"
WRONG_TYPE = "wrong_type"


class CommandError(ValueError):
    """Validation failed: the state is unchanged (package 16 A4).

    reason: a stable id of the refusal kind (the UI picks its text by it later; the English text stays for now).
    params: numbers / ids for that text; "values" = the arguments of the English message, in order."""

    def __init__(self, text="", reason=INVALID, **params):
        super().__init__(text)
        self.text = text
        self.reason = reason or INVALID
        self.params = dict(params)


@dataclass(frozen=True)
class Result:
    state: Any                         # the new Character
    entry: LogEntry
    events: Tuple[str, ...] = (CHANGED,)
    info: Dict[str, Any] = field(default_factory=dict)


def normalize(ch):
    """States at HP < 0 exist only while HP < 0 (resources.md): at HP >= 0 the state is cleared. In combat the
    balance never stays above the current balance cap (package 22 A3: restores are clamped, not refused)."""
    if ch.negative_state is not None and ch.hp_current >= 0:
        ch = replace(ch, negative_state=None)
    if ch.in_combat:
        from wp.model import derived_view as dv
        cap = dv.balance_max(ch)
        if ch.balance_current > cap:
            ch = replace(ch, balance_current=cap)
    return ch


def commit(ch, command, summary, info=None):
    """Wrap the new (normalized) state in a Result. The journal entry is written by dispatch (package 14 H:
    ids and numbers only); `summary` is a developer note and is NOT stored."""
    return Result(state=normalize(ch), entry=LogEntry(command=command), info=dict(info or {}))


REGISTRY = {}


def command(fn):
    """Register a command under its function name."""
    REGISTRY[fn.__name__] = fn
    return fn


def _fire_events(before, result, cmd):
    """The events of the command (end_cycle -> cycle_end ...) and "HP fell below 1" fire their triggers."""
    from wp.model import trigger_view as tv
    state = result.state
    if not hasattr(state, "trigger_notes"):
        return result
    event = tv.EVENT_OF.get(cmd)
    if event:
        state = tv.fire(state, event)
    if before.hp_current >= 1 > state.hp_current:
        state = tv.fire(state, tv.HP_BELOW_ONE)
    return result if state is result.state else replace(result, state=state)


def dispatch(ch, cmd, listeners=(), /, **params):
    """Run a command by name; on success notify listeners(result)."""
    if cmd not in REGISTRY:
        raise CommandError("unknown command: %r" % (cmd,), UNKNOWN_COMMAND, command=cmd)
    from wp.commands import params as cp
    from wp.model import cache
    from wp.rules_data import rules as rd
    from wp.storage import typecheck
    cache.clear()                      # a read cache never survives a command (package 23 B)
    try:
        with rd.using(ch):             # rule constants of this character (package 20, D23)
            cp.check(cmd, REGISTRY[cmd], params, ch)     # declared parameter types first (package 27 B, D29)
            result = REGISTRY[cmd](ch, **params)
    except CommandError:
        raise
    except KeyError as e:
        raise CommandError(str(e), NOT_FOUND)
    except ValueError as e:
        raise CommandError(str(e), INVALID)
    except (TypeError, AttributeError, OverflowError, RecursionError, ZeroDivisionError) as e:
        # a safety net, not the main check (package 27 B): a wrong value never crashes the UI
        raise CommandError("invalid value for %s: %s" % (cmd, e), INVALID, command=cmd)
    bad = typecheck.character_problem(result.state, ch)
    if bad:                            # the result must still fit the stored types (review 5 F5)
        raise CommandError("the result of %s does not fit the character: %s" % (cmd, bad), WRONG_TYPE, command=cmd,
                           values=(bad,))
    result = _fire_events(ch, result, cmd)   # package 36 (decision 6): event triggers become reminder notes
    if CHANGED in result.events and result.state == ch:
        result = replace(result, events=tuple(e for e in result.events if e != CHANGED))   # no-op: not logged (F7)
    if CHANGED in result.events:       # read-only / refused-softly / no-op commands are not logged
        from wp.commands import journal
        result = journal.record(ch, result, cmd, params)
    for listener in listeners:
        listener(result)
    return result
