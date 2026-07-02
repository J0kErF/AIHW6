"""MCP server integration tests (in-memory FastMCP transport)."""
import pytest

from src.common.schemas import Role
from src.servers.base_server import create_server
from src.servers.client import GameMcpClient
from tests.conftest import make_config

TOKEN = "test-token-123"


def thief_server(tmp_path):
    cfg = make_config(logging={"dir": str(tmp_path)})
    return create_server(Role.THIEF, cfg, token=TOKEN)


async def test_handshake_rejects_bad_token(tmp_path):
    server = thief_server(tmp_path)
    async with GameMcpClient(server, token="wrong") as c:
        with pytest.raises(Exception, match="invalid token"):
            await c.handshake("moamteam", "cop")


async def test_handshake_and_game_config(tmp_path):
    server = thief_server(tmp_path)
    async with GameMcpClient(server, token=TOKEN) as c:
        sid = await c.handshake("moamteam", "cop")
        assert sid
        gc = await c.get_game_config()
        assert gc["server_role"] == "thief"
        assert gc["grid_size"] == [5, 5] and gc["max_moves"] == 25


async def test_invalid_session_rejected(tmp_path):
    server = thief_server(tmp_path)
    async with GameMcpClient(server, token=TOKEN) as c:
        c.session_id = "forged"
        with pytest.raises(Exception, match="invalid or expired"):
            await c.send_message(0, "hello")


async def test_fifty_messages_order_and_no_loss(tmp_path):
    server = thief_server(tmp_path)
    async with GameMcpClient(server, token=TOKEN) as sender, GameMcpClient(
        server, token=TOKEN
    ) as receiver:
        sid = await sender.handshake("moamteam", "cop")
        receiver.session_id = sid  # same session: sender deposits, agent-side reads
        for i in range(50):
            await sender.send_message(i, f"free text message number {i}")
        got = []
        while True:
            msg = await receiver.receive_message()
            if msg["empty"]:
                break
            got.append(msg)
        assert [m["turn"] for m in got] == list(range(50))
        assert got[7]["text"] == "free text message number 7"


async def test_verify_state_detects_divergence(tmp_path):
    server = thief_server(tmp_path)
    async with GameMcpClient(server, token=TOKEN) as c:
        await c.handshake("moamteam", "thief")
        await c.report_position(3, (1, 2))
        ok = await c.verify_state(3)
        assert ok["ok"] and ok["expected_turn"] == 3
        bad = await c.verify_state(5)
        assert not bad["ok"] and bad["expected_turn"] == 3


async def test_audit_log_written(tmp_path):
    server = thief_server(tmp_path)
    async with GameMcpClient(server, token=TOKEN) as c:
        await c.handshake("moamteam", "cop")
        await c.send_message(0, "hi")
    log = tmp_path / "mcp_thief.jsonl"
    assert log.exists()
    content = log.read_text(encoding="utf-8")
    assert "handshake" in content and "send_message" in content
