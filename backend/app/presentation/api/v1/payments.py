from fastapi import APIRouter
from app.presentation.schemas.payment_schemas import PaymentRequest, PaymentResponse
from app.application.services.payment_service import simulate_payment

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/", response_model=PaymentResponse)
def process_payment(data: PaymentRequest):
    """Simulate payment processing without a real payment gateway."""
    result = simulate_payment(data.total_price, data.card_number)
    return PaymentResponse(
        order_id=data.order_id,
        total_price=data.total_price,
        success=result["success"],
        message=result["message"]
    )