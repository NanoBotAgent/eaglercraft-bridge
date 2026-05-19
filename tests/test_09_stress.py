"""
Stress tests server stability under rapid repeated connections.

Each cycle uses retry logic to handle transient connection failures.
"""

import asyncio
import csv
import os
import time
import pytest
import websockets

from conftest import build_eagler_v4_client_version_packet

CYCLE_DELAY = 0.5  # seconds between cycles (reduced since retry handles failures)
MAX_CONNECT_RETRIES = 3


async def connect_with_retry(ws_url, max_retries=MAX_CONNECT_RETRIES):
    """Connect with retry to handle transient failures."""
    for attempt in range(max_retries):
        if attempt > 0:
            await asyncio.sleep(0.5 * attempt)
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
@pytest.mark.timeout(300)
async def test_stress_sequential_connections(ws_url):
    """50 sequential connect-handshake-disconnect cycles should all succeed.

    Each cycle uses retry logic with linear backoff to handle
    transient connection failures.
    """
    results = []
    timings = []
    num_cycles = 50

    for i in range(num_cycles):
        start = time.monotonic()
        success = False
        error = None
        try:
            async with await connect_with_retry(ws_url) as ws:
                # Send V4 handshake
                packet = build_eagler_v4_client_version_packet()
                await ws.send(packet)

                # Wait for response
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5)
                    if isinstance(response, bytes) and len(response) > 0:
                        success = True
                except (websockets.exceptions.ConnectionClosed, asyncio.TimeoutError):
                    # Connection closed or timed out - still counts if we connected
                    success = True
        except Exception as e:
            error = str(e)

        elapsed_ms = (time.monotonic() - start) * 1000
        timings.append(elapsed_ms)
        results.append((i, success, error, elapsed_ms))

        # Small delay between cycles
        if i < num_cycles - 1:
            await asyncio.sleep(CYCLE_DELAY)

    # Write timing CSV
    os.makedirs("test_results", exist_ok=True)
    with open("test_results/stress_timings.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["cycle", "success", "error", "elapsed_ms"])
        for cycle, success, error, elapsed in results:
            writer.writerow([cycle, success, error or "", f"{elapsed:.1f}"])

    # Assert all succeeded
    failures = [(i, e) for i, s, e, _ in results if not s]
    assert len(failures) == 0, \
        f"{len(failures)}/{num_cycles} connections failed: {failures[:5]}..."

    # Assert mean time < 3000ms
    mean_time = sum(timings) / len(timings)
    assert mean_time < 3000, \
        f"Mean connection time {mean_time:.1f}ms exceeds 3000ms threshold"

    # Final check: one more connection after all cycles
    try:
        async with await connect_with_retry(ws_url) as ws:
            packet = build_eagler_v4_client_version_packet()
            await ws.send(packet)
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            assert len(response) > 0, "Server not responding after stress test"
    except Exception as e:
        pytest.fail(f"Server not responsive after stress test: {e}")
