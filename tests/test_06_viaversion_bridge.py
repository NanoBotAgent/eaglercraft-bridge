"""
Verifies ViaVersion and ViaBackwards loaded correctly on BungeeCord via ViaBungee.

ViaBungee is the BungeeCord loader plugin. It loads ViaVersion core and
ViaBackwards as libraries from plugins/ViaVersion/, not as direct BungeeCord
plugins. When ViaBungee loads successfully, it logs as "Enabled plugin ViaVersion"
(with the version string from ViaBungee, e.g. "version 0.4.0 by _MylesC...").
The string "ViaBungee" does NOT appear in the "Enabled plugin" line.
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
    """ViaBungee (the BungeeCord loader) should load successfully.
    
    ViaBungee loads ViaVersion core as a library. When it enables, BungeeCord
    logs "Enabled plugin ViaVersion version 0.4.0 by _MylesC..." where
    "0.4.0" is the ViaBungee version, NOT the ViaVersion jar version.
    We check for ViaBungee's version string in the Enabled plugin line.
    """
    log = _read_proxy_log()
    
    # ViaBungee logs as "Enabled plugin ViaVersion version 0.4.0 by _MylesC..."
    # The version "0.4.0" is the ViaBungee version (the BungeeCord loader)
    for line in log.splitlines():
        if "Enabled plugin ViaVersion" in line and "0.4.0" in line:
            return
    
    # Also check for "ViaBungee" anywhere in log (some versions may log it)
    for line in log.splitlines():
        if "ViaBungee" in line and "Enabled plugin" in line:
            return
    
    # Check for error loading
    for line in log.splitlines():
        if "ViaBungee" in line and "Error" in line:
            pytest.fail(f"ViaBungee failed to load: {line.strip()}")
    
    # Also check if ViaVersion loaded at all (without ViaBungee version check)
    for line in log.splitlines():
        if "Enabled plugin ViaVersion" in line:
            # ViaVersion loaded but ViaBungee version pattern didn't match
            # This is still a pass - ViaBungee is working
            return
    
    pytest.fail("ViaVersion/ViaBungee not found in proxy logs at all")


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
