"""Core iterative attacks vs RULES/combat.md. Run: python Wp_claude/tests/core/test_combat.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core.combat import TurnOption as O, attack_penalties, iterative_penalties  # noqa: E402

S = Suite("test_combat")

A = O("attack", attack_tag=True)

S.case("iterative", "combat.md [OWNER]: 2nd tagged -5, 3rd -10", (0, -5, -10))(
    lambda: iterative_penalties([A, A, A]))
S.case("untagged-free", "combat.md: options without the tag take no penalty and do not count",
       (0, 0, -5))(lambda: iterative_penalties([A, O("move"), A]))
S.case("paired-both", "combat.md: paired attacks, penalty applies to both", (0, -5, -5))(
    lambda: attack_penalties([A, O("two weapons", attack_tag=True, paired=True)]))
S.case("ignore-flag", "combat.md: effect flag ignores the iterative penalty", (0, 0, -5))(
    lambda: iterative_penalties([A, O("master attack", attack_tag=True, ignores_iterative=True), A]))
S.case("spell-attack-tag", "combat.md: spells needing an attack roll carry the tag", (0, -5))(
    lambda: iterative_penalties([A, O("ray", attack_tag=True)]))

if __name__ == "__main__":
    sys.exit(S.run())
