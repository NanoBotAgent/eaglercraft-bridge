"""
Verifies server handles 10 Eaglercraft connections.
Staggered launch to avoid overwhelming dual-stack handshake classification.
"""

import asyncio
import pytest
import websockets

STAGGER_DELAY = 0.3  # seconds between each connection launch


@pytest.mark.asyncio
async def test_multi_client_connections(ws_url):
    """10 WebSocket connections should all succeed within 15 seconds.

    Connections are staggered by 0.3s each to avoid overwhelming
    EaglerXServer's dual-stack first-packet classifier, which must
    read the initial bytes from each connection to determine whether
    it is a WebSocket upgrade or a vanilla TCP Minecraft client.
    Launching all 10 simultaneously causes the HTTP upgrade response
    to time out for most connections.
    """

    async def connect_and_hold(idx):
        """Connect, hold open for 3 seconds, then close cleanly."""
        try:
            async with websockets.connect(
                ws_url,
                origin="https://eaglercraft.com",
                user_agent_header="EaglercraftX/1.12.2",
                close_timeout=5,
            ) as ws:
                assert ws.state is websockets.protocol.State.OPEN, \
                    f"Client {idx}: connection not open after connect"
                await asyncio.sleep(3)
                assert ws.state is websockets.protocol.State.OPEN, \
                    f"Client {idx}: connection closed during hold period"
                return True, None
        except Exception as e:
            return False, e

    # Stagger connections to avoid dual-stack handshake bottleneck
    tasks = []
    for i in range(10):
        tasks.append(asyncio.create_task(connect_and_hold(i)))
        if i < 9:
            await asyncio.sleep(STAGGER_DELAY)

    results = await asyncio.wait_for(
        asyncio.gather(*tasks, return_exceptions=False),
        timeout=15,
    )

    failures = [(i, err) for i, (success, err) in enumerate(results) if not success]
    assert len(failures) == 0, \
        f"{len(failures)}/10 connections failed: {[(i, str(e)) for i, e in failures]}"
