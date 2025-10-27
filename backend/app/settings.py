import os
from dotenv import load_dotenv
ENV_FILE = os.getenv("ENV_FILE", ".env")
load_dotenv(dotenv_path=ENV_FILE, override=False)

MQTT_HOST       = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT       = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TLS        = os.getenv("MQTT_TLS", "false").lower() in ("1","true","yes")
MQTT_USERNAME   = os.getenv("MQTT_USERNAME") or None
MQTT_PASSWORD   = os.getenv("MQTT_PASSWORD") or None

MQTT_SUB_TOPIC  = os.getenv("MQTT_SUB_TOPIC", "orders/new")
MQTT_PUB_READY  = os.getenv("MQTT_PUB_READY", "food/ready")
