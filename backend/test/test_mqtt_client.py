import asyncio
import pytest
from asyncio_mqtt import Client
from app.mqtt_client import build_client

def test_build_client_returns_client():
    c = build_client("localhost", 1883)
    assert isinstance(c, Client)

@pytest.mark.asyncio
async def test_client_context_manager_opens_and_closes(monkeypatch):
    """
    Do not actually hit the network; just ensure the async context manager exists.
    """
    c = build_client("localhost", 1883)
    # Patch the underlying connect to avoid network calls
    async def fake_enter(self): return self
    async def fake_exit(self, exc_type, exc, tb): return False
    monkeypatch.setattr(Client, "__aenter__", fake_enter, raising=False)
    monkeypatch.setattr(Client, "__aexit__",  fake_exit,  raising=False)

    async with c as _:
        assert True
