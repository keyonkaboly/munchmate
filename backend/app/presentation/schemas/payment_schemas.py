from pydantic import BaseModel

class PaymentRequest(BaseModel):
    order_id: int
    total_price: float
    card_number: str

class PaymentResponse(BaseModel):
    order_id: int
    total_price: float
    success: bool
    message: str
