import os, asyncio, sys
from asyncio_mqtt import MqttError, Topic
from .mqtt_client import build_client
from .handler import handle_order
from .logger import logger

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC_ORDERS_STR = "orders/new"
TOPIC_ORDERS = Topic(TOPIC_ORDERS_STR)

async def run() -> None:
    backoff = 2
    while True:
        try:
            client = build_client(MQTT_HOST, MQTT_PORT)
            async with client:
                logger.info(f"Connected to MQTT {MQTT_HOST}:{MQTT_PORT}")

                async with client.messages() as messages:
                    # PASS THE STRING here ⤵️
                    await client.subscribe(TOPIC_ORDERS_STR, qos=1)
                    logger.info(f"Subscribed to {TOPIC_ORDERS_STR}")

                    async for msg in messages:
                        # Log what we see
                        t = str(getattr(msg, "topic", "<unknown>"))
                        logger.info(f"RX on {t}: {msg.payload!r}")

                        # Use Topic.matches() to filter
                        if TOPIC_ORDERS.matches(msg.topic):
                            asyncio.create_task(handle_order(client, msg.payload))

        except (MqttError, OSError) as e:
            logger.error(f"MQTT disconnected from {MQTT_HOST}:{MQTT_PORT}: {e}. Reconnecting in {backoff}s.")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 10)
        except Exception as e:
            logger.error(f"Fatal loop error: {e}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
