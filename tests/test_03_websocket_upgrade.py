"""
Verifies EaglerXServer successfully upgrades HTTP to WebSocket.
Uses Eaglercraft-compatible headers (Origin, User-Agent) to pass
the EaglerXServer initial handler validation.
"""

import asyncio
import pytest
import websockets


EAGLERCRAFT_ORIGIN = "https://eaglercraft.com"


@pytest.mark.asyncio
async def test_websocket_upgrade(ws_url):
    """WebSocket connection should upgrade successfully with Eaglercraft headers."""
    try:
        async with websockets.connect(
            ws_url,
            origin=EAGLERCRAFT_ORIGIN,
            user_agent_header="EaglercraftX/1.12.2",
            close_timeout=5,
        ) as ws:
            # Connection established, wait briefly to ensure it stays open
            await asyncio.sleep(1)
            assert ws.open, "WebSocket closed unexpectedly during wait period"
    except ConnectionRefusedError:
        pytest.fail(f"WebSocket connection refused at {ws_url}")
    except websockets.exceptions.InvalidStatusCode as e:
        pytest.fail(f"WebSocket upgrade failed with HTTP status: {e}")
    except EOFError:
        pytest.fail(f"WebSocket connection closed immediately (EaglerXServer rejected upgrade). "
                     f"Check origin_whitelist in listeners.yml — allow_all_origins may be needed.")
    except Exception as e:
        pytest.fail(f"Unexpected WebSocket error: {type(e).__name__}: {e}")
