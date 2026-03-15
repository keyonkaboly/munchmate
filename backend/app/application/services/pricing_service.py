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

