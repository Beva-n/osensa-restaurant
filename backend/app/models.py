# backend/app/models.py
from pydantic import BaseModel, Field, constr
import time

class Order(BaseModel):
    """Inbound order from the UI. Validated at the backend boundary."""
    v: int = 1
    type: constr(pattern=r"^ORDER$") = "ORDER"
    orderId: str
    tableId: int = Field(ge=1, le=4)
    foodName: constr(min_length=1, max_length=80)
    requestedAt: float = Field(default_factory=lambda: time.time())

class FoodReady(BaseModel):
    v: int = 1
    type: constr(pattern=r"^FOOD_READY$") = "FOOD_READY"
    orderId: str
    tableId: int
    foodName: str
    readyAt: float
    prepMs: int
