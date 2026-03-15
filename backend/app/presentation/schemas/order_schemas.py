from pydantic import BaseModel
from typing import List

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int


class OrderCreate(BaseModel):
    restaurant_id: int
    items: List[OrderItemCreate]