from pydantic import BaseModel
from typing import Optional

class PaymentRequest(BaseModel):
    order_id: str
    card_number: str
    total_cost: Optional[float] = None


class PaymentResponse(BaseModel):
    order_id: str
    total_cost: float
    success: bool
    message: str
