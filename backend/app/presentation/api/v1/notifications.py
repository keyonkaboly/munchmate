"""Module for order notification endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order, Notification, Restaurant, MenuItem

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/order-confirmed")
def notify_order_created(order_id: str, customer_id: int, db: Session = Depends(get_db)):
    """Send a notification when a new order is created."""
    order = db.query(Order).filter(Order.combined_order_id == order_id).first()
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
    order = db.query(Order).filter(Order.combined_order_id == order_id).first()
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
def notify_delivery_status(order_id: str, customer_id: int, db: Session = Depends(get_db)):
    """Send a notification when delivery status changes."""
    order = db.query(Order).filter(Order.combined_order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    status = order.status

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

    notification_list = []
    for n in notifications:
        notification_list.append({
            "id": n.id,
            "order_id": n.order_id,
            "message": n.message,
            "notification_type": n.notification_type,
            "is_read": n.is_read
        })
    return {"notifications": notification_list}


@router.post("/incoming-order")
def notify_incoming_order(order_id: str, restaurant_id: int, db: Session = Depends(get_db)):
    """Send a notification to a restaurant owner when a new order is placed."""
    order = db.query(Order).filter(Order.combined_order_id == order_id).first()
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

    notification_list = []
    for n in notifications:
        notification_list.append({
            "id": n.id,
            "order_id": n.order_id,
            "message": n.message,
            "notification_type": n.notification_type,
            "is_read": n.is_read
        })
    return {"notifications": notification_list}

@router.get("/reorder-suggestions/{customer_id}")
def get_reorder_suggestions(customer_id: int, db: Session = Depends(get_db)):
    """Analyze a customer's recent order history and suggest reorders."""
    customer_orders = (
        db.query(Order)
        .filter(Order.customer_id == customer_id)
        .order_by(Order.id.desc())
        .all()
    )

    if not customer_orders:
        raise HTTPException(status_code=404, detail="No order history found for this customer.")

    seen_restaurants = set()
    recent_orders = []
    for order in customer_orders:
        if order.restaurant_id not in seen_restaurants:
            seen_restaurants.add(order.restaurant_id)
            recent_orders.append(order)

    suggestions = []
    for order in recent_orders:
        restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
        restaurant_name = restaurant.food_item if restaurant else f"Restaurant #{order.restaurant_id}"

        if order.food_item:
            message = f"Craving {order.food_item} again? Reorder from {restaurant_name} with one tap!"
        else:
            message = f"You recently ordered from {restaurant_name}. Want to reorder?"

        notification = Notification(
            customer_id=customer_id,
            order_id=order.combined_order_id or str(order.order_id),
            message=message,
            notification_type="reorder_suggestion"
        )
        db.add(notification)
        db.flush()

        suggestions.append({
            "id": notification.id,
            "restaurant_id": order.restaurant_id,
            "restaurant_name": restaurant_name,
            "order_id": order.combined_order_id or str(order.order_id),
            "message": message,
            "notification_type": "reorder_suggestion",
            "is_read": False
        })

    db.commit()
    return {"customer_id": customer_id, "suggestions": suggestions, "count": len(suggestions)}
