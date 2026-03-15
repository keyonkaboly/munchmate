"""Module for payment simulation and confirmation endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order, Payment


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/simulate")
def simulate_payment(order_id: str, amount: int, db: Session = Depends(get_db)):
    """Simulate a payment attempt for an order."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if amount <= 0:
        payment = Payment(order_id=order_id, status="failed", amount=amount)
        db.add(payment)
        db.commit()
        raise HTTPException(status_code=400, detail="Payment failed: amount must be a positive integer")

    payment = Payment(order_id=order_id, status="success", amount=amount)
    db.add(payment)
    db.commit()

    return {"message": "Payment successful", "order_id": order_id, "payment_status": "success"}


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
        "amount": payment.amount,
        "status": "Paid / Confirmed"
    }