# FalixNodes Proxy Setup Guide

This guide covers setting up the BungeeCord proxy on FalixNodes for the Eaglercraft Bridge.

## Prerequisites

- FalixNodes account with a Minecraft server slot
- Java 25+ (required by BungeeCord and EaglerXServer)
- The proxy must be accessible on port 25565 via WebSocket

## Steps

### 1. Create a BungeeCord Server

1. Log into FalixNodes panel
2. Create a new Minecraft server
3. Select **BungeeCord** as the server type
4. Choose **Java 25** as the runtime
5. Set the server port to **25565**

### 2. Upload Files

Upload the following files from the `proxy/` directory:

- `BungeeCord.jar` - Main proxy JAR
- `config.yml` - BungeeCord configuration
- `eaglerxserver/listeners.yml` - EaglerXServer listener config
- `plugins/EaglerXServer.jar` - EaglerXServer plugin
- `plugins/ViaVersion-*.jar` - ViaVersion plugin
- `plugins/ViaBackwards-*.jar` - ViaBackwards plugin
- `server-icon.png` - Required by EaglerXServer (64x64 PNG)

### 3. Configure BungeeCord

Edit `config.yml` and update the backend address:

```yaml
servers:
  backend:
    motd: '&1Backend'
    address: YOUR_BACKEND_IP:25566
    restricted: false
```

Replace `YOUR_BACKEND_IP` with the IP address of your Paper 26.1.2 backend server.

### 4. Configure EaglerXServer

Edit `plugins/EaglerXServer/listeners.yml`:

```yaml
listeners:
  - inject_address: "0.0.0.0:25565"
    eagler_players_cap: -1
    allow_eagler_players: true
    allow_vanilla_players: true
```

### 5. Configure ViaVersion

ViaVersion and ViaBackwards will auto-generate their configs on first boot. Default settings should work for bridging 1.12.2 to 26.1.2.

### 6. Start the Proxy

Start the server from the FalixNodes panel. Check the console for:

- `Listening on` - BungeeCord is ready
- `EaglerXServer` - Plugin loaded successfully
- `ViaVersion` - Protocol translator loaded
- `ViaBackwards` - Backwards compatibility loaded

### 7. Verify WebSocket

The proxy should now accept WebSocket connections on port 25565. Test by connecting from Eaglercraft:

`wss://YOUR-SERVER-IP:25565`

## Important Notes

- FalixNodes must allow WebSocket connections on port 25565
- Some hosts block WebSocket - contact support if connections fail
- The proxy requires Java 25+ - EaglerXServer will fail with `UnsupportedClassVersionError` on older Java
- **EaglerXServer requires `server-icon.png`** in the proxy root - missing this causes a crash on startup
- The backend server must be started before the proxy, or the proxy will fail to connect
