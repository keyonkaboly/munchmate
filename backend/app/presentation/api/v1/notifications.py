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

@router.get("/history/{customer_id}")
def get_notification_history(customer_id: int, db: Session = Depends(get_db)):
    """Retrieve all notifications for a specific customer."""
    notifications = db.query(Notification).filter(
        Notification.customer_id == customer_id
    ).all()

    if not notifications:
        return {"notifications": [], "message": "No notifications found for this customer"}

    return {
        "notifications": [
            {
                "id": n.id,
                "order_id": n.order_id,
                "message": n.message,
                "notification_type": n.notification_type,
                "is_read": n.is_read
            }
            for n in notifications
        ]
    }