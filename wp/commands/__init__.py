"""Commands (D5): the only way to change a Character. The UI calls only these.

Usage: result = dispatch(ch, "take_damage", amount=10); new_ch = result.state
"""
from wp.commands.base import CHANGED, REGISTRY, CommandError, Result, dispatch  # noqa: F401
from wp.commands import combat_cmds, resource_cmds, training_cmds  # noqa: F401  (register)
