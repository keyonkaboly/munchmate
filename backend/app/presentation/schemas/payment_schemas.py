from pydantic import BaseModel
from typing import Optional

class PaymentRequest(BaseModel):
    order_id: str
    card_number: str

class PaymentResponse(BaseModel):
    order_id: str
    total_cost: float
    success: bool
    message: str
