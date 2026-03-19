from pydantic import BaseModel, Field
from typing import List, Optional

class OrderCreate(BaseModel):
    customer_id: Optional[int] = None
    restaurant_id: int
    food_items: List[str] = Field(default=[])
    order_value: float = Field(default=0.0, ge=0)
    

    
    