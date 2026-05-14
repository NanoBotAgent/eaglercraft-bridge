# Eaglercraft Bridge — Master Prompt

**Saved**: 2026-05-13 21:12 UTC  
**Status**: Not started yet — awaiting user go-ahead  
**Resume Point**: Begin repository creation and file generation from line 1 of the spec

---

This is the full specification for building the Eaglercraft 1.12.2 → Minecraft 26.1.2 Bridge Server.
The original prompt was received via Telegram and is reproduced in full below.

---

## What You Are Building

A **two-server bridge system** that lets players using Eaglercraft 1.12.2 (browser-based Minecraft client) join a Paper 26.1.2 backend server. This requires a BungeeCord proxy in front of the game server because EaglerXServer cannot run directly on Paper versions above 1.12.2.

### Architecture

```
Eaglercraft 1.12.2 browser client
↓ WebSocket (wss://)
┌─────────────────────────────────┐
│ BungeeCord Proxy (Java 17+)    │ ← EaglerXServer plugin handles WebSocket
│ Port: 25565                    │
└─────────────────────────────────┘
↓ Internal TCP (localhost:25566)
┌─────────────────────────────────┐
│ Paper 26.1.2 Backend (Java 21+)│ ← ViaVersion + ViaBackwards handle
│ Port: 25566 (internal only)    │ the 1.12.2 ↔ 26.1.2 protocol gap
└─────────────────────────────────┘
```

### Why This Architecture

- EaglerXServer's official README explicitly states it does NOT support being installed on Spigot/Paper versions above 1.12.2 as a Bukkit plugin — it MUST run on BungeeCord or Velocity when used with a modern backend.
- EaglerXServer source and releases: **https://github.com/lax1dude/eaglerxserver/releases**
- Download the latest `EaglerXServer.jar` at runtime using: `https://api.github.com/repos/lax1dude/eaglerxserver/releases/latest`
- ViaBackwards bridges the Eaglercraft 1.12.2 client protocol to the 26.1.2 server protocol. It runs on BungeeCord (not on the Paper backend).

---

## Plugin Download URLs

All plugins must be downloaded at CI/build time using these sources. Never hardcode version numbers — always fetch latest:

| Plugin | Source | How to fetch |
|---|---|---|
| EaglerXServer | `https://github.com/lax1dude/eaglerxserver/releases/latest` | GitHub API → find asset named `EaglerXServer.jar` |
| ViaVersion | `https://github.com/ViaVersion/ViaVersion/releases/latest` | GitHub API → find asset named `ViaVersion-*.jar` |
| ViaBackwards | `https://github.com/ViaVersion/ViaBackwards/releases/latest` | GitHub API → find asset named `ViaBackwards-*.jar` |
| BungeeCord | `https://ci.md-5.net/job/BungeeCord/lastSuccessfulBuild/artifact/bootstrap/target/BungeeCord.jar` | Direct download |
| Paper 26.1.2 | `https://api.papermc.io/v2/projects/paper/versions/26.1.2/builds/` → get latest build → construct download URL | PaperMC API |

---

## Repository Structure

