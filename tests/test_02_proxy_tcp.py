"""
Verifies BungeeCord proxy is listening on the public port.
"""

import socket
import pytest


def test_proxy_tcp_connect(proxy_host, proxy_port):
    """Proxy should accept TCP connections on port 25565."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((proxy_host, proxy_port))
        assert True  # Connected successfully
    except (ConnectionRefusedError, socket.timeout, OSError) as e:
        pytest.fail(f"Failed to connect to proxy at {proxy_host}:{proxy_port}: {e}")
    finally:
        sock.close()
