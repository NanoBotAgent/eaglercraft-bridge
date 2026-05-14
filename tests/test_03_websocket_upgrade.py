"""
Verifies EaglerXServer successfully upgrades HTTP to WebSocket.
"""

import asyncio
import pytest
import websockets


@pytest.mark.asyncio
async def test_websocket_upgrade(ws_url):
    """WebSocket connection should upgrade successfully and stay open for 2 seconds."""
    try:
        async with websockets.connect(ws_url, close_timeout=5) as ws:
            # Connection established, wait 2 seconds to ensure it stays open
            await asyncio.sleep(2)
            assert ws.open, "WebSocket closed unexpectedly during wait period"
    except ConnectionRefusedError:
        pytest.fail(f"WebSocket connection refused at {ws_url}")
    except websockets.exceptions.InvalidStatusCode as e:
        pytest.fail(f"WebSocket upgrade failed with HTTP status: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected WebSocket error: {e}")
