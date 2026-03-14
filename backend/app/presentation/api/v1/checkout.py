from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.infrastructure.database.database import get_db
from app.application.services.pricing_service import calculate_order_total
from app.infrastructure.database.models import Order
from app.presentation.schemas.cart_schemas import CheckoutRequest, CheckoutResponse

router = APIRouter(prefix="/checkout", tags=["checkout"])

"""Calls calculate method from pricing service and returns checkout totals for order (recalculation endpoint)"""
@router.post("/calculate", response_model = CheckoutResponse)
def checkout_calculate(data: CheckoutRequest, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == data.order_id).first()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found. ")
    
    final_total = calculate_order_total(order.subtotal)

    return{"order_id": order.order_id, "subtotal": final_total["subtotal"], "tax": final_total["tax"], "delivery_cost": final_total["delivery_cost"], "total_cost": final_total["total_cost"]}

"""Calls calculate method"""
@router.post("/orders/{order_id}/place-order", response_model = CheckoutResponse)
def place_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")

    final_total = calculate_order_total(order.subtotal)

    order.subtotal = final_total["subtotal"]
    order.tax = final_total["tax"]
    order.delivery_cost=final_total["delivery_cost"]
    order.total_cost=final_total["total_cost"]

    db.commit()
    db.refresh(order)

    return{"order_id": order.order_id, "subtotal": final_total["subtotal"], "tax": final_total["tax"], "delivery_cost": final_total["delivery_cost"], "total_cost": final_total["total_cost"]}