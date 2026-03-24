"""Module for payment processing endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.presentation.schemas.payment_schemas import PaymentRequest, PaymentResponse
from app.application.services.payment_service import simulate_payment
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order, Payment


router = APIRouter(prefix="/payments", tags=["payments"])


def build_payment_response(order_id: str, total_cost: float, result: dict) -> PaymentResponse:
    """Build a payment response from order data and simulation result."""
    return PaymentResponse(
        order_id=order_id,
        total_cost=total_cost,
        success=result["success"],
        message=result["message"]
    )


@router.post("/", response_model=PaymentResponse)
def process_payment(data: PaymentRequest, db: Session = Depends(get_db)):
    """Simulate payment processing using the actual combined order total from the database."""
    orders = db.query(Order).filter(Order.combined_order_id == data.order_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="Order not found")
    total_cost = sum(o.total_cost for o in orders if o.total_cost)
    result = simulate_payment(total_cost, data.card_number)
    if result["success"]:
        payment = Payment(order_id=data.order_id, status="success", amount=int(total_cost))
        db.add(payment)
        db.commit()
    return build_payment_response(data.order_id, total_cost=, result)


@router.post("/checkout", response_model=PaymentResponse)
def checkout(data: PaymentRequest, db: Session = Depends(get_db)):
    """Accept mock payment details and trigger simulated payment during checkout."""
    orders = db.query(Order).filter(Order.combined_order_id == data.order_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="Order not found")
    total_cost = sum(o.total_cost for o in orders if o.total_cost)
    result = simulate_payment(total_cost, data.card_number)
    if result["success"]:
        payment = Payment(order_id=data.order_id, status="success", amount=int(total_cost))
        db.add(payment)
        db.commit()
    return build_payment_response(data.order_id, total_cost, result)


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


@router.post("/retry")
def retry_payment(order_id: str, db: Session = Depends(get_db)):
    """Retry a payment for an order after a previous failed attempt."""
    orders = db.query(Order).filter(Order.combined_order_id == order_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="Order not found")
    total_cost = sum(o.total_cost for o in orders if o.total_cost)
    result = simulate_payment(total_cost, "4111111111111111")
    if result["success"]:
        payment = Payment(order_id=order_id, status="success", amount=int(total_cost))
        db.add(payment)
        db.commit()
    return {"message": result["message"], "order_id": order_id, "payment_status": "success" if result["success"] else "failed"}