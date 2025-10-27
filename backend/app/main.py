# app/main.py
import asyncio, contextlib, sys
from asyncio_mqtt import MqttError, Topic
from app.mqtt_client import build_client          # <- reads envs & TLS itself
from app.handler import handle_order
from app.logger import logger
from app.settings import MQTT_SUB_TOPIC, MQTT_HOST, MQTT_PORT

# Windows asyncio fix
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TOPIC_ORDERS_STR = MQTT_SUB_TOPIC
TOPIC_ORDERS = Topic(TOPIC_ORDERS_STR)

async def run() -> None:
    """
    Connect to MQTT, subscribe to orders, and hand off to handle_order().
    Reconnects with exponential backoff.
    """
    backoff = 2
    while True:
        try:
            # build_client() already applies username/password and TLS if MQTT_TLS=true
            async with build_client() as client:
                logger.info(f"[MQTT] connected -> {MQTT_HOST}:{MQTT_PORT}")
                backoff = 2  # reset backoff after a successful connect

                async with client.messages() as messages:
                    await client.subscribe(TOPIC_ORDERS_STR, qos=1)
                    logger.info(f"[MQTT] subscribed to {TOPIC_ORDERS_STR}")

                    async for msg in messages:
                        t = str(getattr(msg, "topic", "<unknown>"))
                        logger.info(f"[MQTT] RX {t}: {msg.payload!r}")

                        if TOPIC_ORDERS.matches(msg.topic):
                            # fan out without blocking the receive loop
                            asyncio.create_task(handle_order(client, msg.payload))

        except (MqttError, OSError) as e:
            logger.error(f"[MQTT] disconnected {MQTT_HOST}:{MQTT_PORT}: {e}. Reconnecting in {backoff}s…")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 10)
        except Exception as e:
            logger.exception(f"[MQTT] fatal loop error: {e}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
