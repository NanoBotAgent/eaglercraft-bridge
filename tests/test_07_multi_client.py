"""
Verifies server handles 10 simultaneous Eaglercraft connections.
"""

import asyncio
import pytest
import websockets


@pytest.mark.asyncio
async def test_multi_client_connections(ws_url):
    """10 simultaneous WebSocket connections should all succeed within 10 seconds."""

    async def connect_and_hold(idx):
        """Connect, hold open for 3 seconds, then close cleanly."""
        try:
            async with websockets.connect(ws_url, origin="https://eaglercraft.com", user_agent_header="EaglercraftX/1.12.2", close_timeout=5) as ws:
                assert ws.open, f"Client {idx}: connection not open after connect"
                await asyncio.sleep(3)
                assert ws.open, f"Client {idx}: connection closed during hold period"
            return True, None
        except Exception as e:
            return False, e

    # Launch 10 simultaneous connections
    tasks = [connect_and_hold(i) for i in range(10)]
    results = await asyncio.wait_for(
        asyncio.gather(*tasks, return_exceptions=False),
        timeout=10
    )

    failures = [(i, err) for i, (success, err) in enumerate(results) if not success]
    assert len(failures) == 0, \
        f"{len(failures)}/10 connections failed: {[(i, str(e)) for i, e in failures]}"
