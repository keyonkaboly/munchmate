from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order, MenuItem
from app.presentation.schemas.order_schema import StartOrderRequest
import uuid
from app.presentation.schemas.delivery_schemas import OrderCreate, OrderResponse

router_order = APIRouter(prefix="/orders", tags=["orders"])

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
def ensure_order_not_completed(combined_order_id: str, db: Session):
    items = get_order_items_or_404(combined_order_id, db)
    if items[0].status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="Cannot modify a completed order"
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

@router_order.post("/create")
def create_order(order: StartOrderRequest, db: Session = Depends(get_db)):
   combined_order_id = str(uuid.uuid4())
   
   if not order.food_items:
       raise HTTPException(status_code=400, detail="Order must contain at least one item")
   
   # this validate that items exist on the restaurant menu
   for item in order.food_items:
       validate_menu_item(order.restaurant_id, item, db)    

   for item in order.food_items:
        new_order = Order(
            combined_order_id=combined_order_id,
            restaurant_id=order.restaurant_id,
            food_item=item,
            customer_id=order.customer_id
        )
        db.add(new_order)
    
   db.commit()

   return {
        "message": "Order created successfully",
        "order_id": combined_order_id,
        "food_items": order.food_items,
        "count": len(order.food_items)
    }


@router_order.post("/{order_id}/add-item")
def add_item(order_id: str, food_item: str, db: Session = Depends(get_db)):
    items = ensure_order_not_completed(order_id, db)
    order = items[0]
    
    validate_menu_item(order.restaurant_id, food_item, db)
    
    new_item = Order(
        combined_order_id=order_id,
        restaurant_id=order.restaurant_id,
        customer_id=order.customer_id,
        food_item=food_item
    )
    db.add(new_item)
    db.commit()
    return {"message": f"'{food_item}' added to order {order_id}"}



@router_order.delete("/{order_id}/remove-item")
def remove_item(order_id: str, food_item: str, db: Session = Depends(get_db)):
    ensure_order_not_completed(order_id, db)
    
    item = db.query(Order).filter(
        Order.combined_order_id == order_id,
        Order.food_item == food_item
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in order")
    
    db.delete(item)
    db.commit()
    return {"message": f"'{food_item}' removed from order {order_id}"}


@router_order.patch("/{order_id}/update-item")
def update_item_quantity(order_id: str, food_item: str, quantity: int, db: Session = Depends(get_db)):
    ensure_order_not_completed(order_id, db)
    
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
                food_item=food_item
            ))
    elif quantity < current_qty:
        for item in items[quantity:]:
            db.delete(item)

    db.commit()
    return {"message": f"'{food_item}' quantity updated to {quantity}"}

# order validation
def validate_order(order_id: str, db: Session):
    items = db.query(Order).filter(Order.combined_order_id == order_id).all()

    if not items:
        raise HTTPException(status_code=400, detail="Order has no items")

    for item in items:
        validate_menu_item(item.restaurant_id, item.food_item, db)

    return items

@router_order.post("/{order_id}/submit")
def submit_order(order_id: str, db: Session = Depends(get_db)):
    ensure_order_not_completed(order_id, db)
    items = validate_order(order_id, db)

    if items[0].status == "Submitted":
        raise HTTPException(status_code=400, detail="Order already submitted")

    for item in items:
        item.status = "Submitted"

    db.commit()
    return {"message": f"Order {order_id} submitted successfully"}

@router_order.patch("/{order_id}/in-progress")
def mark_order_in_progress(order_id: str, db: Session = Depends(get_db)):
    items = get_order_items_or_404(order_id, db)

    if items[0].status != "Submitted":
        raise HTTPException(
            status_code=400,
            detail="Order must be submitted before it can be in progress"
        )

    for item in items:
        item.status = "In Progress"

    db.commit()
    return {"message": f"Order {order_id} marked as in progress"}

@router_order.patch("/{order_id}/complete")
def complete_order(order_id: str, db: Session = Depends(get_db)):
    items = get_order_items_or_404(order_id, db)

    if items[0].status != "In Progress":
        raise HTTPException(
            status_code=400,
            detail="Order must be in progress before it can be completed"
        )

    for item in items:
        item.status = "Completed"

    db.commit()
    return {"message": f"Order {order_id} completed"}

@router_order.patch("/{order_id}/cancel")
def cancel_order(order_id: str, db: Session = Depends(get_db)):
    ensure_order_not_completed(order_id, db)
    items = get_order_items_or_404(order_id, db)

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
                "food_items": []
            }

        grouped_orders[order_id]["food_items"].append(order.food_item)

    current_orders = []
    past_orders = []

    for grouped_order in grouped_orders.values():
        if grouped_order["status"] in ["Submitted", "In Progress"]:
            current_orders.append(grouped_order)
        elif grouped_order["status"] in ["Completed", "Canceled"]:
            past_orders.append(grouped_order)

    return {
        "customer_id": customer_id,
        "current_orders": current_orders,
        "past_orders": past_orders
    }

@router_order.post("/", response_model=OrderResponse)
def create_delivery_order(data: OrderCreate, db: Session = Depends(get_db)):
    existing_order = db.query(Order).filter(Order.order_id == data.order_id).first()
    if existing_order:
        raise HTTPException(status_code=409, detail="Order ID already exists")
    order = Order(**data.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router_order.get("/{order_id}", response_model=OrderResponse)
def get_delivery_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order