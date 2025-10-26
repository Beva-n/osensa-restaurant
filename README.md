

# Brian's Restaurant

Frontend: **Svelte + TypeScript + Vite**
Backend: **Python (asyncio)**
Transport: **MQTT**. The browser publishes `orders/new`; the backend processes and publishes `food/ready`.

## Quick Start (Windows)

### 0) MQTT Broker (Mosquitto)

Start one verbose instance and keep it running:

```powershell
& "C:\Program Files\mosquitto\mosquitto.exe" -v -c "C:\mosq\mosquitto.conf"
```

Minimal dev config (`C:\mosq\mosquitto.conf`):

```
listener 1883
protocol mqtt

listener 9001
protocol websockets

allow_anonymous true   # dev only
```

### 1) Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# run (uses TCP 1883)
$env:MQTT_HOST="127.0.0.1"
$env:MQTT_PORT="1883"
python -m app.main
```

Expected logs:
`Connected to MQTT 127.0.0.1:1883` → `Subscribed to orders/new`

### 2) Frontend

```powershell
cd frontend
npm install
npm install mqtt

# dev server
npm run dev -- --host
# open the printed URL (e.g., http://localhost:5173)
```

The frontend connects to `ws://<host>:9001` by default (see `src/mqtt.ts`).

---

## What to Expect

* Click **ORDER** on a table → enter a food name
* UI publishes to **`orders/new`** (QoS 1)
* Backend simulates prep (random 2–8s) and publishes **`food/ready`** (QoS 1)
* UI moves item from **Preparing → Ready**

---

## Topics & Payloads

**Publish (UI → backend):** `orders/new`

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

**Publish (backend → UI):** `food/ready`

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

Notes:

* **QoS:** 1 both ways (at-least-once).
* UI removes from “Preparing” by **full `orderId`** match (short ID is display-only).

---

## Project Structure

```
frontend/
  src/
    App.svelte        # 4-table UI, ORDER button, Preparing → Ready
    mqtt.ts           # connects via mqtt.js (WebSockets)
    stores.ts         # state per table
    lib/uuid.ts       # id helpers
  vite.config.ts

backend/
  app/
    __init__.py
    main.py           # MQTT loop, subscribe to orders/new
    handler.py        # validates Order, simulates prep, publishes food/ready
    models.py         # Pydantic models (Order, FoodReady)
    logger.py         # Loguru setup
    mqtt_client.py    # minimal TCP client builder
  requirements.txt
  pytest.ini
  test/               # pytest suite
```

---

## Configuration

Environment variables:

* **Backend**

    * `MQTT_HOST` (default `127.0.0.1`)
    * `MQTT_PORT` (default `1883`)
* **Frontend**

    * `VITE_MQTT_URL` (optional) override, e.g. `wss://your-broker.example.com/mqtt`
      If unset, it uses `ws://<current-host>:9001`.

---

## Security & Input Validation

* **Frontend:** Svelte escapes text by default; we **do not** use `{@html}`. Food name is validated (length & charset) before publish.
* **Backend:** Pydantic model validation; invalid payloads are dropped and logged.
* **Dev only:** `allow_anonymous true`. For an internet demo, use a managed MQTT with user/pass + WSS (and reconfigure frontend `VITE_MQTT_URL`).

---

## Logging

Backend logs the lifecycle:

* Connect/subscribe messages
* Inbound `orders/new` (sanitized)
* Outbound `food/ready`
* Errors (validation drop, disconnect/retry)

---

## Tests

Backend tests (pytest) cover models, handler happy- and error-paths, and client creation.

Run:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

**Backend Test Coverage:** 100% of application code (`app/*`).
(Overall repo coverage lower(98%) due to test helpers.)

---