```
eaglercraft-bridge/
├── .github/
│   └── workflows/
│       ├── 01-validate-configs.yml
│       ├── 02-download-verify-plugins.yml
│       ├── 03-proxy-boot.yml
│       ├── 04-backend-boot.yml
│       ├── 05-full-stack-boot.yml
│       ├── 06-websocket-connect.yml
│       ├── 07-eaglercraft-handshake.yml
│       ├── 08-viaversion-bridge.yml
│       ├── 09-multi-client.yml
│       ├── 10-stress-test.yml
│       ├── 11-crash-recovery.yml
│       ├── 12-config-integrity.yml
│       ├── 13-release-package.yml
│       └── 14-nightly.yml
├── proxy/
│   ├── config.yml                 # BungeeCord config
│   ├── plugins/
│   │   └── .gitkeep
│   └── eaglerxserver/
│       └── listeners.yml          # EaglerXServer listener config
├── backend/
│   ├── server.properties          # Paper 26.1.2 config
│   ├── spigot.yml                 # bungeecord: true
│   ├── bukkit.yml
│   ├── paper.yml
│   ├── eula.txt                   # eula=true
│   └── plugins/
│       └── .gitkeep
├── scripts/
│   ├── download_all.sh            # Downloads all JARs
│   ├── download_eaglerxserver.sh  # EaglerXServer from GitHub releases
│   ├── download_viaversion.sh     # ViaVersion from GitHub releases
│   ├── download_viabackwards.sh   # ViaBackwards from GitHub releases
│   ├── download_bungeecord.sh     # BungeeCord from md-5 CI
│   ├── download_paper.sh          # Paper 26.1.2 from PaperMC API
│   ├── start_backend.sh           # Starts Paper 26.1.2
│   ├── start_proxy.sh             # Starts BungeeCord
│   ├── start_all.sh               # Starts backend then proxy
│   ├── stop_all.sh                # Gracefully stops both
│   ├── wait_for_backend.sh        # Polls until Paper is ready
│   └── wait_for_proxy.sh          # Polls until BungeeCord+WebSocket is ready
├── tests/
│   ├── conftest.py
│   ├── test_01_backend_tcp.py
│   ├── test_02_proxy_tcp.py
│   ├── test_03_websocket_upgrade.py
│   ├── test_04_eaglercraft_handshake.py
│   ├── test_05_motd.py
│   ├── test_06_viaversion_bridge.py
│   ├── test_07_multi_client.py
│   ├── test_08_invalid_packets.py
│   ├── test_09_stress.py
│   ├── test_10_crash_recovery.py
│   └── test_11_plugin_loaded.py
├── docker/
│   ├── Dockerfile.proxy           # BungeeCord + EaglerXServer
│   ├── Dockerfile.backend         # Paper 26.1.2
│   └── docker-compose.yml         # Full stack local dev
├── deploy/
│   ├── falixnodes-proxy-guide.md
│   ├── falixnodes-backend-guide.md
│   └── connect-guide.md           # How to connect via Eaglercraft
├── requirements.txt               # Python: websockets pytest asyncio
├── Makefile
└── README.md
```

---

## Configuration Files

### `proxy/config.yml` (BungeeCord)

```yaml
server_connect_timeout: 5000
listeners:
- query_port: 25565
  motd: '&aEaglercraft Server'
  tab_list: GLOBAL_PING
  query_enabled: true
  proxy_protocol: false
  forced_hosts: {}
  ping_passthrough: false
  priorities:
  - backend
  bind_local_address: true
  host: 0.0.0.0:25565
  max_players: 100
  force_default_server: false
  tab_size: 60
servers:
  backend:
    motd: '&1Backend'
    address: localhost:25566
    restricted: false
groups: {}
permissions: {}
online_mode: false
ip_forward: true
```

### `proxy/eaglerxserver/listeners.yml`

This file must configure EaglerXServer to inject into BungeeCord's existing listener. Key required fields:
```yaml
listeners:
- inject_address: "0.0.0.0:25565"
  eagler_players_cap: -1
  allow_eagler_players: true
  allow_vanilla_players: true
```

### `backend/server.properties`

```properties
online-mode=false
server-port=25566
server-ip=127.0.0.1
enable-query=false
motd=Backend
max-players=100
view-distance=10
```

### `backend/spigot.yml`

Must contain:
```yaml
settings:
  bungeecord: true
```

### `backend/eula.txt`

```
eula=true
```

---

## Scripts — Detailed Specs

All scripts must:
- Start with `#!/usr/bin/env bash`
- Have `set -euo pipefail` on line 2
- Print each action with a `[INFO]` prefix
- Exit 1 with a clear error message on failure

### `scripts/download_eaglerxserver.sh`

```bash
# Fetches latest EaglerXServer.jar from:
# https://api.github.com/repos/lax1dude/eaglerxserver/releases/latest
# Parses JSON with jq or Python to find the asset with name == "EaglerXServer.jar"
# Downloads to proxy/plugins/EaglerXServer.jar
# Prints the version tag it downloaded (e.g. "v1.1.0")
# Exits 1 if no asset found or download fails
```

