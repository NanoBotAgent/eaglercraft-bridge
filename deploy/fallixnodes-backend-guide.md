# FalixNodes Backend Setup Guide

This guide covers setting up the Paper 26.1.2 backend server on FalixNodes for the Eaglercraft Bridge.

## Prerequisites

- FalixNodes account with a Minecraft server slot (separate from the proxy slot)
- Java 25+ (required by Paper 26.1.2)
- The backend does NOT need to be publicly accessible - only the proxy connects to it

## Important

FalixNodes may not support Java 25 yet for Minecraft servers. If Java 25 is unavailable, you will need to use a different hosting provider that supports it. Paper 26.1.2 requires Java 25 minimum and will not start on Java 17 or Java 21.

## Steps

### 1. Create a Paper Server

1. Log into FalixNodes panel
2. Create a new Minecraft server
3. Select **Paper** as the server type (version 26.1.2)
4. Choose **Java 25** as the runtime
5. Set the server port to **25566**

### 2. Upload Files

Upload the following files from the `backend/` directory:

- `paper-26.1.2.jar` - Paper server JAR
- `server.properties` - Server configuration
- `spigot.yml` - Spigot/Paper configuration (bungeecord: true)
- `eula.txt` - EULA acceptance

### 3. Configure server.properties

Verify these key settings:

```properties
online-mode=false
server-port=25566
server-ip=127.0.0.1
```

`online-mode=false` is required because Eaglercraft clients cannot authenticate with Mojang servers. The proxy handles BungeeCord forwarding instead.

### 4. Configure spigot.yml

Verify this critical setting:

```yaml
settings:
  bungeecord: true
```

This tells Paper to accept connections from the BungeeCord proxy. Without it, players will be kicked.

### 5. Start the Backend

Start the server from the FalixNodes panel. Check the console for:

- `Done (` - Paper is fully loaded and ready

### 6. Connect to the Proxy

Once the backend is running, start the BungeeCord proxy. The proxy will connect to the backend on port 25566.

## Security Warning

The backend server has `online-mode=false` which means anyone with direct access to port 25566 could impersonate players. Ensure the backend is only accessible from the proxy:

- Set `server-ip=127.0.0.1` in server.properties
- Use firewall rules to block external access to port 25566
- Only the proxy should connect to the backend

## Java Version Check

If Paper fails to start with a version error, check that Java 25+ is being used:

```bash
java -version
```

If the host does not support Java 25, Paper 26.1.2 will not work. Consider using a host that supports modern Java versions.
