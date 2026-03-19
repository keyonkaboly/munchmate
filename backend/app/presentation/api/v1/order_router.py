from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.presentation.schemas.order_schema import OrderCreate
from app.application.services import order_service

router_order = APIRouter(prefix="/orders", tags=["orders"])


@router_order.post("/create")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return order_service.create_order(
        restaurant_id=order.restaurant_id,
        food_items=order.food_items,
        order_value=order.order_value,
        customer_id=order.customer_id,
        db=db
    )


@router_order.post("/{order_id}/add-item")
def add_item(order_id: str, food_item: str, db: Session = Depends(get_db)):
    return order_service.add_item(order_id=order_id, food_item=food_item, db=db)


@router_order.delete("/{order_id}/remove-item")
def remove_item(order_id: str, food_item: str, db: Session = Depends(get_db)):
    return order_service.remove_item(order_id=order_id, food_item=food_item, db=db)


@router_order.patch("/{order_id}/update-item")
def update_item_quantity(order_id: str, food_item: str, quantity: int, db: Session = Depends(get_db)):
    return order_service.update_item_quantity(order_id=order_id, food_item=food_item, quantity=quantity, db=db)


@router_order.post("/{order_id}/submit")
def submit_order(order_id: str, db: Session = Depends(get_db)):
    return order_service.submit_order(order_id=order_id, db=db)