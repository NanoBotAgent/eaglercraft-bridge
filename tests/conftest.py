"""
Pytest fixtures for Eaglercraft Bridge test suite.

Provides common connection parameters and the Eaglercraft V4 handshake
packet builder based on the EaglerXServer protocol specification:
  - First packet: PROTOCOL_CLIENT_VERSION (0x01)
  - Format for V2+: [0x01, 0x00, 0x02] + eagler_protocol_list + minecraft_protocol_list
    + brand_len(1) + brand + version_len(1) + version + auth_bool(1) + auth_username_len(1) + auth_username
  - Eaglercraft 1.12.2 uses MC protocol 340
"""

import pytest
import os
import struct


@pytest.fixture
def proxy_host():
    return os.getenv("PROXY_HOST", "localhost")


@pytest.fixture
def proxy_port():
    return int(os.getenv("PROXY_PORT", "25565"))


@pytest.fixture
def backend_host():
    return os.getenv("BACKEND_HOST", "localhost")


@pytest.fixture
def backend_port():
    return int(os.getenv("BACKEND_PORT", "25566"))


@pytest.fixture
def ws_url(proxy_host, proxy_port):
    return f"ws://{proxy_host}:{proxy_port}"


def build_eagler_v4_client_version_packet(
    eagler_protocols=None,
    minecraft_protocols=None,
    brand="Eaglercraft",
    version="u23",
    auth=False,
    auth_username=b"",
):
    """
    Build an Eaglercraft V4 CLIENT_VERSION (0x01) packet.

    Wire format (from WebSocketEaglerInitialHandler.decode):
      Byte 0: 0x01 (PROTOCOL_CLIENT_VERSION)
      Byte 1: 0x00 (first byte of eagler protocol count, unsigned short)
      Byte 2: eagler_protocol_count (second byte, e.g. 0x02 for 2 protocols)
      For each eagler protocol: unsigned short (2 = V2, 3 = V3, 4 = V4, 5 = V5)
      Then: minecraft_protocol_count (unsigned short)
      For each minecraft protocol: unsigned short (340 = 1.12.2, 47 = 1.8)
      Then: brand_len (unsigned byte) + brand (ASCII)
      Then: version_len (unsigned byte) + version (ASCII)
      Then: auth (boolean, 1 byte)
      Then: auth_username_len (unsigned byte) + auth_username (bytes)
    """
    if eagler_protocols is None:
        eagler_protocols = [4]  # V4
    if minecraft_protocols is None:
        minecraft_protocols = [340]  # MC 1.12.2

    buf = bytearray()
    # Packet ID
    buf.append(0x01)
    # Eagler protocol count (unsigned short)
    buf.extend(struct.pack(">H", len(eagler_protocols)))
    for p in eagler_protocols:
        buf.extend(struct.pack(">H", p))
    # Minecraft protocol count (unsigned short)
    buf.extend(struct.pack(">H", len(minecraft_protocols)))
    for p in minecraft_protocols:
        buf.extend(struct.pack(">H", p))
    # Brand
    brand_bytes = brand.encode("ascii")
    buf.append(len(brand_bytes))
    buf.extend(brand_bytes)
    # Version
    version_bytes = version.encode("ascii")
    buf.append(len(version_bytes))
    buf.extend(version_bytes)
    # Auth
    buf.append(1 if auth else 0)
    # Auth username
    buf.append(len(auth_username))
    buf.extend(auth_username)

    return bytes(buf)


def build_eagler_v4_request_login_packet(
    username="TestPlayer",
    requested_server="",
    auth_password=b"",
    enable_cookie=False,
    cookie_data=b"",
):
    """
    Build an Eaglercraft V4 CLIENT_REQUEST_LOGIN (0x04) packet.

    Wire format (from HandshakerV4.handleInboundRequestLogin):
      Byte 0: 0x04 (PROTOCOL_CLIENT_REQUEST_LOGIN)
      username_len (unsigned byte) + username (ASCII)
      requested_server_len (unsigned byte) + requested_server (ASCII)
      auth_password_len (unsigned byte) + auth_password (bytes)
      enable_cookie (boolean, 1 byte)
      cookie_len (unsigned byte) + cookie_data (bytes, only if enable_cookie)
    """
    buf = bytearray()
    buf.append(0x04)
    # Username
    username_bytes = username.encode("ascii")
    buf.append(len(username_bytes))
    buf.extend(username_bytes)
    # Requested server
    server_bytes = requested_server.encode("ascii")
    buf.append(len(server_bytes))
    buf.extend(server_bytes)
    # Auth password
    buf.append(len(auth_password))
    buf.extend(auth_password)
    # Cookie
    buf.append(1 if enable_cookie else 0)
    if enable_cookie:
        buf.append(len(cookie_data))
        buf.extend(cookie_data)
    else:
        buf.append(0)

    return bytes(buf)


def build_eagler_v4_finish_login_packet():
    """
    Build an Eaglercraft V4 CLIENT_FINISH_LOGIN (0x08) packet.
    No payload beyond the packet ID.
    """
    return bytes([0x08])


@pytest.fixture
def eagler_handshake_packet():
    """Standard Eaglercraft V4 CLIENT_VERSION intro packet for 1.12.2 client."""
    return build_eagler_v4_client_version_packet()


@pytest.fixture
def eagler_login_packet():
    """Standard Eaglercraft V4 REQUEST_LOGIN packet for a test player."""
    return build_eagler_v4_request_login_packet()


@pytest.fixture
def eagler_finish_login_packet():
    """Standard Eaglercraft V4 FINISH_LOGIN packet."""
    return build_eagler_v4_finish_login_packet()
