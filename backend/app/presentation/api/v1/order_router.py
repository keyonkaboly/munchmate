from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order, MenuItem
from app.presentation.schemas.order_schema import OrderCreate

router_order = APIRouter(prefix="/orders", tags=["orders"])

@router_order.post("/create")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
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