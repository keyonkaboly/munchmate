from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order, MenuItem
from app.presentation.schemas.order_schema import OrderCreate

router_order = APIRouter(prefix="/orders", tags=["orders"])

# helper func
def get_order_or_404(order_id: str, db: Session) -> Order:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# shared validation
def validate_menu_item(restaurant_id: str, food_item: str, db: Session):
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
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
   
   # this validate that items exist on the restaurant menu
    for item in order.food_items:
        validate_menu_item(order.restaurant_id, item, db)
   
    created_orders = []
    
    for item in order.food_items:
        new_order = Order(
            order_id=order.order_id,
            restaurant_id=order.restaurant_id,
            food_item=item,
            order_value=order.order_value,
            customer_id=order.customer_id
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        created_orders.append(new_order.order_id)

    return {"message": "Order created successfully", "order_ids": created_orders}


@router_order.post("/{order_id}/add-item")
def add_item(order_id: str, food_item: str, db: Session = Depends(get_db)):
    order = get_order_or_404(order_id, db)
    
    validate_menu_item(order.restaurant_id, food_item, db)
    
    new_item = Order(
        order_id=order_id,
        restaurant_id=order.restaurant_id,
        customer_id=order.customer_id,
        order_value=order.order_value,
        food_item=food_item
    )
    db.add(new_item)
    db.commit()
    return {"message": f"'{food_item}' added to order {order_id}"}



@router_order.delete("/{order_id}/remove-item")
def remove_item(order_id: str, food_item: str, db: Session = Depends(get_db)):
    order = get_order_or_404(order_id, db)
    
    item = db.query(Order).filter(
        Order.order_id == order_id,
        Order.food_item == food_item
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in order")
    
    db.delete(item)
    db.commit()
    return {"message": f"'{food_item}' removed from order {order_id}"}


@router_order.patch("/{order_id}/update-item")
def update_item_quantity(order_id: str, food_item: str, quantity: int, db: Session = Depends(get_db)):
    order = get_order_or_404(order_id, db)
    
    #this validates that the quanity is positive
    if quantity < 0:
        raise HTTPException(status_code=422, detail="Quantity cannot be negative")
    
    # Get all rows for this item in the order
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
                food_item=food_item
            ))
    elif quantity < current_qty:
       
        for item in items[quantity:]:
            db.delete(item)

    db.commit()
    return {"message": f"'{food_item}' quantity updated to {quantity}"}

# order validation
def validate_order(order_id: str, db: Session):
    items = db.query(Order).filter(Order.order_id == order_id).all()

    if not items:
        raise HTTPException(status_code=400, detail="Order has no items")

    for item in items:
        validate_menu_item(item.restaurant_id, item.food_item, db)

    return items

@router_order.post("/{order_id}/submit")
def submit_order(order_id: str, db: Session = Depends(get_db)):
    items = validate_order(order_id, db)

    if items[0].status == "submitted":
        raise HTTPException(status_code=400, detail="Order already submitted")

    for item in items:
        item.status = "submitted"

    db.commit()
    return {"message": f"Order {order_id} submitted successfully"}