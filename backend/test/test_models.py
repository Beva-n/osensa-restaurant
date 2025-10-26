from app.models import Order, FoodReady

def test_order_validation():
    o = Order(orderId="abc", tableId=1, foodName="Burger")
    assert o.type == "ORDER"
    assert o.tableId == 1

def test_food_ready_model():
    f = FoodReady(orderId="abc", tableId=1, foodName="Burger", readyAt=1.0, prepMs=5000)
    assert f.type == "FOOD_READY"