import json
import pytest
from app.handler import handle_order

@pytest.mark.asyncio
async def test_handle_order_happy_path(dummy_client, fast_sleep, fixed_prep):
    payload = {
        "v": 1, "type": "ORDER",
        "orderId": "o-123", "tableId": 4, "foodName": "Burger"
    }
    await handle_order(dummy_client, json.dumps(payload).encode())

    assert len(dummy_client.published) == 1
    topic, raw, qos = dummy_client.published[0]
    assert topic == "food/ready"
    data = json.loads(raw.decode("utf-8"))
    assert data["orderId"] == "o-123"
    assert data["prepMs"] == 3000

@pytest.mark.asyncio
async def test_handle_order_drops_bad_payload(dummy_client, fast_sleep):
    """
    Malformed JSON or wrong fields should be logged and dropped silently
    (no publishes).
    """
    # not JSON
    await handle_order(dummy_client, b"\xff\x00\xff")
    # missing required fields
    await handle_order(dummy_client, json.dumps({"type": "ORDER"}).encode())

    assert dummy_client.published == []



