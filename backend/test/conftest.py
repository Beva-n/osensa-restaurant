import asyncio
import pytest
from typing import Union

class DummyClient:
    """Minimal async client that records publishes."""
    def __init__(self):
        self.published = []

    async def publish(self, topic: str, payload: Union[str, bytes, bytearray], qos: int = 1):
        if isinstance(payload, str):
            payload_bytes = payload.encode("utf-8")
        elif isinstance(payload, (bytes, bytearray)):
            payload_bytes = bytes(payload)
        else:
            raise TypeError("payload must be str|bytes|bytearray")
        self.published.append((topic, payload_bytes, qos))

@pytest.fixture
def dummy_client():
    return DummyClient()

@pytest.fixture
def fast_sleep(monkeypatch):
    async def _noop(_):
        return None
    monkeypatch.setattr(asyncio, "sleep", _noop)
    return _noop

@pytest.fixture
def fixed_prep(monkeypatch):
    # Force deterministic prep time (e.g., 3 seconds)
    monkeypatch.setattr("app.handler.random.randint", lambda a, b: 3)
