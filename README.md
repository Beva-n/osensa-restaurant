# Brian’s Restaurant — Grader Notes

**Stack**

Frontend: Svelte + TypeScript + Vite (browser → MQTT over **WSS :8884**)

Backend: Python (asyncio) with `asyncio-mqtt` (server → MQTT over **TLS :8883**)

Broker: HiveMQ Cloud (managed)

**Data flow**
Frontend publishes `orders/new`; backend processes and publishes `food/ready`. No HTTP API required.

---

## Build & Run (Local)

### Local MQTT Broker 

Use a tiny Mosquitto config in the repo:

```
dev/mosquitto-dev.conf
```

```conf
listener 1883
protocol mqtt

listener 9001
protocol websockets

allow_anonymous true
persistence false
```

**Run Example (Windows):**

```powershell
& "C:\Program Files\mosquitto\mosquitto.exe" -v -c ".\dev\mosquitto-dev.conf"
```

**Wire local envs:**

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

---

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

*(If not running a local broker, skip the Mosquitto step and use the HiveMQ Cloud envs instead.)*


---

## Cloud Demo (HiveMQ Cloud)

### Frontend (production env at build time)

Set Vite variables:

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

### Backend 

`backend/.env.hivemq`:

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
$env:ENV_FILE=".env.hivemq"   # app/settings.py loads this
python -m app.main
```

TLS uses `ssl.create_default_context()` and configures the underlying paho client via `tls_set_context` (no CA file path needed).

---

## Verify

**Backend logs**

```
[MQTT] connected -> <cluster-host>:8883
[MQTT] subscribed to orders/new
```

**HiveMQ Web Client**
Connect with WSS `:8884`, path `/mqtt`. Subscribe to `orders/#` and `food/ready`.
Publishing a valid JSON to `orders/new` should result in a `food/ready` message.

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
    lib/
      uuid.ts         # id helpers
    main.ts           # Svelte bootstrap
    app.css
  index.html
  vite.config.ts
  package.json
  .env.example        # sample (no secrets)
  .env.local          # local dev (gitignored)
  .env.production.local  # prod values for local build tests (gitignored)

backend/
  app/
    __init__.py
    main.py           # MQTT loop; subscribes 'orders/new' and dispatches handler
    handler.py        # validates Order; simulates prep; publishes 'food/ready'
    models.py         # Pydantic models (Order, FoodReady)
    logger.py         # logging setup
    mqtt_client.py    # asyncio-mqtt client; sets TLS on paho
    settings.py       # loads .env / .env.hivemq via ENV_FILE
  requirements.txt
  pytest.ini
  .env.example        # sample (no secrets)
  .env                # local dev (gitignored)
  .env.hivemq         # HiveMQ creds (gitignored)
  test/               # pytest suite
```

---

## Configuration (reference)

**Backend envs**

* `MQTT_HOST` (default `127.0.0.1`)
* `MQTT_PORT` (default `1883`)
* `MQTT_TLS` (`true|false`)
* `MQTT_USERNAME`, `MQTT_PASSWORD`
* `MQTT_SUB_TOPIC`, `MQTT_PUB_READY`

**Frontend envs (Vite)**

* `VITE_MQTT_URL` (e.g., `wss://<cluster-host>:8884/mqtt`)
* `VITE_MQTT_USERNAME`, `VITE_MQTT_PASSWORD`

---

## Tests & Coverage

Run:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

Coverage:

```powershell
python -m coverage run -m pytest
python -m coverage report -m
# optional HTML:
python -m coverage html
```

(The suite covers core logic; TLS configuration is covered by monkey-patching `paho.Client.tls_set_context`.)
