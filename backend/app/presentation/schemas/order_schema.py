from pydantic import BaseModel, Field
from typing import List

class OrderCreate(BaseModel):
    order_id: str
    customer_id: int
    restaurant_id: int
    food_items: List[str] = Field(default=[])
    order_value: float = Field(default=0.0, ge=0)
    

    
    