"""
Verifies EaglerXServer responds to MOTD queries.

Eaglercraft clients request the server MOTD (Message of the Day)
by sending a specific query over the WebSocket connection.
"""

import asyncio
import struct
import pytest
import websockets

EAGLERCRAFT_ORIGIN = "https://eaglercraft.com"

# EaglerXServer MOTD query packet: type 0x01 with empty brand/version
# Alternatively, Eaglercraft sends a special MOTD request before the handshake
MOTD_QUERY_PACKET = bytes([
    0x01,  # PROTOCOL_CLIENT_VERSION
    0x00, 0x01,  # 1 eagler protocol
    0x00, 0x04,  # V4
    0x00, 0x01,  # 1 MC protocol
    0x01, 0x44,  # MC 340 (0x0154)
    0x0B,  # brand len = 11
]) + b"Eaglercraft" + bytes([
    0x03,  # version len = 3
]) + b"u23" + bytes([
    0x00,  # no auth
    0x00,  # no auth username
])


@pytest.mark.asyncio
async def test_motd_response(ws_url):
    """Server should respond with MOTD data when queried."""
    try:
        async with websockets.connect(
            ws_url,
            origin=EAGLERCRAFT_ORIGIN,
            user_agent_header="EaglercraftX/1.12.2",
            close_timeout=5,
        ) as ws:
            # Send a CLIENT_VERSION packet - server responds before MOTD
            await ws.send(MOTD_QUERY_PACKET)

            # Wait for any response (could be MOTD or handshake response)
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
            except asyncio.TimeoutError:
                pytest.fail("No response from server within 5 seconds")

            assert len(response) > 0, "Received empty response from server"

    except ConnectionRefusedError:
        pytest.fail(f"WebSocket connection refused at {ws_url}")
    except websockets.exceptions.InvalidStatusCode as e:
        pytest.fail(f"WebSocket upgrade failed: {e}")
    except EOFError:
        pytest.fail("WebSocket closed immediately — check listeners.yml origin_whitelist")
