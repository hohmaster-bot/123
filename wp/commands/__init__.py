"""Commands (D5): the only way to change a Character. The UI calls only these.

Usage: result = dispatch(ch, "take_damage", amount=10); new_ch = result.state
"""
from wp.commands.base import CHANGED, REGISTRY, CommandError, Result, dispatch  # noqa: F401
from wp.commands import (attack_cmds, combat_cmds, gear_cmds, item_cmds, maneuver_cmds,  # noqa: F401
                         pool_cmds, progression_cmds, resource_cmds, sheet_cmds, spell_cmds, training_cmds,
                         usage_cmds, edit_cmds, notebook_cmds, settings_char_cmds, reaction_cmds, doll_cmds, class_cmds, action_cmds, xp_cmds, drive_cmds)  # (register)
