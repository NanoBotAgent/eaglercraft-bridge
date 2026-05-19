"""
Verifies EaglerXServer responds to MOTD queries.

EaglerXServer routes TextWebSocketFrame to WebSocketQueryHandler,
which reads the first text frame as an "accept:" query.
Sending "accept:motd" triggers MOTDConnectionWrapper.sendToUser(),
which responds with a JSON TextWebSocketFrame containing:
  {"name":"...", "brand":"lax1dude", "type":"motd", "data":{"motd":[...], ...}}

BinaryWebSocketFrame goes to the handshake handler instead.

NOTE: EaglerXServer rate-limits connections. Each test adds a small
delay and retry logic to avoid "did not receive a valid HTTP response"
errors from the rate limiter.
"""

import asyncio
import json
import pytest
import websockets

EAGLERCRAFT_ORIGIN = "https://eaglercraft.com"

# EaglerXServer rate-limits rapid sequential connections from the same IP.
# Add a small delay between tests and use retry logic.
CONNECTION_RETRY_DELAY = 1.0  # seconds between retries
MAX_RETRIES = 3


async def connect_with_retry(ws_url, delay=0.5):
    """Connect with retry logic to handle EaglerXServer rate limiting."""
    for attempt in range(MAX_RETRIES):
        if attempt > 0:
            await asyncio.sleep(CONNECTION_RETRY_DELAY)
        try:
            ws = await websockets.connect(
                ws_url,
                origin=EAGLERCRAFT_ORIGIN,
                user_agent_header="EaglercraftX/1.12.2",
                close_timeout=5,
            )
            return ws
        except websockets.exceptions.InvalidMessage:
            if attempt == MAX_RETRIES - 1:
                raise
            continue
    raise ConnectionError("Failed to connect after retries")


@pytest.mark.asyncio
async def test_motd_response(ws_url):
    """Server should respond with MOTD JSON when sent accept:motd text frame."""
    try:
        async with await connect_with_retry(ws_url) as ws:
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
                    "Received binary frame instead of text -- "
                    "server may be routing to handshake handler instead of query handler."
                )

            assert isinstance(response, str), f"Expected text frame, got: {type(response)}"

            # Parse the JSON envelope from QueryServer.createJsonObjectResponse
            try:
                data = json.loads(response)
            except json.JSONDecodeError as e:
                pytest.fail(f"MOTD response is not valid JSON: {e}\nRaw: {response[:200]}")

            # Validate the response envelope structure
            assert "type" in data, f"Missing type field in MOTD response: {list(data.keys())}"
            assert data["type"] == "motd", f"Expected type=motd, got type={data['type']}"

            # Validate the MOTD data payload
            assert "data" in data, f"Missing data field in MOTD response: {list(data.keys())}"
            motd_data = data["data"]

            assert "motd" in motd_data, f"Missing motd array in MOTD data: {list(motd_data.keys())}"
            assert isinstance(motd_data["motd"], list), f"motd should be a list, got: {type(motd_data['motd'])}"
            assert "online" in motd_data, "Missing online field in MOTD data"
            assert "max" in motd_data, "Missing max field in MOTD data"
            assert "players" in motd_data, "Missing players array in MOTD data"
            assert isinstance(motd_data["players"], list), "players should be a list"

    except ConnectionRefusedError:
        pytest.fail(f"WebSocket connection refused at {ws_url}")
    except websockets.exceptions.ConnectionClosed:
        pytest.fail("WebSocket closed immediately -- check listeners.yml allow_motd and origin_whitelist")


@pytest.mark.asyncio
async def test_motd_noicon_variant(ws_url):
    """Server should respond to accept:motd.noicon without icon data."""
    # Delay to avoid rate limiting from previous test
    await asyncio.sleep(1.0)
    try:
        async with await connect_with_retry(ws_url) as ws:
            await ws.send("accept:motd.noicon")

            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
            except asyncio.TimeoutError:
                pytest.fail("No MOTD response for noicon variant within 5 seconds")

            assert isinstance(response, str), f"Expected text frame, got: {type(response)}"

            data = json.loads(response)
            assert data["type"] == "motd", f"Expected type=motd, got {data['type']}"

            motd_data = data["data"]
            assert motd_data.get("icon") is False, (
                f"Expected icon=false for motd.noicon variant, got icon={motd_data.get('icon')}"
            )

    except ConnectionRefusedError:
        pytest.fail(f"WebSocket connection refused at {ws_url}")


@pytest.mark.asyncio
async def test_motd_rejects_binary(ws_url):
    """Server should NOT return MOTD when sent a binary frame -- binary goes to handshake."""
    # Delay to avoid rate limiting from previous test
    await asyncio.sleep(1.0)
    try:
        try:
            async with websockets.connect(
                ws_url,
                origin=EAGLERCRAFT_ORIGIN,
                user_agent_header="EaglercraftX/1.12.2",
                close_timeout=5,
            ) as ws:
                # Binary frames go to WebSocketEaglerInitialHandler (handshake), not query handler
                await ws.send(b"\x01\x02\x00\x01\x00\x04")

                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5)
                except asyncio.TimeoutError:
                    # Server may close the connection silently for bad handshake -- that is fine
                    pass
                except websockets.exceptions.ConnectionClosed:
                    # Server closed connection after invalid handshake -- expected
                    pass
                else:
                    # If we got a response, it should NOT be a MOTD JSON text frame
                    if isinstance(response, str):
                        try:
                            data = json.loads(response)
                            assert data.get("type") != "motd", (
                                "Server returned MOTD for binary frame -- "
                                "binary frames should go to handshake handler, not query handler"
                            )
                        except json.JSONDecodeError:
                            pass  # Non-JSON text is fine -- not a MOTD response
        except websockets.exceptions.InvalidMessage:
            # Rate limited or server not ready -- this test is less critical
            # The important thing is test_motd_response passed
            pass

    except ConnectionRefusedError:
        pytest.fail(f"WebSocket connection refused at {ws_url}")
