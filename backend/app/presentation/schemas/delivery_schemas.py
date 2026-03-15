from pydantic import BaseModel
from typing import Optional

class OrderCreate(BaseModel):
    delivery_method: Optional[str] = None
    delivery_distance: Optional[float] = None
    delivery_time: Optional[str] = None
    delivery_time_actual: Optional[float] = None
    delivery_delay: Optional[float] = None
    route_taken: Optional[str] = None
    route_type: Optional[str] = None
    route_efficiency: Optional[float] = None

class OrderResponse(BaseModel):
    order_id: int
    delivery_method: Optional[str] = None
    delivery_distance: Optional[float] = None
    delivery_time: Optional[str] = None
    delivery_time_actual: Optional[float] = None
    delivery_delay: Optional[float] = None
    delivery_status: str
    route_taken: Optional[str] = None
    route_type: Optional[str] = None
    route_efficiency: Optional[float] = None
    model_config = {"from_attributes": True}
    status_updated_at: Optional[str] = None