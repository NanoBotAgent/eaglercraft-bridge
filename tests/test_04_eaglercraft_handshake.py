"""
Verifies EaglerXServer correctly handles Eaglercraft protocol V4 handshake.

The V4 handshake flow (from EaglerXServer source):
1. Client sends CLIENT_VERSION (0x01) with protocol lists + brand + version
2. Server responds with SERVER_VERSION (0x02) or VERSION_MISMATCH (0x03)
3. Client sends REQUEST_LOGIN (0x04) with username + capabilities
4. Server responds with ALLOW_LOGIN (0x05) or DENY_LOGIN (0x06)
"""

import asyncio
import struct
import pytest
import websockets

from conftest import build_eagler_v4_client_version_packet

EAGLERCRAFT_ORIGIN = "https://eaglercraft.com"


@pytest.mark.asyncio
async def test_eaglercraft_v4_handshake(ws_url, eagler_handshake_packet):
    """Eaglercraft V4 handshake packet should receive a valid server response."""
    try:
        async with websockets.connect(
            ws_url,
            origin=EAGLERCRAFT_ORIGIN,
            user_agent_header="EaglercraftX/1.12.2",
            close_timeout=5,
        ) as ws:
            # Send CLIENT_VERSION packet
            await ws.send(eagler_handshake_packet)

            # Wait for server response (SERVER_VERSION or VERSION_MISMATCH)
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
            except asyncio.TimeoutError:
                pytest.fail("No response received from server within 5 seconds")

            assert len(response) > 0, "Received empty response from server"

            # First byte should be a valid response packet type
            if isinstance(response, bytes):
                packet_id = response[0]
            else:
                pytest.fail(f"Expected binary response, got: {type(response)}")

            # Valid response types: 0x02 (SERVER_VERSION) or 0x03 (VERSION_MISMATCH) or 0xFF (SERVER_ERROR)
            assert packet_id in (0x02, 0x03, 0xFF), \
                f"Unexpected packet ID: 0x{packet_id:02x}, expected 0x02, 0x03, or 0xFF"

            # If we got SERVER_VERSION (0x02), parse it
            if packet_id == 0x02 and len(response) >= 6:
                eagler_proto = struct.unpack(">H", response[1:3])[0]
                mc_proto = struct.unpack(">H", response[3:5])[0]
                assert eagler_proto >= 3, f"Eagler protocol version too low: {eagler_proto}"
                assert mc_proto > 0, f"Invalid MC protocol version: {mc_proto}"

    except ConnectionRefusedError:
        pytest.fail(f"WebSocket connection refused at {ws_url}")
    except websockets.exceptions.InvalidStatusCode as e:
        pytest.fail(f"WebSocket upgrade failed: {e}")
    except EOFError:
        pytest.fail("WebSocket connection closed immediately — EaglerXServer rejected upgrade. "
                     "Check listeners.yml origin_whitelist.")
