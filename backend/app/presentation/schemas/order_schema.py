from pydantic import BaseModel, Field
from typing import List

class OrderCreate(BaseModel):
    order_id: str
    customer_id: int
    restaurant_id: int
    food_items: List[str] = Field(default=[])

class StartOrderRequest(BaseModel):
    customer_id: int
    restaurant_id: int
    food_items: List[str] = Field(default=[])


class EarlyCancelRefundResponse(BaseModel):
    message: str
    order_id: str
    refund_amount: float

    