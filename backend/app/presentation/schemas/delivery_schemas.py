from pydantic import BaseModel
from typing import Optional

class OrderCreate(BaseModel):
    order_id: str
    restaurant_id: int
    delivery_method: Optional[str] = None
    delivery_distance: Optional[float] = None
    delivery_time: Optional[str] = None
    delivery_time_actual: Optional[float] = None
    delivery_delay: Optional[float] = None
    route_taken: Optional[str] = None
    route_type: Optional[str] = None
    route_efficiency: Optional[float] = None

class OrderResponse(BaseModel):
    order_id: str
    delivery_method: Optional[str] = None
    delivery_distance: Optional[float] = None
    delivery_time: Optional[str] = None
    delivery_time_actual: Optional[float] = None
    delivery_delay: Optional[float] = None
    route_taken: Optional[str] = None
    route_type: Optional[str] = None
    route_efficiency: Optional[float] = None
    model_config = {"from_attributes": True}