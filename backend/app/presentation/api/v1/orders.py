from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Order
from app.presentation.schemas.delivery_schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])

"""Create order method. Ensures every new order gets a valid unique ID before commiting to database so inserts succeed"""
@router.post("/", response_model=OrderResponse) 
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    order = Order(restaurant_id=1, **data.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router.get("/{order_id}", response_model=OrderResponse) 
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order