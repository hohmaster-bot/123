"""Command plumbing (D5): validate -> new state -> action log -> 'changed' event.

A command is a plain function `cmd(ch, **params) -> Result`. It never mutates
the character: it returns a new one. `dispatch` looks a command up by name,
runs it and calls listeners (the future UI) with the result.
"""
from dataclasses import dataclass, field, replace
from typing import Any, Dict, Tuple

from wp.model.character import LogEntry

CHANGED = "changed"


class CommandError(ValueError):
    """Validation failed: the state is unchanged."""


@dataclass(frozen=True)
class Result:
    state: Any                         # the new Character
    entry: LogEntry
    events: Tuple[str, ...] = (CHANGED,)
    info: Dict[str, Any] = field(default_factory=dict)


def normalize(ch):
    """States at HP < 0 exist only while HP < 0 (resources.md): at HP >= 0 the state is cleared."""
    if ch.negative_state is not None and ch.hp_current >= 0:
        return replace(ch, negative_state=None)
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


def dispatch(ch, cmd, listeners=(), /, **params):
    """Run a command by name; on success notify listeners(result)."""
    if cmd not in REGISTRY:
        raise CommandError("unknown command: %r" % (cmd,))
    try:
        result = REGISTRY[cmd](ch, **params)
    except CommandError:
        raise
    except (ValueError, KeyError) as e:
        raise CommandError(str(e))
    if CHANGED in result.events:       # read-only / refused-softly commands are not logged
        from wp.commands import journal
        result = journal.record(ch, result, cmd, params)
    for listener in listeners:
        listener(result)
    return result
