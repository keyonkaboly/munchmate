"""Module for order notification endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order, Notification


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/order-created")
def notify_order_created(order_id: str, customer_id: int, db: Session = Depends(get_db)):
    """Send a notification when a new order is created."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    notification = Notification(
        customer_id=customer_id,
        order_id=order_id,
        message=f"Your order {order_id} has been confirmed.",
        notification_type="order_created"
    )
    db.add(notification)
    db.commit()

    return {
        "message": f"Order {order_id} confirmed",
        "notification_type": "order_created",
        "customer_id": customer_id
    }


@router.post("/order-cancelled")
def notify_order_cancelled(order_id: str, customer_id: int, db: Session = Depends(get_db)):
    """Send a notification when an order is cancelled."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    notification = Notification(
        customer_id=customer_id,
        order_id=order_id,
        message=f"Your order {order_id} has been cancelled.",
        notification_type="order_cancelled"
    )
    db.add(notification)
    db.commit()

    return {
        "message": f"Order {order_id} has been cancelled",
        "notification_type": "order_cancelled",
        "customer_id": customer_id
    }

@router.post("/delivery-status")
def notify_delivery_status(order_id: str, customer_id: int, status: str, db: Session = Depends(get_db)):
    """Send a notification when delivery status changes."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    notification = Notification(
        customer_id=customer_id,
        order_id=order_id,
        message=f"Your order {order_id} status has changed to: {status}",
        notification_type="delivery_status"
    )
    db.add(notification)
    db.commit()

    return {
        "message": f"Order {order_id} status updated to {status}",
        "notification_type": "delivery_status",
        "customer_id": customer_id,
        "status": status
    }