import socket, ssl
from asyncio_mqtt import Client
from app.settings import MQTT_HOST, MQTT_PORT, MQTT_TLS, MQTT_USERNAME, MQTT_PASSWORD

def build_client() -> Client:
    c = Client(
        hostname=MQTT_HOST,
        port=MQTT_PORT,
        username=MQTT_USERNAME or None,
        password=MQTT_PASSWORD or None,
        transport="tcp",
        client_id=f"py_backend_{socket.gethostname()}",
        clean_session=True,
        keepalive=60,
    )

    if MQTT_TLS:
        # Use system CA bundle (works for HiveMQ Cloud)
        ctx = ssl.create_default_context()
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        c._client.tls_set_context(ctx)

    return c
