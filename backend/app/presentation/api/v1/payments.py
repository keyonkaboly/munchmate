from fastapi import APIRouter, Depends, HTTPException
from app.presentation.schemas.payment_schemas import PaymentRequest, PaymentResponse
from app.application.services.payment_service import simulate_payment
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order
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

@router.post("/checkout", response_model=PaymentResponse)
def checkout(data: PaymentRequest, db: Session = Depends(get_db)):
    """Accept mock payment details and trigger simulated payment during checkout."""
    order = db.query(Order).filter(Order.order_id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    result = simulate_payment(data.total_price, data.card_number)
    return PaymentResponse(
        order_id=data.order_id,
        total_price=data.total_price,
        success=result["success"],
        message=result["message"]
    )