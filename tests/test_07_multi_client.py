"""
Verifies server handles 10 Eaglercraft connections.

Staggered launch to avoid overwhelming EaglerXServer's connection
rate limiter. The default config allows ~15 connections per minute
per IP, but the rate limiter window is shorter on localhost.
"""

import asyncio
import pytest
import websockets

# EaglerXServer rate-limits connections from the same IP.
# 1.5s stagger gives the rate limiter time to accept each connection.
STAGGER_DELAY = 1.5  # seconds between each connection launch
HOLD_TIME = 3.0      # seconds to hold each connection open


@pytest.mark.asyncio
async def test_multi_client_connections(ws_url):
    """10 WebSocket connections should all succeed within 30 seconds.

    Connections are staggered by 1.5s each to avoid triggering
    EaglerXServer's connection rate limiter, which rejects rapid
    sequential connections from the same IP with an HTTP error.
    """
    async def connect_and_hold(idx):
        """Connect, hold open for a few seconds, then close cleanly."""
        try:
            async with websockets.connect(
                ws_url,
                origin="https://eaglercraft.com",
                user_agent_header="EaglercraftX/1.12.2",
                close_timeout=5,
            ) as ws:
                assert ws.state is websockets.protocol.State.OPEN, \
                    f"Client {idx}: connection not open after connect"
                await asyncio.sleep(HOLD_TIME)
                assert ws.state is websockets.protocol.State.OPEN, \
                    f"Client {idx}: connection closed during hold period"
                return True, None
        except Exception as e:
            return False, e

    # Stagger connections to avoid rate limiting
    tasks = []
    for i in range(10):
        tasks.append(asyncio.create_task(connect_and_hold(i)))
        if i < 9:
            await asyncio.sleep(STAGGER_DELAY)

    results = await asyncio.wait_for(
        asyncio.gather(*tasks, return_exceptions=False),
        timeout=30,
    )

    failures = [(i, err) for i, (success, err) in enumerate(results) if not success]
    assert len(failures) == 0, \
        f"{len(failures)}/10 connections failed: {[(i, str(e)) for i, e in failures]}"
