# backend/app/handlers.py
import asyncio, json, random, time
from asyncio_mqtt import Client
from .models import Order, FoodReady
from .logger import logger

async def handle_order(client: Client, payload: bytes) -> None:
    """
    Process an ORDER message from 'orders/new'.

    - Validates JSON payload into Order model.
    - Simulates a random prep delay.
    - Publishes FOOD_READY to 'food/ready' with same orderId/tableId.

    Drops invalid payloads (logs a warning) without crashing.
    """
    try:
        data = json.loads(payload.decode("utf-8"))
        order = Order(**data)
    except Exception as e:
        logger.warning(f"[DROP] invalid order: {e}")
        return

    # Simulate preparation
    prep_s = random.randint(5, 20)
    logger.info(f"[ORDER] {order.orderId} t{order.tableId} '{order.foodName}' prep={prep_s}s")
    await asyncio.sleep(prep_s)

    ready = FoodReady(
        orderId=order.orderId,
        tableId=order.tableId,
        foodName=order.foodName,
        readyAt=time.time(),
        prepMs=prep_s * 1000,
    )
    await client.publish(
        "food/ready",
        json.dumps(ready.model_dump()).encode("utf-8"),
        qos=1
    )
    logger.info(f"[READY] {order.orderId} published")
