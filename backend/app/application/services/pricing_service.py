from sqlalchemy.orm import Session
from app.infrastructure.database.models import Order, MenuItem

TAX = 0.12
DELIVERY_COST = 5.00

"""Calculate tax assume 12% BC standard for deliveries. Note round 2 decimal places everywhere"""
def calculate_tax(subtotal: float) -> float:
    return round(subtotal * TAX, 2)

"""Calculate total, assume $5 standard for all deliveries"""
def calculate_total(subtotal: float, tax: float, delivery_cost: float):
    return round(subtotal + tax + delivery_cost, 2)

"""Calculate order total and return as dict all endpoints can be seen at once"""
def calculate_order_total(subtotal: float) -> dict:
    tax = calculate_tax(subtotal)
    total_cost = calculate_total(subtotal, tax, DELIVERY_COST)

    return {"subtotal": subtotal, "tax": tax, "delivery_cost": DELIVERY_COST, "total_cost": total_cost}

def calculate_combined_order_total(db: Session, combined_order_id: str) -> dict | None:
    items = db.query(Order).filter(Order.combined_order_id == combined_order_id).all()
    if not items:
        return None

    subtotal = 0.0
    for item in items:
        menu_item = db.query(MenuItem).filter(MenuItem.restaurant_id == item.restaurant_id, MenuItem.food_item == item.food_item).first()

        if menu_item and menu_item.price is not None:
            subtotal += float(menu_item.price)

    return calculate_order_total(round(subtotal, 2))

def recalculate_and_persist_combined_order_totals(db: Session, combined_order_id: str) -> dict:
    totals = calculate_combined_order_total(db, combined_order_id)
    if totals is None:
        return calculate_order_total(0.0)

    items = db.query(Order).filter(Order.combined_order_id == combined_order_id).all()
    for item in items:
        item.subtotal = totals["subtotal"]
        item.tax = totals["tax"]
        item.delivery_cost = totals["delivery_cost"]
        item.total_cost = totals["total_cost"]

    db.commit()
    return totals
