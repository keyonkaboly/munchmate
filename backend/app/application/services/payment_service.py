def simulate_payment(total_cost: float, card_number: str) -> dict:
    if total_cost <= 0:
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