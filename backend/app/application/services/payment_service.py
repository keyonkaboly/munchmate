"""Simulates payment processing without a real payment gateway"""
def simulate_payment(total_price: float, card_number: str) -> dict:
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