import pytest
import ssl
from asyncio_mqtt import Client
from app.mqtt_client import build_client

def test_build_client_returns_client():
    c = build_client()
    assert isinstance(c, Client)

def test_tls_context_is_set_when_tls_true(monkeypatch):
    import app.mqtt_client as mc
    monkeypatch.setattr(mc, "MQTT_TLS", True, raising=False)

    calls = {}
    import paho.mqtt.client as paho
    def fake_tls_set_context(self, ctx):
        calls["ctx"] = ctx

    monkeypatch.setattr(paho.Client, "tls_set_context", fake_tls_set_context, raising=False)

    client = mc.build_client()

    # Assert: our fake was called with an SSLContext
    assert "ctx" in calls, "tls_set_context was not called"
    assert isinstance(calls["ctx"], ssl.SSLContext)

def test_tls_not_set_when_tls_false(monkeypatch):
    import app.mqtt_client as mc
    monkeypatch.setattr(mc, "MQTT_TLS", False, raising=False)
    calls = {}
    import paho.mqtt.client as paho
    def fake_tls_set_context(self, ctx):
        calls["ctx"] = ctx

    monkeypatch.setattr(paho.Client, "tls_set_context", fake_tls_set_context, raising=False)

    client = mc.build_client()

    assert "ctx" not in calls, "tls_set_context should not be called when MQTT_TLS=False"