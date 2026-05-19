"""
Verifies EaglerXServer responds to MOTD queries.

EaglerXServer routes TextWebSocketFrame to WebSocketQueryHandler,
which reads the first text frame as an "accept:" query.
Sending "accept:motd" triggers MOTDConnectionWrapper.sendToUser(),
which responds with a JSON TextWebSocketFrame containing:
  {"name":"...", "brand":"lax1dude", "type":"motd", "data":{"motd":[...], ...}}

BinaryWebSocketFrame goes to the handshake handler instead —
the old test was incorrectly sending binary and never hitting MOTD.
"""

import asyncio
import json
import pytest
import websockets

EAGLERCRAFT_ORIGIN = "https://eaglercraft.com"


@pytest.mark.asyncio
async def test_motd_response(ws_url):
    """Server should respond with MOTD JSON when sent 'accept:motd' text frame."""
    try:
        async with websockets.connect(
            ws_url,
            origin=EAGLERCRAFT_ORIGIN,
            user_agent_header="EaglercraftX/1.12.2",
            close_timeout=5,
        ) as ws:
            # MOTD queries use TextWebSocketFrame, not BinaryWebSocketFrame.
            # WebSocketInitialHandler routes Text -> WebSocketQueryHandler,
            # which parses "accept:<type>" and dispatches to the MOTD handler.
            await ws.send("accept:motd")

            # Wait for MOTD JSON response (TextWebSocketFrame)
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
            except asyncio.TimeoutError:
                pytest.fail("No MOTD response from server within 5 seconds")

            # Response should be a text frame containing JSON
            if isinstance(response, bytes):
                pytest.fail(
                    "Received binary frame instead of text — "
                    "server may be routing to handshake handler instead of query handler. "
                    "Did you send a TextWebSocketFrame?"
                )

            assert isinstance(response, str), f"Expected text frame, got: {type(response)}"

            # Parse the JSON envelope from QueryServer.createJsonObjectResponse
            try:
                data = json.loads(response)
            except json.JSONDecodeError as e:
                pytest.fail(f"MOTD response is not valid JSON: {e}\nRaw: {response[:200]}")

            # Validate the response envelope structure
            # QueryServer adds: name, brand, vers, plaf, cracked, time, uuid, type, data
            assert "type" in data, f"Missing 'type' field in MOTD response: {list(data.keys())}"
            assert data["type"] == "motd", f"Expected type='motd', got type='{data['type']}'"

            # Validate the MOTD data payload
            assert "data" in data, f"Missing 'data' field in MOTD response: {list(data.keys())}"
            motd_data = data["data"]

            assert "motd" in motd_data, f"Missing 'motd' array in MOTD data: {list(motd_data.keys())}"
            assert isinstance(motd_data["motd"], list), f"'motd' should be a list, got: {type(motd_data['motd'])}"
            assert "online" in motd_data, f"Missing 'online' field in MOTD data"
            assert "max" in motd_data, f"Missing 'max' field in MOTD data"
            assert "players" in motd_data, f"Missing 'players' array in MOTD data"
            assert isinstance(motd_data["players"], list), f"'players' should be a list"

    except ConnectionRefusedError:
        pytest.fail(f"WebSocket connection refused at {ws_url}")
    except websockets.exceptions.InvalidStatusCode as e:
        pytest.fail(f"WebSocket upgrade failed: {e}")
    except EOFError:
        pytest.fail("WebSocket closed immediately — check listeners.yml allow_motd and origin_whitelist")


@pytest.mark.asyncio
async def test_motd_noicon_variant(ws_url):
    """Server should respond to 'accept:motd.noicon' without icon data."""
    try:
        async with websockets.connect(
            ws_url,
            origin=EAGLERCRAFT_ORIGIN,
            user_agent_header="EaglercraftX/1.12.2",
            close_timeout=5,
        ) as ws:
            await ws.send("accept:motd.noicon")

            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
            except asyncio.TimeoutError:
                pytest.fail("No MOTD response for noicon variant within 5 seconds")

            assert isinstance(response, str), f"Expected text frame, got: {type(response)}"

            data = json.loads(response)
            assert data["type"] == "motd", f"Expected type='motd', got '{data['type']}'"

            motd_data = data["data"]
            assert motd_data.get("icon") is False, (
                f"Expected icon=false for motd.noicon variant, got icon={motd_data.get('icon')}"
            )

    except ConnectionRefusedError:
        pytest.fail(f"WebSocket connection refused at {ws_url}")
    except websockets.exceptions.InvalidStatusCode as e:
        pytest.fail(f"WebSocket upgrade failed: {e}")


@pytest.mark.asyncio
async def test_motd_rejects_binary(ws_url):
    """Server should NOT return MOTD when sent a binary frame — binary goes to handshake."""
    try:
        async with websockets.connect(
            ws_url,
            origin=EAGLERCRAFT_ORIGIN,
            user_agent_header="EaglercraftX/1.12.2",
            close_timeout=5,
        ) as ws:
            # Binary frames go to WebSocketEaglerInitialHandler (handshake), not query handler
            await ws.send(b"\x01\x00\x01\x00\x04")

            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
            except asyncio.TimeoutError:
                # Server may close the connection silently for bad handshake — that's fine
                pass
            else:
                # If we got a response, it should be a handshake response (0x02/0x03/0xFF),
                # NOT a MOTD JSON text frame
                if isinstance(response, str):
                    try:
                        data = json.loads(response)
                        assert data.get("type") != "motd", (
                            "Server returned MOTD for binary frame — "
                            "binary frames should go to handshake handler, not query handler"
                        )
                    except json.JSONDecodeError:
                        pass  # Non-JSON text is fine — not a MOTD response

    except ConnectionRefusedError:
        pytest.fail(f"WebSocket connection refused at {ws_url}")
    except websockets.exceptions.InvalidStatusCode as e:
        pytest.fail(f"WebSocket upgrade failed: {e}")