### `scripts/download_paper.sh`

```bash
# Step 1: GET https://api.papermc.io/v2/projects/paper/versions/26.1.2/builds
# Step 2: Parse JSON, get the last build's "build" number
# Step 3: Construct URL:
# https://api.papermc.io/v2/projects/paper/versions/26.1.2/builds/{BUILD}/downloads/paper-26.1.2-{BUILD}.jar
# Step 4: Download to backend/paper-26.1.2.jar
# Step 5: Print build number downloaded
```

### `scripts/start_backend.sh`

```bash
# Run from backend/ directory
# Command:
java -Xms512M -Xmx2G \
  -XX:+UseG1GC \
  -XX:+ParallelRefProcEnabled \
  -XX:MaxGCPauseMillis=200 \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+DisableExplicitGC \
  -XX:G1NewSizePercent=30 \
  -XX:G1MaxNewSizePercent=40 \
  -XX:G1HeapRegionSize=8M \
  -XX:G1ReservePercent=20 \
  -jar paper-26.1.2.jar nogui \
  > logs/latest.log 2>&1 &
# Write PID to backend/server.pid
```

### `scripts/start_proxy.sh`

```bash
# Run from proxy/ directory
# Command:
java -Xms256M -Xmx512M \
  -XX:+UseG1GC \
  -jar BungeeCord.jar \
  > logs/latest.log 2>&1 &
# Write PID to proxy/server.pid
```

### `scripts/wait_for_backend.sh`

- Poll `localhost:25566` TCP every 2 seconds
- Also grep `backend/logs/latest.log` for `Done (`
- Timeout after 180 seconds (26.1.2 takes longer to boot than 1.12.2)
- Print progress every 15 seconds

### `scripts/wait_for_proxy.sh`

- Poll `localhost:25565` TCP every 2 seconds
- Also grep `proxy/logs/latest.log` for `Listening on`
- Additionally verify WebSocket responds by attempting a Python WebSocket connect
- Timeout after 60 seconds

---

## GitHub Actions Workflows — Detailed Specs

Every workflow must have:
- `timeout-minutes: 15` on every job
- Java 21 setup using `actions/setup-java@v4` with `distribution: temurin`, `java-version: 21`
- Python 3.11 setup using `actions/setup-python@v5`
- Upload of ALL log files as artifacts on both success AND failure
- A final step that prints a clear PASS/FAIL summary

### Workflow 01: `validate-configs.yml`
**Trigger:** Push to any branch, PR to main

**Steps:**
1. Check `backend/server.properties` contains `online-mode=false`
2. Check `backend/server.properties` contains `server-port=25566`
3. Check `backend/spigot.yml` contains `bungeecord: true`
4. Check `backend/eula.txt` contains `eula=true`
5. Check `proxy/config.yml` contains `online_mode: false`
6. Check `proxy/config.yml` contains `address: localhost:25566`
7. Validate all `.yml` files are parseable using Python `yaml.safe_load()`
8. Check all `.sh` scripts have execute permission (`git ls-files --stage scripts/`)
9. Fail with specific line-level errors for any mismatch

### Workflow 02: `download-verify-plugins.yml`
**Trigger:** Push to main, PR to main, scheduled weekly

**Steps:**
1. Run `scripts/download_all.sh`
2. Verify `proxy/plugins/EaglerXServer.jar` exists and is > 1MB
3. Verify `proxy/plugins/ViaVersion-*.jar` exists and is > 1MB
4. Verify `proxy/plugins/ViaBackwards-*.jar` exists and is > 1MB
5. Verify `proxy/BungeeCord.jar` exists and is > 1MB
6. Verify `backend/paper-26.1.2.jar` exists and is > 10MB
7. Run `java -jar backend/paper-26.1.2.jar --version` and assert output contains `26.1.2`
8. Print all downloaded versions to the log
9. Upload all downloaded JARs as artifacts (for reproducibility)

