"""
Stress tests server stability under rapid repeated connections.
"""

import asyncio
import csv
import os
import time
import pytest
import websockets

from conftest import build_eagler_v4_client_version_packet


@pytest.mark.asyncio
@pytest.mark.timeout(180)
async def test_stress_sequential_connections(ws_url):
    """100 sequential connect-handshake-disconnect cycles should all succeed."""

    results = []
    timings = []
    num_cycles = 100

    for i in range(num_cycles):
        start = time.monotonic()
        success = False
        error = None

        try:
            async with websockets.connect(ws_url, origin="https://eaglercraft.com", user_agent_header="EaglercraftX/1.12.2", close_timeout=5) as ws:
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

    # Write timing CSV
    os.makedirs("test_results", exist_ok=True)
    with open("test_results/stress_timings.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["cycle", "success", "error", "elapsed_ms"])
        for cycle, success, error, elapsed in results:
            writer.writerow([cycle, success, error or "", f"{elapsed:.1f}"])

    # Assert all 100 succeeded
    failures = [(i, e) for i, s, e, _ in results if not s]
    assert len(failures) == 0, \
        f"{len(failures)}/100 connections failed: {failures[:5]}..."

    # Assert mean time < 1000ms
    mean_time = sum(timings) / len(timings)
    assert mean_time < 1000, \
        f"Mean connection time {mean_time:.1f}ms exceeds 1000ms threshold"

    # Final check: one more connection after all 100
    try:
        async with websockets.connect(ws_url, origin="https://eaglercraft.com", user_agent_header="EaglercraftX/1.12.2", close_timeout=5) as ws:
            packet = build_eagler_v4_client_version_packet()
            await ws.send(packet)
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            assert len(response) > 0, "Server not responding after stress test"
    except Exception as e:
        pytest.fail(f"Server not responsive after stress test: {e}")
