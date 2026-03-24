from pydantic import BaseModel

class PaymentRequest(BaseModel):
    order_id: str
    total_cost: float
    card_number: str

class PaymentResponse(BaseModel):
    order_id: str
    total_cost: float
    success: bool
    message: str