### Workflow 03: `proxy-boot.yml`
**Trigger:** Push to main, PR to main

**Steps:**
1. Download all plugins
2. Start ONLY the proxy (`scripts/start_proxy.sh`)
3. Wait up to 60 seconds for BungeeCord to boot
4. Assert `proxy/logs/latest.log` contains `Listening on`
5. Assert log does NOT contain `Could not load 'plugins/EaglerXServer.jar'`
6. Assert log does NOT contain `UnsupportedClassVersionError`
7. Assert log contains `EaglerXServer` (plugin loaded)
8. Stop proxy
9. Upload logs

### Workflow 04: `backend-boot.yml`
**Trigger:** Push to main, PR to main

**Steps:**
1. Download Paper 26.1.2
2. Start ONLY the backend (`scripts/start_backend.sh`)
3. Wait up to 180 seconds for Paper to boot
4. Assert `backend/logs/latest.log` contains `Done (`
5. Assert log does NOT contain `[ERROR]` for any critical plugin
6. Stop backend
7. Upload logs

### Workflow 05: `full-stack-boot.yml`
**Trigger:** Push to main, PR to main

**Steps:**
1. Download all plugins
2. Start backend, wait for it to fully boot
3. Start proxy, wait for it to fully boot
4. Assert both PIDs are still alive (server didn't crash)
5. Assert `proxy/logs/latest.log` shows successful connection to backend (look for `backend` server registration)
6. Stop all
7. Upload all logs

### Workflow 06: `websocket-connect.yml`
**Trigger:** Push to main, PR to main

**Steps:**
1. Full stack boot
2. `pip install websockets pytest`
3. Run `pytest tests/test_03_websocket_upgrade.py -v`
4. Test must open a WebSocket to `ws://localhost:25565` and assert it does not immediately close with an error
5. Upload test results as JUnit XML

### Workflow 07: `eaglercraft-handshake.yml`
**Trigger:** Push to main, PR to main

**Steps:**
1. Full stack boot
2. Run `pytest tests/test_04_eaglercraft_handshake.py tests/test_05_motd.py -v`
3. Handshake test: send Eaglercraft V4 intro packet, assert valid response received
4. MOTD test: request MOTD, assert server name returned matches `proxy/config.yml` motd value
5. Upload results

### Workflow 08: `viaversion-bridge.yml`
**Trigger:** Push to main, PR to main

**Steps:**
1. Full stack boot
2. Run `pytest tests/test_06_viaversion_bridge.py -v`
3. This test verifies ViaVersion and ViaBackwards loaded on the proxy by checking `proxy/logs/latest.log` for:
   - `ViaVersion` loaded successfully
   - `ViaBackwards` loaded successfully
   - No ViaVersion errors related to protocol translation
4. Upload results

### Workflow 09: `multi-client.yml`
**Trigger:** Push to main

**Steps:**
1. Full stack boot
2. Run `pytest tests/test_07_multi_client.py -v`
3. Opens 10 simultaneous WebSocket connections using `asyncio.gather()`
4. All 10 must connect within 10 seconds
5. All 10 held open for 3 seconds
6. All closed cleanly
7. Upload results

### Workflow 10: `stress-test.yml`
**Trigger:** Push to main, scheduled weekly (Sunday 02:00 UTC)

**Steps:**
1. Full stack boot
2. Run `pytest tests/test_09_stress.py -v --timeout=180`
3. 100 sequential connect → handshake → disconnect cycles
4. Assert zero failures across all 100
5. Assert mean connection time < 1000ms
6. Assert server still alive and responsive after all cycles
7. Upload results + timing CSV

### Workflow 11: `crash-recovery.yml`
**Trigger:** Push to main

**Steps:**
1. Full stack boot
2. Run `pytest tests/test_10_crash_recovery.py -v`
3. This test:
   - Sends 20 completely invalid binary payloads over WebSocket
   - Asserts server closes connection gracefully each time (not a crash)
   - Opens a valid WebSocket after each invalid one and asserts it still responds
   - Verifies backend Paper server is still running throughout
4. Upload results

### Workflow 12: `config-integrity.yml`
**Trigger:** Push to main, PR to main

**Steps:**
1. Full stack boot and clean shutdown
2. After shutdown:
   - Assert `backend/server.properties` still has `online-mode=false` (Paper didn't overwrite it)
   - Assert `backend/spigot.yml` still has `bungeecord: true`
   - Assert `proxy/plugins/EaglerXServer/` config directory was created
   - Assert `proxy/plugins/ViaVersion/` config directory was created
   - Assert `proxy/plugins/ViaBackwards/` config directory was created
   - Parse all generated configs with `yaml.safe_load()` and assert they are valid
3. Upload all generated config directories as artifacts

### Workflow 13: `release-package.yml`
**Trigger:** Push of tag matching `v*` (e.g. `v1.0.0`)

**Steps:**
1. Run all download scripts
2. Boot full stack, run full test suite, stop
3. If tests pass, create `eaglercraft-bridge-{TAG}.zip` containing:
   - `proxy/` directory (with BungeeCord.jar, all plugin JARs, all configs)
   - `backend/` directory (with paper-26.1.2.jar, all configs)
   - `scripts/` directory
   - `deploy/` guides
   - `README.md`
4. Create GitHub Release using `softprops/action-gh-release`
5. Attach ZIP to release
6. Release notes must include:
   - EaglerXServer version used (from GitHub releases tag)
   - BungeeCord build number
   - Paper 26.1.2 build number
   - ViaVersion version
   - ViaBackwards version
   - Connect instructions: "Open eaglercraft.com/play → 1.12.2 → Multiplayer → Add Server → `wss://YOUR-IP:25565`"

### Workflow 14: `nightly.yml`
**Trigger:** Scheduled daily at 04:00 UTC

**Jobs:**
1. `full-suite` — Runs workflows 01 through 12 in sequence
2. `check-updates` — Hits GitHub API for EaglerXServer, ViaVersion, ViaBackwards; if newer than what's pinned in the repo, opens a GitHub Issue titled "Plugin update available: {name} {newVersion}"
3. `nightly-report` — Posts a commit status with total pass/fail count

---

## Python Tests — Detailed Specs

### `conftest.py`

```python
import pytest, os

@pytest.fixture
def proxy_host(): return "localhost"

@pytest.fixture
def proxy_port(): return int(os.getenv("PROXY_PORT", "25565"))

@pytest.fixture
def backend_host(): return "localhost"

@pytest.fixture
def backend_port(): return int(os.getenv("BACKEND_PORT", "25566"))

@pytest.fixture
def ws_url(proxy_host, proxy_port): return f"ws://{proxy_host}:{proxy_port}"

@pytest.fixture
def eagler_handshake_packet():
    # Standard Eaglercraft V4 WebSocket intro packet bytes
    # Research exact format from https://github.com/lax1dude/eaglerxserver source
    # This is the binary packet sent by Eaglercraft 1.12.2 clients on first connect
    return bytes([...]) # AI: implement from EaglerXServer source
```

### `test_01_backend_tcp.py`
- Raw TCP socket to `localhost:25566`
- Assert connects within 3 seconds
- Docstring: "Verifies Paper 26.1.2 backend is listening on its internal port"

### `test_02_proxy_tcp.py`
- Raw TCP socket to `localhost:25565`
- Assert connects within 3 seconds
- Docstring: "Verifies BungeeCord proxy is listening on the public port"

### `test_03_websocket_upgrade.py`
- `websockets.connect("ws://localhost:25565")`
- Assert no `ConnectionRefusedError`
- Assert no HTTP 400/500 response
- Assert connection stays open for 2 seconds
- Docstring: "Verifies EaglerXServer successfully upgrades HTTP to WebSocket"

### `test_04_eaglercraft_handshake.py`
- Connect WebSocket
- Send Eaglercraft V4 handshake packet (binary)
- Assert response received within 5 seconds
- Assert response length > 0
- Docstring: "Verifies EaglerXServer correctly handles Eaglercraft protocol V4 handshake"

### `test_05_motd.py`
- Connect WebSocket
- Send MOTD query packet
- Assert non-empty MOTD string returned
- Docstring: "Verifies server correctly serves MOTD to Eaglercraft clients"

### `test_06_viaversion_bridge.py`
- Read `proxy/logs/latest.log`
- Assert contains `ViaVersion` (loaded)
- Assert contains `ViaBackwards` (loaded)
- Assert does NOT contain `ViaVersion] Could not` or `ViaBackwards] Could not`
- Docstring: "Verifies ViaVersion and ViaBackwards loaded correctly to bridge 1.12.2 ↔ 26.1.2"

### `test_07_multi_client.py`
- `asyncio.gather()` 10 simultaneous WebSocket connections
- All 10 must succeed within 10 seconds
- Hold all 10 open for 3 seconds
- Close all cleanly
- Assert zero exceptions across all 10
- Docstring: "Verifies server handles 10 simultaneous Eaglercraft connections"

### `test_08_invalid_packets.py`
- Send 5 random garbage binary payloads to WebSocket
- Assert server closes connection gracefully (no crash)
- After each bad packet, open a fresh valid WebSocket and assert it responds
- Docstring: "Verifies server gracefully handles malformed packets without crashing"

### `test_09_stress.py`
- 100 sequential connect → send handshake → disconnect cycles
- Record time of each
- Assert all 100 succeed
- Assert mean time < 1000ms
- Write timing CSV to `test_results/stress_timings.csv`
- Final check: open one more connection after all 100, assert it still works
- Docstring: "Stress tests server stability under rapid repeated connections"

### `test_10_crash_recovery.py`
- 20 cycles of: send garbage → assert server still alive → valid connect → assert responds
- Between each: check `proxy/server.pid` PID is still running using `os.kill(pid, 0)`
- Also check `backend/server.pid` is still running
- Docstring: "Verifies both proxy and backend remain alive after repeated invalid connections"

### `test_11_plugin_loaded.py`
- Read `proxy/logs/latest.log`
- Assert contains `EaglerXServer` (loaded without error)
- Assert does NOT contain `Could not load 'plugins/EaglerXServer.jar'`
- Assert does NOT contain `UnsupportedClassVersionError`
- Assert contains `EaglerXServer` and NOT `ERROR` on the same line
- Docstring: "Verifies EaglerXServer plugin loaded successfully on BungeeCord"

---

## Docker Setup

### `docker/Dockerfile.proxy`

```dockerfile
FROM eclipse-temurin:21-jre-jammy
WORKDIR /proxy
COPY proxy/ .
EXPOSE 25565
CMD ["java", "-Xms256M", "-Xmx512M", "-XX:+UseG1GC", "-jar", "BungeeCord.jar"]
```

### `docker/Dockerfile.backend`

```dockerfile
FROM eclipse-temurin:21-jre-jammy
WORKDIR /backend
COPY backend/ .
EXPOSE 25566
CMD ["java", "-Xms512M", "-Xmx2G", "-XX:+UseG1GC", "-jar", "paper-26.1.2.jar", "nogui"]
```

### `docker/docker-compose.yml`

```yaml
version: "3.9"
services:
  backend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.backend
    ports: []  # NOT exposed publicly — internal only
    networks:
      - mcnet
    volumes:
      - ./backend/world:/backend/world
      - ./backend/logs:/backend/logs

  proxy:
    build:
      context: ..
      dockerfile: docker/Dockerfile.proxy
    ports:
      - "25565:25565"
    networks:
      - mcnet
    depends_on:
      - backend
    volumes:
      - ./proxy/logs:/proxy/logs

networks:
  mcnet:
    driver: bridge
```

---

## Makefile

```makefile
.PHONY: setup start stop test test-all docker-build docker-run clean

setup:
	@bash scripts/download_all.sh

start:
	@bash scripts/start_all.sh

stop:
	@bash scripts/stop_all.sh

test:
	@pip install -r requirements.txt -q
	@pytest tests/ -v

test-all: setup start
	@sleep 5
	@$(MAKE) test
	@$(MAKE) stop

docker-build:
	@cd docker && docker compose build

docker-run: docker-build
	@cd docker && docker compose up

clean:
	@rm -f proxy/BungeeCord.jar proxy/plugins/*.jar
	@rm -f backend/paper-26.1.2.jar backend/plugins/*.jar
	@rm -rf backend/world backend/cache backend/logs
	@rm -rf proxy/logs
```

---

## `requirements.txt`

```
websockets>=12.0
pytest>=8.0
pytest-asyncio>=0.23
pytest-timeout>=2.3
aiohttp>=3.9
pyyaml>=6.0
```

---

## `README.md` Must Include

### 1. Architecture diagram (text)
Show the proxy → backend flow clearly.

### 2. Prerequisites
- Java 21+ on BOTH servers
- Python 3.11+ (for tests only)
- Two separate server slots (e.g. FalixNodes for proxy, MCServerHost for backend — but MCServerHost must support Java 21 for the 26.1.2 backend, which may require a different host)

### 3. Quick start
```bash
make setup  # Downloads all JARs
make start  # Starts backend then proxy
make test   # Runs full test suite
```

### 4. How to connect
> Open [eaglercraft.com/play](https://eaglercraft.com/play) → Select **1.12.2** → Multiplayer → Add Server → enter `wss://YOUR-PROXY-IP:25565`

### 5. Deployment guides
Link to `deploy/falixnodes-proxy-guide.md` and `deploy/falixnodes-backend-guide.md`

### 6. Important limitations
Explain that ViaBackwards bridges the protocol but new 26.1.2 blocks/mobs/items (added after 1.12.2) will appear as old or substituted blocks on the Eaglercraft client side. This is unavoidable.

### 7. CI badge
```markdown
![Server Boot](https://github.com/YOUR_USER/eaglercraft-bridge/actions/workflows/05-full-stack-boot.yml/badge.svg)
![WebSocket](https://github.com/YOUR_USER/eaglercraft-bridge/actions/workflows/06-websocket-connect.yml/badge.svg)
```

### 8. Troubleshooting table

| Error | Cause | Fix |
|---|---|---|
| `UnsupportedClassVersionError` on EaglerXServer | BungeeCord running on Java 8 | Switch proxy host to Java 17+ |
| `Could not load EaglerXServer.jar` | Same Java issue | Same fix |
| `Could not connect to backend` in proxy log | Paper backend not yet started / wrong port | Start backend first, check port 25566 |
| WebSocket connection refused | EaglerXServer not loaded on proxy | Check proxy logs for plugin errors |
| `bungeecord: false` warning in Paper log | Forgot to set bungeecord: true in spigot.yml | Set it and restart backend |
| New 26.1.2 blocks look wrong | ViaBackwards limitation | Expected — cannot be fixed |
| Connection timeout | Host blocking WebSocket on port 25565 | Contact host support |

---

## Quality Requirements

### Workflows
- Every job must have `timeout-minutes: 15`
- Every job must upload logs as artifact on success AND failure using `if: always()`
- Step names must be descriptive (not "Run step 1")
- Each workflow file must have a top-level comment explaining what it tests and why

### Scripts
- Every `download_*.sh` must print: `[INFO] Downloaded {name} version {version} → {path}`
- Every `wait_for_*.sh` must print elapsed time every 15 seconds
- All scripts must be idempotent (safe to run multiple times)

### Tests
- Every test file must have a module-level docstring explaining the test scenario
- Every test function must have a docstring
- All async tests must use `@pytest.mark.asyncio`
- Tests must clean up (close connections, kill processes) even on failure using `try/finally`
- Tests must be individually runnable: `pytest tests/test_03_websocket_upgrade.py`

### The final repo must pass all 14 workflows on a clean checkout with zero manual steps beyond `make setup`.
