# Eaglercraft Bridge

BungeeCord proxy + Paper 26.1.2 backend that lets Eaglercraft 1.12.2 browser clients join a modern Minecraft server via ViaVersion protocol translation.

## Architecture

```
Eaglercraft 1.12.2 browser client
  |  WebSocket (wss://)
  v
+-----------------------------------+
| BungeeCord Proxy (Java 21+)      | <-- EaglerXServer plugin handles WebSocket
| Port: 25565                       | <-- ViaVersion + ViaBackwards translate protocol
+-----------------------------------+
  |  Internal TCP (localhost:25566)
  v
+-----------------------------------+
| Paper 26.1.2 Backend (Java 21+)  |
| Port: 25566 (internal only)      |
+-----------------------------------+
```

EaglerXServer cannot run directly on Paper versions above 1.12.2 as a Bukkit plugin. It must run on BungeeCord (or Velocity) when connecting to a modern backend. ViaBackwards bridges the 1.12.2 client protocol to the 26.1.2 server protocol.

## Prerequisites

- **Java 21+** on both the proxy and backend servers
- **Python 3.11+** (for tests only, not required for production)
- Two separate server slots (e.g. FalixNodes for proxy, another host for backend)
- The backend host must support Java 21 (Paper 26.1.2 requirement)

## Quick Start

```bash
make setup   # Downloads all JARs (BungeeCord, EaglerXServer, ViaVersion, ViaBackwards, Paper)
make start   # Starts backend then proxy
make test    # Runs full test suite against running servers
make stop    # Gracefully stops both servers
```

## How to Connect

Open [eaglercraft.com/play](https://eaglercraft.com/play), select **1.12.2**, click Multiplayer, Add Server, and enter:

```
wss://YOUR-PROXY-IP:25565
```

See [deploy/connect-guide.md](deploy/connect-guide.md) for detailed instructions.

## Deployment

- [FalixNodes Proxy Setup](deploy/falixnodes-proxy-guide.md)
- [FalixNodes Backend Setup](deploy/fallixnodes-backend-guide.md) (note: requires Java 21+)

## CI Status

![Server Boot](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/05-full-stack-boot.yml/badge.svg)
![WebSocket](https://github.com/NanoBotAgent/eaglercraft-bridge/actions/workflows/06-websocket-connect.yml/badge.svg)

## Important Limitations

ViaBackwards bridges the protocol between 1.12.2 and 26.1.2, but blocks, items, and mobs added after 1.12.2 will appear as old or substituted blocks on the Eaglercraft client side. This is an inherent limitation of protocol translation and cannot be fixed.

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `UnsupportedClassVersionError` on EaglerXServer | BungeeCord running on Java 8 | Switch proxy host to Java 17+ |
| `Could not load EaglerXServer.jar` | Same Java issue | Same fix |
| `Could not connect to backend` in proxy log | Paper backend not yet started / wrong port | Start backend first, check port 25566 |
| WebSocket connection refused | EaglerXServer not loaded on proxy | Check proxy logs for plugin errors |
| `bungeecord: false` warning in Paper log | Forgot to set bungeecord: true in spigot.yml | Set it and restart backend |
| New 26.1.2 blocks look wrong | ViaBackwards limitation | Expected - cannot be fixed |
| Connection timeout | Host blocking WebSocket on port 25565 | Contact host support |

## Project Structure

```
eaglercraft-bridge/
  proxy/         BungeeCord config + EaglerXServer/ViaVersion/ViaBackwards plugins
  backend/       Paper 26.1.2 config + eula
  scripts/       Download, start, stop, wait scripts
  tests/         Python pytest suite (WebSocket, handshake, stress, crash recovery)
  docker/        Dockerfiles + docker-compose for local dev
  deploy/        Hosting setup guides
  .github/       14 CI workflows for automated validation
```
