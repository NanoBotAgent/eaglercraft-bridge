"""
Verifies ViaVersion and ViaBackwards loaded correctly on BungeeCord via ViaBungee.
Checks for actual success indicators, not just presence of strings in error lines.
"""

import os
import pytest


def _read_proxy_log():
    """Helper to read proxy log, skipping if unavailable."""
    log_path = os.getenv("PROXY_LOG_PATH", "proxy/logs/latest.log")
    if not os.path.exists(log_path):
        pytest.skip(f"Proxy log file not found at {log_path}")
    with open(log_path, "r", errors="replace") as f:
        return f.read()


def test_viabungee_loaded():
    """ViaBungee (the BungeeCord loader) should load successfully."""
    log = _read_proxy_log()
    # ViaBungee should appear in "Loaded plugin" or "Enabled plugin" lines
    for line in log.splitlines():
        if "ViaBungee" in line and ("Loaded plugin" in line or "Enabled plugin" in line):
            return
    # If we see an error loading ViaBungee, fail with that
    for line in log.splitlines():
        if "ViaBungee" in line and "Error" in line:
            pytest.fail(f"ViaBungee failed to load: {line.strip()}")
    pytest.fail("ViaBungee not found in proxy logs at all")


def test_viaversion_no_bukkit_classdef_error():
    """ViaVersion/ViaBackwards must NOT fail with JavaPlugin NoClassDefFoundError.

    This happens when the Bukkit jars are placed directly in proxy/plugins/
    instead of proxy/plugins/ViaVersion/ where ViaBungee expects them.
    """
    log = _read_proxy_log()
    for line in log.splitlines():
        if "NoClassDefFoundError" in line and "JavaPlugin" in line:
            if "ViaVersion" in line or "ViaBackwards" in line:
                pytest.fail(
                    f"ViaVersion/ViaBackwards loaded as BungeeCord plugin "
                    f"(should be in plugins/ViaVersion/ subfolder): {line.strip()}"
                )


def test_no_plugin_load_errors():
    """No plugin should have an 'Error loading plugin' entry in the log."""
    log = _read_proxy_log()
    for line in log.splitlines():
        if "Error loading plugin" in line:
            pytest.fail(f"Plugin load error: {line.strip()}")
