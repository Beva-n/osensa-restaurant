# Restaurant Frontend (Svelte + TypeScript + Vite)

Minimal UI for placing table orders and receiving `FOOD_READY` events over **MQTT (WebSockets)**.
Pairs with the Python asyncio backend and an MQTT broker. No REST.

## Prereqs

* **Node.js LTS ≥ 22.12** (recommended: 22.21.0)
* **MQTT broker** with a **WebSocket** listener (dev example uses Mosquitto on `ws://localhost:9001`)

## Quick start

```bash
# from repo root (or cd frontend first)
cd frontend
npm install
npm install mqtt

# start dev server
npm run dev -- --host
# open the printed URL (e.g., http://localhost:5173)
```

## Configure MQTT

`src/mqtt.ts` defines the WebSocket URL:

```ts
// src/mqtt.ts
const url = `ws://${location.hostname}:9001`; // change if needed (e.g., wss://your-broker.example.com/mqtt)
```

Common values:

* Local broker (dev): `ws://localhost:9001`
* LAN test: `ws://<your-lan-ip>:9001`
* Public/managed broker: `wss://<host>:443/mqtt` (must be **wss** if your site is **https**)

## Scripts

```bash
npm run dev       # dev server with HMR
npm run build     # production build -> dist/
npm run preview   # locally serve dist/ for a quick check
```

## Files to know

```
frontend/
  src/
    App.svelte        # UI: 4 tables, ORDER button, Preparing → Ready flow
    mqtt.ts           # MQTT client (mqtt.js) over WebSockets
    stores.ts         # Svelte store for per-table state
    lib/uuid.ts       # small ID helpers
  index.html
  vite.config.ts
```

## Topics & payloads

* **Publish (UI → backend):** `orders/new`

```json
{
  "v": 1,
  "type": "ORDER",
  "orderId": "uuid",
  "tableId": 1,
  "foodName": "Burger",
  "requestedAt": 1730000000.123
}
```

* **Subscribe (backend → UI):** `food/ready`

```json
{
  "v": 1,
  "type": "FOOD_READY",
  "orderId": "uuid",
  "tableId": 1,
  "foodName": "Burger",
  "readyAt": 1730000005.456,
  "prepMs": 5000
}
```

Notes: **QoS 1** used both ways. UI removes a preparing item by **full `orderId`** match (short ID is for display only).

## Dev broker (example)

Mosquitto config (for local dev):

```
listener 1883
protocol mqtt
listener 9001
protocol websockets
allow_anonymous true
```

Start on Windows:

```powershell
& "C:\Program Files\mosquitto\mosquitto.exe" -v -c "C:\mosq\mosquitto.conf"
```

## Troubleshooting

* **Browser can’t connect to MQTT:** broker not running, wrong port, or missing **websockets** listener. If your site is HTTPS, use **wss://**.
* **Orders never become Ready:** backend not running/subscribed, or frontend points to a different broker host/port.
* **Port conflicts:** change the WS port in both the broker config and `src/mqtt.ts`.
