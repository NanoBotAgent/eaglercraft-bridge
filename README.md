# Eaglercraft Bridge

BungeeCord proxy + Paper 26.1.2 backend that lets Eaglercraft 1.12.2 browser clients join a modern Minecraft server via ViaVersion protocol translation.

## Architecture

```
Eaglercraft 1.12.2 browser client
        |
  WebSocket (wss://)
        v
+-----------------------------------+
|  BungeeCord Proxy (Java 25+)      |
|  EaglerXServer plugin (WebSocket) |
|  ViaVersion + ViaBackwards        |
|  Port: 25565                      |
+-----------------------------------+
        |
  Internal TCP (localhost:25566)
        v
+-----------------------------------+
|  Paper 26.1.2 Backend (Java 25+)  |
|  Port: 25566 (internal only)      |
+-----------------------------------+
```

EaglerXServer cannot run directly on Paper versions above 1.12.2 as a Bukkit plugin. It must run on BungeeCord (or Velocity) when connecting to a modern backend. ViaBackwards bridges the 1.12.2 client protocol to the 26.1.2 server protocol.

## Prerequisites

- **Java 25+** on both the proxy and backend servers
- **Python 3.11+** (for running the test suite only, not required for production)
- Two separate server slots (e.g. FalixNodes for proxy, another host for backend)
- The backend host must support Java 25 (Paper 26.1.2 requirement)

## Quick Start

```bash
make setup    # Downloads all JARs (BungeeCord, EaglerXServer, ViaVersion, ViaBackwards, Paper)
make start    # Starts backend then proxy
make test     # Runs full pytest suite against running servers
make stop     # Gracefully stops both servers
make clean    # Removes downloaded JARs and generated world data
```

### Docker

```bash
make docker-build   # Build proxy + backend images
make docker-run     # Start via docker compose
```

## How to Connect

Open [eaglercraft.com/play](https://eaglercraft.com/play), select **1.12.2**, click Multiplayer, Add Server, and enter:

```
wss://YOUR-PROXY-IP:25565
```

See [deploy/connect-guide.md](deploy/connect-guide.md) for detailed instructions.

## Deployment

- [FalixNodes Proxy Setup](deploy/falixnodes-proxy-guide.md)
- [FalixNodes Backend Setup](deploy/fallixnodes-backend-guide.md) (requires Java 25+)

## CI Status

| Workflow | Badge |
|---|---|
| Validate Configs | ![Validate Configs](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/01-validate-configs.yml/badge.svg) |
| Download & Verify Plugins | ![Download Plugins](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/02-download-verify-plugins.yml/badge.svg) |
| Proxy Boot | ![Proxy Boot](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/03-proxy-boot.yml/badge.svg) |
| Backend Boot | ![Backend Boot](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/04-backend-boot.yml/badge.svg) |
| Full Stack Boot | ![Full Stack](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/05-full-stack-boot.yml/badge.svg) |
| WebSocket Connect | ![WebSocket](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/06-websocket-connect.yml/badge.svg) |
| Eaglercraft Handshake | ![Handshake](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/07-eaglercraft-handshake.yml/badge.svg) |
| ViaVersion Bridge | ![ViaVersion](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/08-viaversion-bridge.yml/badge.svg) |
| Multi Client | ![Multi Client](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/09-multi-client.yml/badge.svg) |
| Stress Test | ![Stress](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/10-stress-test.yml/badge.svg) |
| Crash Recovery | ![Crash Recovery](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/11-crash-recovery.yml/badge.svg) |
| Config Integrity | ![Config Integrity](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/12-config-integrity.yml/badge.svg) |
| Release Package | ![Release](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/13-release-package.yml/badge.svg) |
| Nightly | ![Nightly](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/14-nightly.yml/badge.svg) |

## Test Suite

11 pytest tests covering the full connection pipeline:

| Test | Description |
|---|---|
| `test_01_backend_tcp` | Backend TCP reachability |
| `test_02_proxy_tcp` | Proxy TCP reachability |
| `test_03_websocket_upgrade` | WebSocket handshake upgrade |
| `test_04_eaglercraft_handshake` | Eaglercraft 1.12.2 protocol handshake |
| `test_05_motd` | MOTD/ping response |
| `test_06_viaversion_bridge` | ViaVersion protocol translation |
| `test_07_multi_client` | Concurrent client connections |
| `test_08_invalid_packets` | Malformed packet handling |
| `test_09_stress` | High-volume connection stress |
| `test_10_crash_recovery` | Server crash recovery |
| `test_11_plugin_loaded` | Plugin load verification |

Run with `make test` or `pytest tests/ -v`.

## Important Limitations

ViaBackwards bridges the protocol between 1.12.2 and 26.1.2, but blocks, items, and mobs added after 1.12.2 will appear as old or substituted blocks on the Eaglercraft client side. This is an inherent limitation of protocol translation and cannot be fixed.

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `UnsupportedClassVersionError` on EaglerXServer | BungeeCord running on old Java | Switch proxy host to Java 25+ |
| `Could not load EaglerXServer.jar` | Same Java issue | Same fix |
| `Could not connect to backend` in proxy log | Paper backend not yet started / wrong port | Start backend first, check port 25566 |
| WebSocket connection refused | EaglerXServer not loaded on proxy | Check proxy logs for plugin errors |
| `bungeecord: false` warning in Paper log | Forgot to set bungeecord: true in spigot.yml | Set it and restart backend |
| New 26.1.2 blocks look wrong | ViaBackwards limitation | Expected - cannot be fixed |
| Connection timeout | Host blocking WebSocket on port 25565 | Contact host support |
| Missing `server-icon.png` crash | EaglerXServer requires server-icon.png | Place a 64x64 server-icon.png in proxy root |

## Project Structure

```
eaglercraft-bridge/
  proxy/          BungeeCord config + EaglerXServer/ViaVersion/ViaBackwards plugins
  backend/        Paper 26.1.2 config + eula
  scripts/        Download, start, stop, wait, patch scripts
  tests/          Python pytest suite (WebSocket, handshake, stress, crash recovery)
  docker/         Dockerfiles + docker-compose for local dev
  deploy/         Hosting setup guides
  .github/        14 CI workflows for automated validation
```
