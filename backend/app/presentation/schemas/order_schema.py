from pydantic import BaseModel, Field
from typing import List

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0)
    
class OrderCreate(BaseModel):
    customer_id: int
    restaurant_id: int
    items: List[OrderItemCreate]