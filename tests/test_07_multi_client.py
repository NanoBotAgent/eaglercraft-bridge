"""
Verifies server handles 10 Eaglercraft connections.

Each connection uses retry logic with exponential backoff
to handle transient connection failures.
"""

import asyncio
import pytest
import websockets

STAGGER_DELAY = 1.0  # seconds between each connection launch
HOLD_TIME = 3.0      # seconds to hold each connection open
MAX_CONNECT_RETRIES = 3


async def connect_with_retry(ws_url, max_retries=MAX_CONNECT_RETRIES):
    """Connect with retry to handle transient failures."""
    for attempt in range(max_retries):
        if attempt > 0:
            await asyncio.sleep(1.0 * attempt)  # linear backoff
        try:
            ws = await websockets.connect(
                ws_url,
                origin="https://eaglercraft.com",
                user_agent_header="EaglercraftX/1.12.2",
                close_timeout=5,
            )
            return ws
        except websockets.exceptions.InvalidMessage:
            if attempt == max_retries - 1:
                raise
            continue
    raise ConnectionError("Failed to connect after retries")


@pytest.mark.asyncio
async def test_multi_client_connections(ws_url):
    """10 WebSocket connections should all succeed within 45 seconds.

    Connections are staggered by 1s and use retry logic
    to handle transient connection failures.
    """
    async def connect_and_hold(idx):
        """Connect, hold open for a few seconds, then close cleanly."""
        try:
            async with await connect_with_retry(ws_url) as ws:
                assert ws.state is websockets.protocol.State.OPEN, \
                    f"Client {idx}: connection not open after connect"
                await asyncio.sleep(HOLD_TIME)
                assert ws.state is websockets.protocol.State.OPEN, \
                    f"Client {idx}: connection closed during hold period"
                return True, None
        except Exception as e:
            return False, e

    # Stagger connections
    tasks = []
    for i in range(10):
        tasks.append(asyncio.create_task(connect_and_hold(i)))
        if i < 9:
            await asyncio.sleep(STAGGER_DELAY)

    results = await asyncio.wait_for(
        asyncio.gather(*tasks, return_exceptions=False),
        timeout=45,
    )

    failures = [(i, err) for i, (success, err) in enumerate(results) if not success]
    assert len(failures) == 0, \
        f"{len(failures)}/10 connections failed: {[(i, str(e)) for i, e in failures]}"
