# at the top (keep your Windows loop policy fix if you added it)
import os, asyncio, signal, sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from asyncio_mqtt import MqttError
from .mqtt_client import build_client
from .handler import handle_order
from .logger import logger

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC_ORDERS = "orders/new"

async def run() -> None:
    backoff = 2
    while True:
        try:
            client = build_client(MQTT_HOST, MQTT_PORT)
            async with client:
                logger.info(f"Connected to MQTT {MQTT_HOST}:{MQTT_PORT}")

                async with client.filtered_messages(TOPIC_ORDERS) as messages:
                    await client.subscribe(TOPIC_ORDERS, qos=1)
                    async for msg in messages:
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
