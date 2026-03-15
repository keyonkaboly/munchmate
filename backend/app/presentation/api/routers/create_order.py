from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database import models
from app.presentation.schemas.order_schemas import OrderCreate

router_order = APIRouter(prefix="/orders", tags=["orders"])

@router_order.post("/")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):

    # create new order
    new_order = models.Order(
        customer_id=order.customer_id,
        restaurant_id=order.restaurant_id
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # add items to the order
    for item in order.items:

        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.id == item.menu_item_id
        ).first()

        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        order_item = models.OrderItem(
            order_id=new_order.order_id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity
        )

        db.add(order_item)

    db.commit()

    return {
        "message": "Order created successfully",
        "order_id": new_order.order_id
    }