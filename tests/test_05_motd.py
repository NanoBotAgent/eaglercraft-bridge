"""
Verifies server correctly serves MOTD to Eaglercraft clients.

EaglerXServer responds to initial WebSocket connections with server
information. When a client connects and does not immediately send
a handshake packet, the server may send a MOTD response instead.
This test verifies the WebSocket endpoint responds with data.
"""

import asyncio
import pytest
import websockets


@pytest.mark.asyncio
async def test_motd_response(ws_url):
    """Server should respond with data on WebSocket connect (MOTD or handshake response)."""
    try:
        async with websockets.connect(ws_url, close_timeout=5) as ws:
            # The server may proactively send MOTD data, or we need to wait
            # Some EaglerXServer configurations send MOTD as first message
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                assert len(response) > 0, "Received empty MOTD response"
            except asyncio.TimeoutError:
                # Server may not send MOTD proactively - this is acceptable
                # as long as it responds to our handshake
                from conftest import build_eagler_v4_client_version_packet
                packet = build_eagler_v4_client_version_packet()
                await ws.send(packet)
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                assert len(response) > 0, "No response received from server"

    except ConnectionRefusedError:
        pytest.fail(f"WebSocket connection refused at {ws_url}")
    except websockets.exceptions.InvalidStatusCode as e:
        pytest.fail(f"WebSocket upgrade failed: {e}")
