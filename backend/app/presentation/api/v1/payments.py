"""Module for payment processing endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.presentation.schemas.payment_schemas import PaymentRequest, PaymentResponse
from app.application.services.payment_service import simulate_payment
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order, Payment

router = APIRouter(prefix="/payments", tags=["payments"])


def build_payment_response(order_id: str, total_price: float, result: dict) -> PaymentResponse:
    return PaymentResponse(
        order_id=order_id,
        total_price=total_price,
        success=result["success"],
        message=result["message"]
    )


@router.post("/", response_model=PaymentResponse)
def process_payment(data: PaymentRequest, db: Session = Depends(get_db)):
    """Simulate payment processing using the actual combined order total from the database."""
    orders = db.query(Order).filter(Order.combined_order_id == data.order_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="Order not found")
    total_price = sum(o.total_cost for o in orders if o.total_cost) or data.total_price
    result = simulate_payment(data.total_price, data.card_number)
    return build_payment_response(data.order_id, data.total_price, result)


@router.post("/checkout", response_model=PaymentResponse)
def checkout(data: PaymentRequest, db: Session = Depends(get_db)):
    """Accept mock payment details and trigger simulated payment during checkout."""
    orders = db.query(Order).filter(Order.combined_order_id == data.order_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="Order not found")
    total_price = sum(o.total_cost for o in orders if o.total_cost) or data.total_price
    result = simulate_payment(data.total_price, data.card_number)
    return build_payment_response(data.order_id, data.total_price, result)

@router.get("/confirmation/{order_id}")
def get_payment_confirmation(order_id: str, db: Session = Depends(get_db)):
    """Return confirmation message if payment was successful for an order."""
    payment = db.query(Payment).filter(
        Payment.order_id == order_id,
        Payment.status == "success"
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="No successful payment found for this order")

    return {
        "message": "Payment confirmed",
        "order_id": order_id,
        "status": "Payment Successful"
    }

@router.get("/failure/{order_id}")
def get_payment_failure(order_id: str, db: Session = Depends(get_db)):
    """Return failure message if payment was rejected for an order."""
    payment = db.query(Payment).filter(
        Payment.order_id == order_id,
        Payment.status == "failed"
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="No failed payment found for this order")
    return {
        "message": "Payment failed",
        "order_id": order_id,
        "reason": "Amount must be a positive integer",
        "status": "Payment rejected, order not placed"
    }


@router.post("/retry")
def retry_payment(order_id: str, amount: int, db: Session = Depends(get_db)):
    """Retry a payment for an order after a previous failed attempt."""
    orders = db.query(Order).filter(Order.combined_order_id == order_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="Order not found")
    if amount <= 0:
        payment = Payment(order_id=order_id, status="failed", amount=amount)
        db.add(payment)
        db.commit()
        raise HTTPException(status_code=400, detail="Retry failed: amount must be a positive integer")
    payment = Payment(order_id=order_id, status="success", amount=amount)
    db.add(payment)
    db.commit()
    return {
        "message": "Retry successful",
        "order_id": order_id,
        "payment_status": "success"
    }
