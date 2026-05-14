"""
Verifies ViaVersion and ViaBackwards loaded correctly on BungeeCord
to bridge the 1.12.2 to 26.1.2 protocol gap.
"""

import os
import pytest


def test_viaversion_loaded():
    """ViaVersion should be present in proxy logs."""
    log_path = os.getenv("PROXY_LOG_PATH", "proxy/logs/latest.log")
    if not os.path.exists(log_path):
        pytest.skip(f"Proxy log file not found at {log_path}")

    with open(log_path, "r", errors="replace") as f:
        log_content = f.read()

    assert "ViaVersion" in log_content, \
        "ViaVersion not found in proxy logs - plugin may have failed to load"


def test_viabackwards_loaded():
    """ViaBackwards should be present in proxy logs."""
    log_path = os.getenv("PROXY_LOG_PATH", "proxy/logs/latest.log")
    if not os.path.exists(log_path):
        pytest.skip(f"Proxy log file not found at {log_path}")

    with open(log_path, "r", errors="replace") as f:
        log_content = f.read()

    assert "ViaBackwards" in log_content, \
        "ViaBackwards not found in proxy logs - plugin may have failed to load"


def test_no_viaversion_errors():
    """ViaVersion and ViaBackwards should not have critical load errors."""
    log_path = os.getenv("PROXY_LOG_PATH", "proxy/logs/latest.log")
    if not os.path.exists(log_path):
        pytest.skip(f"Proxy log file not found at {log_path}")

    with open(log_path, "r", errors="replace") as f:
        log_content = f.read()

    for line in log_content.splitlines():
        if "ViaVersion" in line and "Could not" in line:
            pytest.fail(f"ViaVersion error in log: {line.strip()}")
        if "ViaBackwards" in line and "Could not" in line:
            pytest.fail(f"ViaBackwards error in log: {line.strip()}")
