"""Module for order notification endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order, Notification


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/order-confirmed")
def notify_order_created(order_id: str, customer_id: int, db: Session = Depends(get_db)):
    """Send a notification when a new order is created."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    notification = Notification(
        customer_id=customer_id,
        order_id=order_id,
        message=f"Your order {order_id} has been confirmed.",
        notification_type="order_confirmed"
    )
    db.add(notification)
    db.commit()

    return {
        "message": f"Order {order_id} confirmed",
        "notification_type": "order_confirmed",
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


@router.post("/incoming-order")
def notify_incoming_order(order_id: str, restaurant_id: int, db: Session = Depends(get_db)):
    """Send a notification to a restaurant owner when a new order is placed."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    notification = Notification(
        customer_id=restaurant_id,
        order_id=order_id,
        message=f"New order {order_id} has been placed at your restaurant.",
        notification_type="incoming_order"
    )
    db.add(notification)
    db.commit()

    return {
        "message": f"New order {order_id} received",
        "notification_type": "incoming_order",
        "restaurant_id": restaurant_id,
        "order_id": order_id
    }


@router.get("/restaurant/{restaurant_id}")
def get_restaurant_notifications(restaurant_id: int, db: Session = Depends(get_db)):
    """Retrieve all incoming order notifications for a restaurant owner."""
    notifications = db.query(Notification).filter(
        Notification.customer_id == restaurant_id,
        Notification.notification_type == "incoming_order"
    ).all()

    if not notifications:
        return {"notifications": [], "message": "No incoming orders found for this restaurant"}

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

@router.post("/order-delivered")
def notify_order_delivered(order_id: str, customer_id: int, db: Session = Depends(get_db)):
    """Send a notification when an order has been delivered."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    notification = Notification(
        customer_id=customer_id,
        order_id=order_id,
        message=f"Your order {order_id} has been delivered. Enjoy your meal!",
        notification_type="order_delivered"
    )
    db.add(notification)
    db.commit()

    return {
        "message": f"Order {order_id} has been delivered",
        "notification_type": "order_delivered",
        "customer_id": customer_id,
        "order_id": order_id
    }