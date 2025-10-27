# Brian’s Restaurant

**Stack**
* Frontend: Svelte + TypeScript + Vite 
* Backend: Python (asyncio) with `asyncio-mqtt` 
* Broker: HiveMQ Cloud (managed)
* Hosting (frontend): **Netlify**

**Data flow**
Frontend publishes `orders/new`; backend processes and publishes `food/ready`. No HTTP API.

---

## Live Demo

**Site:** [https://osensarestaurant.netlify.app/](https://osensarestaurant.netlify.app/)

**What to expect on the site**

* 4-table UI. Click **ORDER** on any table, enter a food name.
* The app publishes `orders/new` to MQTT; items appear under **Preparing**.
* When the backend (running separately) receives the order, it simulates a short delay and publishes `food/ready`; the item moves to **Ready** in real time.
* If the backend is offline, the UI still accepts orders (they stay in **Preparing**).

**Backend runtime**

The backend runs privately on a headless PC (no public HTTP). It only makes an
outbound TLS MQTT connection to HiveMQ Cloud. The frontend talks
directly to HiveMQ over WSS, so no server URL is needed.

Live demo behavior:
- If the backend is online, orders move from “Preparing” → “Ready” in real time.
- If the backend is offline, the UI still accepts orders; they remain in “Preparing”.
---

## Build & Run (Local)

### Local MQTT Broker (optional, offline dev)

`dev/mosquitto-dev.conf`

```conf
listener 1883
protocol mqtt
listener 9001
protocol websockets
allow_anonymous true
persistence false
```

**Run (Windows):**

```powershell
& "C:\Program Files\mosquitto\mosquitto.exe" -v -c ".\dev\mosquitto-dev.conf"
```

**Local envs**

* Backend `.env`

  ```
  MQTT_HOST=localhost
  MQTT_PORT=1883
  MQTT_TLS=false
  ```
* Frontend `.env.local`

  ```
  VITE_MQTT_URL=ws://localhost:9001
  ```

### Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main
```

### Frontend

```powershell
cd frontend
npm install
npm run dev -- --host
# open printed URL (e.g., http://localhost:5173)
```

*(If not using a local broker, skip Mosquitto and use the HiveMQ settings below.)*

---

## Cloud Demo (HiveMQ Cloud)

### Frontend (build-time Vite envs)

Set (on Netlify or `.env.production.local`):

```
VITE_MQTT_URL=wss://<cluster-host>:8884/mqtt
VITE_MQTT_USERNAME=<user>
VITE_MQTT_PASSWORD=<pass>
```

Then:

```powershell
npm run build
npm run preview -- --host
```

### Backend (runs privately; outbound only)

`backend/.env.hivemq`

```
MQTT_HOST=<cluster-host>
MQTT_PORT=8883
MQTT_TLS=true
MQTT_USERNAME=<user>
MQTT_PASSWORD=<pass>
MQTT_SUB_TOPIC=orders/new
MQTT_PUB_READY=food/ready
```

Run:

```powershell
.\.venv\Scripts\Activate.ps1
$env:ENV_FILE=".env.hivemq"
python -m app.main
```

TLS uses `ssl.create_default_context()` and applies it via paho `tls_set_context` (no CA file path needed).

---

## Verify

**Backend logs**

```
[MQTT] connected -> <cluster-host>:8883
[MQTT] subscribed to orders/new
```

**HiveMQ Web Client** (WSS `:8884`, path `/mqtt`)
Subscribe to `orders/#` and `food/ready`. Publishing a valid JSON to `orders/new` results in `food/ready`.

---

## Topics & Payloads

**UI → backend** `orders/new` (QoS 1)

```json
{"v":1,"type":"ORDER","orderId":"uuid","tableId":1,"foodName":"Burger","requestedAt":1730000000.123}
```

**backend → UI** `food/ready` (QoS 1)

```json
{"v":1,"type":"FOOD_READY","orderId":"uuid","tableId":1,"foodName":"Burger","readyAt":1730000005.456,"prepMs":5000}
```

---

## Project Structure

```
frontend/
  src/
    App.svelte        # 4-table UI: Order → Preparing → Ready
    mqtt.ts           # mqtt.js client (reads VITE_MQTT_*; WSS for prod)
    table.ts          # table/state helpers
    lib/uuid.ts       # id helpers
    main.ts, app.css
  index.html, vite.config.ts, package.json
  .env.example, .env.local, .env.production.local

backend/
  app/
    main.py           # MQTT loop; subscribes 'orders/new' → handler
    handler.py        # validates order; publishes 'food/ready'
    models.py, logger.py
    mqtt_client.py    # asyncio-mqtt; sets TLS on paho
    settings.py       # loads .env / .env.hivemq via ENV_FILE
  requirements.txt, pytest.ini, .env.example, .env, .env.hivemq, test/
```

---

## Configuration (reference)

**Backend envs:** `MQTT_HOST`, `MQTT_PORT`, `MQTT_TLS`, `MQTT_USERNAME`, `MQTT_PASSWORD`, `MQTT_SUB_TOPIC`, `MQTT_PUB_READY`
**Frontend envs (Vite):** `VITE_MQTT_URL`, `VITE_MQTT_USERNAME`, `VITE_MQTT_PASSWORD`

---

## Tests & Coverage

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest -q
python -m coverage run -m pytest
python -m coverage report -m
# optional:
python -m coverage html
```
