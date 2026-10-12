"""A config file reached by two enumeration sources is read once."""

from __future__ import annotations

from adr_discovery.contracts.records import Kind
from adr_discovery.enumerator import enumerate_candidates
from adr_discovery.pipeline import discover

CLAUDE_JSON = {
    "mcpServers": {"alpha": {"command": "npx", "args": ["a"]}, "beta": {"url": "https://beta.example/mcp"}}
}


def _world(world):
    world.dir("/Users/alice")
    world.json("/Users/alice/.claude.json", CLAUDE_JSON)
    return world


def test_the_file_really_is_reached_by_both_sources(world):
    candidates = enumerate_candidates(_world(world).gate())

    sources = {c.source for c in candidates if c.path == "/Users/alice/.claude.json"}
    assert "app_state:config" in sources and "sweep" in sources


def test_one_declaration_and_one_evidence_entry_per_server(world, catalog):
    snapshot = discover(_world(world).gate(), catalog)

    servers = {a.name: a for a in snapshot.assets if a.kind is Kind.MCP_SERVER}
    assert set(servers) == {"alpha", "beta"}
    for asset in servers.values():
        paths = [e.path for e in asset.evidence if e.path.endswith(".claude.json")]
        assert paths == ["/Users/alice/.claude.json"]
        assert not any(f.startswith("merged_") for f in asset.flags)


def test_a_symlinked_alias_of_the_same_file_is_read_once(world, catalog):
    _world(world)
    world.symlink("/Users/alice/work/.mcp.json", "/Users/alice/.claude.json")

    snapshot = discover(world.gate(), catalog)

    alpha = [a for a in snapshot.assets if a.name == "alpha"]
    assert len(alpha) == 1 and len(alpha[0].evidence) == 1
