"""Traversal cost: what the sweep spends its budget on.

Each case builds a small tree on disk and drives the real gate over it, so
the budget numbers are the ones a live scan would produce.
"""

from __future__ import annotations

from adr_discovery.enumerator import enumerate_candidates
from adr_discovery.world.budget import Budget


def _paths(candidates, suffix: str) -> list[str]:
    return [c.path for c in candidates if c.path.endswith(suffix)]


def _boundaries(gate, kind: str):
    return [b for b in gate.ledger.freeze().boundaries_hit if b.boundary == kind]


def test_excluded_tree_costs_no_budget(world):
    for i in range(3000):
        world.file(f"/Users/alice/.cache/blob/f{i}", "x")
    world.file("/Users/alice/.claude/skills/x/SKILL.md", "---\nname: x\n---\n")
    gate = world.gate(budget=Budget(max_entries=200))

    found = enumerate_candidates(gate)

    assert gate.budget.entries_used < 50, "a skipped tree must not be listed or charged"
    assert _paths(found, "/.claude/skills")
    assert not _boundaries(gate, "budget_exhausted")
