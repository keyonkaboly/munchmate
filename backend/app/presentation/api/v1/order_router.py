from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order, MenuItem, OrderItem
from app.presentation.schemas.order_schema import OrderCreate

router_order = APIRouter(prefix="/orders", tags=["orders"])

@router_order.post("/create")
def create_order_with_items(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(
        customer_id=order.customer_id,
        restaurant_id=order.restaurant_id
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in order.items:
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item.menu_item_id
        ).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        db.add(OrderItem(
            order_id=new_order.order_id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity
        ))

    db.commit()
    return {"message": "Order created successfully", "order_id": new_order.order_id}