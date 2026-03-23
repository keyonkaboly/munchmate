"""Simulates payment processing without a real payment gateway"""
def simulate_payment(total_price: float, card_number: str) -> dict:
    """
    Simulates payment based on predefined rules.
    - Cards ending in 0000 are always declined
    - Orders with total_price <= 0 are rejected
    - Everything else succeeds
    """
    if total_price <= 0:
        return {
            "success": False,
            "message": "Payment failed: invalid order amount"
        }
    if card_number.endswith("0000"):
        return {
            "success": False,
            "message": "Payment failed: card declined"
        }
    return {
        "success": True,
        "message": "Payment successful"
    }