from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class OrderCreate(BaseModel):
    customer_id: UUID
    restaurant_id: int
    food_items: List[str] = Field(default=[])
    order_value: float = Field(default=0.0, ge=0)
    
    

    
    