import time
import pytest
from pydantic import ValidationError
from app.models import Order, FoodReady

def test_order_validation_minimal_ok():
    o = Order(orderId="abc", tableId=1, foodName="Burger")
    assert o.type == "ORDER"
    assert 1 <= o.tableId <= 99
    assert isinstance(o.requestedAt, float)

def test_order_rejects_empty_food():
    with pytest.raises(ValidationError):
        Order(orderId="x", tableId=1, foodName="")

def test_order_rejects_overlong_food():
    with pytest.raises(ValidationError):
        Order(orderId="x", tableId=1, foodName="x" * 999)

def test_order_rejects_out_of_range_table():
    with pytest.raises(ValidationError):
        Order(orderId="x", tableId=0, foodName="Soup")
    with pytest.raises(ValidationError):
        Order(orderId="x", tableId=100, foodName="Soup")

def test_food_ready_model_ok():
    f = FoodReady(orderId="abc", tableId=1, foodName="Burger", readyAt=time.time(), prepMs=5000)
    assert f.type == "FOOD_READY"
    assert f.prepMs == 5000
