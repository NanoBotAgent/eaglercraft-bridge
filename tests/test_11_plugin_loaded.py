"""
Verifies EaglerXServer plugin loaded successfully on BungeeCord.
"""

import os
import pytest


def test_eaglerxserver_loaded():
    """EaglerXServer should appear in proxy logs without errors."""
    log_path = os.getenv("PROXY_LOG_PATH", "proxy/logs/latest.log")
    if not os.path.exists(log_path):
        pytest.skip(f"Proxy log file not found at {log_path}")

    with open(log_path, "r", errors="replace") as f:
        log_content = f.read()

    assert "EaglerXServer" in log_content, \
        "EaglerXServer not found in proxy logs - plugin may have failed to load"


def test_no_eaglerxserver_load_error():
    """EaglerXServer should not have 'Could not load' errors."""
    log_path = os.getenv("PROXY_LOG_PATH", "proxy/logs/latest.log")
    if not os.path.exists(log_path):
        pytest.skip(f"Proxy log file not found at {log_path}")

    with open(log_path, "r", errors="replace") as f:
        log_content = f.read()

    assert "Could not load 'plugins/EaglerXServer.jar'" not in log_content, \
        "EaglerXServer JAR failed to load on BungeeCord"


def test_no_unsupported_class_version():
    """EaglerXServer should not have UnsupportedClassVersionError (wrong Java version)."""
    log_path = os.getenv("PROXY_LOG_PATH", "proxy/logs/latest.log")
    if not os.path.exists(log_path):
        pytest.skip(f"Proxy log file not found at {log_path}")

    with open(log_path, "r", errors="replace") as f:
        log_content = f.read()

    assert "UnsupportedClassVersionError" not in log_content, \
        "UnsupportedClassVersionError found - Java version too low for EaglerXServer"


def test_no_eaglerxserver_error_on_same_line():
    """No line should contain both 'EaglerXServer' and 'ERROR'."""
    log_path = os.getenv("PROXY_LOG_PATH", "proxy/logs/latest.log")
    if not os.path.exists(log_path):
        pytest.skip(f"Proxy log file not found at {log_path}")

    with open(log_path, "r", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            if "EaglerXServer" in line and "ERROR" in line:
                pytest.fail(
                    f"Line {line_num} contains both 'EaglerXServer' and 'ERROR': {line.strip()}"
                )
