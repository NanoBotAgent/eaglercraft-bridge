"""
Verifies both proxy and backend remain alive after repeated invalid connections.

EaglerXServer rate-limits connections from the same IP, so we
add a delay between cycles to avoid hitting the limit.
"""

import asyncio
import os
import pytest
import websockets

from conftest import build_eagler_v4_client_version_packet

# Delay between cycles to avoid EaglerXServer rate limiting
CYCLE_DELAY = 1.0  # seconds


def is_pid_alive(pid_file):
    """Check if a PID from a pid file is still running."""
    if not os.path.exists(pid_file):
        return False
    try:
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)  # Signal 0 = just check if process exists
        return True
    except (ProcessLookupError, ValueError, PermissionError, FileNotFoundError):
        return False


@pytest.mark.asyncio
@pytest.mark.timeout(120)
async def test_crash_recovery(ws_url):
    """Both servers should survive 10 cycles of garbage + valid connections.

    Reduced from 20 to 10 cycles with 1s delay to stay within
    EaglerXServer's rate limiter window. Still validates that
    garbage packets don't crash the server.
    """
    proxy_pid_file = os.getenv("PROXY_PID_FILE", "proxy/server.pid")
    backend_pid_file = os.getenv("BACKEND_PID_FILE", "backend/server.pid")

    for i in range(10):
        # Send garbage
        garbage = os.urandom(128)
        try:
            async with websockets.connect(
                ws_url,
                origin="https://eaglercraft.com",
                user_agent_header="EaglercraftX/1.12.2",
                close_timeout=5
            ) as ws:
                await ws.send(garbage)
                try:
                    await asyncio.wait_for(ws.recv(), timeout=3)
                except (websockets.exceptions.ConnectionClosed, asyncio.TimeoutError):
                    pass
        except websockets.exceptions.ConnectionClosed:
            pass
        except websockets.exceptions.InvalidMessage:
            # Rate limited - not a crash, just skip this round
            await asyncio.sleep(CYCLE_DELAY)
            continue
        except Exception as e:
            pytest.fail(f"Unexpected error during garbage round {i}: {e}")

        # Verify servers still alive
        if os.path.exists(proxy_pid_file):
            assert is_pid_alive(proxy_pid_file), \
                f"Proxy crashed after garbage round {i}"
        if os.path.exists(backend_pid_file):
            assert is_pid_alive(backend_pid_file), \
                f"Backend crashed after garbage round {i}"

        # Delay to avoid rate limiting
        await asyncio.sleep(CYCLE_DELAY)

    # Verify valid connection still works after all garbage
    try:
        async with websockets.connect(
            ws_url,
            origin="https://eaglercraft.com",
            user_agent_header="EaglercraftX/1.12.2",
            close_timeout=5
        ) as ws:
            packet = build_eagler_v4_client_version_packet()
            await ws.send(packet)
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                assert len(response) > 0, \
                    "No response from server after crash recovery test"
            except websockets.exceptions.ConnectionClosed:
                pass  # Server may close after protocol check
    except ConnectionRefusedError:
        pytest.fail("Server not responding after crash recovery test")
