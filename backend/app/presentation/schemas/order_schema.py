from pydantic import BaseModel, Field
from typing import List

class OrderCreate(BaseModel):
    order_id: str
    customer_id: int
    restaurant_id: int
    food_items: List[str]
    order_value: float
    