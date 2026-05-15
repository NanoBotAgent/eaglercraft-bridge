"""
Verifies server gracefully handles malformed packets without crashing.
"""

import asyncio
import os
import pytest
import websockets

from conftest import build_eagler_v4_client_version_packet


@pytest.mark.asyncio
async def test_invalid_packets_graceful_disconnect(ws_url):
    """Server should close connection gracefully after receiving garbage data, not crash."""

    garbage_payloads = [
        os.urandom(64) for _ in range(5)
    ]

    for i, payload in enumerate(garbage_payloads):
        # Send garbage
        try:
            async with websockets.connect(ws_url, origin="https://eaglercraft.com", user_agent_header="EaglercraftX/1.12.2", close_timeout=5) as ws:
                await ws.send(payload)
                # Server should close the connection or we close it
                try:
                    await asyncio.wait_for(ws.recv(), timeout=3)
                except (websockets.exceptions.ConnectionClosed, asyncio.TimeoutError):
                    pass  # Expected - server closed or we timed out
        except websockets.exceptions.ConnectionClosed:
            pass  # Acceptable - server closed connection after garbage
        except Exception as e:
            pytest.fail(f"Unexpected error sending garbage packet {i}: {e}")

        # After each garbage send, verify a fresh valid connection works
        try:
            async with websockets.connect(ws_url, origin="https://eaglercraft.com", user_agent_header="EaglercraftX/1.12.2", close_timeout=5) as ws:
                packet = build_eagler_v4_client_version_packet()
                await ws.send(packet)
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5)
                    assert len(response) > 0, \
                        f"No response from server after garbage round {i}"
                except websockets.exceptions.ConnectionClosed:
                    # Server may close after version mismatch - that's OK
                    pass
        except ConnectionRefusedError:
            pytest.fail(f"Server not responding after garbage round {i} - may have crashed")
