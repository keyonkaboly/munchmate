import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order, MenuItem
from app.presentation.schemas.order_schema import StartOrderRequest
import uuid
from app.presentation.schemas.delivery_schemas import OrderCreate, OrderResponse

router_order = APIRouter(prefix="/orders", tags=["orders"])

DELIVERY_METHOD_RANK = {"Walk": 1, "Bike": 2, "Car": 3}
ROUTE_TYPE_RANK = {"Bike-friendly": 1, "Mixed": 2, "Car-only": 3}

def get_most_restrictive_delivery(restaurant_id: int, food_items: list, db: Session) -> dict:
    matching_rows = db.query(Order).filter(
        Order.restaurant_id == restaurant_id,
        Order.food_item.in_(food_items)
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


# helper func
def get_order_or_404(combined_order_id: str, db: Session) -> Order:
    order = db.query(Order).filter(Order.combined_order_id == combined_order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

#helper func - returns all rows/items for one grouped order
def get_order_items_or_404(combined_order_id: str, db: Session):
    items = db.query(Order).filter(Order.combined_order_id == combined_order_id).all()
    if not items:
        raise HTTPException(status_code=404, detail="Order not found")
    return items

#prevents any modification once order is completed
def ensure_order_editable(combined_order_id: str, db: Session):
    items = get_order_items_or_404(combined_order_id, db)
    if items[0].status != "Created":
        raise HTTPException(
            status_code=400,
            detail="This order can no longer be modified"
        )
    return items

# shared validation
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

# order validation
def validate_order(combined_order_id: str, db: Session):
    items = get_order_items_or_404(combined_order_id, db)

    if not items:
        raise HTTPException(status_code=400, detail="Order has no items")

    for item in items:
        validate_menu_item(item.restaurant_id, item.food_item, db)

    return items

@router_order.post("/create")
def create_order(order: StartOrderRequest, db: Session = Depends(get_db)):
   combined_order_id = str(uuid.uuid4())
   
   if not order.food_items:
       raise HTTPException(status_code=400, detail="Order must contain at least one item")
   
   for item in order.food_items:
       validate_menu_item(order.restaurant_id, item, db)

   delivery_method = random.choice(["Walk", "Bike", "Car"])
   delivery_distance = round(random.uniform(1, 8), 2)
   delivery_delay = random.randint(0, 10)
   route_taken = random.choice(["Main Street", "Broadway", "4th Ave"])
   route_type = random.choice(["Bike-friendly", "Mixed", "Car-only"])
   route_efficiency = round(random.uniform(0.7, 0.95), 2)

   for item in order.food_items:
        new_order = Order(
            combined_order_id=combined_order_id,
            restaurant_id=order.restaurant_id,
            food_item=item,
            customer_id=order.customer_id,
            status="Created",
            delivery_method=delivery_method,
            delivery_distance=delivery_distance,
            delivery_delay=delivery_delay,
            route_taken=route_taken,
            route_type=route_type,
            route_efficiency=route_efficiency
        )
        db.add(new_order)
    
   db.commit()

   return {
        "message": "Order created successfully",
        "order_id": combined_order_id,
        "combined_order_id": combined_order_id,
        "food_items": order.food_items,
        "count": len(order.food_items)
    }


@router_order.post("/{order_id}/add-item")
def add_item(order_id: str, food_item: str, db: Session = Depends(get_db)):
    items = ensure_order_editable(order_id, db)
    order = items[0]
    
    validate_menu_item(order.restaurant_id, food_item, db)
    
    new_item = Order(
        combined_order_id=order_id,
        restaurant_id=order.restaurant_id,
        customer_id=order.customer_id,
        food_item=food_item,
        status="Created"
    )
    db.add(new_item)
    db.commit()
    
    all_items = db.query(Order).filter(Order.combined_order_id == order_id).all()
    food_items = [item.food_item for item in all_items]

    return {
        "message": f"'{food_item}' added to order",
        "combined_order_id": order_id,
        "food_items": food_items,
        "count": len(food_items)
    }

@router_order.delete("/{order_id}/remove-item")
def remove_item(order_id: str, food_item: str, db: Session = Depends(get_db)):
    ensure_order_editable(order_id, db)
    
    item = db.query(Order).filter(
        Order.combined_order_id == order_id,
        Order.food_item == food_item
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in order")
    
    db.delete(item)
    db.commit()
    
    remaining_items = db.query(Order).filter(
        Order.combined_order_id == order_id
    ).all()

    food_items = [i.food_item for i in remaining_items]

    return {
        "message": f"'{food_item}' removed from order",
        "combined_order_id": order_id,
        "food_items": food_items,
        "count": len(food_items)
    }


@router_order.patch("/{order_id}/update-item")
def update_item_quantity(order_id: str, food_item: str, quantity: int, db: Session = Depends(get_db)):
    ensure_order_editable(order_id, db)
    
    #this validates that the quanity is positive
    if quantity < 0:
        raise HTTPException(status_code=422, detail="Quantity cannot be negative")
    
    #get all rows for this item in the order
    items = db.query(Order).filter(
        Order.combined_order_id == order_id,
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
                combined_order_id=order_id,
                restaurant_id=items[0].restaurant_id,
                customer_id=items[0].customer_id,
                food_item=food_item,
                status="Created"
            ))
    elif quantity < current_qty:
        for item in items[quantity:]:
            db.delete(item)

    db.commit()
    
    all_items = db.query(Order).filter(
        Order.combined_order_id == order_id
    ).all()

    food_items = [item.food_item for item in all_items]

    return {
        "message": f"'{food_item}' quantity updated to {quantity}",
        "combined_order_id": order_id,
        "food_items": food_items,
        "count": len(food_items)
    }

@router_order.post("/{order_id}/submit")
def submit_order(order_id: str, db: Session = Depends(get_db)):
    ensure_order_editable(order_id, db)
    items = validate_order(order_id, db)

    if items[0].status == "Submitted":
        raise HTTPException(status_code=400, detail="Order already submitted")

    for item in items:
        item.status = "Submitted"

    db.commit()

    return {"message": f"Order {order_id} submitted successfully"}

@router_order.patch("/{order_id}/complete")
def complete_order(order_id: str, db: Session = Depends(get_db)):
    items = get_order_items_or_404(order_id, db)

    if items[0].status != "Submitted":
        raise HTTPException(
            status_code=400,
            detail="Order must be submitted before it can be completed"
        )

    food_items = [item.food_item for item in items]
    delivery_info = get_most_restrictive_delivery(items[0].restaurant_id, food_items, db)

    for item in items:
        item.status = "Completed"
        item.delivery_method = delivery_info["delivery_method"]
        item.delivery_distance = delivery_info["delivery_distance"]
        item.delivery_delay = delivery_info["delivery_delay"]
        item.route_taken = delivery_info["route_taken"]
        item.route_type = delivery_info["route_type"]
        item.route_efficiency = delivery_info["route_efficiency"]

    db.commit()
    return {"message": f"Order {order_id} completed", "delivery_info": delivery_info}

@router_order.patch("/{order_id}/cancel")
def cancel_order(order_id: str, db: Session = Depends(get_db)):
    items = get_order_items_or_404(order_id, db)
    
    if items[0].status in ["Completed", "Canceled"]:
        raise HTTPException(
            status_code=400,
            detail="This order cannot be canceled"
        )

    for item in items:
        item.status = "Canceled"

    db.commit()
    return {"message": f"Order {order_id} canceled"}

@router_order.get("/customer/{customer_id}")
def get_customer_orders(customer_id: str, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()

    if not orders:
        return {
            "customer_id": customer_id,
            "current_orders": [],
            "past_orders": []
        }

    grouped_orders = {}

    for order in orders:
        order_id = order.combined_order_id

        if order_id not in grouped_orders:
            grouped_orders[order_id] = {
                "order_id": order.combined_order_id,
                "restaurant_id": order.restaurant_id,
                "customer_id": order.customer_id,
                "status": order.status,
                "food_items": [],
                "delivery_method": order.delivery_method,
                "delivery_distance": order.delivery_distance,
                "delivery_delay": order.delivery_delay,
                "route_taken": order.route_taken,
                "route_type": order.route_type,
                "route_efficiency": order.route_efficiency
            }

        grouped_orders[order_id]["food_items"].append(order.food_item)

    current_orders = []
    past_orders = []

    for grouped_order in grouped_orders.values():
        if grouped_order["status"] in ["Created", "Submitted"]:
            current_orders.append(grouped_order)
        elif grouped_order["status"] in ["Completed", "Canceled"]:
            past_orders.append(grouped_order)

    return {
        "customer_id": customer_id,
        "current_orders": current_orders,
        "past_orders": past_orders
    }

@router_order.get("/{order_id}", response_model=OrderResponse)
def get_delivery_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter((Order.order_id == order_id) | (Order.combined_order_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.order_id is None:
        order.order_id = order.combined_order_id
    return order