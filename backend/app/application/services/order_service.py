from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.infrastructure.database.models import Order, MenuItem
import uuid


DELIVERY_METHOD_RANK = {"Walk": 1, "Bike": 2, "Car": 3}
ROUTE_TYPE_RANK = {"Bike-friendly": 1, "Mixed": 2, "Car-only": 3}


def get_order_or_404(order_id: str, db: Session) -> Order:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def validate_menu_item(restaurant_id: int, food_item: str, db: Session):
    exists = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.food_item == food_item
    ).first()
    if not exists:
        raise HTTPException(
            status_code=404,
            detail=f"'{food_item}' does not exist on this restaurant's menu"
        )


def get_most_restrictive_delivery(restaurant_id: int, food_items: list, db: Session) -> dict:
    matching_rows = db.query(Order).filter(
        Order.restaurant_id == restaurant_id,
        Order.food_item.in_(food_items),
        Order.status == "seeded"
    ).all()

    if not matching_rows:
        return {
            "delivery_method": None,
            "delivery_distance": None,
            "delivery_delay": None,
            "route_taken": None,
            "route_type": None,
            "route_efficiency": None,
        }

    best_method = matching_rows[0].delivery_method
    best_route_type = matching_rows[0].route_type
    max_delay = matching_rows[0].delivery_delay
    max_distance = matching_rows[0].delivery_distance
    min_efficiency = matching_rows[0].route_efficiency
    worst_delay_row = matching_rows[0]

    for row in matching_rows:
        if DELIVERY_METHOD_RANK.get(row.delivery_method, 0) > DELIVERY_METHOD_RANK.get(best_method, 0):
            best_method = row.delivery_method

        if ROUTE_TYPE_RANK.get(row.route_type, 0) > ROUTE_TYPE_RANK.get(best_route_type, 0):
            best_route_type = row.route_type

        if row.delivery_delay is not None and row.delivery_delay > max_delay:
            max_delay = row.delivery_delay
            worst_delay_row = row

        if row.delivery_distance is not None and row.delivery_distance > max_distance:
            max_distance = row.delivery_distance

        if row.route_efficiency is not None and row.route_efficiency < min_efficiency:
            min_efficiency = row.route_efficiency

    return {
        "delivery_method": best_method,
        "delivery_distance": max_distance,
        "delivery_delay": max_delay,
        "route_taken": worst_delay_row.route_taken,
        "route_type": best_route_type,
        "route_efficiency": min_efficiency,
    }


def create_order(restaurant_id: int, food_items: list, order_value: float, customer_id: str, db: Session) -> dict:
    for item in food_items:
        validate_menu_item(restaurant_id, item, db)

    order_id = str(uuid.uuid4())
    delivery_info = get_most_restrictive_delivery(restaurant_id, food_items, db)

    for item in food_items:
        db.add(Order(
            order_id=order_id,
            restaurant_id=restaurant_id,
            food_item=item,
            order_value=order_value,
            customer_id=customer_id,
            delivery_method=delivery_info["delivery_method"],
            delivery_distance=delivery_info["delivery_distance"],
            delivery_delay=delivery_info["delivery_delay"],
            route_taken=delivery_info["route_taken"],
            route_type=delivery_info["route_type"],
            route_efficiency=delivery_info["route_efficiency"],
            status="draft"
        ))

    db.commit()
    return {"message": "Order created successfully", "order_id": order_id}


def add_item(order_id: str, food_item: str, db: Session) -> dict:
    order = get_order_or_404(order_id, db)
    validate_menu_item(order.restaurant_id, food_item, db)

    db.add(Order(
        order_id=order_id,
        restaurant_id=order.restaurant_id,
        customer_id=order.customer_id,
        order_value=order.order_value,
        food_item=food_item,
        status="draft"
    ))
    db.commit()
    return {"message": f"'{food_item}' added to order {order_id}"}


def remove_item(order_id: str, food_item: str, db: Session) -> dict:
    get_order_or_404(order_id, db)

    item = db.query(Order).filter(
        Order.order_id == order_id,
        Order.food_item == food_item
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in order")

    db.delete(item)
    db.commit()
    return {"message": f"'{food_item}' removed from order {order_id}"}


def update_item_quantity(order_id: str, food_item: str, quantity: int, db: Session) -> dict:
    if quantity < 0:
        raise HTTPException(status_code=422, detail="Quantity cannot be negative")

    get_order_or_404(order_id, db)

    items = db.query(Order).filter(
        Order.order_id == order_id,
        Order.food_item == food_item
    ).all()
    if not items:
        raise HTTPException(status_code=404, detail="Item not found in order")

    current_qty = len(items)

    if quantity == 0:
        for item in items:
            db.delete(item)
    elif quantity > current_qty:
        for _ in range(quantity - current_qty):
            db.add(Order(
                order_id=order_id,
                restaurant_id=items[0].restaurant_id,
                customer_id=items[0].customer_id,
                order_value=items[0].order_value,
                food_item=food_item,
                status="draft"
            ))
    elif quantity < current_qty:
        for item in items[quantity:]:
            db.delete(item)

    db.commit()
    return {"message": f"'{food_item}' quantity updated to {quantity}"}


def submit_order(order_id: str, db: Session) -> dict:
    items = db.query(Order).filter(Order.order_id == order_id).all()

    if not items:
        raise HTTPException(status_code=400, detail="Order has no items")

    for item in items:
        validate_menu_item(item.restaurant_id, item.food_item, db)

    if items[0].status == "submitted":
        raise HTTPException(status_code=400, detail="Order already submitted")

    for item in items:
        item.status = "submitted"

    db.commit()
    return {"message": f"Order {order_id} submitted successfully"}