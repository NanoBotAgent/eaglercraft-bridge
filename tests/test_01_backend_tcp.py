"""
Verifies Paper 26.1.2 backend is listening on its internal port.
"""

import socket
import pytest


def test_backend_tcp_connect(backend_host, backend_port):
    """Backend should accept TCP connections on port 25566."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((backend_host, backend_port))
        assert True  # Connected successfully
    except (ConnectionRefusedError, socket.timeout, OSError) as e:
        pytest.fail(f"Failed to connect to backend at {backend_host}:{backend_port}: {e}")
    finally:
        sock.close()
