# How to Connect via Eaglercraft

This guide explains how to connect to your Eaglercraft Bridge server from a web browser.

## Steps

1. Open [eaglercraft.com/play](https://eaglercraft.com/play) in your web browser
2. Select **Minecraft 1.12.2** from the version selector
3. Click **Multiplayer**
4. Click **Add Server**
5. Enter the server address: `wss://YOUR-PROXY-IP:25565`
   - Replace `YOUR-PROXY-IP` with the public IP or domain of your BungeeCord proxy
6. Click **Done** and then **Join Server**

## Connection Address Format

```
wss://<proxy-ip-or-domain>:25565
```

If your proxy is running on the default port (25565) and has a domain, you can use:

```
wss://play.example.com:25565
```

## Requirements

- A modern web browser with WebSocket support (Chrome, Firefox, Edge, Safari)
- Stable internet connection (Wi-Fi recommended over mobile data)
- The proxy server must allow WebSocket connections on port 25565

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Proxy server is not running or port 25565 is blocked |
| "End of stream" | Reduce the server's view distance in server.properties |
| "Outdated Client" | Eaglercraft version does not match the server protocol |
| "Disconnected" | Check proxy logs for errors |
| Long loading time | Normal for first connection - server generates chunks |

## Limitations

Because the Eaglercraft 1.12.2 client connects to a Paper 26.1.2 backend via ViaBackwards protocol translation:

- Blocks, items, and mobs added after 1.12.2 will appear as substitute blocks or items
- Some 26.1.2 features may not work correctly on the Eaglercraft client
- This is an inherent limitation of protocol translation and cannot be fixed
